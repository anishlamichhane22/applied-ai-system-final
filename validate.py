#!/usr/bin/env python3
"""
PawPal Validation Script
Tests that all components work together without requiring API keys.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    try:
        from agent.tools import suggest_tasks, optimize_schedule, explain_plan
        from agent.planner import run_planner
        import main
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_dependencies():
    """Test that all dependencies are installed"""
    try:
        import anthropic
        import streamlit
        import dotenv
        import pytest
        print("✅ All dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    required_files = [
        'main.py',
        'README.md',
        'model_card.md',
        'requirements.txt',
        'agent/tools.py',
        'agent/planner.py',
        'eval/test_cases.py',
        '.env.example'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)

    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present")
        return True

def test_readme_content():
    """Test that README has required sections"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read().lower()

        required_sections = [
            'pawpal',
            'installation',
            'usage',
            'testing',
            'architecture',
            'demo'
        ]

        missing = []
        for section in required_sections:
            if section not in content:
                missing.append(section)

        if missing:
            print(f"❌ README missing sections: {missing}")
            return False
        else:
            print("✅ README has all required sections")
            return True
    except Exception as e:
        print(f"❌ Error reading README: {e}")
        return False

def main():
    """Run all validation tests"""
    print("🐾 PawPal Validation Script")
    print("=" * 40)

    tests = [
        test_file_structure,
        test_dependencies,
        test_imports,
        test_readme_content
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print("=" * 40)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All validation tests passed! Your PawPal project is ready.")
        print("\nNext steps:")
        print("1. Set up your Anthropic API key in .env")
        print("2. Run: streamlit run main.py")
        print("3. Test with different pet scenarios")
        return 0
    else:
        print("❌ Some validation tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())