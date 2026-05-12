"""
Консольное представление для Random Task Generator
"""

from models import TaskType, Difficulty

class ConsoleView:
    """Консольный интерфейс пользователя"""
    
    @staticmethod
    def clear_screen():
        """Очистка экрана"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def display_header():
        """Отображение заголовка"""
        print("\n" + "=" * 70)
        print("         🎲 RANDOM TASK GENERATOR 🎲")
        print("=" * 70)
    
    @staticmethod
    def display_menu():
        """Отображение главного меню"""
        print("\n" + "-" * 70)
        print("ГЛАВНОЕ МЕНЮ")
        print("-" * 70)
        print("1. 🎲 Сгенерировать случайную задачу")
        print("2. 🔧 Добавить свою задачу")
        print("3. 📋 Показать историю задач")
        print("4. 🔍 Фильтрация задач")
        print("5. ✅ Отметить задачу выполненной")
        print("6. 📊 Статистика")
        print("7. 💾 Сохранить историю")
        print("8. 📂 Загрузить историю")
        print("9. 🗑️ Очистить историю")
        print("0. 🚪 Выход")
        print("-" * 70)
    
    @staticmethod
    def display_filter_menu():
        """Меню фильтрации"""
        print("\n--- ФИЛЬТРАЦИЯ ЗАДАЧ ---")
        print("1. По типу")
        print("2. По сложности")
        print("3. Назад")
    
    @staticmethod
    def display_task_types():
        """Отображение доступных типов задач"""
        print("\nДоступные типы задач:")
        for i, task_type in enumerate(TaskType.get_all(), 1):
            icon_map = {
                TaskType.WORK: "💼",
                TaskType.SPORT: "🏃",
                TaskType.STUDY: "📚",
                TaskType.HOBBY: "🎨",
                TaskType.HEALTH: "🏥",
                TaskType.SOCIAL: "👥"
            }
            icon = icon_map.get(task_type, "📌")
            print(f"  {i}. {icon} {task_type.value}")
    
    @staticmethod
    def display_difficulties():
        """Отображение уровней сложности"""
        print("\nУровни сложности:")
        difficulties = ["Легкая", "Средняя", "Сложная"]
        for i, diff in enumerate(difficulties, 1):
            print(f"  {i}. {diff}")
    
    @staticmethod
    def display_task(task, show_full_description=True):
        """Отображение одной задачи"""
        icon = task.get_icon()
        status = "✅" if task.is_completed() else "⏳"
        
        print(f"\n{icon} {status} [{task.get_id()}]")
        print(f"   Описание: {task.get_description()}")
        print(f"   Тип: {task.get_task_type().value}")
        print(f"   Сложность: {task.get_difficulty().value}")
        print(f"   Время: {task.get_estimated_time()} мин.")
        print(f"   Создана: {task.get_created_at()}")
    
    @staticmethod
    def display_tasks(tasks, title="ИСТОРИЯ ЗАДАЧ"):
        """Отображение списка задач"""
        if not tasks:
            print("\n❌ Задачи не найдены")
            return
        
        print(f"\n{'='*70}")
        print(f"{title}: {len(tasks)} задач(и)")
        print(f"{'='*70}")
        
        for i, task in enumerate(tasks, 1):
            icon = task.get_icon()
            status = "✅" if task.is_completed() else "⏳"
            print(f"\n{i}. {icon} {status} [{task.get_id()}]")
            print(f"   {task.get_description()}")
            print(f"   📍 {task.get_task_type().value} | 🎯 {task.get_difficulty().value} | ⏱️ {task.get_estimated_time()} мин.")
        
        print(f"\n{'-'*70}")
    
    @staticmethod
    def display_statistics(stats):
        """Отображение статистики"""
        print("\n" + "=" * 70)
        print("СТАТИСТИКА ЗАДАЧ")
        print("=" * 70)
        print(f"Всего задач: {stats['total']}")
        print(f"Выполнено: {stats['completed']}")
        
        if stats['total'] > 0:
            completion_rate = (stats['completed'] / stats['total']) * 100
            print(f"Прогресс: {completion_rate:.1f}%")
        
        print(f"\nОбщее время: {stats['total_time']} минут ({stats['total_time'] // 60} часов {stats['total_time'] % 60} минут)")
        
        print("\n📊 По типам:")
        for task_type, count in stats['by_type'].items():
            print(f"   {task_type}: {count}")
        
        print("\n📊 По сложности:")
        for difficulty, count in stats['by_difficulty'].items():
            print(f"   {difficulty}: {count}")
        
        print("=" * 70)
    
    @staticmethod
    def display_generated_task(task):
        """Отображение сгенерированной задачи"""
        print("\n" + "🎉" * 35)
        print("СГЕНЕРИРОВАНА НОВАЯ ЗАДАЧА!")
        print("🎉" * 35)
        ConsoleView.display_task(task)
        print("\n💡 Удачи в выполнении!")
    
    @staticmethod
    def get_string_input(prompt, required=True, max_length=200):
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
    def get_task_type_choice():
        """Получение выбора типа задачи"""
        ConsoleView.display_task_types()
        while True:
            try:
                choice = input("\nВыберите тип задачи (1-6): ").strip()
                if not choice:
                    print("❌ Пожалуйста, сделайте выбор")
                    continue
                
                choice_int = int(choice)
                if 1 <= choice_int <= 6:
                    return TaskType.get_all()[choice_int - 1]
                else:
                    print("❌ Пожалуйста, введите число от 1 до 6")
            except ValueError:
                print("❌ Пожалуйста, введите корректное число")
    
    @staticmethod
    def get_difficulty_choice():
        """Получение выбора сложности"""
        ConsoleView.display_difficulties()
        while True:
            try:
                choice = input("\nВыберите сложность (1-3): ").strip()
                if not choice:
                    print("❌ Пожалуйста, сделайте выбор")
                    continue
                
                choice_int = int(choice)
                if 1 <= choice_int <= 3:
                    difficulties = [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]
                    return difficulties[choice_int - 1]
                else:
                    print("❌ Пожалуйста, введите число от 1 до 3")
            except ValueError:
                print("❌ Пожалуйста, введите корректное число")
    
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
    def wait_for_enter():
        """Ожидание нажатия Enter"""
        input("\nНажмите Enter для продолжения...")
