"""
Контроллер приложения Random Task Generator
"""

from models import TaskType, Difficulty
from factories import TaskGenerator
from utils import TaskHistoryQueue, JSONHandler

class TaskManagerController:
    """Контроллер для управления задачами"""
    
    def __init__(self):
        self.generator = TaskGenerator()
        self.history = TaskHistoryQueue()
        self.json_handler = JSONHandler()
    
    def generate_random_task(self, task_type=None, difficulty=None):
        """Сгенерировать случайную задачу"""
        try:
            task = self.generator.generate_random_task(task_type, difficulty)
            self.history.add(task)
            return task
        except Exception as e:
            raise Exception(f"Ошибка генерации задачи: {e}")
    
    def add_custom_task(self, task_type, description, difficulty):
        """Добавить пользовательскую задачу"""
        try:
            task = self.generator.generate_task_by_template(task_type, description, difficulty)
            self.history.add(task)
            return task
        except Exception as e:
            raise Exception(f"Ошибка добавления задачи: {e}")
    
    def get_all_tasks(self):
        """Получить все задачи из истории"""
        return self.history.get_all()
    
    def filter_by_type(self, task_type):
        """Фильтрация задач по типу"""
        if isinstance(task_type, str):
            task_type = TaskType.from_string(task_type)
        return self.history.get_by_type(task_type)
    
    def filter_by_difficulty(self, difficulty):
        """Фильтрация задач по сложности"""
        if isinstance(difficulty, str):
            difficulty = Difficulty.from_string(difficulty)
        return self.history.get_by_difficulty(difficulty)
    
    def get_statistics(self):
        """Получить статистику по задачам"""
        tasks = self.history.get_all()
        
        if not tasks:
            return {
                "total": 0,
                "by_type": {},
                "by_difficulty": {},
                "total_time": 0,
                "completed": 0
            }
        
        stats = {
            "total": len(tasks),
            "by_type": {},
            "by_difficulty": {},
            "total_time": 0,
            "completed": sum(1 for t in tasks if t.is_completed())
        }
        
        for task in tasks:
            # Статистика по типам
            type_name = task.get_task_type().value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            
            # Статистика по сложности
            diff_name = task.get_difficulty().value
            stats["by_difficulty"][diff_name] = stats["by_difficulty"].get(diff_name, 0) + 1
            
            # Общее время
            stats["total_time"] += task.get_estimated_time()
        
        return stats
    
    def mark_task_completed(self, task_id):
        """Отметить задачу как выполненную"""
        tasks = self.history.get_all()
        for task in tasks:
            if task.get_id() == task_id:
                task.complete()
                return True
        return False
    
    def clear_history(self):
        """Очистить историю"""
        self.history.clear()
    
    def save_history(self):
        """Сохранить историю в JSON"""
        tasks = self.history.get_all()
        self.json_handler.save_history(tasks)
    
    def load_history(self):
        """Загрузить историю из JSON"""
        tasks = self.json_handler.load_history()
        for task in tasks:
            self.history.add(task)
        return len(tasks)
