"""
Модели данных приложения Random Task Generator
Содержит абстрактный класс Task и конкретные типы задач
"""

from abc import ABC, abstractmethod
from enum import Enum
import uuid
from datetime import datetime

class Difficulty(Enum):
    """Уровни сложности задач"""
    EASY = "Легкая"
    MEDIUM = "Средняя"
    HARD = "Сложная"
    
    @classmethod
    def get_all(cls):
        return [cls.EASY, cls.MEDIUM, cls.HARD]
    
    @classmethod
    def from_string(cls, value):
        for difficulty in cls:
            if difficulty.value.lower() == value.lower():
                return difficulty
        raise ValueError(f"Неверный уровень сложности: {value}")


class TaskType(Enum):
    """Типы задач"""
    WORK = "Работа"
    SPORT = "Спорт"
    STUDY = "Учеба"
    HOBBY = "Хобби"
    HEALTH = "Здоровье"
    SOCIAL = "Социальное"
    
    @classmethod
    def get_all(cls):
        return list(cls)
    
    @classmethod
    def get_names(cls):
        return [t.value for t in cls]
    
    @classmethod
    def from_string(cls, value):
        for task_type in cls:
            if task_type.value.lower() == value.lower():
                return task_type
        raise ValueError(f"Неверный тип задачи: {value}")


class Task(ABC):
    """Абстрактный базовый класс для всех задач"""
    
    def __init__(self, description, difficulty, task_type, task_id=None, created_at=None):
        self.__task_id = task_id if task_id else str(uuid.uuid4())[:8]
        self.__description = description
        self.__difficulty = difficulty
        self.__task_type = task_type
        self.__created_at = created_at if created_at else datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.__completed = False
    
    # Геттеры
    def get_id(self):
        return self.__task_id
    
    def get_description(self):
        return self.__description
    
    def get_difficulty(self):
        return self.__difficulty
    
    def get_task_type(self):
        return self.__task_type
    
    def get_created_at(self):
        return self.__created_at
    
    def is_completed(self):
        return self.__completed
    
    # Сеттеры с валидацией
    def set_description(self, description):
        if not description or not description.strip():
            raise ValueError("Описание задачи не может быть пустым")
        if len(description) > 200:
            raise ValueError("Описание не может превышать 200 символов")
        self.__description = description.strip()
    
    def set_difficulty(self, difficulty):
        if isinstance(difficulty, str):
            difficulty = Difficulty.from_string(difficulty)
        self.__difficulty = difficulty
    
    def complete(self):
        self.__completed = True
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            "task_id": self.__task_id,
            "description": self.__description,
            "difficulty": self.__difficulty.value,
            "task_type": self.__task_type.value,
            "created_at": self.__created_at,
            "completed": self.__completed
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание задачи из словаря"""
        task_type = TaskType.from_string(data["task_type"])
        difficulty = Difficulty.from_string(data["difficulty"])
        
        # Создаем задачу через соответствующую фабрику
        from factories import TaskFactory
        task = TaskFactory.create_task(
            task_type=task_type,
            description=data["description"],
            difficulty=difficulty
        )
        # Устанавливаем сохраненные значения
        task._Task__task_id = data["task_id"]
        task._Task__created_at = data["created_at"]
        task._Task__completed = data["completed"]
        
        return task
    
    @abstractmethod
    def get_estimated_time(self):
        """Оценочное время выполнения задачи (в минутах)"""
        pass
    
    @abstractmethod
    def get_icon(self):
        """Иконка для типа задачи"""
        pass
    
    def __str__(self):
        status = "✅" if self.__completed else "⏳"
        return f"{status} [{self.__task_id}] {self.__description} | {self.__difficulty.value} | {self.__task_type.value}"


class WorkTask(Task):
    """Задача рабочего типа"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 30
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 60
        else:
            return 120
    
    def get_icon(self):
        return "💼"


class SportTask(Task):
    """Задача спортивного типа"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 20
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 45
        else:
            return 90
    
    def get_icon(self):
        return "🏃"


class StudyTask(Task):
    """Задача учебного типа"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 25
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 50
        else:
            return 100
    
    def get_icon(self):
        return "📚"


class HobbyTask(Task):
    """Задача для хобби"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 15
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 40
        else:
            return 80
    
    def get_icon(self):
        return "🎨"


class HealthTask(Task):
    """Задача для здоровья"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 10
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 30
        else:
            return 60
    
    def get_icon(self):
        return "🏥"


class SocialTask(Task):
    """Социальная задача"""
    
    def get_estimated_time(self):
        if self.get_difficulty() == Difficulty.EASY:
            return 20
        elif self.get_difficulty() == Difficulty.MEDIUM:
            return 40
        else:
            return 80
    
    def get_icon(self):
        return "👥"
