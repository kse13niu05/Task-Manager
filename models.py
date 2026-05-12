"""
Модели данных приложения
Содержит классы Task и TaskStatus
"""

from enum import Enum
import uuid
from datetime import datetime

class TaskStatus(Enum):
    """Статусы задач"""
    TO_DO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    
    @classmethod
    def get_russian(cls, status):
        """Возвращает русское название статуса"""
        russian = {
            "To Do": "Нужно сделать",
            "In Progress": "В процессе",
            "Done": "Готово"
        }
        if isinstance(status, TaskStatus):
            return russian[status.value]
        return russian.get(status, status)
    
    @classmethod
    def from_string(cls, status_str):
        """Преобразует строку в статус"""
        # Проверка английских названий
        for status in cls:
            if status.value.lower() == status_str.lower():
                return status
        
        # Проверка русских названий
        russian_map = {
            "нужно сделать": cls.TO_DO,
            "в процессе": cls.IN_PROGRESS,
            "готово": cls.DONE
        }
        if status_str.lower() in russian_map:
            return russian_map[status_str.lower()]
        
        raise ValueError(f"Неверный статус: {status_str}")


class Task:
    """Класс задачи"""
    
    def __init__(self, title, description, priority, status=None, task_id=None, created_at=None):
        self.__task_id = task_id if task_id else str(uuid.uuid4())[:8]
        self.__title = title
        self.__description = description
        self.__priority = priority
        self.__status = status if status else TaskStatus.TO_DO
        self.__created_at = created_at if created_at else datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Геттеры
    def get_id(self):
        return self.__task_id
    
    def get_title(self):
        return self.__title
    
    def get_description(self):
        return self.__description
    
    def get_priority(self):
        return self.__priority
    
    def get_status(self):
        return self.__status
    
    def get_created_at(self):
        return self.__created_at
    
    # Сеттеры с валидацией
    def set_title(self, title):
        if not title or not title.strip():
            raise ValueError("Название не может быть пустым")
        self.__title = title.strip()
    
    def set_description(self, description):
        self.__description = description.strip() if description else ""
    
    def set_priority(self, priority):
        valid_priorities = ["Низкий", "Средний", "Высокий"]
        # Поддержка английских названий
        priority_map = {
            "Low": "Низкий", "Medium": "Средний", "High": "Высокий",
            "Низкий": "Низкий", "Средний": "Средний", "Высокий": "Высокий"
        }
        priority = priority_map.get(priority, priority)
        if priority not in valid_priorities:
            raise ValueError(f"Приоритет должен быть: {', '.join(valid_priorities)}")
        self.__priority = priority
    
    def set_status(self, status):
        if isinstance(status, str):
            status = TaskStatus.from_string(status)
        self.__status = status
    
    def get_priority_value(self):
        """Числовое значение приоритета для сортировки"""
        values = {"Низкий": 1, "Средний": 2, "Высокий": 3}
        return values.get(self.__priority, 1)
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            "task_id": self.__task_id,
            "title": self.__title,
            "description": self.__description,
            "priority": self.__priority,
            "status": self.__status.value,
            "created_at": self.__created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание задачи из словаря"""
        status = TaskStatus.from_string(data["status"])
        return cls(
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            status=status,
            task_id=data["task_id"],
            created_at=data["created_at"]
        )
    
    def __str__(self):
        return f"[{self.__task_id}] {self.__title} | Приоритет: {self.__priority}"
