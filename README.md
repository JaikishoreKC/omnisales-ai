# OmniSales AI

Production-ready AI-powered sales assistant platform.

## Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Database**: MongoDB Atlas with Motor
- **AI**: OpenRouter API
- **Frontend**: React + Vite + Tailwind CSS
- **Deployment**: Render (backend), Vercel (frontend)

## Project Structure

```
omnisales-ai/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── agents/
│   │   │   ├── base_agent.py
│   │   │   ├── sales_agent.py
│   │   │   └── analytics_agent.py
│   │   ├── orchestrator/
│   │   │   └── agent_orchestrator.py
│   │   ├── memory/
│   │   │   └── conversation_memory.py
│   │   ├── db/
│   │   │   └── mongodb.py
│   │   ├── models/
│   │   │   ├── conversation.py
│   │   │   └── user.py
│   │   ├── services/
│   │   │   └── openrouter.py
│   │   └── api/
│   │       ├── routes.py
│   │       └── endpoints/
│   │           ├── chat.py
│   │           ├── users.py
│   │           └── analytics.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── main.jsx
    │   ├── App.jsx
    │   ├── index.css
    │   ├── components/
    │   │   ├── Layout.jsx
    │   │   ├── ChatInterface.jsx
    │   │   └── AnalyticsDashboard.jsx
    │   ├── pages/
    │   │   ├── HomePage.jsx
    │   │   ├── ChatPage.jsx
    │   │   └── AnalyticsPage.jsx
    │   ├── services/
    │   │   └── api.js
    │   └── store/
    │       └── useStore.js
    ├── package.json
    ├── vite.config.js
    ├── tailwind.config.js
    ├── postcss.config.js
    ├── vercel.json
    └── .env.example
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- Node.js 18+
- MongoDB Atlas account
- OpenRouter API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Configure environment variables in `.env`:
- Set `MONGODB_URL` with your MongoDB Atlas connection string
- Set `OPENROUTER_API_KEY` with your OpenRouter API key
- Generate `SECRET_KEY`: `openssl rand -hex 32`

6. Run the server:
```bash
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Configure `VITE_API_BASE_URL` in `.env`

5. Run development server:
```bash
npm run dev
```

Frontend runs at `http://localhost:5173`

## Deployment

### Backend (Render)

1. Push code to GitHub
2. Connect repository to Render
3. Use `render.yaml` for configuration
4. Set environment variables in Render dashboard

### Frontend (Vercel)

1. Push code to GitHub
2. Import project in Vercel
3. Set `VITE_API_BASE_URL` environment variable
4. Deploy

## API Endpoints

### Chat
- `POST /api/v1/chat/` - Send message
- `GET /api/v1/chat/conversations/{id}` - Get conversation
- `GET /api/v1/chat/user/{user_id}/conversations` - Get user conversations

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{user_id}` - Get user

### Analytics
- `POST /api/v1/analytics/analyze` - Analyze data

## Features

- Multi-agent AI system (Sales & Analytics agents)
- Conversation memory management
- Real-time chat interface
- Analytics dashboard
- MongoDB integration
- OpenRouter AI integration
- Production-ready deployment configuration
