"""
FastAPI Backend for Voice AI Restaurant Agent
Integrates with Square Sandbox and Vapi webhooks
"""

import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from square import Square
from square.client import SquareEnvironment
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Settings
class Settings(BaseSettings):
    square_access_token: str = Field(..., alias="SQUARE_ACCESS_TOKEN")
    square_location_id: str = Field(..., alias="SQUARE_LOCATION_ID")
    vapi_api_key: str = Field(..., alias="VAPI_API_KEY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

# Initialize Square Client with Sandbox environment
square_client = Square(
    token=settings.square_access_token,
    environment=SquareEnvironment.SANDBOX
)

# FastAPI app
app = FastAPI(
    title="Voice AI Restaurant Agent",
    description="B2C Voice AI Waiter backend with Square integration",
    version="1.0.0"
)


# Pydantic Models
class MenuItem(BaseModel):
    """Simplified menu item representation"""
    id: str
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None


class OrderItem(BaseModel):
    """Order item for Square Orders API"""
    catalog_object_id: str
    quantity: str
    modifiers: Optional[List[Dict[str, Any]]] = None


class OrderRequest(BaseModel):
    """Order request from Vapi"""
    items: List[OrderItem]
    customer_name: Optional[str] = None
    special_instructions: Optional[str] = None


class VapiWebhook(BaseModel):
    """Vapi webhook payload"""
    type: str
    message: Optional[Dict[str, Any]] = None
    call: Optional[Dict[str, Any]] = None
    function_call: Optional[Dict[str, Any]] = None
    toolCall: Optional[Dict[str, Any]] = None
    toolCalls: Optional[List[Dict[str, Any]]] = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "service": "Voice AI Restaurant Agent"}


@app.get("/menu", response_model=List[MenuItem])
async def get_menu():
    """
    Fetches catalog from Square Sandbox and returns simplified JSON
    of items, prices, and descriptions for RAG/Context
    """
    try:
        # Fetch catalog from Square
        catalog_api = square_client.catalog
        result = catalog_api.list()
        
        # The list() method returns a SyncPager, iterate to get results
        catalog_objects = []
        for page in result:
            if hasattr(page, 'body') and page.body:
                page_objects = page.body.get('objects', [])
                catalog_objects.extend(page_objects)
            elif isinstance(page, dict):
                catalog_objects.extend(page.get('objects', []))
        
        menu_items = []
        
        # Process catalog objects
        for obj in catalog_objects:
            obj_type = obj.get('type')
            
            # Only process ITEM type objects
            if obj_type == 'ITEM':
                item_data = obj.get('item_data', {})
                variations = item_data.get('variations', [])
                
                # Process each variation (size/type variant)
                for variation in variations:
                    var_data = variation.get('item_variation_data', {})
                    
                    # Get pricing if available
                    price = None
                    if 'price_money' in var_data:
                        price_money = var_data.get('price_money', {})
                        amount = price_money.get('amount', 0)
                        # Square stores prices in cents
                        price = amount / 100 if amount else None
                    
                    menu_item = MenuItem(
                        id=variation.get('id', ''),
                        name=item_data.get('name', 'Unknown Item'),
                        description=item_data.get('description'),
                        price=price,
                        category=item_data.get('category_id')
                    )
                    menu_items.append(menu_item)
        
        logger.info(f"Fetched {len(menu_items)} menu items from Square")
        return menu_items
        
    except Exception as e:
        logger.error(f"Error fetching menu: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching menu: {str(e)}")


@app.post("/vapi-webhook")
async def vapi_webhook(request: Request):
    """
    Receives webhooks from Vapi
    Handles 'tool-calls', 'function-call', and 'end-of-call-report' events
    """
    try:
        payload = await request.json()
        logger.info(f"Received Vapi webhook: {payload.get('type', 'unknown')}")
        
        webhook_type = payload.get('type')
        
        # Handle tool-calls (primary method for Vapi function tools)
        if webhook_type == 'tool-calls':
            tool_calls = payload.get('toolCalls', [])
            if not tool_calls:
                # Fallback to single toolCall if present
                tool_call = payload.get('toolCall')
                if tool_call:
                    tool_calls = [tool_call]
            
            responses = []
            for tool_call in tool_calls:
                tool_name = tool_call.get('function', {}).get('name') if isinstance(tool_call.get('function'), dict) else tool_call.get('name')
                
                if tool_name == 'place_order':
                    # Extract parameters from tool call
                    if isinstance(tool_call.get('function'), dict):
                        parameters = tool_call['function'].get('parameters', {})
                    else:
                        parameters = tool_call.get('parameters', {})
                    
                    # Parse order items from parameters
                    order_items = []
                    if 'items' in parameters:
                        for item in parameters['items']:
                            # Map item_id to catalog_object_id for Square
                            catalog_object_id = item.get('item_id') or item.get('catalog_object_id')
                            if not catalog_object_id:
                                logger.warning(f"Missing item_id in order item: {item}")
                                continue
                            
                            # Process modifiers if present
                            modifiers = None
                            if item.get('modifiers'):
                                modifiers = item['modifiers']
                            
                            order_items.append(OrderItem(
                                catalog_object_id=catalog_object_id,
                                quantity=str(item.get('quantity', '1')),
                                modifiers=modifiers
                            ))
                    
                    if not order_items:
                        error_msg = "No valid items found in order"
                        logger.error(error_msg)
                        return JSONResponse(
                            status_code=400,
                            content={
                                "error": error_msg,
                                "message": "I apologize, but I couldn't process your order. Please try again or speak with a staff member."
                            }
                        )
                    
                    # Create order in Square
                    try:
                        order_result = await create_square_order(order_items, parameters)
                        order_id = order_result.get('order_id', 'N/A')
                        total_money = order_result.get('total_money', {})
                        total_amount = total_money.get('amount', 0) / 100 if total_money.get('amount') else 0
                        
                        # Return confirmation message for AI to speak
                        confirmation_message = f"Great! I've placed your order. Your order number is {order_id[-8:]}."
                        if total_amount > 0:
                            confirmation_message += f" Your total comes to ${total_amount:.2f}."
                        confirmation_message += " Your order will be ready shortly. Is there anything else I can help you with?"
                        
                        responses.append({
                            "toolCallId": tool_call.get('id') or tool_call.get('toolCallId'),
                            "result": confirmation_message,
                            "error": None
                        })
                        
                        logger.info(f"Order placed successfully: {order_id}")
                        
                    except Exception as order_error:
                        logger.error(f"Error creating order: {str(order_error)}")
                        error_message = "I apologize, but there was an issue processing your order. Please try again or speak with a staff member for assistance."
                        responses.append({
                            "toolCallId": tool_call.get('id') or tool_call.get('toolCallId'),
                            "result": None,
                            "error": error_message
                        })
                else:
                    logger.info(f"Unhandled tool call: {tool_name}")
                    responses.append({
                        "toolCallId": tool_call.get('id') or tool_call.get('toolCallId'),
                        "result": f"Tool {tool_name} received but not handled",
                        "error": None
                    })
            
            return JSONResponse(content={"responses": responses})
        
        # Legacy function-call support
        elif webhook_type == 'function-call':
            function_call = payload.get('functionCall', {})
            function_name = function_call.get('name')
            
            if function_name == 'order_placed' or function_name == 'place_order':
                parameters = function_call.get('parameters', {})
                
                order_items = []
                if 'items' in parameters:
                    for item in parameters['items']:
                        catalog_object_id = item.get('item_id') or item.get('catalog_object_id')
                        if not catalog_object_id:
                            continue
                        
                        order_items.append(OrderItem(
                            catalog_object_id=catalog_object_id,
                            quantity=str(item.get('quantity', '1')),
                            modifiers=item.get('modifiers')
                        ))
                
                if order_items:
                    order_result = await create_square_order(order_items, parameters)
                    return JSONResponse(content={
                        "status": "success",
                        "message": "Order processed successfully",
                        "order_id": order_result.get('order_id') if order_result else None
                    })
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"status": "error", "message": "No valid items in order"}
                    )
            
            else:
                logger.info(f"Unhandled function call: {function_name}")
                return JSONResponse(content={"status": "received", "function": function_name})
        
        elif webhook_type == 'end-of-call-report':
            # Handle end of call report
            call_data = payload.get('call', {})
            logger.info(f"Call ended: {call_data.get('id', 'unknown')}")
            return JSONResponse(content={"status": "received", "type": "end-of-call-report"})
        
        else:
            logger.info(f"Received webhook type: {webhook_type}")
            return JSONResponse(content={"status": "received", "type": webhook_type})
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")


async def create_square_order(
    items: List[OrderItem],
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Creates a 'Proposed' order in Square Sandbox using Orders API
    """
    try:
        orders_api = square_client.orders
        
        # Build line items for Square Orders API
        line_items = []
        for item in items:
            line_item = {
                "quantity": item.quantity,
                "catalog_object_id": item.catalog_object_id,
                "catalog_version": None  # Use latest version
            }
            
            if item.modifiers:
                line_item["modifiers"] = item.modifiers
            
            line_items.append(line_item)
        
        # Create order request
        order_request = {
            "idempotency_key": f"voice-order-{os.urandom(8).hex()}",
            "order": {
                "location_id": settings.square_location_id,
                "reference_id": metadata.get('customer_name') if metadata else None,
                "line_items": line_items,
                "state": "DRAFT"  # Draft order state (will be opened later)
            }
        }
        
        # Add special instructions if provided
        if metadata and metadata.get('special_instructions'):
            order_request["order"]["note"] = metadata.get('special_instructions')
        
        # Create order in Square
        result = orders_api.create_order(order_request)
        
        if not result.is_success():
            logger.error(f"Square Orders API error: {result.errors}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create order: {result.errors}"
            )
        
        order = result.body.get('order', {})
        logger.info(f"Order created successfully: {order.get('id')}")
        
        return {
            "order_id": order.get('id'),
            "state": order.get('state'),
            "total_money": order.get('total_money')
        }
        
    except Exception as e:
        logger.error(f"Error creating Square order: {str(e)}")
        raise


@app.get("/orders/recent")
async def get_recent_orders(limit: int = 3):
    """
    Retrieves the last N orders from Square Sandbox
    Useful for verifying that orders are being created successfully
    """
    try:
        orders_api = square_client.orders
        
        # Search for orders at the location
        # Square's search method takes keyword arguments with query as dict
        query_dict = {
            "filter": {
                "state_filter": {
                    "states": ["OPEN", "COMPLETED", "CANCELED", "DRAFT"]
                }
            },
            "sort": {
                "sort_field": "CREATED_AT",
                "sort_order": "DESC"
            }
        }
        
        result = orders_api.search(
            location_ids=[settings.square_location_id],
            query=query_dict,
            limit=limit
        )
        
        # Handle the response (may be SyncPager or direct response)
        orders = []
        if hasattr(result, 'body'):
            orders = result.body.get('orders', [])
        elif hasattr(result, '__iter__'):
            # It's a pager, iterate through pages
            for page in result:
                if hasattr(page, 'body') and page.body:
                    orders.extend(page.body.get('orders', []))
                elif isinstance(page, dict):
                    orders.extend(page.get('orders', []))
        else:
            # Try direct access
            orders = result.get('orders', []) if isinstance(result, dict) else []
        
        # Format orders for response
        formatted_orders = []
        for order in orders:
            order_id = order.get('id', 'N/A')
            state = order.get('state', 'UNKNOWN')
            created_at = order.get('created_at', 'N/A')
            total_money = order.get('total_money', {})
            total_amount = total_money.get('amount', 0) / 100 if total_money.get('amount') else 0
            currency = total_money.get('currency', 'USD')
            
            # Extract line items
            line_items = []
            for line_item in order.get('line_items', []):
                item_info = {
                    "name": line_item.get('name', 'Unknown Item'),
                    "quantity": line_item.get('quantity', '0'),
                    "catalog_object_id": line_item.get('catalog_object_id', 'N/A')
                }
                # Get price if available
                if 'base_price_money' in line_item:
                    price = line_item['base_price_money'].get('amount', 0) / 100
                    item_info["price"] = price
                line_items.append(item_info)
            
            formatted_orders.append({
                "order_id": order_id,
                "state": state,
                "created_at": created_at,
                "total_amount": total_amount,
                "currency": currency,
                "line_items": line_items,
                "reference_id": order.get('reference_id'),
                "note": order.get('note')
            })
        
        logger.info(f"Retrieved {len(formatted_orders)} recent orders")
        
        return JSONResponse(content={
            "status": "success",
            "count": len(formatted_orders),
            "orders": formatted_orders
        })
        
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving orders: {str(e)}")


@app.post("/order")
async def create_order(order_request: OrderRequest):
    """
    Direct endpoint to create an order (for testing)
    """
    try:
        metadata = {
            "customer_name": order_request.customer_name,
            "special_instructions": order_request.special_instructions
        }
        
        result = await create_square_order(order_request.items, metadata)
        return JSONResponse(content={"status": "success", "order": result})
        
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
