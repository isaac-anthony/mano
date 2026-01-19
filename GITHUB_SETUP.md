# GitHub Setup Instructions

## ✅ Git Repository Initialized

Your local git repository has been initialized and all files have been committed.

## 📤 Push to GitHub

### Option 1: Create New Repository on GitHub

1. **Go to GitHub:**
   - Visit: https://github.com/new
   - Log in to your GitHub account

2. **Create Repository:**
   - Repository name: `Mano.ai` (or your preferred name)
   - Description: "B2C Voice AI Restaurant Agent using Vapi and Square"
   - Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click **Create repository**

3. **Connect and Push:**
   ```bash
   cd /Users/isaacgutierrez/Cursor/Mano.ai
   
   # Add the remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/Mano.ai.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### Option 2: Use GitHub CLI (if installed)

```bash
cd /Users/isaacgutierrez/Cursor/Mano.ai
gh repo create Mano.ai --public --source=. --remote=origin --push
```

## 🔒 Security Reminder

Before pushing, verify that sensitive files are NOT committed:

```bash
git ls-files | grep -E "\.env|ngrok"
```

If you see `.env` or `ngrok` in the output, remove them:
```bash
git rm --cached .env
git rm --cached ngrok
git commit -m "Remove sensitive files"
```

## ✅ Verify What's Committed

Check what will be pushed:
```bash
git ls-files
```

You should see:
- ✅ All Python files
- ✅ Documentation files
- ✅ Configuration files (JSON, TXT)
- ❌ NO .env file
- ❌ NO ngrok binary

## 📝 Next Steps After Pushing

1. Add a description to your GitHub repository
2. Add topics/tags: `voice-ai`, `fastapi`, `square`, `vapi`, `restaurant`
3. Consider adding a LICENSE file
4. Update README with any additional setup instructions

## 🔄 Future Updates

To push future changes:
```bash
git add .
git commit -m "Your commit message"
git push
```
