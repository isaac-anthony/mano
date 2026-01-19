# Vapi Setup Guide

This guide walks you through configuring Vapi to connect with your FastAPI backend server.

## Prerequisites

- ✅ FastAPI server running locally on port 8000
- ✅ ngrok tunnel active (e.g., `https://[id].ngrok-free.app`)
- ✅ Vapi account created and logged in

## Step 1: Configure Server URL in Vapi Dashboard

1. **Navigate to Vapi Dashboard**
   - Go to [https://dashboard.vapi.ai](https://dashboard.vapi.ai)
   - Log in to your account

2. **Access Server Settings**
   - In the left sidebar, click on **"Servers"** or **"Settings"** → **"Servers"**
   - Click **"Create Server"** or edit an existing server

3. **Set Server URL**
   - In the **"Server URL"** field, paste your ngrok URL with the webhook endpoint:
     ```
     https://[your-ngrok-id].ngrok-free.app/vapi-webhook
     ```
   - Example: `https://abc123def456.ngrok-free.app/vapi-webhook`
   - **Important:** Make sure to include `/vapi-webhook` at the end
   - Click **"Save"** or **"Create"**

4. **Note the Server ID**
   - After creating/saving, note the Server ID (you'll need this when creating your Assistant)

## Step 2: Create the `place_order` Tool

1. **Navigate to Tools**
   - In the left sidebar, click on **"Tools"** or **"Functions"**
   - Click **"Create Tool"** or **"Add Function"**

2. **Import Tool Schema**
   - Select **"Import from JSON"** or **"JSON Schema"** option
   - Open the `vapi_tool_configuration.json` file from this project
   - Copy the entire JSON content
   - Paste it into the Vapi tool configuration editor
   - OR manually configure:
     - **Name:** `place_order`
     - **Type:** `function`
     - **Description:** "Places an order with the restaurant. Use this when the customer confirms they want to place their order."
     - **Parameters:** Copy the `parameters` object from `vapi_tool_configuration.json`

3. **Configure Tool Settings**
   - **Server:** Select the server you created in Step 1
   - **Async:** Leave unchecked (synchronous execution)
   - **Function Name:** `place_order` (must match the name in the schema)

4. **Save the Tool**
   - Click **"Save"** or **"Create"**
   - Note the Tool ID if provided

## Step 3: Create or Configure Your Assistant

1. **Navigate to Assistants**
   - In the left sidebar, click on **"Assistants"**
   - Click **"Create Assistant"** or edit an existing one

2. **Basic Configuration**
   - **Name:** "Restaurant Waiter" (or your preferred name)
   - **Model:** Select your preferred voice model (e.g., GPT-4, Claude, etc.)
   - **Voice:** Choose a voice for the AI waiter

3. **Add System Prompt**
   - In the **"System Prompt"** or **"Instructions"** field, paste the content from `system_prompt.txt`
   - This defines the waiter persona and behavior

4. **Attach the Tool**
   - Scroll to the **"Tools"** or **"Functions"** section
   - Click **"Add Tool"** or **"Add Function"**
   - Select the `place_order` tool you created in Step 2
   - The tool should now appear in your assistant's available tools

5. **Configure Server (if required)**
   - In the **"Server"** or **"Webhook"** section, select the server you created in Step 1
   - This ensures webhooks are sent to your FastAPI backend

6. **Save Assistant**
   - Click **"Save"** or **"Create"**
   - Note the Assistant ID or Phone Number

## Step 4: Test the Connection

1. **Verify ngrok is Running**
   - Check that your ngrok tunnel is active
   - Note the current ngrok URL (it may have changed)

2. **Update Server URL if Needed**
   - If your ngrok URL changed, update it in Vapi Dashboard → Servers
   - Make sure the URL ends with `/vapi-webhook`

3. **Run Test Script**
   - Use the `test_vapi_connection.py` script to send a mock tool-call
   - This verifies the connection without making a phone call
   - See the script output for success/error messages

4. **Check Square Sandbox**
   - Use the `/orders/recent` endpoint or run the verification script
   - Verify that test orders appear in your Square Sandbox dashboard

## Step 5: Make a Test Call

1. **Get Phone Number**
   - In your Assistant settings, note the phone number assigned
   - Or configure a phone number in Vapi settings

2. **Make a Test Call**
   - Call the phone number from your device
   - Test the conversation flow:
     - Ask about menu items
     - Place an order (e.g., "I'd like 1 burger and 1 coke")
     - Confirm the order
   - The AI should call the `place_order` tool automatically

3. **Monitor Logs**
   - Watch your FastAPI server logs for incoming webhooks
   - Check the ngrok web interface for request logs
   - Verify orders appear in Square Sandbox

## Troubleshooting

### Webhook Not Receiving Requests
- ✅ Verify ngrok is running: `ngrok http 8000`
- ✅ Check the Server URL in Vapi includes `/vapi-webhook`
- ✅ Ensure FastAPI server is running: `uvicorn main:app --reload`
- ✅ Test with `test_vapi_connection.py` script

### Tool Not Being Called
- ✅ Verify the tool is attached to your Assistant
- ✅ Check the tool name matches exactly: `place_order`
- ✅ Review the system prompt to ensure it instructs the AI to use the tool
- ✅ Check Vapi call logs in the dashboard

### Orders Not Appearing in Square
- ✅ Verify Square credentials in `.env` file
- ✅ Check Square Sandbox location ID is correct
- ✅ Review FastAPI server logs for Square API errors
- ✅ Use `/orders/recent` endpoint to check recent orders

### ngrok URL Changed
- ✅ Update the Server URL in Vapi Dashboard
- ✅ Restart ngrok and update the URL immediately
- ✅ Consider using ngrok's static domain (paid feature) for stability

## Next Steps

After successful setup:
1. Test with real phone calls
2. Monitor order creation in Square Sandbox
3. Refine the system prompt based on conversation quality
4. Add error handling and logging improvements
5. Consider production deployment with a static domain
