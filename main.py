#!/usr/bin/env python3
"""
Менеджер задач - Главный файл приложения
"""

from controllers import TaskManager
from views import TaskManagerGUI

def main():
    """Точка входа в приложение"""
    try:
        # Создаем контроллер (модель)
        task_manager = TaskManager()

        # Создаем и запускаем GUI
        app = TaskManagerGUI(task_manager)
        app.run()

    except KeyboardInterrupt:
        print("\nПрограмма прервана")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
