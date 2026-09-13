# Quick Start Guide

## First Time Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application**:
   ```bash
   python main.py
   ```

## Basic Workflow

### Step 1: Login

**Recommended: Manual Login** 🔓
1. Click "🔐 Login" in the sidebar
2. Select "Manual Login (Recommended)"
3. Click "Open Browser & Login Manually"
4. Log in manually in the browser window (you can handle CAPTCHA/2FA yourself)
5. The bot will automatically detect when you're logged in
6. You'll see a confirmation message when ready

**Alternative: Auto Login** 🤖
1. Click "🔐 Login" in the sidebar
2. Select "Auto Login"
3. Enter your Instagram username and password
4. Click "Auto Login & Open Browser"
5. Complete any CAPTCHA or 2FA if prompted
6. The browser will stay open - keep it open while using the bot

**Tip**: Manual login is recommended because:
- You can use saved browser sessions/cookies
- Handles CAPTCHA/2FA more smoothly
- Less automated behavior = lower detection risk

### Step 2: Create a Message Template (Optional)
1. Click "📝 Templates" in the sidebar
2. Enter a template name (e.g., "Welcome Message")
3. Type your message
4. Click "Save Template"
5. You can now use this template when sending messages

### Step 3: Send Messages

#### Option A: Send to One User
1. Click "💬 Send Single DM"
2. Enter the username
3. Type or load a message template
4. Click "Send DM"

#### Option B: Send to Multiple Users
1. Click "📢 Bulk Messages"
2. Choose your source:
   - **Manual List**: Paste usernames (one per line)
   - **Contact List**: Select a saved contact list
   - **Followers of User**: Enter a username to get their followers
3. Enter or load your message
4. Set max messages (optional limit)
5. Click "Send Bulk Messages"

### Step 4: Manage Contact Lists
1. Click "📋 Contact Lists"
2. To create a new list:
   - Enter usernames (one per line) or import from file
   - Click "Save List"
   - Enter a name for the list
3. To use an existing list:
   - Select it from the dropdown
   - Click "Load List"

## Example: Import Contact List from File

Create a text file `contacts.txt` with usernames (one per line):
```
user1
user2
user3
```

Then:
1. Go to "📋 Contact Lists"
2. Click "Import from File"
3. Select your `contacts.txt` file
4. Click "Save List" and give it a name

## Tips

- **Start Small**: Test with 1-2 messages first
- **Use Delays**: Default delays (5-10 seconds) help avoid detection
- **Monitor Browser**: Keep the browser window visible to monitor activity
- **Check Statistics**: Use "📊 Statistics" to see your sending history
- **Adjust Settings**: Go to "⚙️ Settings" to customize delays and limits

## Safety Recommendations

- Don't send more than 20-30 messages per hour
- Use delays of at least 5-10 seconds between messages
- Take breaks between bulk sends
- Monitor your account for any restrictions
