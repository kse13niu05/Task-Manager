"""
Утилиты: очередь, стек и работа с JSON
"""

from collections import deque
import json
import os

class PriorityTaskQueue:
    """Очередь задач с приоритетом"""

    def __init__(self):
        self.__high = deque()   # Высокий приоритет
        self.__medium = deque() # Средний приоритет
        self.__low = deque()    # Низкий приоритет

    def enqueue(self, task):
        """Добавить задачу в очередь"""
        priority = task.get_priority()
        if priority == "Высокий":
            self.__high.append(task)
        elif priority == "Средний":
            self.__medium.append(task)
        else:
            self.__low.append(task)

    def dequeue(self):
        """Извлечь задачу с наивысшим приоритетом"""
        if self.__high:
            return self.__high.popleft()
        elif self.__medium:
            return self.__medium.popleft()
        elif self.__low:
            return self.__low.popleft()
        return None

    def get_all(self):
        """Получить все задачи в порядке приоритета"""
        tasks = []
        tasks.extend(self.__high)
        tasks.extend(self.__medium)
        tasks.extend(self.__low)
        return tasks

    def is_empty(self):
        return len(self.__high) == 0 and len(self.__medium) == 0 and len(self.__low) == 0

    def size(self):
        return len(self.__high) + len(self.__medium) + len(self.__low)


class UndoStack:
    """Стек для отмены действий"""

    def __init__(self, max_size=50):
        self.__stack = []
        self.__max_size = max_size

    def push(self, action):
        """Добавить действие в стек"""
        self.__stack.append(action)
        if len(self.__stack) > self.__max_size:
            self.__stack.pop(0)

    def pop(self):
        """Извлечь последнее действие"""
        if self.__stack:
            return self.__stack.pop()
        return None

    def is_empty(self):
        return len(self.__stack) == 0

    def clear(self):
        self.__stack.clear()


class JSONHandler:
    """Обработчик JSON файлов"""

    def __init__(self, filename="tasks.json"):
        self.__filename = filename

    def save(self, tasks):
        """Сохранить задачи в файл"""
        try:
            data = [task.to_dict() for task in tasks]
            with open(self.__filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            raise Exception(f"Ошибка сохранения: {e}")

    def load(self):
        """Загрузить задачи из файла"""
        if not os.path.exists(self.__filename):
            return []

        try:
            with open(self.__filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            tasks = []
            for item in data:
                try:
                    from models import Task
                    tasks.append(Task.from_dict(item))
                except Exception as e:
                    print(f"Ошибка загрузки задачи: {e}")
            return tasks
        except Exception as e:
            raise Exception(f"Ошибка загрузки: {e}")
