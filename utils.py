"""
Утилиты: очередь истории, JSON обработчик
"""

import json
import os
from collections import deque

class TaskHistoryQueue:
    """Очередь для хранения истории сгенерированных задач"""
    
    def __init__(self, max_size=100):
        self.__queue = deque(maxlen=max_size)
    
    def add(self, task):
        """Добавить задачу в историю"""
        self.__queue.append(task)
    
    def get_all(self):
        """Получить все задачи в истории"""
        return list(self.__queue)
    
    def get_last(self, count=1):
        """Получить последние N задач"""
        tasks = list(self.__queue)
        return tasks[-count:] if tasks else []
    
    def clear(self):
        """Очистить историю"""
        self.__queue.clear()
    
    def size(self):
        return len(self.__queue)
    
    def is_empty(self):
        return len(self.__queue) == 0
    
    def get_by_type(self, task_type):
        """Фильтрация по типу"""
        return [t for t in self.__queue if t.get_task_type() == task_type]
    
    def get_by_difficulty(self, difficulty):
        """Фильтрация по сложности"""
        if isinstance(difficulty, str):
            from models import Difficulty
            difficulty = Difficulty.from_string(difficulty)
        return [t for t in self.__queue if t.get_difficulty() == difficulty]


class JSONHandler:
    """Обработчик JSON файлов"""
    
    def __init__(self, filename="task_history.json"):
        self.__filename = filename
    
    def save_history(self, tasks):
        """Сохранить историю задач в файл"""
        try:
            data = [task.to_dict() for task in tasks]
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Ошибка сохранения: {e}")
    
    def load_history(self):
        """Загрузить историю задач из файла"""
        if not os.path.exists(self.__filename):
            return []
        
        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            from models import Task
            tasks = []
            for item in data:
                try:
                    task = Task.from_dict(item)
                    tasks.append(task)
                except Exception as e:
                    print(f"Ошибка загрузки задачи: {e}")
            return tasks
        except json.JSONDecodeError as e:
            raise Exception(f"Ошибка чтения JSON файла: {e}")
        except Exception as e:
            raise Exception(f"Ошибка загрузки: {e}")
