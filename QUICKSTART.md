# Quick Start Guide - AI Text Cleaning API

Get up and running in 5 minutes!

## Option 1: Docker (Recommended for Production)

### Prerequisites
- Docker
- Docker Compose

### Steps

1. **Start the application**
```bash
docker-compose up -d
```

This will:
- Build the FastAPI application image
- Start PostgreSQL database
- Automatically create tables and seed default plans
- API will be available at http://localhost:8000

2. **Verify it's running**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "AI Text Cleaning API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00"
}
```

---

## Option 2: Local Development

### Prerequisites
- Python 3.11+
- PostgreSQL 16 running locally
- pip / virtualenv

### Steps

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup database**
```bash
# Create .env file
cp .env.example .env

# Make sure PostgreSQL is running and accessible
# Edit .env with your database credentials if needed

# Initialize database and seed plans
python -m app.seed_data
```

4. **Start development server**
```bash
uvicorn app.main:app --reload --port 8000
```

Server will be available at http://localhost:8000

---

## First Steps

### 1. Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "MySecurePassword123",
    "full_name": "Your Name"
  }'
```

Response:
```json
{
  "message": "Registration successful",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "you@example.com"
}
```

### 2. Login and Get Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "you@example.com",
    "password": "MySecurePassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Save the `access_token`** - you'll need it for API requests!

### 3. Clean Your First Text

```bash
curl -X POST http://localhost:8000/clean/text \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ur email is john@example.com. do u have time??? 😂😂😂",
    "operations": ["grammar", "spaces", "emojis", "pii"],
    "target_style": "formal"
  }'
```

Response:
```json
{
  "original_text": "ur email is john@example.com. do u have time??? 😂😂😂",
  "cleaned_text": "Your email is [EMAIL REDACTED]. Do you have time?",
  "operations_applied": ["grammar", "spaces", "emojis", "pii"],
  "metadata": {
    "original_length": 58,
    "cleaned_length": 42,
    "changes_made": {
      "grammar": {"count": 2, "examples": ["Text speak"]},
      "spaces": {"count": 1, "removed_extra_spaces": 2},
      "emojis": {"count": 3, "removed_emojis": ["😂", "😂", "😂"]},
      "pii": {"count": 1, "entities_removed": ["EMAIL"]}
    }
  }
}
```

Congratulations! You've successfully cleaned your first text! 🎉

---

## Try Different Operations

### Grammar Fix Only
```bash
curl -X POST http://localhost:8000/clean/grammar \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=ur text needs grammar fixing"
```

### Remove Profanity
```bash
curl -X POST http://localhost:8000/clean/remove-profanity \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=This is a bad word text"
```

### Remove PII
```bash
curl -X POST http://localhost:8000/clean/remove-pii \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "text=My email is john@example.com and SSN is 123-45-6789"
```

### Batch Processing
```bash
curl -X POST http://localhost:8000/clean/batch \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "texts": [
      "text 1 with errors!!!",
      "text 2 has   extra   spaces",
      "text 3 😂😂😂"
    ],
    "operations": ["grammar", "spaces", "emojis"]
  }'
```

---

## Create an API Key (For Production Use)

Instead of passing JWT tokens, you can create API keys:

```bash
curl -X POST http://localhost:8000/api-keys \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Production API Key"}'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440020",
  "name": "My Production API Key",
  "key": "atc_1234567890abcdefghijklmnopqrstuvwxyz",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "last_used_at": null
}
```

**⚠️ Save the `key` securely!** It's never returned again.

Now use it in requests:
```bash
curl -X POST http://localhost:8000/clean/text \
  -H "X-API-Key: atc_1234567890abcdefghijklmnopqrstuvwxyz" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "text with errors",
    "operations": ["grammar"]
  }'
```

---

## Interactive API Documentation

Open your browser and visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly in the browser!

---

## Check Your Subscription

```bash
curl -X GET http://localhost:8000/subscriptions/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "active",
  "current_period_start": "2024-01-15T00:00:00Z",
  "current_period_end": "2024-02-15T00:00:00Z",
  "cancelled_at": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Upgrade Your Plan

```bash
curl -X POST http://localhost:8000/subscriptions/upgrade \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "starter",
    "gateway": "stripe"
  }'
```

(Payment gateway integration coming soon!)

---

## Stop the Application

```bash
# If using Docker Compose
docker-compose down

# If running locally, press Ctrl+C in terminal
```

---

## Troubleshooting

### Database connection error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Make sure database exists and user has permissions

### Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000
kill -9 <PID>

# Or use a different port
uvicorn app.main:app --port 8001
```

### Tables don't exist
```bash
# Run seed script
python -m app.seed_data
```

### Import errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

---

## Next Steps

1. **Read the full documentation**: See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
2. **Explore all operations**: Test each cleaning operation
3. **Integrate with your app**: Use the API in your application
4. **Setup webhooks**: When payment integration is ready
5. **Monitor usage**: Track your API consumption

---

## Support

- **Docs**: http://localhost:8000/docs
- **API Reference**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Issues**: Create a GitHub issue
- **Email**: support@aitextcleaning.com

Enjoy! 🚀
