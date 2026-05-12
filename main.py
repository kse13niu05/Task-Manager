#!/usr/bin/env python3
"""
Password Manager - Консольное приложение для управления паролями
Автор: Студент
Описание: Приложение для безопасного хранения и управления паролями
         с функцией генерации сложных паролей.
"""

from controllers import PasswordManager
from views import ConsoleView
from utils import PasswordGenerator, JSONHandler

class PasswordManagerController:
    """Контроллер приложения"""
    
    def __init__(self):
        self.manager = PasswordManager()
        self.view = ConsoleView()
        self.json_handler = JSONHandler()
        self.running = True
    
    def run(self):
        """Запуск приложения"""
        self.load_data()
        
        while self.running:
            self.view.display_header()
            self.view.display_menu()
            
            choice = self.view.get_choice("\nВаш выбор (1-9): ", 1, 9)
            
            actions = {
                1: self.add_password,
                2: self.view_all_passwords,
                3: self.search_passwords,
                4: self.edit_password,
                5: self.delete_password,
                6: self.generate_password,
                7: self.show_statistics,
                8: self.undo_action,
                9: self.exit_app
            }
            
            actions.get(choice, lambda: None)()
    
    def add_password(self):
        """Добавление нового пароля"""
        print("\n--- ДОБАВЛЕНИЕ НОВОГО ПАРОЛЯ ---")
        
        service = self.view.get_string_input("Название сервиса: ", required=True, max_length=100)
        username = self.view.get_string_input("Имя пользователя / Email: ", required=True, max_length=100)
        
        # Выбор способа ввода пароля
        print("\nСпособы ввода пароля:")
        print("1. Ввести пароль вручную")
        print("2. Сгенерировать пароль")
        password_choice = self.view.get_choice("Выберите способ (1-2): ", 1, 2)
        
        if password_choice == 2:
            settings = self.view.get_generator_settings()
            password = PasswordGenerator.generate(**settings)
            self.view.display_generated_password(
                password,
                PasswordGenerator.calculate_strength(password),
                PasswordGenerator.get_strength_label(PasswordGenerator.calculate_strength(password))
            )
            
            if not self.view.get_confirm("Использовать этот пароль? (y/n): "):
                password = self.view.get_password_input("Введите пароль вручную: ")
        else:
            password = self.view.get_password_input("Введите пароль: ")
        
        self.view.display_categories()
        category = self.view.get_string_input("Выберите категорию: ", required=True, max_length=20)
        
        # Проверка категории
        from models import PasswordCategory
        if not PasswordCategory.is_valid(category):
            print("❌ Неверная категория, выбрана 'other'")
            category = "other"
        
        notes = self.view.get_string_input("Заметки (необязательно): ", required=False, max_length=500)
        
        try:
            record = self.manager.add_record(service, username, password, category, notes)
            self.view.display_message(f"Пароль успешно добавлен! ID: {record.get_id()}", is_success=True)
            self.save_data()
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def view_all_passwords(self):
        """Просмотр всех паролей"""
        records = self.manager.get_all_records()
        
        if not records:
            self.view.display_message("Нет сохраненных паролей", is_error=True)
        else:
            self.view.display_records(records, "ВСЕ ПАРОЛИ")
            
            # Показать детали выбранной записи
            if self.view.get_confirm("\nПоказать полный пароль для записи? (y/n): "):
                record_id = self.view.get_string_input("Введите ID записи: ", required=True, max_length=8)
                record = self.manager.get_record_by_id(record_id)
                if record:
                    self.view.display_record_detail(record)
                else:
                    self.view.display_message(f"Запись с ID {record_id} не найдена", is_error=True)
        
        self.view.wait_for_enter()
    
    def search_passwords(self):
        """Поиск паролей"""
        while True:
            self.view.display_search_menu()
            choice = self.view.get_choice("Выберите действие (1-4): ", 1, 4)
            
            if choice == 1:
                query = self.view.get_string_input("Введите название сервиса: ", required=True)
                results = self.manager.search_by_service(query)
                self.view.display_records(results, f"РЕЗУЛЬТАТЫ ПОИСКА ПО СЕРВИСУ: {query}")
            
            elif choice == 2:
                query = self.view.get_string_input("Введите имя пользователя: ", required=True)
                results = self.manager.search_by_username(query)
                self.view.display_records(results, f"РЕЗУЛЬТАТЫ ПОИСКА ПО ПОЛЬЗОВАТЕЛЮ: {query}")
            
            elif choice == 3:
                self.view.display_categories()
                category = self.view.get_string_input("Выберите категорию: ", required=True)
                from models import PasswordCategory
                if PasswordCategory.is_valid(category):
                    results = self.manager.filter_by_category(category)
                    display_name = PasswordCategory.get_display_name(category)
                    self.view.display_records(results, f"ЗАПИСИ В КАТЕГОРИИ: {display_name}")
                else:
                    self.view.display_message("Неверная категория", is_error=True)
            
            else:
                break
            
            if results:
                if self.view.get_confirm("\nПоказать полный пароль для записи? (y/n): "):
                    record_id = self.view.get_string_input("Введите ID записи: ", required=True, max_length=8)
                    record = self.manager.get_record_by_id(record_id)
                    if record:
                        self.view.display_record_detail(record)
                    else:
                        self.view.display_message(f"Запись с ID {record_id} не найдена", is_error=True)
            
            self.view.wait_for_enter()
    
    def edit_password(self):
        """Редактирование пароля"""
        record_id = self.view.get_string_input("Введите ID записи для редактирования: ", required=True, max_length=8)
        record = self.manager.get_record_by_id(record_id)
        
        if not record:
            self.view.display_message(f"Запись с ID {record_id} не найдена", is_error=True)
            self.view.wait_for_enter()
            return
        
        self.view.display_update_menu()
        print(f"\nТекущий сервис: {record.get_service()}")
        new_service = self.view.get_string_input("Новый сервис (Enter - не менять): ", required=False, max_length=100)
        
        print(f"\nТекущий пользователь: {record.get_username()}")
        new_username = self.view.get_string_input("Новый пользователь (Enter - не менять): ", required=False, max_length=100)
        
        print("\nВыберите действие для пароля:")
        print("1. Оставить текущий пароль")
        print("2. Ввести новый вручную")
        print("3. Сгенерировать новый")
        pass_choice = self.view.get_choice("Выберите (1-3): ", 1, 3)
        
        new_password = None
        if pass_choice == 2:
            new_password = self.view.get_password_input("Введите новый пароль: ")
        elif pass_choice == 3:
            settings = self.view.get_generator_settings()
            new_password = PasswordGenerator.generate(**settings)
            self.view.display_generated_password(
                new_password,
                PasswordGenerator.calculate_strength(new_password),
                PasswordGenerator.get_strength_label(PasswordGenerator.calculate_strength(new_password))
            )
            if not self.view.get_confirm("Использовать этот пароль? (y/n): "):
                new_password = self.view.get_password_input("Введите пароль вручную: ")
        
        print(f"\nТекущая категория: {record.get_category_display()}")
        self.view.display_categories()
        new_category = self.view.get_string_input("Новая категория (Enter - не менять): ", required=False, max_length=20)
        
        print(f"\nТекущие заметки: {record.get_notes()}")
        new_notes = self.view.get_string_input("Новые заметки (Enter - не менять): ", required=False, max_length=500)
        
        try:
            updates = {}
            if new_service:
                updates['service'] = new_service
            if new_username:
                updates['username'] = new_username
            if new_password:
                updates['password'] = new_password
            if new_category:
                from models import PasswordCategory
                if PasswordCategory.is_valid(new_category):
                    updates['category'] = new_category
            if new_notes:
                updates['notes'] = new_notes
            
            if updates:
                self.manager.update_record(record_id, **updates)
                self.view.display_message("Запись успешно обновлена", is_success=True)
                self.save_data()
            else:
                self.view.display_message("Изменения не внесены")
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def delete_password(self):
        """Удаление пароля"""
        record_id = self.view.get_string_input("Введите ID записи для удаления: ", required=True, max_length=8)
        record = self.manager.get_record_by_id(record_id)
        
        if not record:
            self.view.display_message(f"Запись с ID {record_id} не найдена", is_error=True)
        else:
            print(f"\nЗапись для удаления:")
            print(f"  Сервис: {record.get_service()}")
            print(f"  Пользователь: {record.get_username()}")
            
            if self.view.get_confirm("\nВы уверены, что хотите удалить эту запись? (y/n): "):
                if self.manager.delete_record(record_id):
                    self.view.display_message("Запись успешно удалена", is_success=True)
                    self.save_data()
                else:
                    self.view.display_message("Не удалось удалить запись", is_error=True)
        
        self.view.wait_for_enter()
    
    def generate_password(self):
        """Генерация пароля"""
        self.view.display_password_generator_menu()
        settings = self.view.get_generator_settings()
        
        try:
            password = PasswordGenerator.generate(**settings)
            strength = PasswordGenerator.calculate_strength(password)
            label = PasswordGenerator.get_strength_label(strength)
            
            self.view.display_generated_password(password, strength, label)
            
            if self.view.get_confirm("\nСохранить этот пароль как новую запись? (y/n): "):
                service = self.view.get_string_input("Название сервиса: ", required=True)
                username = self.view.get_string_input("Имя пользователя: ", required=True)
                
                self.view.display_categories()
                category = self.view.get_string_input("Категория (по умолчанию other): ", required=False)
                if not category:
                    category = "other"
                
                from models import PasswordCategory
                if not PasswordCategory.is_valid(category):
                    category = "other"
                
                notes = self.view.get_string_input("Заметки: ", required=False)
                
                self.manager.add_record(service, username, password, category, notes)
                self.view.display_message("Пароль сохранен!", is_success=True)
                self.save_data()
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def show_statistics(self):
        """Показать статистику"""
        stats = self.manager.get_statistics()
        self.view.display_statistics(stats)
        self.view.wait_for_enter()
    
    def undo_action(self):
        """Отмена последнего действия"""
        result = self.manager.undo()
        self.view.display_message(result)
        self.save_data()
        self.view.wait_for_enter()
    
    def load_data(self):
        """Загрузка данных из файла"""
        try:
            records = self.json_handler.load()
            for record in records:
                self.manager.add_record(
                    record.get_service(),
                    record.get_username(),
                    record.get_password(),
                    record.get_category(),
                    record.get_notes()
                )
            if records:
                self.view.display_message(f"Загружено {len(records)} записей", is_success=True)
        except Exception as e:
            self.view.display_message(f"Ошибка загрузки: {e}", is_error=True)
    
    def save_data(self):
        """Сохранение данных в файл"""
        try:
            records = self.manager.get_all_records()
            self.json_handler.save(records)
        except Exception as e:
            self.view.display_message(f"Ошибка сохранения: {e}", is_error=True)
    
    def exit_app(self):
        """Выход из приложения"""
        if self.view.get_confirm("\nСохранить изменения перед выходом? (y/n): "):
            self.save_data()
        self.view.display_message("До свидания!", is_success=True)
        self.running = False


def main():
    """Точка входа в приложение"""
    try:
        app = PasswordManagerController()
        app.run()
    except KeyboardInterrupt:
        print("\n\n❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
