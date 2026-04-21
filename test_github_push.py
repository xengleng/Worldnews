#!/usr/bin/env python3
"""
Test GitHub push functionality
"""

import subprocess
import os
from pathlib import Path

def test_github_push():
    """Test pushing a file to GitHub."""
    print("🧪 Testing GitHub push functionality...")
    
    # Create a test file
    obsidian_vault = Path.home() / "Documents" / "openclaw"
    test_file = obsidian_vault / "World News" / "test_github_push.md"
    
    test_file.parent.mkdir(exist_ok=True)
    test_file.write_text("# Test GitHub Push\n\nThis is a test file to verify GitHub push works.\n")
    
    print(f"📝 Created test file: {test_file}")
    
    # Navigate to Obsidian vault
    original_cwd = Path.cwd()
    os.chdir(obsidian_vault)
    
    try:
        # Add file to git
        print("📤 Adding file to git...")
        subprocess.run(["git", "add", str(test_file.relative_to(obsidian_vault))], 
                      check=True, capture_output=True, text=True)
        
        # Commit
        print("💾 Committing changes...")
        subprocess.run(["git", "commit", "-m", "🧪 Test: GitHub push verification"], 
                      check=True, capture_output=True, text=True)
        
        # Push to GitHub
        print("🚀 Pushing to GitHub...")
        result = subprocess.run(["git", "push", "origin", "main"], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ SUCCESS: GitHub push works!")
            print(f"📊 Output: {result.stdout}")
        else:
            print("⚠️  Push failed, trying with -u flag...")
            result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ SUCCESS: GitHub push works (with -u flag)!")
            else:
                print(f"❌ FAILED: {result.stderr}")
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e.stderr}")
    finally:
        # Return to original directory
        os.chdir(original_cwd)
        
        # Clean up test file
        test_file.unlink(missing_ok=True)
        print("🧹 Cleaned up test file")

if __name__ == "__main__":
    test_github_push()