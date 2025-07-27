from datetime import datetime, date
from typing import Dict, Tuple, Optional

class TaskManager:
    """Manages task storage and operations"""
    
    def __init__(self):
        self.tasks: Dict[int, dict] = {}
        self.next_task_id = 1
    
    def add_task(self, description: str, deadline_str: str, user_id: int, user_name: str, channel_id: int) -> Tuple[bool, str]:
        """
        Add a new task with deadline
        Returns: (success, message)
        """
        try:
            # Parse deadline
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            
            # Check if deadline is in the past
            if deadline < date.today():
                return False, "Deadline cannot be in the past."
            
            # Create task
            task = {
                'id': self.next_task_id,
                'description': description,
                'deadline': deadline,
                'creator_id': user_id,
                'creator_name': user_name,
                'channel_id': channel_id,
                'created_at': datetime.now(),
                'completed': False
            }
            
            self.tasks[self.next_task_id] = task
            task_id = self.next_task_id
            self.next_task_id += 1
            
            return True, f"Task #{task_id} added successfully! Deadline: {deadline_str}"
            
        except ValueError:
            return False, "Invalid date format. Please use YYYY-MM-DD format."
        except Exception as e:
            return False, f"Error adding task: {str(e)}"
    
    def complete_task(self, task_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Mark a task as completed
        Returns: (success, message)
        """
        if task_id not in self.tasks:
            return False, f"Task #{task_id} not found."
        
        task = self.tasks[task_id]
        
        if task['creator_id'] != user_id:
            return False, f"Only the task creator can mark Task #{task_id} as completed."
        
        if task['completed']:
            return False, f"Task #{task_id} is already completed."
        
        # Remove completed task
        description = task['description']
        del self.tasks[task_id]
        
        return True, f"Task #{task_id} '{description}' marked as completed and removed!"
    
    def get_all_tasks(self) -> Dict[int, dict]:
        """Get all active tasks"""
        return {task_id: task for task_id, task in self.tasks.items() if not task['completed']}
    
    def get_tasks_for_reminder(self) -> Dict[int, dict]:
        """Get tasks that need reminders (due today or overdue)"""
        today = date.today()
        reminder_tasks = {}
        
        for task_id, task in self.tasks.items():
            if task['completed']:
                continue
                
            days_until_deadline = (task['deadline'] - today).days
            
            # Include tasks that are due today, due tomorrow, or overdue
            if days_until_deadline <= 1:
                reminder_tasks[task_id] = task
        
        return reminder_tasks
    
    def get_current_date(self) -> date:
        """Get current date (useful for testing)"""
        return date.today()
    
    def get_task_count(self) -> int:
        """Get count of active tasks"""
        return len([task for task in self.tasks.values() if not task['completed']])
    
    def cleanup_overdue_tasks(self, days_threshold: int = 30) -> int:
        """
        Remove tasks that are overdue by more than specified days
        Returns: number of tasks removed
        """
        today = date.today()
        tasks_to_remove = []
        
        for task_id, task in self.tasks.items():
            if task['completed']:
                continue
                
            days_overdue = (today - task['deadline']).days
            if days_overdue > days_threshold:
                tasks_to_remove.append(task_id)
        
        for task_id in tasks_to_remove:
            del self.tasks[task_id]
        
        return len(tasks_to_remove)
