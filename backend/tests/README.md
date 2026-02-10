# Running Tests

## Setup

Install test dependencies:
```bash
pip install -r requirements.txt
```

## Run All Tests

```bash
pytest
```

## Run Specific Test Classes

```bash
# Test chat endpoint
pytest tests/test_integration.py::TestChatEndpoint

# Test recommendation agent
pytest tests/test_integration.py::TestRecommendationAgent

# Test inventory agent
pytest tests/test_integration.py::TestInventoryAgent

# Test payment agent
pytest tests/test_integration.py::TestPaymentAgent
```

## Run with Verbose Output

```bash
pytest -v
```

## Run with Coverage

```bash
pip install pytest-cov
pytest --cov=app --cov-report=html
```

## Test Requirements

- MongoDB connection (set MONGO_URI in .env)
- OpenRouter API key (optional, mocked in tests)

## Test Coverage

- ✓ Health endpoint
- ✓ Chat endpoint with different intents
- ✓ Recommendation agent
- ✓ Inventory agent (stock check)
- ✓ Payment agent (order creation)
- ✓ Fulfillment agent (order tracking)
- ✓ Decision engine (intent detection)
