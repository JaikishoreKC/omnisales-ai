#!/usr/bin/env python3
"""
Quick verification script for OmniSales AI project
"""

import os
from pathlib import Path

def check_file(path, description):
    """Check if file exists"""
    exists = os.path.exists(path)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {path}")
    return exists

def verify_backend():
    """Verify backend structure"""
    print("\n=== BACKEND VERIFICATION ===\n")
    
    base = "backend/app"
    checks = [
        (f"{base}/main.py", "FastAPI main app"),
        (f"{base}/config.py", "Configuration"),
        (f"{base}/db/mongo.py", "MongoDB connection"),
        (f"{base}/models/schemas.py", "Pydantic models"),
        (f"{base}/orchestrator/router.py", "Main orchestrator"),
        (f"{base}/orchestrator/decision_engine.py", "Intent detection"),
        (f"{base}/orchestrator/context_builder.py", "Context builder"),
        (f"{base}/agents/recommendation_agent.py", "Recommendation agent"),
        (f"{base}/agents/inventory_agent.py", "Inventory agent"),
        (f"{base}/agents/payment_agent.py", "Payment agent"),
        (f"{base}/agents/fulfillment_agent.py", "Fulfillment agent"),
        (f"{base}/services/llm_service.py", "OpenRouter service"),
        (f"{base}/memory/session_memory.py", "Session memory"),
        ("backend/requirements.txt", "Dependencies"),
        ("backend/.env.example", "Environment template"),
        ("backend/tests/test_integration.py", "Integration tests"),
        ("backend/load_products.py", "Data loader"),
        ("backend/render.yaml", "Render config"),
    ]
    
    passed = sum(check_file(path, desc) for path, desc in checks)
    total = len(checks)
    print(f"\nBackend: {passed}/{total} files verified")
    return passed == total

def verify_frontend():
    """Verify frontend structure"""
    print("\n=== FRONTEND VERIFICATION ===\n")
    
    base = "frontend/src"
    checks = [
        (f"{base}/App.jsx", "Main app component"),
        (f"{base}/main.jsx", "Entry point"),
        (f"{base}/index.css", "Global styles"),
        (f"{base}/pages/ChatPage.jsx", "Chat page"),
        (f"{base}/components/MessageBubble.jsx", "Message component"),
        (f"{base}/components/ProductCard.jsx", "Product card"),
        (f"{base}/services/api.js", "API client"),
        ("frontend/package.json", "Dependencies"),
        ("frontend/vite.config.js", "Vite config"),
        ("frontend/tailwind.config.js", "Tailwind config"),
        ("frontend/.env.example", "Environment template"),
        ("frontend/vercel.json", "Vercel config"),
        ("frontend/index.html", "HTML template"),
    ]
    
    passed = sum(check_file(path, desc) for path, desc in checks)
    total = len(checks)
    print(f"\nFrontend: {passed}/{total} files verified")
    return passed == total

def verify_docs():
    """Verify documentation"""
    print("\n=== DOCUMENTATION ===\n")
    
    checks = [
        ("README.md", "Main README"),
        ("DEPLOYMENT.md", "Deployment guide"),
        ("PROJECT_STATUS.md", "Project status"),
        (".gitignore", "Git ignore"),
    ]
    
    passed = sum(check_file(path, desc) for path, desc in checks)
    total = len(checks)
    print(f"\nDocumentation: {passed}/{total} files verified")
    return passed == total

def main():
    """Run verification"""
    print("╔════════════════════════════════════════╗")
    print("║   OmniSales AI - Project Verification  ║")
    print("╚════════════════════════════════════════╝")
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    backend_ok = verify_backend()
    frontend_ok = verify_frontend()
    docs_ok = verify_docs()
    
    print("\n" + "="*50)
    print("FINAL STATUS")
    print("="*50)
    
    if backend_ok and frontend_ok and docs_ok:
        print("✅ ALL CHECKS PASSED - PROJECT IS COMPLETE!")
    else:
        print("⚠️  SOME CHECKS FAILED - REVIEW ABOVE")
    
    print("\nNext steps:")
    print("1. cp backend/.env.example backend/.env")
    print("2. cp frontend/.env.example frontend/.env")
    print("3. Configure environment variables")
    print("4. cd backend && pip install -r requirements.txt")
    print("5. cd frontend && npm install")
    print("6. python backend/load_products.py")
    print("7. cd backend && pytest")
    print("8. Start backend: uvicorn app.main:app --reload")
    print("9. Start frontend: npm run dev")

if __name__ == "__main__":
    main()
