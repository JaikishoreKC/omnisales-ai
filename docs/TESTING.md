# Testing

The backend uses pytest with async support and mocked database fixtures.

## Run tests

```bash
cd backend
pytest -v
```

## Focused runs

```bash
pytest tests/unit -v
pytest tests/integration -v
pytest tests/api -v
```

## Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

## Notes

- Most tests use mocks and do not require MongoDB.
- If you run integration tests that touch the database, ensure `MONGO_URI` is set.
