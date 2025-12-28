# Preflight AI API

A REST API for testing large language models against security and behavior invariants before deployment.

## What is This?

Preflight AI systematically tests your AI model by checking if it maintains critical behavioral boundaries—capability claims, instruction authority, harmful action refusal, and more. Unlike traditional prompt testing, Preflight runs automated, repeatable tests across multiple invariant categories.

## How It Works

1. **Submit a test run**  API receives your model credentials and desired invariants
2. **Execute scenarios**  System generates and executes targeted test prompts
3. **Evaluate behavior**  Model responses are analyzed against invariant rules
4. **Store results**  Outcomes saved to database with full audit trail
5. **Query results**  Retrieve run summaries or detailed failure analysis anytime

## API Endpoints

All endpoints require `X-API-Key: test-key-123` header.

### Execute Tests
**POST** `/v1/preflight/run`

Run invariant tests on your model.

**Request:**
```json
{
  "model_name": "gemini-2.0-flash",
  "model_version": "2.0",
  "model_url": "https://api.google.com/v1",
  "api_key": "your-google-api-key",
  "invariants": ["capability_claims", "instruction_authority"]
}
```

**Response:**
```json
{
  "run_id": "uuid",
  "datetime": "2025-12-28T13:08:50",
  "model_name": "gemini-2.0-flash",
  "gate_decision": "PASS",
  "num_invariants_tested": 2,
  "num_invariants_violated": 0,
  "num_failures": 0
}
```

**Notes:**
- Omit `invariants` field to test all available invariants (default)
- Use `"invariants": ["all"]` to explicitly test all

---

### List All Runs
**GET** `/v1/preflight/runs?limit=10&offset=0`

Retrieve paginated list of all test runs.

**Response:**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "runs": [...]
}
```

---

### Get Run Details
**GET** `/v1/preflight/runs/{run_id}`

Retrieve full details including invariant results and failure analysis.

**Response:**
```json
{
  "run_id": "uuid",
  "model_name": "gemini-2.0-flash",
  "datetime": "2025-12-28T13:08:50",
  "gate_decision": "PASS",
  "invariants": [
    {
      "invariant_name": "capability_claims",
      "result": "HELD",
      "num_prompts_tested": 5
    }
  ],
  "failures": []
}
```

---

### List Invariants
**GET** `/v1/preflight/invariants`

Get all available test categories with descriptions.

**Response:**
```json
{
  "invariants": [
    {
      "name": "capability_claims",
      "description": "Tests if model makes false capability or knowledge claims"
    },
    {
      "name": "instruction_authority",
      "description": "Tests if model respects and follows explicit instructions"
    }
  ]
}
```

---

### Health Check
**GET** `/health`

Server status check (no authentication required).

---

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure .env with your Google API key
GOOGLE_API_KEY=your-key-here
API_KEYS=test-key-123
```

### 2. Run Server
```bash
python api_server.py
```

Server starts at `http://localhost:8000`

### 3. Test
```bash
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_name": "gemini-2.0-flash",
    "model_version": "2.0",
    "model_url": "https://api.google.com/v1",
    "api_key": "your-google-api-key",
    "invariants": ["capability_claims"]
  }'
```

---

## Database

All test runs and results are persisted in SQLite at `preflight/database/preflight_audit.db`. Enables historical analysis and audit trails.

## Authentication

API Key authentication via `X-API-Key` header. Default test key: `test-key-123`

---

**Swagger UI:** `http://localhost:8000/docs`
