# LiteFinPad Expense Tracker - Optimized Dependencies
# Generated: 2025-12-13
# See DEPENDENCY_AUDIT_REPORT.md for details

# Windows-specific (tray icon functionality)
pywin32>=306

# GUI Framework
customtkinter~=5.2.2

# Image processing
# NOTE: May not be needed - comments in main.py suggest PIL was removed
# Test before keeping this dependency
Pillow>=12.0.0

# Build tool
pyinstaller>=6.17.0

# Export functionality
xlsxwriter>=3.2.0
fpdf2>=2.8.0

# AI Chat feature (local LLM inference)
llama-cpp-python>=0.3.16
