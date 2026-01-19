# Quick Start Guide

## ✅ Installation Complete!

ngrok has been installed and configured. You're ready to start!

## 🚀 Starting the System

### Step 1: Start FastAPI Server

In your first terminal window:

```bash
# Make sure you're in the project directory
cd /Users/isaacgutierrez/Cursor/Mano.ai

# Activate virtual environment (if you have one)
# source venv/bin/activate  # Uncomment if using venv

# Install dependencies (if not already done)
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
```

The server will run on `http://localhost:8000`

### Step 2: Start ngrok Tunnel

In a **second terminal window**:

```bash
# Navigate to project directory
cd /Users/isaacgutierrez/Cursor/Mano.ai

# Option 1: Use the helper script
./start_ngrok.sh

# Option 2: Run directly
./ngrok http 8000
```

You'll see output like:
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

**Copy the HTTPS URL** (e.g., `https://abc123.ngrok-free.app`)

### Step 3: Configure Vapi Dashboard

1. Go to [Vapi Dashboard](https://dashboard.vapi.ai)
2. Navigate to **Servers** → Create/Edit Server
3. Set **Server URL** to: `https://abc123.ngrok-free.app/vapi-webhook`
   (Replace with your actual ngrok URL)
4. Save the server

### Step 4: Test the Connection

Run the test script:

```bash
# Set your ngrok URL
export NGROK_URL=https://abc123.ngrok-free.app

# Run the test
python test_vapi_connection.py
```

## 📋 Useful Commands

### Check Recent Orders
```bash
curl http://localhost:8000/orders/recent
```

### View Menu Items
```bash
curl http://localhost:8000/menu
```

### Health Check
```bash
curl http://localhost:8000/
```

## 🔧 Troubleshooting

### ngrok URL Changed?
- Update the Server URL in Vapi Dashboard
- Update `NGROK_URL` environment variable for testing

### Port Already in Use?
- Make sure port 8000 is available
- Or change the port in `main.py` and update ngrok accordingly

### Can't Connect?
- Verify FastAPI server is running: `curl http://localhost:8000/`
- Verify ngrok is running: Check the ngrok web interface at `http://127.0.0.1:4040`
- Check firewall settings

## 📚 Next Steps

1. Follow `VAPI_SETUP_GUIDE.md` for complete Vapi configuration
2. Test with `test_vapi_connection.py`
3. Make a real test call through Vapi
4. Monitor orders with `GET /orders/recent`

## 🎉 You're All Set!

Your system is ready for testing. Good luck! 🚀
