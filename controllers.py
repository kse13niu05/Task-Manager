"""
Контроллер и менеджер паролей
"""

from models import PasswordRecord, PasswordCategory
from utils import PasswordGenerator, UndoStack

class PasswordManager:
    """Менеджер паролей - основная бизнес-логика"""
    
    def __init__(self):
        self.__records = {}
        self.__undo_stack = UndoStack()
    
    def add_record(self, service, username, password, category="other", notes=""):
        """Добавить новую запись пароля"""
        record = PasswordRecord(service, username, password, category, notes)
        self.__records[record.get_id()] = record
        self.__undo_stack.push(("add", record.get_id(), None))
        return record
    
    def delete_record(self, record_id):
        """Удалить запись по ID"""
        if record_id in self.__records:
            deleted = self.__records[record_id]
            del self.__records[record_id]
            self.__undo_stack.push(("delete", record_id, deleted.to_dict()))
            return True
        return False
    
    def update_record(self, record_id, **kwargs):
        """Обновить запись"""
        if record_id in self.__records:
            record = self.__records[record_id]
            old_state = record.to_dict()
            
            if "service" in kwargs:
                record.set_service(kwargs["service"])
            if "username" in kwargs:
                record.set_username(kwargs["username"])
            if "password" in kwargs:
                record.set_password(kwargs["password"])
            if "category" in kwargs:
                record.set_category(kwargs["category"])
            if "notes" in kwargs:
                record.set_notes(kwargs["notes"])
            
            self.__undo_stack.push(("update", record_id, old_state))
            return True
        return False
    
    def undo(self):
        """Отменить последнее действие"""
        action = self.__undo_stack.pop()
        if not action:
            return "Нечего отменять"
        
        action_type, record_id, old_data = action
        
        if action_type == "add":
            if record_id in self.__records:
                del self.__records[record_id]
                return f"Отменено: удалена запись {record_id}"
        
        elif action_type == "delete":
            if old_data:
                restored = PasswordRecord.from_dict(old_data)
                self.__records[record_id] = restored
                return f"Отменено: восстановлена запись {record_id}"
        
        elif action_type == "update":
            if record_id in self.__records:
                record = self.__records[record_id]
                record.set_service(old_data["service"])
                record.set_username(old_data["username"])
                record.set_password(old_data["password"])
                record.set_category(old_data["category"])
                record.set_notes(old_data["notes"])
                return f"Отменено: восстановлена запись {record_id}"
        
        return "Отмена выполнена"
    
    def get_all_records(self):
        """Получить все записи"""
        return list(self.__records.values())
    
    def get_record_by_id(self, record_id):
        """Получить запись по ID"""
        return self.__records.get(record_id)
    
    def search_by_service(self, query):
        """Поиск по названию сервиса"""
        query_lower = query.lower()
        return [r for r in self.__records.values() 
                if query_lower in r.get_service().lower()]
    
    def search_by_username(self, query):
        """Поиск по имени пользователя"""
        query_lower = query.lower()
        return [r for r in self.__records.values() 
                if query_lower in r.get_username().lower()]
    
    def filter_by_category(self, category):
        """Фильтрация по категории"""
        return [r for r in self.__records.values() 
                if r.get_category() == category]
    
    def get_statistics(self):
        """Получить статистику по паролям"""
        stats = {
            "total": len(self.__records),
            "by_category": {},
            "weak_passwords": 0
        }
        
        for record in self.__records.values():
            category = record.get_category()
            stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
            
            # Оценка сложности пароля
            from utils import PasswordGenerator
            strength = PasswordGenerator.calculate_strength(record.get_password())
            if strength < 40:
                stats["weak_passwords"] += 1
        
        return stats
    
    def clear_all(self):
        """Очистить все записи"""
        self.__records.clear()
        self.__undo_stack.clear()
    
    def get_count(self):
        return len(self.__records)
