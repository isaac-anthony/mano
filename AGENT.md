# Voice AI Restaurant Agent

## Project Goal
B2C Voice AI Waiter for restaurants. This system enables customers to place orders via voice interaction through Vapi orchestration, with orders processed through Square POS/Menu backend.

## Tech Stack
- **FastAPI**: Backend API framework
- **Vapi**: Voice AI orchestration platform
- **Square SDK**: POS/Menu backend integration
- **Pydantic**: Data validation and settings management
- **Uvicorn**: ASGI server for FastAPI

## Current Status
Integration & Testing Phase. Backend is initialized and Square Sandbox connection is established. Webhook endpoint configured to handle Vapi tool calls. Vapi setup guide and testing scripts created. Ready for end-to-end testing with ngrok tunnel.

### Integration Details
- **ngrok URL**: Configured in Vapi Dashboard (see `VAPI_SETUP_GUIDE.md`)
- **Webhook Endpoint**: `/vapi-webhook` receiving `tool-calls` from Vapi
- **Mock Test**: Use `test_vapi_connection.py` to verify connection without phone calls
- **Order Verification**: Use `GET /orders/recent` to check last 3 orders in Square Sandbox

## Environment Configuration
The project uses Square Sandbox credentials for development and testing. Sandbox keys should be stored in `.env` file (see `.env.example` for template). **Do not hardcode credentials in the codebase.**

## Architecture Overview
- **GET /menu**: Fetches catalog from Square Sandbox and returns simplified JSON (items, prices, descriptions) for RAG/Context
- **POST /vapi-webhook**: Receives webhooks from Vapi (tool-calls, function-call events, and end-of-call-report)
- **Order Processing**: When AI triggers `place_order` tool call, server creates a "Proposed" order in Square Sandbox using Orders API and returns a confirmation message for the AI to speak

## Vapi Function Tool Schema

The `place_order` function tool is defined in `vapi_tool_configuration.json`. This tool allows the AI assistant to place orders when customers confirm their selections.

### Tool Schema Structure:
- **Name**: `place_order`
- **Parameters**:
  - `items` (required): Array of order items
    - `item_id` (required): Square catalog object ID (variation ID)
    - `quantity` (required): Quantity as a string
    - `modifiers` (optional): Array of modifier objects for customizations (e.g., "no onions", "extra cheese")
      - Each modifier has `catalog_object_id` and `name`

### Webhook Flow:
1. Customer confirms order via voice
2. Vapi AI calls `place_order` tool with order details
3. Vapi sends `tool-calls` webhook to `/vapi-webhook`
4. Server processes order and creates "PROPOSED" order in Square
5. Server returns confirmation message that AI speaks to customer

## Next Steps
1. Complete Square Sandbox integration
2. Implement order validation and processing
3. Set up Vapi webhook handlers
4. Add error handling and logging
5. Prepare menu data for RAG/Context injection
