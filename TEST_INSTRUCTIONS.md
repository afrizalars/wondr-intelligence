# Test Instructions

## System is Running!

Backend: http://localhost:8001 ✅
Frontend: http://localhost:5173 ✅

## Quick Test

1. Open your browser to: http://localhost:5173
2. Click "Sign up" to register a new account
3. Use these credentials:
   - Email: demo@wondr.com
   - Username: demowondr
   - Password: Wondr123!
   - Full Name: Demo User

Or use the existing test account:
- Email: test@example.com
- Password: Test123

## Manual API Test

```bash
# Test login with existing user
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "Test123"}'
```

## Frontend Configuration

The frontend should now be connecting to port 8001. 
If you still see connection errors to port 8000, please:
1. Clear your browser cache (Cmd+Shift+R on Mac)
2. Open Developer Tools > Network tab
3. Check that requests go to :8001 not :8000

## Backend Logs

Check the backend is responding:
```bash
curl http://localhost:8001/health
```

Should return:
```json
{"status":"healthy","database":"connected","version":"1.0.0"}
```