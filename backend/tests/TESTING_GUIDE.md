# OmniSales AI Test Suite

Testing docs are consolidated in [docs/TESTING.md](../../docs/TESTING.md).

Quick run:

```bash
cd backend
pytest -v
```
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
