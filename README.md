# 🛡️ Preflight AI API

> **Enterprise-Grade AI Safety Testing Framework**

A production-ready REST API for systematically testing Large Language Models against security and behavioral invariants—ensuring your AI systems maintain critical safety boundaries before deployment.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009485.svg)](https://fastapi.tiangolo.com/)

---

## 🎯 Overview

Preflight AI provides **automated, repeatable security testing** for language models by validating adherence to critical behavioral invariants:

- **Capability Claims** — Detects false or exaggerated capability assertions
- **Instruction Authority** — Validates instruction hierarchy and override resistance  
- **Harmful Action Refusal** — Ensures model refuses harmful requests
- **Role Integrity** — Prevents unauthorized role-switching
- **Information Boundaries** — Tests information disclosure constraints
- **Instruction Hierarchy** — Validates instruction priority mechanisms

Unlike manual prompt testing, Preflight provides comprehensive, reproducible analysis with full audit trails.

---

## 🔄 How It Works

```
1. Submit Test → 2. Generate Scenarios → 3. Execute Tests → 4. Analyze Results → 5. Audit Trail
```

- **Submit a test run** — Configure model and select invariants to test
- **Generate scenarios** — System creates targeted attack prompts (100+ per invariant)
- **Execute tests** — Prompts submitted to your model via configured endpoints
- **Analyze responses** — Advanced classifier evaluates model behavior patterns
- **Store results** — Full audit trail with classified behaviors and violations

---

## 📡 API Reference

All endpoints require authentication via `X-API-Key: test-key-123` header.

### Execute Preflight Tests
**`POST`** `/v1/preflight/run`

Initiate a comprehensive security test against your model.

**Request Payload:**
```json
{
  "model_name": "gemini-2.0-flash",
  "model_version": "2.0",
  "model_url": "https://api.google.com/v1",
  "api_key": "your-google-api-key",
  "invariants": ["capability_claims", "instruction_authority"]
}
```

**Success Response (200):**
```json
{
  "run_id": "29d6dd29-a3a7-4875-baae-72c535128b94",
  "datetime": "2025-12-28T13:08:50",
  "model_name": "gemini-2.0-flash",
  "gate_decision": "PASS",
  "num_invariants_tested": 2,
  "num_invariants_violated": 0,
  "num_failures": 0
}
```

**Parameters:**
- `invariants` (optional) — Test specific invariants. Omit for all.
- `model_url` — Endpoint for model API
- `api_key` — Authentication for model provider

---

### List Test Runs
**`GET`** `/v1/preflight/runs?limit=10&offset=0`

Retrieve paginated historical test results.

**Response:**
```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "runs": [
    {
      "run_id": "uuid",
      "model_name": "gemini-2.0-flash",
      "datetime": "2025-12-28T13:08:50",
      "gate_decision": "PASS"
    }
  ]
}
```

---

### Get Run Details
**`GET`** `/v1/preflight/runs/{run_id}`

Retrieve comprehensive test analysis for a specific run.

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
      "num_prompts_tested": 21
    }
  ],
  "failures": []
}
```

---

### List Available Invariants
**`GET`** `/v1/preflight/invariants`

Get metadata on all available safety testing categories.

**Response:**
```json
{
  "invariants": [
    {
      "name": "capability_claims",
      "description": "Tests if model makes false capability or knowledge claims",
      "num_test_prompts": 21
    },
    {
      "name": "instruction_authority",
      "description": "Tests if model respects instruction hierarchy and prevents overrides",
      "num_test_prompts": 13
    }
  ]
}
```

---

### Health Check
**`GET`** `/health`

Server status endpoint (no authentication required).

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-12-28T13:08:50"
}
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip/virtualenv
- API credentials for your LLM provider (Google, OpenAI, etc.)

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/preflight_ai_v1.git
cd preflight_ai_v1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```env
GOOGLE_API_KEY=your-google-api-key-here
API_KEYS=test-key-123
DATABASE_URL=sqlite:///preflight/database/preflight_audit.db
```

### Run Server

```bash
python api_server.py
```

Server starts at `http://localhost:8000`

### Test API

```bash
# Run a complete security audit
curl -X POST http://localhost:8000/v1/preflight/run \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{
    "model_name": "gemini-2.0-flash",
    "model_version": "2.0",
    "model_url": "https://api.google.com/v1",
    "api_key": "YOUR_API_KEY",
    "invariants": ["capability_claims", "instruction_authority"]
  }'

# Get test history
curl -H "X-API-Key: test-key-123" http://localhost:8000/v1/preflight/runs

# View API documentation
# Navigate to: http://localhost:8000/docs
```

---

## 🗄️ Data Persistence

All test runs and detailed results are persisted in SQLite:
- **Location:** `preflight/database/preflight_audit.db`
- **Tables:** runs, invariants, failures (full audit trail)
- **Query:** Access via Postman, curl, or your application

---

## 🔐 Security & Authentication

- **API Key Authentication** via `X-API-Key` header
- **Default Test Key:** `test-key-123` (configure in `.env`)
- **HTTPS Recommended** for production deployments
- **No model data stored** — Only test metadata and results

---

## 📊 Architecture

```
preflight/
├── api/                    # FastAPI routes & endpoints
│   ├── routes.py
│   ├── models.py          # Pydantic schemas
│   └── auth.py
├── engine/                # Classification & execution
│   ├── classifier.py      # Response behavior analysis
│   └── runner.py          # Test orchestration
├── attacks/               # 100+ attack prompts (6 invariants)
│   ├── capability_claims.py
│   ├── instruction_authority.py
│   └── ...
├── core/                  # Core behavior models
├── database/              # SQLite persistence
└── models/                # LLM provider integrations
```

---

## 📚 Documentation

- **API Docs:** `http://localhost:8000/docs` (Swagger UI)
- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Evaluation Guide:** See [EVALUATION_GUIDE.md](preflight/evaluation/EVALUATION_GUIDE.md)

---

## 📝 License

MIT License — See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

Pull requests welcome! Please ensure tests pass and code is well-documented.

---

**Built with ❤️ for AI Safety**
