#!/usr/bin/env python3
"""
Random Task Generator - Консольное приложение для генерации случайных задач
Автор: Студент
Описание: Приложение генерирует случайные задачи разных типов с использованием
         паттерна Factory для создания объектов и очереди для хранения истории.
"""

from controllers import TaskManagerController
from views import ConsoleView

class Application:
    """Главный класс приложения"""
    
    def __init__(self):
        self.controller = TaskManagerController()
        self.view = ConsoleView()
        self.running = True
    
    def run(self):
        """Запуск приложения"""
        self.view.display_message("Добро пожаловать в Random Task Generator!", is_success=True)
        
        # Попытка загрузить сохраненную историю
        try:
            count = self.controller.load_history()
            if count > 0:
                self.view.display_message(f"Загружено {count} задач из истории")
        except Exception as e:
            self.view.display_message(f"Не удалось загрузить историю: {e}", is_error=True)
        
        while self.running:
            self.view.clear_screen()
            self.view.display_header()
            self.view.display_menu()
            
            choice = self.view.get_choice("\nВаш выбор (0-9): ", 0, 9)
            
            actions = {
                1: self.generate_random_task,
                2: self.add_custom_task,
                3: self.show_history,
                4: self.filter_tasks,
                5: self.mark_completed,
                6: self.show_statistics,
                7: self.save_history,
                8: self.load_history,
                9: self.clear_history,
                0: self.exit_app
            }
            
            actions.get(choice, lambda: None)()
    
    def generate_random_task(self):
        """Генерация случайной задачи"""
        print("\n--- ГЕНЕРАЦИЯ СЛУЧАЙНОЙ ЗАДАЧИ ---")
        
        # Опционально: выбор типа и сложности
        use_filters = self.view.get_confirm("Хотите задать тип или сложность? (y/n): ")
        
        task_type = None
        difficulty = None
        
        if use_filters:
            filter_choice = self.view.get_choice("Выбрать тип (1) или сложность (2) или оба (3): ", 1, 3)
            
            if filter_choice in [1, 3]:
                task_type = self.view.get_task_type_choice()
            
            if filter_choice in [2, 3]:
                difficulty = self.view.get_difficulty_choice()
        
        try:
            task = self.controller.generate_random_task(task_type, difficulty)
            self.view.display_generated_task(task)
            self.view.display_message("Задача добавлена в историю!", is_success=True)
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def add_custom_task(self):
        """Добавление своей задачи"""
        print("\n--- ДОБАВЛЕНИЕ СВОЕЙ ЗАДАЧИ ---")
        
        task_type = self.view.get_task_type_choice()
        description = self.view.get_string_input("Описание задачи: ", required=True, max_length=200)
        difficulty = self.view.get_difficulty_choice()
        
        try:
            task = self.controller.add_custom_task(task_type, description, difficulty)
            self.view.display_message(f"Задача успешно добавлена! ID: {task.get_id()}", is_success=True)
            self.view.display_task(task)
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def show_history(self):
        """Показать историю задач"""
        tasks = self.controller.get_all_tasks()
        
        if not tasks:
            self.view.display_message("История пуста. Сгенерируйте или добавьте задачи.", is_error=True)
        else:
            self.view.display_tasks(tasks, "ИСТОРИЯ ЗАДАЧ")
            
            # Показать детали выбранной задачи
            if self.view.get_confirm("\nПоказать детали задачи? (y/n): "):
                task_id = self.view.get_string_input("Введите ID задачи: ", required=True)
                task = next((t for t in tasks if t.get_id() == task_id), None)
                if task:
                    self.view.display_task(task, show_full_description=True)
                else:
                    self.view.display_message(f"Задача с ID {task_id} не найдена", is_error=True)
        
        self.view.wait_for_enter()
    
    def filter_tasks(self):
        """Фильтрация задач"""
        while True:
            self.view.display_filter_menu()
            choice = self.view.get_choice("Выберите действие (1-3): ", 1, 3)
            
            if choice == 1:
                task_type = self.view.get_task_type_choice()
                filtered = self.controller.filter_by_type(task_type)
                self.view.display_tasks(filtered, f"ЗАДАЧИ ТИПА: {task_type.value}")
            
            elif choice == 2:
                difficulty = self.view.get_difficulty_choice()
                filtered = self.controller.filter_by_difficulty(difficulty)
                self.view.display_tasks(filtered, f"ЗАДАЧИ СЛОЖНОСТИ: {difficulty.value}")
            
            else:
                break
            
            self.view.wait_for_enter()
    
    def mark_completed(self):
        """Отметить задачу выполненной"""
        tasks = self.controller.get_all_tasks()
        
        if not tasks:
            self.view.display_message("Нет задач для отметки", is_error=True)
            self.view.wait_for_enter()
            return
        
        self.view.display_tasks(tasks, "ВЫБЕРИТЕ ЗАДАЧУ")
        task_id = self.view.get_string_input("\nВведите ID задачи для отметки: ", required=True)
        
        if self.controller.mark_task_completed(task_id):
            self.view.display_message("Задача отмечена как выполненная! 🎉", is_success=True)
        else:
            self.view.display_message(f"Задача с ID {task_id} не найдена", is_error=True)
        
        self.view.wait_for_enter()
    
    def show_statistics(self):
        """Показать статистику"""
        stats = self.controller.get_statistics()
        self.view.display_statistics(stats)
        self.view.wait_for_enter()
    
    def save_history(self):
        """Сохранить историю"""
        try:
            self.controller.save_history()
            count = len(self.controller.get_all_tasks())
            self.view.display_message(f"Сохранено {count} задач в файл task_history.json", is_success=True)
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def load_history(self):
        """Загрузить историю"""
        try:
            count = self.controller.load_history()
            self.view.display_message(f"Загружено {count} задач из файла", is_success=True)
        except Exception as e:
            self.view.display_message(str(e), is_error=True)
        
        self.view.wait_for_enter()
    
    def clear_history(self):
        """Очистить историю"""
        if self.view.get_confirm("Вы уверены, что хотите очистить всю историю? (y/n): "):
            self.controller.clear_history()
            self.view.display_message("История очищена", is_success=True)
        
        self.view.wait_for_enter()
    
    def exit_app(self):
        """Выход из приложения"""
        if self.view.get_confirm("\nСохранить историю перед выходом? (y/n): "):
            try:
                self.controller.save_history()
                self.view.display_message("История сохранена", is_success=True)
            except Exception as e:
                self.view.display_message(f"Ошибка сохранения: {e}", is_error=True)
        
        self.view.display_message("До свидания! 👋", is_success=True)
        self.running = False


def main():
    """Точка входа в приложение"""
    try:
        app = Application()
        app.run()
    except KeyboardInterrupt:
        print("\n\n❌ Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    main()
