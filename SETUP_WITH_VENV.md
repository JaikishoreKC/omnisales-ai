# 🐍 Virtual Environment Setup Guide

## ✅ Virtual Environment Created!

Location: `venv/` folder in your project root

---

## 🎯 Quick Start (3 Steps)

### Step 1: Activate Virtual Environment

**In PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**In Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

✅ **Success indicator:** You'll see `(venv)` at the start of your command prompt

⚠️ **If you get "execution policy" error in PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
Then try activating again.

---

### Step 2: Install Dependencies (Inside venv)

```powershell
cd backend
pip install -r requirements.txt
```

This installs all packages **inside the virtual environment only**.

---

### Step 3: Run Your App (Inside venv)

```powershell
# Load sample products
python load_products.py

# Start the server
uvicorn app.main:app --reload
```

---

## 📋 Complete Workflow

**Every time you work on this project:**

```powershell
# 1. Navigate to project
cd "d:\Projects\Personal\New folder\omnisales-ai"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. You'll see (venv) in your prompt - now you're safe!

# 4. Work on your project
cd backend
python load_products.py
uvicorn app.main:app --reload

# 5. When done, deactivate
deactivate
```

---

## 🔍 How to Check if venv is Active

Your PowerShell prompt will look like:
```
(venv) PS D:\Projects\Personal\New folder\omnisales-ai>
```

Notice the `(venv)` prefix? That means it's active! ✅

---

## 💡 Why Use Virtual Environment?

✅ **Isolates dependencies** - Packages installed here won't affect other Python projects  
✅ **Prevents conflicts** - Different projects can use different package versions  
✅ **Makes deployment easier** - Everything in one place  
✅ **Best practice** - Industry standard for Python development  

---

## 🛠️ Troubleshooting

### Issue: "cannot be loaded because running scripts is disabled"

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Can't find Activate.ps1

**Make sure you're in the project root:**
```powershell
cd "d:\Projects\Personal\New folder\omnisales-ai"
```

### Issue: pip command not found

**Your venv isn't activated. Run:**
```powershell
.\venv\Scripts\Activate.ps1
```

---

## 📦 What's Installed in venv?

After running `pip install -r requirements.txt`, these packages will be installed **only in venv**:

- FastAPI 0.109.0 - Web framework
- Motor 3.3.2 - MongoDB async driver
- Pydantic 2.5.3 - Data validation
- SlowAPI 0.1.9 - Rate limiting
- python-jose 3.3.0 - JWT authentication
- passlib 1.7.4 - Password hashing
- And 8 more dependencies...

**Total:** 14 packages isolated in your venv!

---

## ✅ Next Steps

Now that venv is set up:

1. ✅ Virtual environment created
2. ⏸️ **Activate it** (run `.\venv\Scripts\Activate.ps1`)
3. ⏸️ Install dependencies (`cd backend` then `pip install -r requirements.txt`)
4. ⏸️ Install Ollama (free AI) from https://ollama.ai/download
5. ⏸️ Download model (`ollama pull qwen2.5:3b`)
6. ⏸️ Load products (`python load_products.py`)
7. ⏸️ Start server (`uvicorn app.main:app --reload`)

---

**Always remember:** Activate venv before working on the project! 🚀
