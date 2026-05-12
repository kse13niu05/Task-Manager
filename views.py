"""
Консольный интерфейс пользователя
"""

from models import PasswordCategory
from utils import PasswordGenerator

class ConsoleView:
    """Консольный интерфейс"""
    
    @staticmethod
    def clear_screen():
        """Очистка экрана"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def display_header():
        """Отображение заголовка"""
        print("\n" + "=" * 60)
        print("         🔐 PASSWORD MANAGER 🔐")
        print("=" * 60)
    
    @staticmethod
    def display_menu():
        """Отображение главного меню"""
        print("\n" + "-" * 60)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 60)
        print("1. 📝 Добавить пароль")
        print("2. 📋 Просмотреть все пароли")
        print("3. 🔍 Поиск паролей")
        print("4. ✏️ Редактировать пароль")
        print("5. 🗑️ Удалить пароль")
        print("6. 🔧 Генератор паролей")
        print("7. 📊 Статистика")
        print("8. ↩️ Отменить последнее действие")
        print("9. 💾 Сохранить и выйти")
        print("-" * 60)
    
    @staticmethod
    def display_search_menu():
        """Меню поиска"""
        print("\n--- ПОИСК ПАРОЛЕЙ ---")
        print("1. По названию сервиса")
        print("2. По имени пользователя")
        print("3. По категории")
        print("4. Назад")
    
    @staticmethod
    def display_categories():
        """Отображение категорий"""
        print("\nДоступные категории:")
        for key, value in PasswordCategory.CATEGORIES.items():
            print(f"  {key} - {value}")
    
    @staticmethod
    def display_records(records, title="СПИСОК ПАРОЛЕЙ"):
        """Отображение списка записей"""
        if not records:
            print("\n❌ Записи не найдены")
            return
        
        print(f"\n{'='*60}")
        print(f"{title}: {len(records)} записей")
        print(f"{'='*60}")
        
        for i, record in enumerate(records, 1):
            print(f"\n{i}. ID: {record.get_id()}")
            print(f"   Сервис: {record.get_service()}")
            print(f"   Пользователь: {record.get_username()}")
            print(f"   Пароль: {record.get_masked_password()}")
            print(f"   Категория: {record.get_category_display()}")
            print(f"   Заметки: {record.get_notes()[:50]}{'...' if len(record.get_notes()) > 50 else ''}")
            print(f"   Создан: {record.get_created_at()}")
            print(f"   Изменен: {record.get_updated_at()}")
            
            # Оценка сложности пароля
            strength_score = PasswordGenerator.calculate_strength(record.get_password())
            strength_label = PasswordGenerator.get_strength_label(strength_score)
            print(f"   Сложность пароля: {strength_label} ({strength_score}/100)")
        
        print(f"\n{'-'*60}")
    
    @staticmethod
    def display_record_detail(record):
        """Отображение деталей одной записи"""
        print("\n" + "=" * 60)
        print("ДЕТАЛИ ЗАПИСИ")
        print("=" * 60)
        print(f"ID: {record.get_id()}")
        print(f"Сервис: {record.get_service()}")
        print(f"Пользователь: {record.get_username()}")
        print(f"Пароль: {record.get_password()}")  # Полный пароль
        print(f"Категория: {record.get_category_display()}")
        print(f"Заметки: {record.get_notes()}")
        print(f"Создан: {record.get_created_at()}")
        print(f"Изменен: {record.get_updated_at()}")
        
        strength = PasswordGenerator.calculate_strength(record.get_password())
        print(f"Сложность пароля: {PasswordGenerator.get_strength_label(strength)} ({strength}/100)")
        print("=" * 60)
    
    @staticmethod
    def display_statistics(stats):
        """Отображение статистики"""
        print("\n" + "=" * 60)
        print("СТАТИСТИКА ПАРОЛЕЙ")
        print("=" * 60)
        print(f"Всего записей: {stats['total']}")
        print(f"Слабых паролей: {stats['weak_passwords']}")
        print("\nПо категориям:")
        for category, count in stats['by_category'].items():
            display_name = PasswordCategory.get_display_name(category)
            print(f"  {display_name}: {count}")
        print("=" * 60)
    
    @staticmethod
    def display_password_generator_menu():
        """Меню генератора паролей"""
        print("\n" + "=" * 60)
        print("ГЕНЕРАТОР ПАРОЛЕЙ")
        print("=" * 60)
    
    @staticmethod
    def get_generator_settings():
        """Получение настроек генерации"""
        print("\nНастройки генерации пароля:")
        
        try:
            length_input = input("Длина пароля (по умолчанию 12, min 4, max 128): ").strip()
            length = int(length_input) if length_input else 12
            if length < 4:
                print("❌ Длина не может быть меньше 4, установлено 4")
                length = 4
            elif length > 128:
                print("❌ Длина не может быть больше 128, установлено 128")
                length = 128
            
            use_uppercase = input("Использовать заглавные буквы? (y/n, по умолчанию y): ").strip().lower() != 'n'
            use_lowercase = input("Использовать строчные буквы? (y/n, по умолчанию y): ").strip().lower() != 'n'
            use_digits = input("Использовать цифры? (y/n, по умолчанию y): ").strip().lower() != 'n'
            use_special = input("Использовать спецсимволы? (y/n, по умолчанию y): ").strip().lower() != 'n'
            
            return {
                'length': length,
                'use_uppercase': use_uppercase,
                'use_lowercase': use_lowercase,
                'use_digits': use_digits,
                'use_special': use_special
            }
        except ValueError:
            print("❌ Неверный ввод, используются настройки по умолчанию")
            return {'length': 12, 'use_uppercase': True, 'use_lowercase': True, 
                    'use_digits': True, 'use_special': True}
    
    @staticmethod
    def get_string_input(prompt, required=True, max_length=100, allow_empty=False):
        """Получение строкового ввода с валидацией"""
        while True:
            value = input(prompt).strip()
            
            if not value and not required:
                return ""
            
            if not value and required:
                print("❌ Поле не может быть пустым")
                continue
            
            if len(value) > max_length:
                print(f"❌ Максимальная длина {max_length} символов")
                continue
            
            return value
    
    @staticmethod
    def get_password_input(prompt="Пароль: "):
        """Получение пароля с проверкой"""
        while True:
            password = input(prompt).strip()
            
            if len(password) < 4:
                print("❌ Пароль должен содержать минимум 4 символа")
                continue
            
            if len(password) > 128:
                print("❌ Пароль не должен превышать 128 символов")
                continue
            
            return password
    
    @staticmethod
    def get_choice(prompt, min_choice, max_choice):
        """Получение выбора пользователя"""
        while True:
            try:
                choice = input(prompt).strip()
                if not choice:
                    print(f"❌ Пожалуйста, введите число от {min_choice} до {max_choice}")
                    continue
                
                choice_int = int(choice)
                if min_choice <= choice_int <= max_choice:
                    return choice_int
                else:
                    print(f"❌ Пожалуйста, введите число от {min_choice} до {max_choice}")
            except ValueError:
                print("❌ Пожалуйста, введите корректное число")
    
    @staticmethod
    def get_confirm(prompt="Вы уверены? (y/n): "):
        """Получение подтверждения"""
        confirm = input(prompt).strip().lower()
        return confirm == 'y' or confirm == 'yes'
    
    @staticmethod
    def display_message(message, is_error=False, is_success=False):
        """Отображение сообщения"""
        if is_error:
            print(f"\n❌ {message}")
        elif is_success:
            print(f"\n✅ {message}")
        else:
            print(f"\nℹ️ {message}")
    
    @staticmethod
    def display_generated_password(password, strength_score, strength_label):
        """Отображение сгенерированного пароля"""
        print("\n" + "=" * 60)
        print("СГЕНЕРИРОВАН ПАРОЛЬ")
        print("=" * 60)
        print(f"Пароль: {password}")
        print(f"Длина: {len(password)} символов")
        print(f"Сложность: {strength_label} ({strength_score}/100)")
        print("=" * 60)
    
    @staticmethod
    def display_update_menu():
        """Меню обновления записи"""
        print("\n--- РЕДАКТИРОВАНИЕ ЗАПИСИ ---")
        print("Оставьте поле пустым, чтобы не менять")
    
    @staticmethod
    def wait_for_enter():
        """Ожидание нажатия Enter"""
        input("\nНажмите Enter для продолжения...")
