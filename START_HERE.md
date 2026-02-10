╔══════════════════════════════════════════════════════════════════════════════╗
║                         SETUP GUIDE FOR BEGINNERS                            ║
║                     Follow these steps in exact order                        ║
╚══════════════════════════════════════════════════════════════════════════════╝

STEP 1: CREATE MONGODB DATABASE (5 minutes)
═══════════════════════════════════════════════════════════════════════════════
1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" → Sign up with Google/Email
3. Create FREE cluster:
   - Choose AWS
   - Select closest region
   - Cluster name: omnisales-cluster
4. Create database user:
   - Click "Database Access" → "Add New Database User"
   - Username: omnisales_user
   - Password: (Generate secure password - SAVE IT!)
5. Allow network access:
   - Click "Network Access" → "Add IP Address"
   - Click "Allow Access from Anywhere" → Confirm
6. Get connection string:
   - Click "Database" → "Connect" → "Connect your application"
   - Copy connection string (looks like: mongodb+srv://...)
   - Replace <password> with your actual password


STEP 2: GET OPENROUTER API KEY (2 minutes)
═══════════════════════════════════════════════════════════════════════════════
1. Go to https://openrouter.ai/
2. Click "Sign In" → Sign up with Google/GitHub
3. Go to https://openrouter.ai/keys
4. Click "Create Key" → Name it "omnisales" → Copy the key
5. Add credits (minimum $5) at https://openrouter.ai/credits


STEP 3: SETUP BACKEND ENVIRONMENT (3 minutes)
═══════════════════════════════════════════════════════════════════════════════
Open PowerShell in project folder, then run:

cd "d:\Projects\Personal\New folder\omnisales-ai\backend"

# Create .env file
New-Item -Path ".env" -ItemType File -Force

# Open .env in notepad
notepad .env

Paste this in .env (replace values with YOUR actual credentials):
───────────────────────────────────────────────────────────────────────────────
MONGO_URI=mongodb+srv://omnisales_user:YOUR_PASSWORD@cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=omnisales
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
SECRET_KEY=your-secret-key-change-this-in-production
───────────────────────────────────────────────────────────────────────────────

Save and close notepad.


STEP 4: INSTALL BACKEND DEPENDENCIES (2 minutes)
═══════════════════════════════════════════════════════════════════════════════
Still in backend folder:

# Install Python packages
pip install -r requirements.txt

Wait for installation to complete...


STEP 5: LOAD SAMPLE PRODUCTS (1 minute)
═══════════════════════════════════════════════════════════════════════════════
python load_products.py

You should see: "Inserted 200 products"


STEP 6: START BACKEND SERVER (1 minute)
═══════════════════════════════════════════════════════════════════════════════
# Start FastAPI server
uvicorn app.main:app --reload

You should see:
  INFO:     Uvicorn running on http://127.0.0.1:8000
  INFO:     Application startup complete.

✓ Backend is running! Keep this terminal open.


STEP 7: SETUP FRONTEND ENVIRONMENT (2 minutes)
═══════════════════════════════════════════════════════════════════════════════
Open NEW PowerShell window:

cd "d:\Projects\Personal\New folder\omnisales-ai\frontend"

# Create .env file
New-Item -Path ".env" -ItemType File -Force
notepad .env

Paste this in .env:
───────────────────────────────────────────────────────────────────────────────
VITE_API_BASE_URL=http://localhost:8000
───────────────────────────────────────────────────────────────────────────────

Save and close notepad.


STEP 8: INSTALL FRONTEND DEPENDENCIES (1 minute)
═══════════════════════════════════════════════════════════════════════════════
Still in frontend folder:

npm install

Wait for installation...


STEP 9: START FRONTEND SERVER (1 minute)
═══════════════════════════════════════════════════════════════════════════════
npm run dev

You should see:
  VITE v5.0.11  ready in 500 ms
  ➜  Local:   http://localhost:5173/

✓ Frontend is running! Keep this terminal open too.


STEP 10: TEST THE APPLICATION (2 minutes)
═══════════════════════════════════════════════════════════════════════════════
1. Open browser: http://localhost:5173
2. You should see chat interface
3. Try these messages:

   "recommend me some products"
   → Should show product cards

   "is Nike Sneakers available?"
   → Should check stock

   "hello"
   → Should get AI greeting


═══════════════════════════════════════════════════════════════════════════════
                              TROUBLESHOOTING
═══════════════════════════════════════════════════════════════════════════════

PROBLEM: "Module not found" error
SOLUTION: Make sure you're in correct folder
          cd "d:\Projects\Personal\New folder\omnisales-ai\backend"

PROBLEM: "Connection refused" on frontend
SOLUTION: Make sure backend is running on port 8000
          Check .env has: VITE_API_BASE_URL=http://localhost:8000

PROBLEM: "Authentication failed" MongoDB
SOLUTION: Check MONGO_URI in backend/.env
          - Password must not have special characters in URL
          - If password has @, #, etc., URL encode it

PROBLEM: "OpenRouter API error"
SOLUTION: Check OPENROUTER_API_KEY in backend/.env
          Make sure you added credits at openrouter.ai/credits

PROBLEM: Backend starts but crashes
SOLUTION: Check terminal for error message
          Most common: Missing environment variable


═══════════════════════════════════════════════════════════════════════════════
                            WHAT YOU HAVE NOW
═══════════════════════════════════════════════════════════════════════════════

✓ Backend API running on http://localhost:8000
✓ Frontend chat UI on http://localhost:5173
✓ MongoDB database with 200 products
✓ 4 AI agents: Recommendation, Inventory, Payment, Fulfillment
✓ Intent detection system
✓ Session memory (stores last 5 messages)


═══════════════════════════════════════════════════════════════════════════════
                              NEXT STEPS
═══════════════════════════════════════════════════════════════════════════════

OPTION A: Keep testing locally
  → Try different queries
  → Check MongoDB Atlas to see data
  → Modify agents to customize behavior

OPTION B: Deploy to production
  → See DEPLOYMENT.md for instructions
  → Backend → Render.com (free tier)
  → Frontend → Vercel.com (free tier)

OPTION C: Learn the codebase
  → Read ARCHITECTURE.md to understand structure
  → Modify agents/recommendation.py to change product logic
  → Modify frontend/src/pages/ChatPage.jsx to change UI


═══════════════════════════════════════════════════════════════════════════════
                         QUICK REFERENCE COMMANDS
═══════════════════════════════════════════════════════════════════════════════

Start backend:
  cd backend
  uvicorn app.main:app --reload

Start frontend:
  cd frontend
  npm run dev

Run tests:
  cd backend
  pytest

Stop servers:
  Press Ctrl+C in terminal

View logs:
  Check terminal where servers are running


═══════════════════════════════════════════════════════════════════════════════

Need help? Check:
- ARCHITECTURE.md → Understand code structure
- DEPLOYMENT.md → Deploy to production
- README.md → Project overview

Your application is PRODUCTION READY! 🚀
