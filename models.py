"""
Модели данных приложения Password Manager
Содержит классы PasswordRecord и PasswordCategory
"""

import uuid
from datetime import datetime
import re

class PasswordCategory:
    """Категории паролей"""
    
    CATEGORIES = {
        "social": "Социальные сети",
        "email": "Электронная почта",
        "banking": "Банки и финансы",
        "work": "Рабочие",
        "entertainment": "Развлечения",
        "other": "Другое"
    }
    
    @classmethod
    def get_all(cls):
        """Получить все категории"""
        return list(cls.CATEGORIES.keys())
    
    @classmethod
    def get_display_name(cls, category):
        """Получить отображаемое имя категории"""
        return cls.CATEGORIES.get(category, category)
    
    @classmethod
    def is_valid(cls, category):
        """Проверить валидность категории"""
        return category in cls.CATEGORIES


class PasswordRecord:
    """Класс записи пароля"""
    
    def __init__(self, service, username, password, category="other", 
                 notes="", record_id=None, created_at=None, updated_at=None):
        self.__record_id = record_id if record_id else str(uuid.uuid4())[:8]
        self.__service = service
        self.__username = username
        self.__password = password
        self.__category = category
        self.__notes = notes
        self.__created_at = created_at if created_at else datetime.now().strftime("%d.%m.%Y %H:%M")
        self.__updated_at = updated_at if updated_at else datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Геттеры
    def get_id(self):
        return self.__record_id
    
    def get_service(self):
        return self.__service
    
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def get_category(self):
        return self.__category
    
    def get_notes(self):
        return self.__notes
    
    def get_created_at(self):
        return self.__created_at
    
    def get_updated_at(self):
        return self.__updated_at
    
    # Сеттеры с валидацией
    def set_service(self, service):
        if not service or not service.strip():
            raise ValueError("Название сервиса не может быть пустым")
        if len(service) > 100:
            raise ValueError("Название сервиса не может превышать 100 символов")
        self.__service = service.strip()
        self.__update_timestamp()
    
    def set_username(self, username):
        if not username or not username.strip():
            raise ValueError("Имя пользователя не может быть пустым")
        if len(username) > 100:
            raise ValueError("Имя пользователя не может превышать 100 символов")
        self.__username = username.strip()
        self.__update_timestamp()
    
    def set_password(self, password):
        if not password:
            raise ValueError("Пароль не может быть пустым")
        if len(password) < 4:
            raise ValueError("Пароль должен содержать минимум 4 символа")
        if len(password) > 128:
            raise ValueError("Пароль не может превышать 128 символов")
        self.__password = password
        self.__update_timestamp()
    
    def set_category(self, category):
        if not PasswordCategory.is_valid(category):
            valid = ", ".join(PasswordCategory.get_all())
            raise ValueError(f"Категория должна быть одной из: {valid}")
        self.__category = category
        self.__update_timestamp()
    
    def set_notes(self, notes):
        if notes and len(notes) > 500:
            raise ValueError("Заметки не могут превышать 500 символов")
        self.__notes = notes.strip() if notes else ""
        self.__update_timestamp()
    
    def __update_timestamp(self):
        """Обновить временную метку изменения"""
        self.__updated_at = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    def get_category_display(self):
        """Получить отображаемое имя категории"""
        return PasswordCategory.get_display_name(self.__category)
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            "record_id": self.__record_id,
            "service": self.__service,
            "username": self.__username,
            "password": self.__password,
            "category": self.__category,
            "notes": self.__notes,
            "created_at": self.__created_at,
            "updated_at": self.__updated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Создание записи из словаря"""
        return cls(
            service=data["service"],
            username=data["username"],
            password=data["password"],
            category=data["category"],
            notes=data.get("notes", ""),
            record_id=data["record_id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"]
        )
    
    def get_masked_password(self):
        """Получить маскированный пароль для отображения"""
        if len(self.__password) <= 8:
            return "*" * len(self.__password)
        return self.__password[:4] + "*" * (len(self.__password) - 8) + self.__password[-4:]
    
    def __str__(self):
        return f"[{self.__record_id}] {self.__service} | {self.__username} | {self.get_category_display()}"
