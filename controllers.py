"""
Контроллер и менеджер задач
"""

from models import Task, TaskStatus
from utils import PriorityTaskQueue, UndoStack

class TaskManager:
    """Менеджер задач - основная бизнес-логика"""

    def __init__(self):
        self.__tasks = {}
        self.__queue = PriorityTaskQueue()
        self.__undo = UndoStack()

    def add_task(self, title, description, priority):
        """Добавить задачу"""
        if not title or not title.strip():
            raise ValueError("Название не может быть пустым")

        task = Task(title, description, priority)
        self.__tasks[task.get_id()] = task
        self.__queue.enqueue(task)
        self.__undo.push(("add", task.get_id(), None))
        return task

    def delete_task(self, task_id):
        """Удалить задачу"""
        if task_id in self.__tasks:
            task = self.__tasks[task_id]
            del self.__tasks[task_id]
            self.__rebuild_queue()
            self.__undo.push(("delete", task_id, task.to_dict()))
            return True
        return False

    def update_task(self, task_id, **kwargs):
        """Обновить задачу"""
        if task_id in self.__tasks:
            task = self.__tasks[task_id]
            old_state = task.to_dict()

            if "title" in kwargs:
                task.set_title(kwargs["title"])
            if "description" in kwargs:
                task.set_description(kwargs["description"])
            if "priority" in kwargs:
                task.set_priority(kwargs["priority"])
            if "status" in kwargs:
                task.set_status(kwargs["status"])

            if "priority" in kwargs:
                self.__rebuild_queue()

            self.__undo.push(("update", task_id, old_state))
            return True
        return False

    def undo(self):
        """Отменить последнее действие"""
        action = self.__undo.pop()
        if not action:
            return "Нечего отменять"

        action_type, task_id, old_data = action

        if action_type == "add":
            if task_id in self.__tasks:
                del self.__tasks[task_id]
                self.__rebuild_queue()
                return f"Отменено: удалена задача {task_id}"

        elif action_type == "delete":
            if old_data:
                task = Task.from_dict(old_data)
                self.__tasks[task_id] = task
                self.__rebuild_queue()
                return f"Отменено: восстановлена задача {task_id}"

        elif action_type == "update":
            if task_id in self.__tasks:
                task = self.__tasks[task_id]
                task.set_title(old_data["title"])
                task.set_description(old_data["description"])
                task.set_priority(old_data["priority"])
                task.set_status(old_data["status"])
                self.__rebuild_queue()
                return f"Отменено: восстановлена задача {task_id}"

        return "Отмена выполнена"

    def __rebuild_queue(self):
        """Перестроить очередь"""
        self.__queue = PriorityTaskQueue()
        for task in self.__tasks.values():
            self.__queue.enqueue(task)

    def get_all_tasks(self):
        """Получить все задачи"""
        return list(self.__tasks.values())

    def get_task_by_id(self, task_id):
        """Получить задачу по ID"""
        return self.__tasks.get(task_id)

    def get_tasks_by_priority(self):
        """Получить задачи, отсортированные по приоритету"""
        return self.__queue.get_all()

    def filter_by_status(self, status):
        """Фильтр по статусу"""
        if isinstance(status, str):
            status = TaskStatus.from_string(status)
        return [t for t in self.__tasks.values() if t.get_status() == status]

    def filter_by_priority(self, priority):
        """Фильтр по приоритету"""
        return [t for t in self.__tasks.values() if t.get_priority() == priority]

    def search(self, query):
        """Поиск задач"""
        query_lower = query.lower()
        return [t for t in self.__tasks.values()
                if query_lower in t.get_title().lower()
                or query_lower in t.get_description().lower()]

    def clear(self):
        """Очистить все задачи"""
        self.__tasks.clear()
        self.__queue = PriorityTaskQueue()
        self.__undo.clear()

    def get_count(self):
        return len(self.__tasks)
