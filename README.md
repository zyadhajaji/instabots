# Instagram DM Automation Bot

A local Instagram DM automation bot with a responsive GUI for managing all commands through an easy-to-use interface. The bot opens a browser window for you to use your Instagram account safely.

## Features

### Core Messaging Functions
- ✅ Send text messages to individual users
- ✅ Send bulk/broadcast messages to multiple users
- ✅ Message templates with easy management
- ✅ Auto-save sent messages log

### Targeting & Filtering
- ✅ Get followers list from any user
- ✅ Import contact lists from files
- ✅ Manage multiple contact lists
- ✅ Send to specific number of users (limits)

### Conversation Management
- ✅ Message history tracking
- ✅ Success/failure logging
- ✅ Session persistence

### Safety & Throttling
- ✅ Randomized delays between messages (configurable)
- ✅ Daily/hourly message limits
- ✅ Human-like typing behavior
- ✅ Browser-based (not headless by default) for better safety

### User Interface
- ✅ Responsive GUI application
- ✅ Dashboard for campaign management
- ✅ Message preview and template management
- ✅ Contact list management
- ✅ Statistics and reporting
- ✅ Settings configuration

## Installation

1. **Install Python 3.8+** if you haven't already

2. **Install Chrome Browser** - The bot uses Chrome/Chromium

3. **Install ChromeDriver**:
   - Download from https://chromedriver.chromium.org/
   - Or use: `pip install webdriver-manager` (auto-downloads driver)

4. **Install dependencies**:
   ```bash
   # On Windows (if pip is not recognized, use):
   py -m pip install -r requirements.txt
   
   # Or if python is in PATH:
   python -m pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   ```bash
   # On Windows:
   py main.py
   
   # Or if python is in PATH:
   python main.py
   ```

2. **Login** (Two Methods):
   
   **Method 1: Manual Login (Recommended)** 🔓
   - Click "🔐 Login" in the sidebar
   - Select "Manual Login (Recommended)"
   - Click "Open Browser & Login Manually"
   - Log in manually in the browser window (handles CAPTCHA/2FA smoothly)
   - The bot will automatically detect when you're logged in
   - This method is safer and less likely to trigger detection
   
   **Method 2: Auto Login** 🤖
   - Click "🔐 Login" in the sidebar
   - Select "Auto Login"
   - Enter your username and password
   - Click "Auto Login & Open Browser"
   - Complete any CAPTCHA or 2FA if prompted
   - The browser will stay open for you to monitor

3. **Send Messages**:
   - **Single DM**: Send a message to one user
   - **Bulk Messages**: Send to multiple users from:
     - Manual list (paste usernames)
     - Contact list (saved lists)
     - Followers of a user (auto-fetch)

4. **Manage Templates**:
   - Create reusable message templates
   - Load templates when sending messages
   - Edit and delete templates

5. **Manage Contact Lists**:
   - Create contact lists
   - Import from text files (one username per line)
   - Save followers lists as contact lists

6. **Configure Settings**:
   - Set delay ranges between messages
   - Set daily/hourly message limits
   - Adjust safety parameters

## File Structure

```
instabot/
├── main.py          # Entry point
├── bot.py           # Core bot logic (Selenium automation)
├── gui.py           # GUI application (Tkinter)
├── config.py        # Configuration management
├── config.json      # Saved configuration (auto-created)
├── session.json     # Session data (auto-created)
└── requirements.txt # Python dependencies
```

## Configuration

All settings are saved in `config.json`:
- Message templates
- Contact lists
- Safety settings
- Message logs

## Safety Features

- **Randomized Delays**: Messages are sent with random delays (default 5-10 seconds)
- **Human-like Typing**: Messages are typed character by character
- **Browser Visible**: Browser stays open so you can monitor activity
- **Rate Limiting**: Configurable daily/hourly limits
- **Session Management**: Tracks sent messages to avoid duplicates

## Important Notes

⚠️ **Use Responsibly**:
- Instagram has rate limits and may restrict accounts that send too many messages
- Start with small batches and low delays
- Monitor your account for any restrictions
- This tool is for educational purposes

⚠️ **Security**:
- Credentials are only used for browser login
- No credentials are stored
- All data is stored locally

## Troubleshooting

**ChromeDriver Issues**:
- Make sure Chrome browser is installed
- Update ChromeDriver to match your Chrome version
- Or install `webdriver-manager` for automatic driver management

**Login Issues**:
- Complete CAPTCHA manually in browser
- Handle 2FA if enabled
- Check internet connection

**Message Sending Fails**:
- Make sure you're logged in
- Check if user exists
- Instagram may have temporary restrictions

## License

This project is for educational purposes only. Use at your own risk.
