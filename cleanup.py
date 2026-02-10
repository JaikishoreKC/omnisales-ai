#!/usr/bin/env python3
"""
OmniSales AI - Automated Cleanup Script
Removes redundant files and fixes broken imports
"""

import os
import shutil
from pathlib import Path

# Change to project root
os.chdir(Path(__file__).parent)

def delete_file(path):
    """Delete a file if it exists"""
    if os.path.exists(path):
        os.remove(path)
        print(f"✓ Deleted: {path}")
        return True
    else:
        print(f"⊘ Not found: {path}")
        return False

def delete_directory(path):
    """Delete a directory if it exists and is empty"""
    if os.path.exists(path) and os.path.isdir(path):
        try:
            os.rmdir(path)
            print(f"✓ Removed empty directory: {path}")
            return True
        except OSError:
            print(f"⊘ Directory not empty, keeping: {path}")
            return False
    return False

def fix_import(filepath, old_import, new_import):
    """Fix an import in a file"""
    if not os.path.exists(filepath):
        print(f"⊘ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if old_import not in content:
        print(f"⊘ Import not found in {filepath}")
        return False
    
    new_content = content.replace(old_import, new_import)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ Fixed import in: {filepath}")
    return True

def remove_import(filepath, import_to_remove):
    """Remove an import line from a file"""
    if not os.path.exists(filepath):
        print(f"⊘ File not found: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = [line for line in lines if import_to_remove not in line]
    
    if len(new_lines) == len(lines):
        print(f"⊘ Import not found in {filepath}")
        return False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✓ Removed import from: {filepath}")
    return True

def main():
    print("╔═══════════════════════════════════════════╗")
    print("║   OmniSales AI - Automated Cleanup        ║")
    print("╚═══════════════════════════════════════════╝\n")
    
    # Step 1: Fix broken imports
    print("Step 1: Fixing Broken Imports")
    print("-" * 50)
    fix_import(
        "backend/app/memory/conversation_memory.py",
        "from app.db.mongodb import get_database",
        "from app.db.mongo import get_database"
    )
    print()
    
    # Step 2: Remove unused imports
    print("Step 2: Removing Unused Imports")
    print("-" * 50)
    remove_import(
        "backend/app/orchestrator/router.py",
        "from app.memory.session_memory import save_message"
    )
    print()
    
    # Step 3: Delete redundant files
    print("Step 3: Deleting Redundant Files")
    print("-" * 50)
    
    files_to_delete = [
        # API files
        "backend/app/api/routes.py",
        "backend/app/api/endpoints/chat.py",
        "backend/app/api/endpoints/users.py",
        "backend/app/api/endpoints/analytics.py",
        
        # Legacy database
        "backend/app/db/mongodb.py",
        
        # Unused orchestrator
        "backend/app/orchestrator/agent_orchestrator.py",
        
        # Unused agents
        "backend/app/agents/base_agent.py",
        "backend/app/agents/sales_agent.py",
        "backend/app/agents/analytics_agent.py",
    ]
    
    deleted = 0
    for file in files_to_delete:
        if delete_file(file):
            deleted += 1
    
    print()
    
    # Step 4: Clean empty directories
    print("Step 4: Cleaning Empty Directories")
    print("-" * 50)
    delete_directory("backend/app/api/endpoints")
    print()
    
    # Summary
    print("=" * 50)
    print("CLEANUP SUMMARY")
    print("=" * 50)
    print(f"✓ Imports fixed: 1")
    print(f"✓ Imports removed: 1")
    print(f"✓ Files deleted: {deleted}")
    print()
    print("✅ Cleanup complete!")
    print()
    print("Next steps:")
    print("1. Run: python verify.py")
    print("2. Run: cd backend && pytest")
    print("3. Review CLEANUP_REPORT.md for details")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        print("Please review CLEANUP_REPORT.md and run cleanup manually if needed.")
