# Discord Task Bot

A Discord bot that manages tasks with deadlines and sends automated daily reminders with user pings.

## Features

- **Slash Commands**: Modern Discord slash commands with separate fields for task name and deadline
- **Task Management**: Add, list, and complete tasks with deadlines
- **Daily Reminders**: Automated daily reminders at 9:00 AM with user pings
- **User Pings**: Mentions users when their tasks are due or overdue
- **Test Commands**: Built-in testing functionality to verify ping system

## Commands

### Main Commands
- `/addtask` - Add a new task (separate fields for name and deadline)
- `/listtasks` - List all active tasks
- `/complete` - Mark a task as completed
- `/setchannel` - Set current channel for daily reminders
- `/help` - Show all available commands

### Testing Commands
- `/testping` - Create a test task due today
- `/testreminder` - Manually trigger reminder now

### Legacy Commands (Still Available)
- `!addtask Task description | YYYY-MM-DD`
- `!listtasks`
- `!complete <task_id>`
- `!setchannel`

## Environment Variables

Required:
- `DISCORD_BOT_TOKEN` - Your Discord bot token

Optional:
- `REMINDER_HOUR` - Hour for daily reminders (default: 9)
- `REMINDER_MINUTE` - Minute for daily reminders (default: 0)
- `REMINDER_CHANNEL_ID` - Default reminder channel
- `OVERDUE_CLEANUP_DAYS` - Days to keep overdue tasks (default: 30)

## Setup

1. Create a Discord application at https://discord.com/developers/applications
2. Create a bot and get the token
3. Set the `DISCORD_BOT_TOKEN` environment variable
4. Run the bot: `python main.py`

## Deployment

This bot is ready for deployment on:
- Fly.io (recommended for free 24/7 hosting)
- Railway
- Render
- Any Docker-compatible platform

## Files

- `main.py` - Main bot file with Discord commands
- `task_manager.py` - Task storage and management
- `reminder_scheduler.py` - Daily reminder system
- `config.py` - Configuration management
- `keep_alive.py` - Web server for keep-alive functionality
- `Dockerfile` - Docker configuration for deployment