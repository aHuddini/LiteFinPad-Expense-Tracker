# GitHub Repository Setup Guide

This guide walks you through setting up LiteFinPad on GitHub, including initial upload, release management, and best practices for maintaining a private repository.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Initial Repository Setup](#initial-repository-setup)
- [First Upload](#first-upload)
- [Creating Releases](#creating-releases)
- [Managing Source Code](#managing-source-code)
- [Repository Settings](#repository-settings)
- [Maintaining the Repository](#maintaining-the-repository)
- [Troubleshooting](#troubleshooting)

---

## 🔑 Prerequisites

### 1. GitHub Account
- Create account at https://github.com
- Verify your email address
- (Optional) Set up two-factor authentication

### 2. Git Installation
Download and install Git:
- **Windows**: https://git-scm.com/download/win
- During installation, select "Git Bash" and "Git from command line"

### 3. Configure Git
```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

## 🆕 Initial Repository Setup

### Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Fill in repository details:

   **Step 1: Repository Basics**
   - **Owner**: Your GitHub username (auto-selected)
   - **Repository name**: `LiteFinPad`
   - **Description**: `Lightweight, offline-first Windows expense tracker with modern UI`
   
   **Step 2: Configuration**
   - **Choose visibility**: 🔒 **Private** (for personal use)
   - **Add README**: ☐ **Off** (we already have README.md locally)
   - **Add .gitignore**: **No .gitignore** (we already have .gitignore locally)
   - **Add license**: **No license** (we already have LICENSE file locally)

   ⚠️ **IMPORTANT**: Leave all three options UNCHECKED/OFF. We already have these files in your local project, and GitHub creating them would cause conflicts when pushing.

3. Click **"Create repository"**

### Step 2: Prepare Local Repository

**First, open terminal in your LiteFinPad folder:**

**Option A: Right-click method (Easiest)**
1. Open File Explorer
2. Navigate to your LiteFinPad folder (where you see main.py, gui.py, etc.)
3. **Shift + Right-click** in empty space
4. Select **"Open PowerShell window here"** or **"Open in Terminal"**
5. Skip to the `git init` command below ✓

**Option B: Manual navigation**
1. Open PowerShell or Command Prompt
2. In File Explorer, navigate to LiteFinPad folder
3. Click address bar, right-click, **Copy address**
4. In PowerShell, type: `cd "` (with opening quote)
5. Right-click to paste the path
6. Add closing quote `"` and press Enter

**Example paths** (yours may be different):
```bash
# If OneDrive path has spaces, use quotes:
cd "C:\Users\YourName\OneDrive - Personal\Documents\LiteFinPad"

# Or simple path:
cd C:\Users\YourName\Documents\LiteFinPad
```

**Now run these commands:**

```bash
# Initialize git repository
git init

# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: LiteFinPad v3.4"
```

### Step 3: Connect to GitHub

```bash
# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/LiteFinPad.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

**Expected Output**:
```
Enumerating objects: 50, done.
Counting objects: 100% (50/50), done.
Writing objects: 100% (50/50), 1.23 MiB | 2.45 MiB/s, done.
Total 50 (delta 0), reused 0 (delta 0)
To https://github.com/YOUR_USERNAME/LiteFinPad.git
 * [new branch]      main -> main
```

---

## 📤 First Upload

### What Gets Uploaded?

Based on your `.gitignore`, the following are **INCLUDED**:
- ✅ Source code (`.py` files)
- ✅ Documentation (`.md` files)
- ✅ Build scripts (`.bat` files)
- ✅ Requirements (`requirements.txt`)
- ✅ License and attribution files
- ✅ Application icon (`icon.ico`)
- ✅ Version file (`version.txt`)
- ✅ PyInstaller specs (`.spec` files)

The following are **EXCLUDED**:
- ❌ Build artifacts (`build/`, `dist/`)
- ❌ User data (`data_*/`, `*.json` except requirements)
- ❌ Logs (`logs/`, `*.log`)
- ❌ Backups (`backup_*/`)
- ❌ Python cache (`__pycache__/`, `*.pyc`)
- ❌ IDE files (`.vscode/`, `.idea/`)
- ❌ Archive documentation (`archive_old_docs/`)

### Verify Upload

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/LiteFinPad`
2. You should see:
   - 📂 All source files
   - 📄 README.md displayed on main page
   - 📝 License information
   - 🚫 No build folders or personal data

---

## 🚀 Creating Releases

Releases are how you distribute compiled executables without including them in the repository.

### Step 1: Build Release Version

```bash
# Navigate to project folder
cd C:\Users\asad2\OneDrive\Documents\LiteFinPad

# Build production release
build_release.bat
```

**Output**: `dist\LiteFinPad_v3.4\` folder with executable

### Step 2: Create Release Archive

1. Navigate to `dist\LiteFinPad_v3.4\`
2. Select all contents of the folder
3. Right-click → **Send to** → **Compressed (zipped) folder**
4. Rename to: `LiteFinPad_v3.4-Windows-x64.zip`

**What to Include in ZIP**:
- ✅ `LiteFinPad_v3.4.exe` (main executable)
- ✅ `_internal/` folder (dependencies)
- ✅ `error_logger.py` (error logging support)
- ✅ `data_2025-10/` folder (empty starter folder)

**ZIP Size**: Should be ~23 MB

### Step 3: Create GitHub Release

1. Go to your repository on GitHub
2. Click **"Releases"** (right sidebar)
3. Click **"Create a new release"**

4. **Tag version**:
   - Click "Choose a tag"
   - Type: `v3.4`
   - Click "Create new tag: v3.4 on publish"

5. **Release title**: `v3.4 - Keyboard Shortcut Enhancements`

6. **Release description**:
   ```markdown
   ## ⌨️ Version 3.4 - Keyboard Shortcut Enhancements
   
   ### What's New
   - ✨ **Sequential Enter Key Navigation**: Press Enter to move between fields (Amount → Description → Submit)
   - ✨ **Escape Key Support**: Close dialogs instantly with Escape key
   - ✨ **Consistent Shortcuts**: Same keyboard behavior across all three expense entry methods
   - 🐛 **Fixed**: Quick Add dialog crash when pressing Enter without description
   
   ### Features
   - 💰 Track monthly expenses with offline storage
   - 📊 Real-time analytics (monthly totals, weekly/daily averages)
   - 📤 Export to Excel and PDF
   - 🎯 System tray integration with Quick Add
   - ⌨️ Full keyboard navigation support
   
   ### Installation
   1. Download `LiteFinPad_v3.4-Windows-x64.zip`
   2. Extract to desired location
   3. Run `LiteFinPad_v3.4.exe`
   4. Look for icon in system tray!
   
   ### Requirements
   - Windows 10 or later
   - No Python installation required
   
   ### File Information
   - **Size**: ~23 MB (compressed)
   - **Type**: Standalone executable
   - **Python Version**: 3.14.0
   - **Architecture**: x64 (64-bit)
   
   ---
   
   **Full Changelog**: [CHANGELOG.md](../blob/main/CHANGELOG.md)
   ```

7. **Attach binary**:
   - Drag and drop `LiteFinPad_v3.4-Windows-x64.zip`
   - Wait for upload to complete (green checkmark)

8. **Release options**:
   - ☑ **Set as the latest release** (check this)
   - ☐ Set as a pre-release (leave unchecked)

9. Click **"Publish release"**

### Step 4: Verify Release

1. Go to your repository's main page
2. You should see a **"Latest"** badge next to **Releases**
3. Click **Releases** → Should see `v3.4` with download link
4. Click the ZIP file to download and test

---

## 📂 Managing Source Code

### Daily Development Workflow

```bash
# Make changes to code
# Test thoroughly

# Stage changes
git add .

# Commit with message
git commit -m "feat: add dark mode support"

# Push to GitHub
git push origin main
```

### Commit Message Best Practices

Use conventional commit format:

| Type | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature | `feat: add category filtering` |
| `fix` | Bug fix | `fix: resolve tray icon crash` |
| `docs` | Documentation | `docs: update README with new features` |
| `refactor` | Code cleanup | `refactor: simplify expense validation` |
| `perf` | Performance | `perf: optimize data loading` |
| `style` | Formatting | `style: format code with black` |
| `chore` | Build/tooling | `chore: update dependencies` |

### Viewing History

```bash
# View commit history
git log --oneline

# View changes in last commit
git show

# View status
git status
```

---

## ⚙️ Repository Settings

### Recommended Settings (Private Repo)

1. Go to repository → **Settings**

2. **General** → **Features**:
   - ✅ Issues (for bug tracking)
   - ✅ Wiki (for extended documentation)
   - ☐ Discussions (optional)
   - ☐ Projects (optional)

3. **General** → **Pull Requests**:
   - ✅ Allow squash merging
   - ☐ Allow merge commits (personal preference)
   - ☐ Allow rebase merging (personal preference)
   - ✅ Automatically delete head branches

4. **Security** → **Code security and analysis**:
   - ✅ Dependency graph
   - ✅ Dependabot alerts
   - ☐ Dependabot security updates (optional)

### Adding Collaborators (Optional)

If you want others to access your private repo:

1. **Settings** → **Collaborators**
2. Click **"Add people"**
3. Enter GitHub username or email
4. Choose permission level:
   - **Read**: View only
   - **Write**: Can push code
   - **Admin**: Full control

---

## 🔄 Maintaining the Repository

### Creating New Releases

**For each new version**:

1. **Develop and test** locally
2. **Update version**:
   ```bash
   # Auto-increment with build script
   build_release.bat major    # For major releases (3.4 → 4.0)
   # OR
   build_dev.bat increment    # For minor updates (3.4 → 3.5)
   ```

3. **Update CHANGELOG.md**:
   - Add new version section at top
   - Document all changes
   - Include bug fixes, features, improvements

4. **Commit changes**:
   ```bash
   git add .
   git commit -m "chore: bump version to v3.5"
   git push origin main
   ```

5. **Create GitHub Release** (follow "Creating Releases" steps above)

### Managing Issues

**Creating Issues** (for tracking your own bugs/features):

1. Go to **Issues** tab
2. Click **"New issue"**
3. Template:
   ```markdown
   **Type**: Bug / Feature / Documentation
   
   **Description**:
   Clear description of issue or feature request
   
   **Steps to Reproduce** (if bug):
   1. Do X
   2. Do Y
   3. See error
   
   **Expected Behavior**:
   What should happen
   
   **Notes**:
   Additional context
   ```

**Closing Issues**:
- Reference in commit: `git commit -m "fix: resolve tray icon bug (fixes #1)"`
- Manually close on GitHub after verification

### Keeping Documentation Updated

Files to update regularly:
- **CHANGELOG.md**: Every release
- **README.md**: Major feature additions
- **DEPENDENCIES.md**: When changing libraries
- **BUILD_SYSTEM_GUIDE.md**: Build process changes

---

## 🌍 Accessing from Another Computer

This is the key reason for GitHub - access your project anywhere!

### Clone Repository

```bash
# On your new computer
cd C:\Users\YourName\Documents

# Clone the repository
git clone https://github.com/YOUR_USERNAME/LiteFinPad.git

# Enter the folder
cd LiteFinPad

# Install dependencies
python -m pip install -r requirements.txt

# Run the application
python main.py
```

### Pull Latest Changes

```bash
# Navigate to repository
cd C:\Users\YourName\Documents\LiteFinPad

# Get latest changes from GitHub
git pull origin main

# If dependencies changed, reinstall
python -m pip install -r requirements.txt --upgrade
```

### Push Changes from New Computer

```bash
# Make changes locally
# Test changes

# Commit and push
git add .
git commit -m "feat: add new feature from laptop"
git push origin main
```

---

## 🔍 Searching Your Code

### GitHub Search

From your repository page:
1. Press `/` or click search bar
2. Search options:
   - **This repository**: Search only this project
   - **Code**: Search in files
   - **Issues**: Search issues
   - **Commits**: Search commit messages

**Example Searches**:
- `def add_expense` - Find function definition
- `TODO` - Find all TODO comments
- `filename:gui.py` - Search specific file

---

## 📊 Repository Insights

View project statistics:

1. Go to repository → **Insights**
2. Useful sections:
   - **Pulse**: Recent activity summary
   - **Contributors**: Who contributed what
   - **Traffic**: Views and clones (for private repos, only you)
   - **Commits**: Commit history visualization
   - **Code frequency**: Lines added/removed over time

---

## 🛠️ Troubleshooting

### Issue: "Permission denied (publickey)"

**Solution**: Set up authentication

**Option A: Personal Access Token (Recommended)**
1. GitHub → **Settings** → **Developer settings** → **Personal access tokens**
2. Generate new token (classic)
3. Give it **repo** permissions
4. Copy token
5. Use token as password when pushing

**Option B: SSH Key**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
```

### Issue: "Failed to push some refs"

**Solution**: Pull first, then push
```bash
git pull origin main --rebase
git push origin main
```

### Issue: ".gitignore not working"

**Solution**: Clear Git cache
```bash
git rm -r --cached .
git add .
git commit -m "chore: fix .gitignore"
git push origin main
```

### Issue: "Large file detected"

**Solution**: Remove large files
```bash
# Remove from git (but keep locally)
git rm --cached path/to/large/file

# Add to .gitignore
echo "path/to/large/file" >> .gitignore

# Commit changes
git add .gitignore
git commit -m "chore: remove large file from git"
```

**Note**: GitHub has a 100 MB file size limit. Use releases for large binaries.

---

## 📝 Quick Reference Commands

### Basic Git Workflow
```bash
# Check status
git status

# Add all changes
git add .

# Commit with message
git commit -m "your message"

# Push to GitHub
git push origin main

# Pull from GitHub
git pull origin main

# View history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename.py
```

### Repository Management
```bash
# View remote URL
git remote -v

# Change remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/LiteFinPad.git

# Create new branch
git checkout -b feature-branch

# Switch branches
git checkout main

# List branches
git branch -a
```

---

## 🔐 Security Best Practices

### ✅ Do's
- ✅ Use `.gitignore` to exclude sensitive data
- ✅ Keep personal data (`data_*/`) out of repository
- ✅ Use personal access tokens instead of passwords
- ✅ Enable two-factor authentication on GitHub
- ✅ Review `.gitignore` before first push

### ❌ Don'ts
- ❌ Don't commit API keys or passwords
- ❌ Don't commit personal expense data
- ❌ Don't commit build artifacts (use releases)
- ❌ Don't commit large binary files
- ❌ Don't share private repo links publicly

---

## 📖 Additional Resources

### Git Learning
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)

### GitHub Features
- [GitHub Docs](https://docs.github.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Issues](https://docs.github.com/en/issues)

---

## ✅ Checklist: First-Time Setup

- [ ] Git installed and configured
- [ ] GitHub account created
- [ ] Repository created on GitHub (private)
- [ ] Local repository initialized
- [ ] Connected local repo to GitHub
- [ ] Pushed initial code
- [ ] Verified files on GitHub (no personal data)
- [ ] Built release version v3.4
- [ ] Created ZIP archive
- [ ] Published first GitHub release
- [ ] Tested downloading and running release
- [ ] Cloned repository on second computer (if applicable)

---

## 📞 Need Help?

- **Git Questions**: https://stackoverflow.com/questions/tagged/git
- **GitHub Support**: https://support.github.com/
- **LiteFinPad Issues**: Open an issue in your repository

---

**Congratulations!** 🎉 Your LiteFinPad project is now professionally managed on GitHub.

You can now:
- ✅ Access your code from any computer
- ✅ Track changes with version control
- ✅ Distribute releases without including source in repo
- ✅ Maintain professional documentation
- ✅ Keep a clean backup in the cloud

---

*Last Updated: October 19, 2025*

