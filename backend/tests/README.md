# OmniSales AI Test Suite

Comprehensive test suite for the OmniSales AI backend system.

## 📁 Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
│
├── unit/                          # Unit tests (fast, isolated)
│   ├── agents/                    # Agent logic tests
│   │   ├── test_inventory.py     # Inventory agent tests
│   │   ├── test_loyalty.py       # Loyalty program tests
│   │   └── test_recommendation.py # Recommendation engine tests
│   │
│   ├── repositories/              # Database layer tests
│   │   └── test_product_repository.py
│   │
│   ├── utils/                     # Utility function tests
│   │   └── test_parsers.py       # Parser utilities tests
│   │
│   ├── orchestrator/              # Orchestration logic tests
│   │   └── test_intent.py        # Intent detection tests
│   │
│   ├── test_models.py             # Pydantic model validation tests
│   └── test_edge_cases.py         # Edge cases and boundary tests
│
├── integration/                   # Integration tests (slower, with dependencies)
│   ├── test_basic_integration.py  # Basic integration tests
│   └── test_agents_integration.py # Full agent integration tests
│
└── api/                           # API endpoint tests
    ├── test_endpoints.py          # All REST endpoint tests
    └── test_api_security.py       # Security and auth tests
```

## 🎯 Test Coverage

### Unit Tests (Fast, Isolated)
- ✅ **Agents**: Inventory, Loyalty, Recommendation
- ✅ **Repositories**: Product database operations
- ✅ **Utils**: Product/order ID parsers
- ✅ **Orchestrator**: Intent detection logic
- ✅ **Models**: Pydantic schema validation
- ✅ **Edge Cases**: Boundary conditions, null inputs, unicode

### Integration Tests (E2E with Database)
- ✅ **Agent Integration**: All 8 agents working together
- ✅ **Basic Integration**: Health checks, simple flows

### API Tests (HTTP Endpoints)
- ✅ **Endpoints**: All REST API routes
- ✅ **Security**: Auth, validation, headers
- ✅ **Error Handling**: 404, 422, 401, 403

## 🚀 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# API tests
pytest tests/api/ -v
```

### Run Specific Test Files
```bash
# Test intent detection
pytest tests/unit/orchestrator/test_intent.py -v

# Test API endpoints
pytest tests/api/test_endpoints.py -v

# Test agents
pytest tests/unit/agents/ -v
```

### Run Tests with Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Tests in Parallel (faster)
```bash
pytest tests/ -n auto
```

## 📊 Test Types

### 1. Unit Tests
- **Speed**: ⚡ Very fast (<1s per test)
- **Dependencies**: None (mocked)
- **Purpose**: Test individual functions/methods
- **Example**: Testing intent detection logic

### 2. Integration Tests
- **Speed**: 🐌 Slower (may take minutes)
- **Dependencies**: Database, Ollama, running server
- **Purpose**: Test full workflows
- **Example**: Testing complete agent conversations

### 3. API Tests
- **Speed**: ⚡ Fast-Medium
- **Dependencies**: FastAPI test client
- **Purpose**: Test HTTP endpoints
- **Example**: Testing /chat endpoint validation

## 🧪 Test Fixtures

Shared test fixtures are defined in `conftest.py`:

- `client`: FastAPI test client
- `api_key`: Valid API key for auth
- `auth_headers`: Pre-configured auth headers
- `test_user`: Sample user data
- `sample_product`: Sample product data
- `sample_order`: Sample order data
- `chat_payload`: Basic chat request

## ✅ Test Quality Standards

All tests follow:

1. **AAA Pattern**:
   - **Arrange**: Set up test data
   - **Act**: Execute the code
   - **Assert**: Verify results

2. **Clear Naming**:
   - `test_<feature>_<expected_behavior>`
   - Example: `test_check_stock_found()`

3. **Comprehensive Coverage**:
   - Success cases
   - Failure cases
   - Edge cases
   - Boundary conditions

4. **Isolation**:
   - Unit tests use mocks
   - No external dependencies in unit tests
   - Integration tests clearly marked

## 🔍 What's Tested

### Core Business Logic ✅
- Intent detection (recommendation, cart, tracking, etc.)
- Product search and matching
- Stock checking
- Loyalty points calculation
- Order ID extraction
- Product name parsing

### API Endpoints ✅
- `/` - Root endpoint
- `/health` - Health check
- `/chat` - Main chat endpoint (all validations)
- `/webhook/whatsapp` - WhatsApp integration
- `/webhook/superu` - Voice integration

### Security ✅
- API key authentication
- Input validation
- Security headers (CSP, HSTS, X-Frame-Options)
- Rate limiting structure
- Webhook payload validation

### Data Models ✅
- User model validation
- Session model validation
- Product model validation
- Order model validation
- ChatRequest/ChatResponse validation

### Error Handling ✅
- 401 Unauthorized
- 403 Forbidden
- 404 Not Found
- 405 Method Not Allowed
- 422 Validation Error

## 📈 Test Metrics

### Current Coverage
- **Unit Tests**: 95+ test cases
- **API Tests**: 35+ test cases
- **Integration Tests**: 10+ test cases
- **Total**: 140+ test cases

### Key Areas Covered
- ✅ Intent Detection: 15+ tests
- ✅ Parsers: 20+ tests
- ✅ Agents: 25+ tests
- ✅ API Endpoints: 35+ tests
- ✅ Models: 20+ tests
- ✅ Repositories: 15+ tests
- ✅ Edge Cases: 25+ tests

## 🐛 Common Issues

### Integration Tests Timeout
- **Issue**: Tests wait for Ollama response
- **Solution**: Ensure Ollama is running or skip integration tests
- **Command**: `pytest tests/unit tests/api -v`

### Import Errors
- **Issue**: `ModuleNotFoundError`
- **Solution**: Activate virtual environment and install dependencies

### Database Connection Errors
- **Issue**: MongoDB connection fails
- **Solution**: Check `.env` file and network access
