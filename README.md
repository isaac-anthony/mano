# Voice AI Restaurant Agent

B2C Voice AI Waiter for restaurants using Vapi orchestration and Square POS backend.

## 🚀 Quick Start

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Create `.env` file:**
   ```
   SQUARE_ACCESS_TOKEN=your_square_sandbox_access_token
   SQUARE_LOCATION_ID=your_square_location_id
   VAPI_API_KEY=your_vapi_api_key
   ```

3. **Test Square connection:**
   ```bash
   python3 test_square_connection.py
   ```

4. **Start the server:**
   ```bash
   python3 -m uvicorn main:app --reload
   ```

5. **Start ngrok tunnel:**
   ```bash
   ./ngrok http 8000
   ```

## 📚 Documentation

- `VAPI_SETUP_GUIDE.md` - Complete Vapi configuration steps
- `QUICK_START.md` - Quick reference guide
- `SUCCESS_SUMMARY.md` - Setup completion summary
- `TEST_RESULTS.md` - Testing documentation

## 🏗️ Architecture

- **FastAPI**: Backend API framework
- **Vapi**: Voice AI orchestration platform
- **Square SDK**: POS/Menu backend integration
- **Pydantic**: Data validation and settings management

## 📡 API Endpoints

- `GET /` - Health check
- `GET /menu` - Fetch menu items from Square Sandbox
- `GET /orders/recent?limit=3` - Retrieve last N orders
- `POST /vapi-webhook` - Receive webhooks from Vapi
- `POST /order` - Direct order creation endpoint (for testing)

## 🔒 Security

- Credentials stored in `.env` (not committed to git)
- `.env` file is in `.gitignore`
- Never commit sensitive credentials

## 📝 License

MIT
