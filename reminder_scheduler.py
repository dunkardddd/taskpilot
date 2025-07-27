import asyncio
import discord
from datetime import datetime, time, date
from task_manager import TaskManager
from config import Config

class ReminderScheduler:
    """Handles daily reminder scheduling and sending"""
    
    def __init__(self, bot, task_manager: TaskManager):
        self.bot = bot
        self.task_manager = task_manager
        self.is_running = False
    
    async def start_daily_reminders(self):
        """Start the daily reminder loop"""
        self.is_running = True
        print("🔔 Daily reminder scheduler started")
        
        while self.is_running:
            try:
                # Calculate time until next reminder
                now = datetime.now()
                reminder_time = datetime.combine(now.date(), time(Config.REMINDER_HOUR, Config.REMINDER_MINUTE))
                
                # If reminder time has passed today, schedule for tomorrow
                if now >= reminder_time:
                    reminder_time = reminder_time.replace(day=reminder_time.day + 1)
                
                # Calculate sleep duration
                sleep_seconds = (reminder_time - now).total_seconds()
                
                print(f"⏰ Next reminder scheduled for: {reminder_time.strftime('%Y-%m-%d %H:%M')}")
                print(f"⏳ Sleeping for {sleep_seconds/3600:.1f} hours")
                
                # Sleep until reminder time
                await asyncio.sleep(sleep_seconds)
                
                # Send daily reminders
                await self.send_daily_reminders()
                
            except Exception as e:
                print(f"❌ Error in reminder scheduler: {str(e)}")
                # Sleep for 1 hour before retrying
                await asyncio.sleep(3600)
    
    async def send_daily_reminders(self):
        """Send daily reminder messages"""
        try:
            # Get tasks that need reminders
            reminder_tasks = self.task_manager.get_tasks_for_reminder()
            
            if not reminder_tasks:
                print("📝 No tasks requiring reminders today")
                return
            
            # Get reminder channel
            channel = self.bot.get_channel(Config.REMINDER_CHANNEL_ID)
            if not channel:
                print(f"❌ Reminder channel {Config.REMINDER_CHANNEL_ID} not found")
                return
            
            # Group tasks by urgency
            overdue_tasks = []
            due_today = []
            due_tomorrow = []
            
            today = date.today()
            
            for task_id, task in reminder_tasks.items():
                days_until_deadline = (task['deadline'] - today).days
                
                if days_until_deadline < 0:
                    overdue_tasks.append((task_id, task))
                elif days_until_deadline == 0:
                    due_today.append((task_id, task))
                elif days_until_deadline == 1:
                    due_tomorrow.append((task_id, task))
            
            # Send reminder message
            embed = discord.Embed(
                title="📅 Daily Task Reminders",
                description=f"Good morning! Here are your task reminders for {today.strftime('%A, %B %d, %Y')}",
                color=0xe74c3c if overdue_tasks else 0xf39c12 if due_today else 0x3498db
            )
            
            # Add overdue tasks
            if overdue_tasks:
                overdue_text = ""
                for task_id, task in overdue_tasks:
                    days_overdue = (today - task['deadline']).days
                    user_mention = f"<@{task['creator_id']}>"
                    overdue_text += f"🚨 **Task #{task_id}**: {task['description']}\n"
                    overdue_text += f"   👤 {user_mention} - Overdue by {days_overdue} days\n\n"
                
                embed.add_field(
                    name="🚨 OVERDUE TASKS",
                    value=overdue_text[:1024],  # Discord field limit
                    inline=False
                )
            
            # Add tasks due today
            if due_today:
                today_text = ""
                for task_id, task in due_today:
                    user_mention = f"<@{task['creator_id']}>"
                    today_text += f"🔥 **Task #{task_id}**: {task['description']}\n"
                    today_text += f"   👤 {user_mention} - Due TODAY!\n\n"
                
                embed.add_field(
                    name="🔥 DUE TODAY",
                    value=today_text[:1024],
                    inline=False
                )
            
            # Add tasks due tomorrow
            if due_tomorrow:
                tomorrow_text = ""
                for task_id, task in due_tomorrow:
                    user_mention = f"<@{task['creator_id']}>"
                    tomorrow_text += f"⏰ **Task #{task_id}**: {task['description']}\n"
                    tomorrow_text += f"   👤 {user_mention} - Due tomorrow\n\n"
                
                embed.add_field(
                    name="⏰ DUE TOMORROW",
                    value=tomorrow_text[:1024],
                    inline=False
                )
            
            # Add footer with helpful commands
            embed.set_footer(text="Use !listtasks to see all tasks • !complete <id> to mark as done")
            
            await channel.send(embed=embed)
            
            # Send individual pings for critical tasks (overdue or due today)
            critical_tasks = overdue_tasks + due_today
            if critical_tasks:
                ping_message = "🔔 **URGENT TASK REMINDERS** 🔔\n"
                for task_id, task in critical_tasks:
                    user_mention = f"<@{task['creator_id']}>"
                    status = "OVERDUE" if (today - task['deadline']).days > 0 else "DUE TODAY"
                    ping_message += f"{user_mention} - Task #{task_id}: {task['description']} ({status})\n"
                
                await channel.send(ping_message)
            
            print(f"✅ Daily reminders sent to {channel.name}")
            
        except Exception as e:
            print(f"❌ Error sending daily reminders: {str(e)}")
    
    def stop(self):
        """Stop the reminder scheduler"""
        self.is_running = False
        print("🛑 Daily reminder scheduler stopped")
