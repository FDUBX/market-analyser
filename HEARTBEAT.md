# HEARTBEAT.md

## Market Analyzer Notifications

Check for pending notifications from Market Analyzer cron jobs and send them to Telegram.

**Frequency:** Every heartbeat (but process each notification only once)

**Steps:**
1. Check `/home/pi/.openclaw/workspace/skills/market-analyzer/notifications/` for `.txt` files
2. If files found:
   - Read each file
   - Send content to Telegram (François, user id: 6812190723)
   - Move processed file to `notifications/sent/` directory
3. If no files, continue silently

**Important:** Only process unprocessed files. Don't repeat notifications.
