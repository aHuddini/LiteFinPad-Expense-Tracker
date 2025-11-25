# Contributing to LiteFinPad

Thank you for considering contributing to LiteFinPad! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Building from Source](#building-from-source)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Project Philosophy](#project-philosophy)

---

## 🤝 Code of Conduct

- Be respectful and constructive
- Focus on what is best for the community
- Show empathy towards other contributors
- Accept constructive criticism gracefully

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** (Python 3.14 recommended)
- **Windows 10+** (currently Windows-only)
- **Git** for version control
- **Text editor** (VS Code recommended)

### System Requirements

- Windows 10 or later
- 100 MB free disk space (for development)
- Internet connection (for installing dependencies)

---

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/LiteFinPad.git
cd LiteFinPad
```

### 2. Install Dependencies

**IMPORTANT**: Use `python -m pip` to ensure packages install to the correct Python version:

```bash
python -m pip install -r requirements.txt
```

This installs:
- `pywin32>=306` - Windows system tray integration
- `xlsxwriter>=3.2.0` - Excel export
- `fpdf==1.7.2` - PDF generation (specific version for size optimization)
- `pyinstaller>=6.16.0` - Executable building

### 3. Verify Installation

```bash
# Run the application from source
python main.py
```

You should see the LiteFinPad icon appear in your system tray.

---

## 🤖 AI-Assisted Development Workflow

LiteFinPad is developed using “vibe-coding” with AI assistance (Claude Sonnet, GPT-Codex).

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│ 1. DISCUSS        User describes feature or change          │
├─────────────────────────────────────────────────────────────┤
│ 2. PLAN           AI proposes implementation approach        │
├─────────────────────────────────────────────────────────────┤
│ 3. IMPLEMENT      AI makes code changes                      │
├─────────────────────────────────────────────────────────────┤
│ 4. REVIEW         User reviews changes, asks questions       │
├─────────────────────────────────────────────────────────────┤
│ 5. TEST           User builds and tests application          │
├─────────────────────────────────────────────────────────────┤
│ 6. ITERATE        Debug if needed, repeat cycle              │
└─────────────────────────────────────────────────────────────┘
```

### Realistic Time Expectations

#### Simple Features (⭐⭐)
- Total: 30–45 min (AI 10–15 min, Review 5–10 min, Testing 15–20 min)

#### Medium Features (⭐⭐⭐)
- Total: 60–90 min (AI 20–30 min, Review 15–20 min, Testing 25–40 min)

#### Complex Features (⭐⭐⭐⭐)
- Total: 90–150 min (AI 30–50 min, Review 20–30 min, Testing 40–70 min)

### Your Role

- Strategic Lead: Define scope, approve approaches
- Quality Gatekeeper: Review code (~35%), test thoroughly (~35%), iterate (~15%)

---

## 🔨 Building from Source

### Development Builds

```bash
build_dev.bat         # Fast test build
build_dev.bat increment
```

### Production Builds

```bash
build_release.bat
build_release.bat major
```

### Manual (Advanced)

```bash
pyinstaller LiteFinPad_v3.4.spec
```

---

## 🛠️ Making Changes

### Branch Naming

- `feature/...`, `bugfix/...`, `docs/...`, `refactor/...`

### Commit Messages (Conventional)

- `feat: add quick add dialog`
- `fix: prevent crash on empty description`

---

## 🧪 Testing

### Manual Checklist

- App starts, tray icon appears
- Add/edit/delete expenses in all flows
- Monthly totals update correctly
- Exports (PDF/Excel) match UI data
- No visual glitches; shortcuts work

### Commands

```bash
python main.py              # source testing
build_dev.bat && dist/...   # build testing
```

---

## 📤 Submitting Changes

1. Branch off `main`
2. Make & test changes
3. Use `feat:`, `fix:` commit prefixes
4. Push and open PR with template

---

## 💻 Coding Standards

- PEP 8, 4 spaces
- Functions < 50 lines preferred
- Comment WHY, not WHAT
- Tkinter widgets named descriptively

---

## 🎯 Project Philosophy

1. Offline-first (no cloud sync, no telemetry)
2. Lightweight & fast (<25 MB bundle, <100 MB RAM)
3. User-centric design
4. Simplicity over feature bloat
5. Windows-native feel

---

## 📝 Documentation

Update:

- `README.md` for user features
- `CHANGELOG.md` for all changes
- Build/Dependency docs if needed

---

## 🐛 Bug Reports & 💡 Feature Requests

Use GitHub Issues with provided templates—include steps, expected behavior, screenshots, environment.

---

## 📜 License

By contributing, you agree your code is licensed under the MIT License.

---

**Thank you for contributing to LiteFinPad!**

