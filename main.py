import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from task_manager import TaskManager
from reminder_scheduler import ReminderScheduler
from config import Config
from keep_alive import keep_alive

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)
task_manager = TaskManager()
reminder_scheduler = None

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    print(f'{bot.user} has connected to Discord!')
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    
    # Start the reminder scheduler
    global reminder_scheduler
    reminder_scheduler = ReminderScheduler(bot, task_manager)
    asyncio.create_task(reminder_scheduler.start_daily_reminders())

@bot.tree.command(name="addtask", description="Add a new task with deadline")
@app_commands.describe(
    task_name="The name/description of the task",
    deadline="The deadline date in YYYY-MM-DD format (e.g., 2025-07-30)"
)
async def add_task_slash(interaction: discord.Interaction, task_name: str, deadline: str):
    """Add a new task with deadline using slash command"""
    try:
        if not task_name.strip():
            await interaction.response.send_message("❌ Task name cannot be empty.", ephemeral=True)
            return
        
        success, message = task_manager.add_task(
            task_name.strip(), 
            deadline.strip(), 
            interaction.user.id, 
            interaction.user.display_name,
            interaction.channel_id
        )
        
        if success:
            await interaction.response.send_message(f"✅ {message}")
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error adding task: {str(e)}", ephemeral=True)

# Keep the old prefix command for backwards compatibility
@bot.command(name='addtask')
async def add_task(ctx, *, task_info):
    """
    Add a new task with deadline
    Usage: !addtask Task description | YYYY-MM-DD
    """
    try:
        if '|' not in task_info:
            await ctx.send("❌ Invalid format. Use: `!addtask Task description | YYYY-MM-DD` or use the slash command `/addtask`")
            return
        
        task_description, deadline_str = task_info.split('|', 1)
        task_description = task_description.strip()
        deadline_str = deadline_str.strip()
        
        if not task_description:
            await ctx.send("❌ Task description cannot be empty.")
            return
        
        success, message = task_manager.add_task(
            task_description, 
            deadline_str, 
            ctx.author.id, 
            ctx.author.display_name,
            ctx.channel.id
        )
        
        if success:
            await ctx.send(f"✅ {message}")
        else:
            await ctx.send(f"❌ {message}")
            
    except Exception as e:
        await ctx.send(f"❌ Error adding task: {str(e)}")

@bot.tree.command(name="listtasks", description="List all active tasks")
async def list_tasks_slash(interaction: discord.Interaction):
    """List all active tasks using slash command"""
    try:
        tasks = task_manager.get_all_tasks()
        
        if not tasks:
            await interaction.response.send_message("📝 No active tasks found.", ephemeral=True)
            return
        
        embed = discord.Embed(title="📋 Active Tasks", color=0x3498db)
        
        for task_id, task in tasks.items():
            creator = task['creator_name']
            description = task['description']
            deadline = task['deadline'].strftime('%Y-%m-%d')
            days_left = (task['deadline'] - task_manager.get_current_date()).days
            
            if days_left < 0:
                status = f"⚠️ Overdue by {abs(days_left)} days"
            elif days_left == 0:
                status = "🔥 Due today!"
            elif days_left <= 3:
                status = f"⏰ {days_left} days left"
            else:
                status = f"📅 {days_left} days left"
            
            embed.add_field(
                name=f"Task #{task_id}: {description}",
                value=f"Created by: {creator}\nDeadline: {deadline}\nStatus: {status}",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error listing tasks: {str(e)}", ephemeral=True)

@bot.command(name='listtasks')
async def list_tasks(ctx):
    """List all active tasks"""
    try:
        tasks = task_manager.get_all_tasks()
        
        if not tasks:
            await ctx.send("📝 No active tasks found.")
            return
        
        embed = discord.Embed(title="📋 Active Tasks", color=0x3498db)
        
        for task_id, task in tasks.items():
            creator = task['creator_name']
            description = task['description']
            deadline = task['deadline'].strftime('%Y-%m-%d')
            days_left = (task['deadline'] - task_manager.get_current_date()).days
            
            if days_left < 0:
                status = f"⚠️ Overdue by {abs(days_left)} days"
            elif days_left == 0:
                status = "🔥 Due today!"
            elif days_left <= 3:
                status = f"⏰ {days_left} days left"
            else:
                status = f"📅 {days_left} days left"
            
            embed.add_field(
                name=f"Task #{task_id}: {description}",
                value=f"Created by: {creator}\nDeadline: {deadline}\nStatus: {status}",
                inline=False
            )
        
        await ctx.send(embed=embed)
        
    except Exception as e:
        await ctx.send(f"❌ Error listing tasks: {str(e)}")

@bot.tree.command(name="complete", description="Mark a task as completed")
@app_commands.describe(task_id="The ID number of the task to mark as complete")
async def complete_task_slash(interaction: discord.Interaction, task_id: int):
    """Mark a task as completed using slash command"""
    try:
        success, message = task_manager.complete_task(task_id, interaction.user.id)
        
        if success:
            await interaction.response.send_message(f"✅ {message}")
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error completing task: {str(e)}", ephemeral=True)

@bot.command(name='complete')
async def complete_task(ctx, task_id: int):
    """
    Mark a task as completed
    Usage: !complete <task_id>
    """
    try:
        success, message = task_manager.complete_task(task_id, ctx.author.id)
        
        if success:
            await ctx.send(f"✅ {message}")
        else:
            await ctx.send(f"❌ {message}")
            
    except ValueError:
        await ctx.send("❌ Invalid task ID. Please provide a valid number.")
    except Exception as e:
        await ctx.send(f"❌ Error completing task: {str(e)}")

@bot.tree.command(name="setchannel", description="Set the current channel as the reminder channel")
async def set_reminder_channel_slash(interaction: discord.Interaction):
    """Set the current channel as the reminder channel using slash command"""
    try:
        Config.REMINDER_CHANNEL_ID = interaction.channel_id
        await interaction.response.send_message(f"✅ Reminder channel set to <#{interaction.channel_id}>")
    except Exception as e:
        await interaction.response.send_message(f"❌ Error setting reminder channel: {str(e)}", ephemeral=True)

@bot.command(name='setchannel')
async def set_reminder_channel(ctx):
    """Set the current channel as the reminder channel"""
    try:
        Config.REMINDER_CHANNEL_ID = ctx.channel.id
        await ctx.send(f"✅ Reminder channel set to {ctx.channel.mention}")
    except Exception as e:
        await ctx.send(f"❌ Error setting reminder channel: {str(e)}")

@bot.tree.command(name="testping", description="Create a test task due today to test ping functionality")
async def test_ping_slash(interaction: discord.Interaction):
    """Create a test task due today to test the ping system"""
    from datetime import date
    try:
        today = date.today().strftime('%Y-%m-%d')
        
        success, message = task_manager.add_task(
            "Test ping task", 
            today, 
            interaction.user.id, 
            interaction.user.display_name,
            interaction.channel_id
        )
        
        if success:
            await interaction.response.send_message(
                f"✅ {message}\n\n"
                f"🔔 **Test Setup Complete!**\n"
                f"• This task is due today and will trigger a ping\n"
                f"• Use `/testreminder` to manually trigger a reminder now\n"
                f"• Or wait until 9:00 AM for the automatic daily reminder"
            )
        else:
            await interaction.response.send_message(f"❌ {message}", ephemeral=True)
            
    except Exception as e:
        await interaction.response.send_message(f"❌ Error creating test task: {str(e)}", ephemeral=True)

@bot.tree.command(name="testreminder", description="Manually send a reminder now (for testing)")
async def test_reminder_slash(interaction: discord.Interaction):
    """Manually trigger a reminder to test the ping system"""
    try:
        # Check if this channel is set as reminder channel
        if Config.REMINDER_CHANNEL_ID == 0:
            await interaction.response.send_message(
                "❌ No reminder channel set! Use `/setchannel` first.", 
                ephemeral=True
            )
            return
        
        if interaction.channel_id != Config.REMINDER_CHANNEL_ID:
            await interaction.response.send_message(
                f"❌ Reminders are sent to <#{Config.REMINDER_CHANNEL_ID}>. Use `/setchannel` here to change it.", 
                ephemeral=True
            )
            return
        
        await interaction.response.send_message("🔔 Sending test reminder now...")
        
        # Manually trigger the reminder
        await reminder_scheduler.send_daily_reminders()
        
    except Exception as e:
        await interaction.response.send_message(f"❌ Error sending test reminder: {str(e)}", ephemeral=True)

@bot.tree.command(name="help", description="Show help for task management commands")
async def help_tasks_slash(interaction: discord.Interaction):
    """Show help for task management commands using slash command"""
    embed = discord.Embed(title="🤖 Task Bot Help", color=0x2ecc71)
    embed.add_field(
        name="Slash Commands (Recommended)",
        value="📌 **Main Commands:**\n"
              "• `/addtask` - Add a new task (with separate fields for name and deadline)\n"
              "• `/listtasks` - List all active tasks\n"
              "• `/complete` - Mark a task as completed\n"
              "• `/setchannel` - Set current channel for daily reminders\n"
              "• `/help` - Show this help message",
        inline=False
    )
    embed.add_field(
        name="Testing Commands",
        value="🧪 **Test Functions:**\n"
              "• `/testping` - Create a test task due today\n"
              "• `/testreminder` - Manually send reminder now",
        inline=False
    )
    embed.add_field(
        name="Legacy Commands (Still Available)",
        value="📝 **Alternative Format:**\n"
              "• `!addtask Task description | 2025-07-30`\n"
              "• `!listtasks`\n"
              "• `!complete 1`\n"
              "• `!setchannel`",
        inline=False
    )
    embed.add_field(
        name="🔔 Daily Reminders",
        value="The bot automatically sends daily reminders at 9:00 AM in your set channel, pinging users with upcoming or overdue tasks.",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.command(name='help_tasks')
async def help_tasks(ctx):
    """Show help for task management commands"""
    embed = discord.Embed(title="🤖 Task Bot Help", color=0x2ecc71)
    embed.add_field(
        name="Slash Commands (Recommended)",
        value="📌 **Main Commands:**\n"
              "• `/addtask` - Add a new task (with separate fields for name and deadline)\n"
              "• `/listtasks` - List all active tasks\n"
              "• `/complete` - Mark a task as completed\n"
              "• `/setchannel` - Set current channel for daily reminders\n"
              "• `/help` - Show this help message",
        inline=False
    )
    embed.add_field(
        name="Legacy Commands",
        value="📝 **Alternative Format:**\n"
              "• `!addtask Task description | 2025-07-30`\n"
              "• `!listtasks`\n"
              "• `!complete 1`\n"
              "• `!setchannel`",
        inline=False
    )
    embed.add_field(
        name="🔔 Daily Reminders",
        value="The bot automatically sends daily reminders at 9:00 AM in your set channel, pinging users with upcoming or overdue tasks.",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required arguments. Use `!help_tasks` for command usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided. Use `!help_tasks` for command usage.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Command error: {error}")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN environment variable not found!")
        print("Please set your Discord bot token in the environment variables.")
        exit(1)
    
    # For Replit development - start keep-alive server
    keep_alive()
    
    # Give Flask server time to start
    import time
    time.sleep(2)
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord bot token!")
    except Exception as e:
        print(f"❌ Error running bot: {str(e)}")

def setup_and_run_bot():
    """Setup and run the Discord bot - called from app.py for Render deployment"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ DISCORD_BOT_TOKEN environment variable not found!")
        return
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        print("❌ Invalid Discord bot token!")
    except Exception as e:
        print(f"❌ Error running bot: {str(e)}")
