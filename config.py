import os

class Config:
    """Configuration settings for the Discord Task Bot"""
    
    # Discord settings
    BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
    
    # Reminder settings
    REMINDER_HOUR = int(os.getenv('REMINDER_HOUR', '9'))  # 9 AM by default
    REMINDER_MINUTE = int(os.getenv('REMINDER_MINUTE', '0'))  # 0 minutes by default
    
    # Default reminder channel ID (can be overridden with !setchannel command)
    REMINDER_CHANNEL_ID = int(os.getenv('REMINDER_CHANNEL_ID', '0'))
    
    # Task cleanup settings
    OVERDUE_CLEANUP_DAYS = int(os.getenv('OVERDUE_CLEANUP_DAYS', '30'))  # Remove tasks overdue by 30+ days
    
    # Bot settings
    COMMAND_PREFIX = '!'
    
    @classmethod
    def validate_config(cls):
        """Validate configuration settings"""
        if not cls.BOT_TOKEN:
            raise ValueError("DISCORD_BOT_TOKEN environment variable is required")
        
        if cls.REMINDER_HOUR < 0 or cls.REMINDER_HOUR > 23:
            raise ValueError("REMINDER_HOUR must be between 0 and 23")
        
        if cls.REMINDER_MINUTE < 0 or cls.REMINDER_MINUTE > 59:
            raise ValueError("REMINDER_MINUTE must be between 0 and 59")
        
        return True
