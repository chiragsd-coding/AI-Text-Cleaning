# AI Text Cleaning API - Complete Documentation

## Overview

The AI Text Cleaning API is a production-grade text cleaning and autocorrection service with subscription management, built with FastAPI, PostgreSQL, and support for multiple payment gateways (Stripe, Razorpay, Cashfree).

### Key Features

- **8 Text Cleaning Operations**: Grammar, spaces, capitalization, emojis, profanity, PII removal, OCR correction, style conversion
- **Subscription Model**: Free, Starter, Pro, Enterprise plans with usage quotas
- **Multiple Payment Gateways**: Stripe, Razorpay, Cashfree integration
- **API Key Authentication**: Secure API access alongside JWT tokens
- **Batch Processing**: Clean up to 1000 texts in a single request
- **Usage Analytics**: Track text processed, API calls, cost attribution
- **RBAC & Audit Trails**: Full access control and activity logging

---

## Authentication

### 1. Register

```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

Users are automatically subscribed to the **Free plan** on registration.

---

### 2. Login

```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

Store the `access_token` and use it in the `Authorization` header for subsequent requests:

```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. Get Current User

```bash
GET /auth/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## Text Cleaning APIs

### 1. Clean Text with Selected Operations

```bash
POST /clean/text
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "ur text has   grammar mistakess!!! 😂🎉 contact me at john@example.com",
  "operations": ["grammar", "spaces", "emojis", "pii"],
  "target_style": "formal"
}
```

**Operations Available:**
- `grammar` - Fix grammar mistakes (your/you're, their/they're, etc.)
- `spaces` - Remove extra spaces, fix punctuation spacing
- `capitalization` - Standardize sentence capitalization, fix "I" pronoun
- `emojis` - Remove all emojis
- `profanity` - Censor profanity with asterisks
- `pii` - Anonymize emails, phone numbers, SSN, credit cards
- `ocr` - Fix OCR errors (0→o, l→I, rn→m, encoding issues)
- `style` - Convert text style (formal, casual, technical, simple)

**Response:**
```json
{
  "original_text": "ur text has   grammar mistakess!!! 😂🎉 contact me at john@example.com",
  "cleaned_text": "Your text has grammar mistakes! Contact me at [EMAIL REDACTED]",
  "operations_applied": ["grammar", "spaces", "emojis", "pii"],
  "metadata": {
    "original_length": 85,
    "cleaned_length": 60,
    "changes_made": {
      "grammar": {"count": 2, "examples": ["Text speak", "Spelling"]},
      "spaces": {"count": 1, "removed_extra_spaces": 4},
      "emojis": {"count": 2, "removed_emojis": ["😂", "🎉"]},
      "pii": {"count": 1, "entities_removed": ["EMAIL"]}
    }
  }
}
```

---

### 2. Autocorrect (Smart Auto-Detection)

Automatically selects the best cleaning operations for the text.

```bash
POST /clean/autocorrect
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "ur email is john@example.com. do u have time?"
}
```

**Response:** Same as `/clean/text`, but operations are auto-selected.

---

### 3. Batch Processing

Clean up to 1000 texts in a single request (efficient for bulk processing resumes, job descriptions, etc.).

```bash
POST /clean/batch
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "texts": [
    "text 1 with errors!!!",
    "text 2 needs cleaning 😂",
    "text 3 has   extra   spaces"
  ],
  "operations": ["spaces", "grammar", "emojis"],
  "target_style": "formal"
}
```

**Response:**
```json
{
  "results": [
    {
      "original_text": "text 1 with errors!!!",
      "cleaned_text": "Text 1 with errors!",
      "operations_applied": ["spaces", "grammar", "emojis"],
      "metadata": {...}
    },
    {
      "original_text": "text 2 needs cleaning 😂",
      "cleaned_text": "Text 2 needs cleaning",
      "operations_applied": ["spaces", "grammar", "emojis"],
      "metadata": {...}
    },
    {
      "original_text": "text 3 has   extra   spaces",
      "cleaned_text": "Text 3 has extra spaces",
      "operations_applied": ["spaces", "grammar", "emojis"],
      "metadata": {...}
    }
  ],
  "total_processed": 3,
  "total_chars_processed": 85
}
```

---

### 4. Specialized Endpoints

**Fix Grammar Only:**
```bash
POST /clean/grammar
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

text=ur text needs grammar fixing
```

**Remove PII:**
```bash
POST /clean/remove-pii
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

text=My email is john@example.com and phone is 555-1234
```

**Remove Profanity:**
```bash
POST /clean/remove-profanity
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

text=This is a bad word text
```

**Remove Emojis:**
```bash
POST /clean/remove-emojis
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

text=Hello 👋 world 🌍
```

**Fix OCR Errors:**
```bash
POST /clean/fix-ocr
Authorization: Bearer <access_token>
Content-Type: application/x-www-form-urlencoded

text=0ptical Character Rec0gnition
```

---

## Subscription Management

### 1. List Available Plans

```bash
GET /subscriptions/plans
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "free",
    "display_name": "Free",
    "price_inr": 0,
    "price_usd": 0,
    "requests_per_day": 100,
    "max_chars_per_request": 5000,
    "features": ["basic_cleaning", "api_access"]
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "starter",
    "display_name": "Starter",
    "price_inr": 999,
    "price_usd": 12,
    "requests_per_day": 1000,
    "max_chars_per_request": 50000,
    "features": ["all_operations", "batch_processing", "api_keys"]
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "name": "pro",
    "display_name": "Pro",
    "price_inr": 4999,
    "price_usd": 60,
    "requests_per_day": 10000,
    "max_chars_per_request": 500000,
    "features": ["all_features", "priority_support"]
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "enterprise",
    "display_name": "Enterprise",
    "price_inr": -1,
    "price_usd": -1,
    "requests_per_day": -1,
    "max_chars_per_request": -1,
    "features": ["unlimited", "custom_support", "sso", "webhooks"]
  }
]
```

---

### 2. Get Current Subscription

```bash
GET /subscriptions/me
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440010",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "active",
  "current_period_start": "2024-01-15T00:00:00Z",
  "current_period_end": "2024-02-15T00:00:00Z",
  "cancelled_at": null,
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 3. Upgrade Subscription

```bash
POST /subscriptions/upgrade
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "plan_name": "pro",
  "gateway": "stripe"
}
```

**Response:**
```json
{
  "subscription_id": "550e8400-e29b-41d4-a716-446655440011",
  "plan_name": "pro",
  "gateway": "stripe",
  "amount": 60,
  "currency": "USD",
  "message": "Payment gateway initiation needed. See payment_url.",
  "payment_url": "https://checkout.stripe.com/pay/cs_test_..."
}
```

---

### 4. Cancel Subscription

```bash
POST /subscriptions/cancel
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "Subscription cancelled successfully"
}
```

---

## API Key Management

### 1. Create API Key

```bash
POST /api-keys
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "My Production API Key"
}
```

**Response (only returned once!):**
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

**⚠️ Important:** Store the `key` securely. It's never returned again. If lost, delete and create a new one.

---

### 2. List API Keys

```bash
GET /api-keys
Authorization: Bearer <access_token>
```

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440020",
    "name": "My Production API Key",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "last_used_at": "2024-01-16T14:22:00Z"
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440021",
    "name": "Development API Key",
    "is_active": true,
    "created_at": "2024-01-14T08:00:00Z",
    "last_used_at": "2024-01-16T10:00:00Z"
  }
]
```

---

### 3. Revoke API Key

```bash
POST /api-keys/{key_id}/revoke
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "API key revoked successfully"
}
```

---

### 4. Activate API Key

```bash
POST /api-keys/{key_id}/activate
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "API key activated successfully"
}
```

---

### 5. Delete API Key

```bash
DELETE /api-keys/{key_id}
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "message": "API key deleted successfully"
}
```

---

## Using API Keys

Instead of JWT tokens, you can authenticate with API keys:

```bash
POST /clean/text
X-API-Key: atc_1234567890abcdefghijklmnopqrstuvwxyz
Content-Type: application/json

{
  "text": "your text here",
  "operations": ["grammar", "spaces"]
}
```

---

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid auth
- `403 Forbidden` - Insufficient permissions (e.g., quota exceeded)
- `404 Not Found` - Resource not found
- `413 Payload Too Large` - Text exceeds max length for plan
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

**Error Response:**
```json
{
  "error": "ValidationError",
  "message": "Text exceeds max length of 5000 chars for your plan",
  "status_code": 413,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Rate Limiting

Rate limits are applied per plan:

- **Free**: 100 requests/day
- **Starter**: 1,000 requests/day
- **Pro**: 10,000 requests/day
- **Enterprise**: Unlimited

Each plan also has a max characters per request:

- **Free**: 5,000 chars
- **Starter**: 50,000 chars
- **Pro**: 500,000 chars
- **Enterprise**: Unlimited

---

## Pricing

### Free Plan
- €0/month
- 100 requests/day
- 5,000 chars per request
- Basic cleaning operations

### Starter Plan
- $12/month (or ₹999)
- 1,000 requests/day
- 50,000 chars per request
- All cleaning operations
- Batch processing
- API keys

### Pro Plan
- $60/month (or ₹4,999)
- 10,000 requests/day
- 500,000 chars per request
- All features + priority support

### Enterprise
- Custom pricing
- Unlimited requests
- Custom integrations
- Dedicated support

---

## Examples

### Python

```python
import requests

API_KEY = "atc_your_api_key"
BASE_URL = "http://localhost:8000"

# Clean text
response = requests.post(
    f"{BASE_URL}/clean/text",
    headers={"X-API-Key": API_KEY},
    json={
        "text": "ur text with errors 😂",
        "operations": ["grammar", "emojis"],
        "target_style": "formal"
    }
)
print(response.json())
```

### cURL

```bash
curl -X POST http://localhost:8000/clean/text \
  -H "X-API-Key: atc_your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ur text with errors 😂",
    "operations": ["grammar", "emojis"],
    "target_style": "formal"
  }'
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

const apiKey = 'atc_your_api_key';
const response = await axios.post('http://localhost:8000/clean/text', {
  text: 'ur text with errors 😂',
  operations: ['grammar', 'emojis'],
  target_style: 'formal'
}, {
  headers: { 'X-API-Key': apiKey }
});

console.log(response.data);
```

---

## Support

For issues, feature requests, or support, contact: support@aitextcleaning.com

---

## License

See LICENSE file in the repository.
