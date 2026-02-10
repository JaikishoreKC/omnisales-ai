# Quick Start Commands

## First Time Setup

```powershell
# 1. Backend setup
cd backend
pip install -r requirements.txt

# Create .env file - see START_HERE.md for details
# Add: MONGO_URI, DB_NAME, OPENROUTER_API_KEY, SECRET_KEY

python load_products.py

# 2. Frontend setup
cd ../frontend
npm install

# Create .env file
# Add: VITE_API_BASE_URL=http://localhost:8000
```

## Daily Development

```powershell
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```

## Access
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Test Queries
- "recommend me some products"
- "is Nike Sneakers available?"
- "show me electronics"
- "hello"
