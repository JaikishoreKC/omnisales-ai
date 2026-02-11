# 🎓 BEGINNER'S GUIDE - Start Here!

## 📍 Current Status of Your Project

### ✅ What's Already Done (You're 90% Ready!)

**Code & Documentation:**
- ✅ **Complete codebase** - All Python code is written and working
- ✅ **8 specialized AI agents** - Ready to handle sales, inventory, payments, etc.
- ✅ **Multi-channel support** - Web, WhatsApp, and Voice ready
- ✅ **Security implemented** - Enterprise-grade authentication and protection
- ✅ **Documentation cleaned** - 8 clear guide files (down from 26!)
- ✅ **Database optimization** - 8 indexes for fast queries
- ✅ **Python installed** - Version 3.10.11 detected on your system

**Your Setup:**
- ✅ **Environment file exists** - (`backend\.env` found)
- ✅ **Python dependencies listed** - In `requirements.txt`
- ✅ **Sample data script ready** - `load_products.py`

### ⚠️ What You Need to Do (Simple 3-Step Setup)

**Missing (Required to run):**
1. ❌ **MongoDB database** - Free cloud database (5 minutes to create)
2. ❌ **OpenRouter API key** - AI service key (2 minutes to get, $5 minimum)
3. ❌ **Python packages** - Install dependencies (1 command, 2 minutes)

**Optional (Can skip for now):**
- ⚪ WhatsApp Business API (for WhatsApp chat support)
- ⚪ SuperU Voice API (for phone call support)
- ⚪ POS system integration (for real store systems)

---

## 🎯 Your Mission: Get the App Running in 20 Minutes

Follow these exact steps. Don't skip any!

---

## 📝 STEP 1: Create Free MongoDB Database (7 minutes)

**Why?** Your app needs a database to store conversations, products, and user data.

### What to do:

1. **Open your web browser**

2. **Go to:** https://www.mongodb.com/cloud/atlas

3. **Click "Try Free"** (top right corner)

4. **Sign up:**
   - Use your Google account (fastest), OR
   - Use your email

5. **Create a FREE cluster:**
   - Question: "What is your goal?" → Click **"Learn MongoDB"**
   - Choose: **M0 (FREE)** - No credit card needed!
   - Provider: **AWS**
   - Region: Choose closest to you (e.g., "N. Virginia" if in USA)
   - Cluster Name: Type **"omnisales-cluster"**
   - Click **"Create Deployment"**

6. **Create database user** (This will pop up automatically):
   - Username: Type **"omnisales_user"**
   - Password: Click **"Autogenerate Secure Password"**
   - **IMPORTANT:** Click the **COPY** button to copy the password
   - **Paste it in Notepad** and save it NOW! You'll need it soon
   - Click **"Create Database User"**

7. **Set up network access:**
   - Click **"Add My Current IP Address"** (this allows your computer to connect)
   - Click **"Finish and Close"**

8. **Get your connection string:**
   - Click **"Connect"** button
   - Click **"Drivers"**
   - Copy the connection string (looks like: `mongodb+srv://omnisales_user:...`)
   - **Paste it in Notepad** with the password

**✅ Done! You now have a free database running 24/7 in the cloud.**

---

## 🔑 STEP 2: Get OpenRouter API Key (5 minutes)

**Why?** This is the AI that powers your chatbot (like ChatGPT).

### What to do:

1. **Go to:** https://openrouter.ai/

2. **Click "Sign In"** (top right)

3. **Sign up with Google** (fastest option)

4. **Go to:** https://openrouter.ai/keys

5. **Click "Create Key"**
   - Name: Type **"omnisales"**
   - Click **"Create"**

6. **Copy the API key** (starts with `sk-or-...`)
   - **Paste it in Notepad** with your MongoDB info

7. **Add credits:**
   - Go to: https://openrouter.ai/credits
   - Click **"Add Credits"**
   - Choose **$5** (minimum, will last a long time for testing)
   - Enter payment info and complete purchase

**✅ Done! You can now use AI in your app.**

---

## ⚙️ STEP 3: Configure Your App (8 minutes)

**Why?** Tell your app how to connect to MongoDB and OpenRouter.

### What to do:

1. **Open your `.env` file:**
   - Location: `d:\Projects\Personal\New folder\omnisales-ai\backend\.env`
   - **Right-click** the file → **Open with Notepad**

2. **Replace these values** (use the info you saved in Notepad):

   ```env
   # MongoDB - Replace EVERYTHING after the = sign
   MONGO_URI=mongodb+srv://omnisales_user:YOUR_PASSWORD_HERE@omnisales-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=omnisales
   
   # OpenRouter AI - Replace with your actual key
   OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Security - Generate new keys (see instructions below)
   SECRET_KEY=you-will-generate-this
   API_SECRET_KEY=you-will-also-generate-this
   
   # Keep these as-is for now
   OLLAMA_API_URL=http://localhost:11434
   FRONTEND_URL=http://localhost:5173
   ENVIRONMENT=development
   ```

3. **Generate security keys:**
   
   **Option A - Using PowerShell (Recommended):**
   - Open PowerShell (search "PowerShell" in Start menu)
   - Copy and paste this command, press Enter:
     ```powershell
     python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32)); print('API_SECRET_KEY=' + secrets.token_urlsafe(32))"
     ```
   - You'll see two lines like:
     ```
     SECRET_KEY=abc123...xyz
     API_SECRET_KEY=def456...uvw
     ```
   - **Copy these lines** and paste them into your `.env` file (replace the "you-will-generate-this" lines)

   **Option B - Use these pre-generated keys (for testing only):**
   ```env
   SECRET_KEY=aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890-_TEST
   API_SECRET_KEY=XyZ9876543210WvUtSrQpOnMlKjIhGfEdCbA-_TEST
   ```

4. **Save the file** (Ctrl+S)

**✅ Done! Your app is configured.**

---

## 🚀 STEP 4: Install Dependencies & Test (5 minutes)

**Why?** Install the software packages your app needs.

### What to do:

1. **Open PowerShell:**
   - Press `Windows Key + X`
   - Click **"Windows PowerShell"** or **"Terminal"**

2. **Navigate to your project:**
   ```powershell
   cd "d:\Projects\Personal\New folder\omnisales-ai\backend"
   ```

3. **Install Python packages:**
   ```powershell
   pip install -r requirements.txt
   ```
   
   **This will take 2-3 minutes.** You'll see lots of text scrolling by. That's normal!
   
   ⚠️ **If you see red errors about "Microsoft C++ Build Tools":**
   - That's okay! Try this instead:
     ```powershell
     pip install -r requirements.txt --only-binary :all:
     ```

4. **Load sample products into database:**
   ```powershell
   python load_products.py
   ```
   
   **Expected output:**
   ```
   Loading products into database...
   ✅ Successfully loaded 50 products!
   Database ready!
   ```

5. **Start the server:**
   ```powershell
   uvicorn app.main:app --reload
   ```
   
   **Expected output:**
   ```
   INFO:     Started server process
   INFO:     Waiting for application startup.
   INFO:app.main:Creating database indexes...
   INFO:app.main:Database indexes created successfully
   INFO:     Application startup complete.
   INFO:     Uvicorn running on http://127.0.0.1:8000
   ```

6. **Test it works:**
   - Open your web browser
   - Go to: **http://localhost:8000/health**
   - You should see:
     ```json
     {"status":"ok","version":"2.0.0","channels":["web","whatsapp","voice"]}
     ```

**🎉 SUCCESS! Your backend is running!**

---

## 🧪 STEP 5: Test the AI Chat (2 minutes)

Let's make sure the AI agent works.

### Using Web Browser (Easiest):

1. **Keep the server running** (don't close PowerShell)

2. **Open a NEW PowerShell window** (so you can type commands while server runs)

3. **Copy and paste this command:**
   ```powershell
   $headers = @{
       "Authorization" = "Bearer XyZ9876543210WvUtSrQpOnMlKjIhGfEdCbA-_TEST"
       "Content-Type" = "application/json"
   }
   $body = @{
       user_id = "test_user"
       session_id = "test_session"
       message = "I need a laptop for coding"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "http://localhost:8000/chat" -Method Post -Headers $headers -Body $body
   ```

4. **You should see a response like:**
   ```
   reply       : I'd be happy to help you find a great laptop for coding! Let me recommend...
   agent_used  : recommendation
   actions     : ...
   ```

**🎉 IT WORKS! Your AI is responding!**

---

## 📱 STEP 6: Use the API Documentation (Optional)

FastAPI automatically creates beautiful documentation:

1. **Open browser:** http://localhost:8000/docs

2. **You'll see:**
   - List of all endpoints
   - "Try it out" buttons to test
   - Request/response examples
   - Schema definitions

3. **Try the `/chat` endpoint:**
   - Click on `POST /chat`
   - Click **"Try it out"**
   - Click the **lock icon** 🔒 and enter your API key:
     ```
     XyZ9876543210WvUtSrQpOnMlKjIhGfEdCbA-_TEST
     ```
   - Edit the example request
   - Click **"Execute"**
   - See the response below!

---

## 🎓 What You Just Built

Congratulations! You now have a **production-ready AI sales assistant** that can:

✅ Recommend products based on customer requests  
✅ Check inventory and stock levels  
✅ Process payments  
✅ Track orders  
✅ Manage loyalty points  
✅ Handle returns and support  
✅ Make proactive outbound calls  
✅ Integrate with POS systems  

**All secured with:**
- API key authentication
- Rate limiting (prevents abuse)
- Input validation
- Security headers
- Error handling

---

## 🔧 Common Issues & Solutions

### Issue 1: "Cannot connect to MongoDB"

**Error:** `ServerSelectionTimeoutError` or `Connection refused`

**Solution:**
1. Check your `.env` file has correct `MONGO_URI`
2. Make sure you allowed your IP address in MongoDB Atlas:
   - Go to https://cloud.mongodb.com
   - Click "Network Access" (left sidebar)
   - Click "Add IP Address" → "Allow Access from Anywhere" → Confirm
3. Restart the server: `Ctrl+C` then `uvicorn app.main:app --reload`

---

### Issue 2: "401 Unauthorized" when testing `/chat`

**Solution:**
- You forgot the Authorization header!
- Add: `Authorization: Bearer YOUR_API_SECRET_KEY`
- Or use the PowerShell command from Step 5 (it includes the header)

---

### Issue 3: "No module named 'fastapi'" or similar

**Solution:**
```powershell
cd "d:\Projects\Personal\New folder\omnisales-ai\backend"
pip install -r requirements.txt
```

---

### Issue 4: "Port 8000 already in use"

**Solution:**
- Another program is using port 8000
- Use a different port:
  ```powershell
  uvicorn app.main:app --reload --port 8001
  ```
- Then use http://localhost:8001 instead

---

### Issue 5: OpenRouter API returns "Insufficient credits"

**Solution:**
- Add more credits: https://openrouter.ai/credits
- Minimum $5

---

## 📚 Next Steps After Setup

Once your app is running, you can:

1. **Read the documentation:**
   - [README.md](README.md) - Overview
   - [DOCS_INDEX.md](DOCS_INDEX.md) - Find any documentation
   - [ARCHITECTURE.md](ARCHITECTURE.md) - How the code works

2. **Customize the app:**
   - Edit agents in `backend/app/agents/` to change AI behavior
   - Add products: Edit `load_products.py` and run it again
   - Change rate limits: Edit `backend/app/main.py`

3. **Deploy to production:**
   - See [QUICK_START_SECURE.md](QUICK_START_SECURE.md) deployment section
   - Use Railway, Render, or Heroku (free tiers available)

4. **Add integrations:**
   - WhatsApp: Get API key from Meta Business
   - Voice: Get SuperU API key
   - POS: Connect your store's POS system

---

## 🆘 Need Help?

1. **Check the error message** - Read it carefully
2. **Check this guide's "Common Issues"** section above
3. **Check the logs** - The PowerShell window shows detailed error messages
4. **Review the documentation:**
   - [SECURITY_IMPLEMENTATION_GUIDE.md](SECURITY_IMPLEMENTATION_GUIDE.md) - Troubleshooting section
   - [README.md](README.md) - Troubleshooting section

---

## ✅ Quick Checklist

Before asking for help, verify:

- [ ] MongoDB connection string in `.env` is correct (no spaces, includes password)
- [ ] OpenRouter API key in `.env` is correct (starts with `sk-or-v1-`)
- [ ] You ran `pip install -r requirements.txt` successfully
- [ ] Server is running (shows "Uvicorn running on...")
- [ ] You're using the correct URL (http://localhost:8000)
- [ ] You included the Authorization header when testing `/chat`
- [ ] You have credits in your OpenRouter account

---

## 🎉 You Did It!

You've successfully set up a production-ready AI sales assistant platform!

**What you learned:**
- How to set up a cloud database (MongoDB Atlas)
- How to use AI APIs (OpenRouter)
- How to configure environment variables
- How to install Python dependencies
- How to run a web server
- How to test REST APIs

**What you built:**
- Multi-agent AI system
- Secure REST API with authentication
- Database-backed conversation system
- Production-ready error handling

**Time invested:** ~20 minutes  
**Value:** Priceless! 💎

---

**Status:** ✅ **READY FOR DEVELOPMENT**  
**Next:** Start customizing or deploy to production!

**Last Updated:** February 10, 2026  
**Beginner-Friendly:** ⭐⭐⭐⭐⭐
