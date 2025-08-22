# Telegram Message Sender

A Python script to send messages to Telegram contacts using their @usernames through your personal Telegram account.

## Features

- ✅ Send messages using your personal Telegram account
- ✅ Message individual users by @username
- ✅ Interactive mode for multiple conversations
- ✅ Bulk messaging to multiple users
- ✅ Rate limiting protection
- ✅ Comprehensive error handling
- ✅ Logging for debugging
- ✅ Secure credential management

## Prerequisites

1. **Telegram API Credentials**: Get your `api_id` and `api_hash` from [my.telegram.org](https://my.telegram.org)
2. **Python 3.7+**: Make sure you have Python installed
3. **Phone Number**: Your phone number registered with Telegram

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   cd tg_link
   pip install -r requirements.txt
   ```

3. **Set up credentials**:
   - Copy `.env.example` to `.env`
   - Fill in your credentials in the `.env` file:
   ```
   API_ID=your_api_id_here
   API_HASH=your_api_hash_here
   PHONE_NUMBER=+1234567890
   SESSION_NAME=telegram_session
   ```

## Usage

### 1. Single Message
Send a message to one user:
```bash
python telegram_sender.py @username "Hello there!"
```

### 2. Interactive Mode
Run in interactive mode for multiple conversations:
```bash
python telegram_sender.py --interactive
```

### 3. Bulk Messaging
Send the same message to multiple users:

First, create a file with usernames (one per line):
```
username1
@username2
username3
```

Then run:
```bash
python telegram_sender.py --bulk usernames.txt "Your bulk message here"
```

Add delay between messages (default is 1 second):
```bash
python telegram_sender.py --bulk usernames.txt "Message" --delay 2
```

## Command Line Options

- `username`: Username to send message to (with or without @)
- `message`: Message to send
- `--interactive`, `-i`: Run in interactive mode
- `--bulk`, `-b`: File containing usernames (one per line)
- `--delay`, `-d`: Delay between bulk messages in seconds (default: 1)

## First Run Authentication

On your first run, the script will:
1. Ask for your phone number (if not in .env)
2. Send you a verification code via Telegram
3. Ask you to enter the verification code
4. If you have 2FA enabled, ask for your password
5. Create a session file for future use (no re-authentication needed)

## Security Notes

- **Never share your API credentials** or session files
- **Use environment variables** (.env file) to store sensitive data
- **Session files** contain authentication tokens - keep them secure
- **Rate limiting** is built-in to avoid getting banned

## Error Handling

The script handles common errors:
- Invalid usernames
- Rate limiting (flood wait)
- Network issues
- Authentication problems
- Missing credentials

## Logging

- Logs are saved to `telegram_sender.log`
- Console output shows real-time status
- Different log levels for debugging

## Troubleshooting

### "Username not found"
- Make sure the username exists and is spelled correctly
- Some users might have privacy settings that prevent messaging

### "Rate limited"
- Wait for the specified time before trying again
- Increase delay between bulk messages

### "Authentication failed"
- Check your API credentials in the .env file
- Delete session files and re-authenticate

### "Missing credentials"
- Make sure your .env file exists and contains all required fields
- Check that API_ID is a number, not a string

## Example .env File

```
API_ID=1234567
API_HASH=abcdef1234567890abcdef1234567890
PHONE_NUMBER=+1234567890
SESSION_NAME=my_telegram_session
```

## Legal Notice

This script is for personal use only. Make sure to:
- Respect Telegram's Terms of Service
- Don't spam users
- Follow local laws regarding automated messaging
- Use responsibly and ethically

## Support

If you encounter issues:
1. Check the logs in `telegram_sender.log`
2. Verify your credentials are correct
3. Make sure you have the latest version of dependencies
4. Check Telegram's API status

---

**Happy messaging! 🚀**
