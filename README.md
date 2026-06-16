# AI Text Cleaning API

A production-grade SaaS platform for automated text cleaning, grammar correction, and autocorrection. Built with FastAPI, PostgreSQL, and support for Stripe, Razorpay, and Cashfree payment gateways.

## Features

### Text Cleaning Operations

- **Grammar Fixing** - Corrects common grammar mistakes (your/you're, their/they're, etc.)
- **Space Normalization** - Removes extra spaces, fixes punctuation spacing
- **Capitalization Standardization** - Standardizes sentence casing, fixes "I" pronoun
- **Emoji Removal** - Strips all emojis from text
- **Profanity Censoring** - Detects and censors profanity with asterisks
- **PII Anonymization** - Detects and redacts emails, phone numbers, SSN, credit cards
- **OCR Error Correction** - Fixes common OCR mistakes (0→O, l→I, rn→m, encoding issues)
- **Style Conversion** - Converts text to different writing styles (formal, casual, technical, simple)

### Platform Features

- **Subscription Management** - Free, Starter, Pro, Enterprise tiers
- **Multi-Gateway Payment** - Stripe, Razorpay, Cashfree integrations
- **API Key Authentication** - Secure API access alongside JWT tokens
- **Batch Processing** - Clean up to 1000 texts in single request
- **Usage Analytics** - Track characters processed, API calls, cost attribution
- **Rate Limiting** - Per-plan quotas and rate limits
- **Scalable Architecture** - Async FastAPI, PostgreSQL, Docker/Kubernetes ready

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 16 (or use Docker)

### Installation

1. **Clone the repository**

```bash
cd AI-Text-Cleaning
```

2. **Setup environment**

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker Compose**

```bash
docker-compose up -d
```

This will:
- Build the FastAPI application
- Start PostgreSQL database
- Initialize the database schema
- Create default subscription plans

4. **Access the API**

- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

### Manual Setup (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Initialize database (ensure PostgreSQL is running)
python -m alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### 1. Register & Authentication

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### 2. Clean Text

```bash
curl -X POST http://localhost:8000/clean/text \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "ur text has   grammar mistakess!!! 😂 contact me at john@example.com",
    "operations": ["grammar", "spaces", "emojis", "pii"],
    "target_style": "formal"
  }'
```

### 3. Using API Keys

```bash
# Create API key
curl -X POST http://localhost:8000/api-keys \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Production Key"}'

# Use API key for requests
curl -X POST http://localhost:8000/clean/text \
  -H "X-API-Key: atc_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "your text here",
    "operations": ["grammar", "spaces"]
  }'
```

## Subscription Plans

| Plan | Price | Requests/Day | Max Chars/Request | Features |
|------|-------|--------------|-------------------|----------|
| Free | $0 | 100 | 5,000 | Basic cleaning |
| Starter | $12/mo | 1,000 | 50,000 | All operations + batch |
| Pro | $60/mo | 10,000 | 500,000 | Everything + priority |
| Enterprise | Custom | Unlimited | Unlimited | Custom + support |

## Project Structure

```
AI-Text-Cleaning/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # SQLAlchemy setup
│   ├── auth.py                 # JWT & password utilities
│   ├── api_keys.py             # API key management
│   ├── rate_limit.py           # Rate limiting config
│   ├── schemas.py              # Pydantic models
│   ├── models/
│   │   ├── __init__.py
│   │   └── base.py            # SQLAlchemy ORM models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── cleaner.py         # Text cleaning logic (8 operations)
│   │   └── payments/          # Payment gateway integrations
│   │       ├── __init__.py
│   │       ├── stripe.py      # Stripe integration
│   │       ├── razorpay.py    # Razorpay integration
│   │       └── cashfree.py    # Cashfree integration
│   └── routes/
│       ├── __init__.py
│       ├── auth.py            # Auth endpoints
│       ├── clean.py           # Text cleaning endpoints
│       ├── subscriptions.py   # Subscription management
│       ├── api_keys.py        # API key management
│       └── payments.py        # Payment webhooks
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_auth.py
│   ├── test_clean.py
│   └── conftest.py
├── migrations/                 # Alembic migrations
├── requirements.txt           # Python dependencies
├── docker-compose.yml         # Docker Compose setup
├── Dockerfile                 # Container image
├── .env.example              # Environment template
├── README.md                 # This file
└── API_DOCUMENTATION.md      # Complete API docs
```

## Database Schema

### Users Table
- `id` (UUID) - Primary key
- `email` (String) - Unique email
- `hashed_password` (String) - bcrypt hashed password
- `full_name` (String) - User's name
- `is_active` (Boolean) - Account status
- `is_verified` (Boolean) - Email verification status
- `created_at` (DateTime) - Registration timestamp

### Plans Table
- `id` (UUID) - Primary key
- `name` (Enum) - free, starter, pro, enterprise
- `price_inr` / `price_usd` (Float) - Monthly price
- `requests_per_day` (Integer) - Request limit (-1 = unlimited)
- `max_chars_per_request` (Integer) - Character limit
- `features` (JSON) - Plan features
- `stripe_price_id`, `razorpay_plan_id`, `cashfree_plan_id` (String) - Gateway IDs

### Subscriptions Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to Users
- `plan_id` (UUID) - Foreign key to Plans
- `status` (Enum) - active, cancelled, expired, etc.
- `gateway` (Enum) - stripe, razorpay, cashfree
- `current_period_start` / `current_period_end` (DateTime) - Billing period
- `created_at` (DateTime) - Subscription start

### API Keys Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to Users
- `key_hash` (String) - SHA256 hash of actual key
- `name` (String) - Human-readable name
- `is_active` (Boolean) - Revocation status
- `last_used_at` (DateTime) - Last usage timestamp

### Usage Logs Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to Users
- `endpoint` (String) - API endpoint called
- `chars_processed` (Integer) - Characters cleaned
- `operations` (JSON) - Operations applied
- `response_ms` (Integer) - Response time in milliseconds
- `created_at` (DateTime) - Request timestamp

### Payment Transactions Table
- `id` (UUID) - Primary key
- `user_id` (UUID) - Foreign key to Users
- `subscription_id` (UUID) - Related subscription (if any)
- `gateway` (Enum) - stripe, razorpay, cashfree
- `gateway_payment_id` (String) - External payment ID
- `amount` (Float) - Transaction amount
- `currency` (String) - Currency code
- `status` (Enum) - pending, success, failed, refunded
- `raw_response` (JSON) - Complete gateway response
- `created_at` / `updated_at` (DateTime) - Timestamps

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/aitextcleaning

# JWT
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Payment Gateways (optional)
STRIPE_SECRET_KEY=sk_test_...
RAZORPAY_KEY_ID=...
RAZORPAY_KEY_SECRET=...
CASHFREE_APP_ID=...
CASHFREE_SECRET_KEY=...

# Server
API_PORT=8000
API_HOST=0.0.0.0
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user profile

### Text Cleaning
- `POST /clean/text` - Clean text with selected operations
- `POST /clean/autocorrect` - Auto-correct with smart operation selection
- `POST /clean/batch` - Batch clean up to 1000 texts
- `POST /clean/grammar` - Fix grammar only
- `POST /clean/remove-pii` - Remove PII only
- `POST /clean/remove-profanity` - Remove profanity only
- `POST /clean/remove-emojis` - Remove emojis only
- `POST /clean/fix-ocr` - Fix OCR errors only

### Subscriptions
- `GET /subscriptions/plans` - List all plans
- `GET /subscriptions/me` - Get current subscription
- `POST /subscriptions/upgrade` - Upgrade plan
- `POST /subscriptions/cancel` - Cancel subscription

### API Keys
- `GET /api-keys` - List API keys
- `POST /api-keys` - Create new API key
- `DELETE /api-keys/{key_id}` - Delete API key
- `POST /api-keys/{key_id}/revoke` - Revoke API key
- `POST /api-keys/{key_id}/activate` - Activate API key

### Payments (TBD)
- `POST /payments/initiate` - Start payment
- `POST /webhooks/stripe` - Stripe webhook
- `POST /webhooks/razorpay` - Razorpay webhook
- `POST /webhooks/cashfree` - Cashfree webhook

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_clean.py

# Run specific test
pytest tests/test_clean.py::test_clean_text_with_grammar
```

## Deployment

### Docker

```bash
# Build image
docker build -t ai-text-cleaning:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://user:pass@db:5432/db \
  -e SECRET_KEY=your-secret \
  ai-text-cleaning:latest
```

### Kubernetes

```bash
# Create ConfigMap
kubectl create configmap app-config --from-env-file=.env

# Deploy
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Cloud Platforms

#### AWS ECS/Fargate
```bash
# Push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
docker tag ai-text-cleaning:latest $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-text-cleaning:latest
docker push $AWS_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/ai-text-cleaning:latest
```

#### Google Cloud Run
```bash
gcloud run deploy ai-text-cleaning \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=... SECRET_KEY=...
```

#### Heroku
```bash
heroku create ai-text-cleaning
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

## Monitoring & Logging

### Metrics to Track

- API response time (p50, p95, p99)
- Error rate by endpoint
- Characters processed per hour
- Active subscriptions by plan
- Payment success rate
- Database connection pool utilization

### Logging

All requests are logged with:
- Timestamp
- User ID
- Endpoint
- Characters processed
- Operations applied
- Response time
- Status code

Configure via `LOG_LEVEL` environment variable.

## Scaling Considerations

### Database
- Add read replicas for scaling reads
- Implement connection pooling (pgBouncer)
- Archive old usage logs periodically
- Index on user_id, created_at for logs

### Application
- Deploy multiple API instances behind load balancer
- Use Redis for caching (subscription plans, user quotas)
- Implement async job processing for heavy operations
- Add rate limiting middleware

### Storage
- Store large text files in S3/GCS (if needed)
- Cache cleaned results in Redis (optional)

## Roadmap

- [ ] Payment gateway integrations (Stripe, Razorpay, Cashfree)
- [ ] Advanced NLP operations (synonym replacement, paraphrasing)
- [ ] Webhooks for subscription events
- [ ] Advanced analytics dashboard
- [ ] Bulk import/export (CSV, JSON)
- [ ] Custom training for domain-specific cleaning
- [ ] Multi-language support
- [ ] OAuth2 integrations (Google, GitHub)
- [ ] Audit trail & activity logs
- [ ] Enterprise SSO (SAML, LDAP)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

- **Documentation**: See API_DOCUMENTATION.md
- **Issues**: GitHub Issues
- **Email**: support@aitextcleaning.com
- **Slack**: [Join our community](https://slack.aitextcleaning.com)

## Acknowledgments

- FastAPI for the awesome web framework
- PostgreSQL for reliable data storage
- Presidio for PII detection
- Better-profanity for profanity filtering
- All open-source contributors

---

**Made with ❤️ for better text quality**
