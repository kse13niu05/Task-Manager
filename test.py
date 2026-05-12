#!/usr/bin/env python3
"""
Модульное тестирование приложения
"""

import unittest
import tempfile
import os
from models import Task, TaskStatus
from controllers import TaskManager
from utils import PriorityTaskQueue, UndoStack, JSONHandler

class TestTask(unittest.TestCase):
    """Тесты для класса Task"""

    def test_create_valid_task(self):
        """Позитивный тест: создание корректной задачи"""
        task = Task("Тест", "Описание", "Высокий")
        self.assertEqual(task.get_title(), "Тест")
        self.assertEqual(task.get_description(), "Описание")
        self.assertEqual(task.get_priority(), "Высокий")
        self.assertIsNotNone(task.get_id())

    def test_empty_title_negative(self):
        """Негативный тест: пустое название"""
        task = Task("Тест", "Описание", "Высокий")
        with self.assertRaises(ValueError):
            task.set_title("")

    def test_empty_title_edge(self):
        """Граничный тест: пробелы в названии"""
        task = Task("Тест", "Описание", "Высокий")
        with self.assertRaises(ValueError):
            task.set_title("   ")

    def test_invalid_priority_negative(self):
        """Негативный тест: неверный приоритет"""
        task = Task("Тест", "Описание", "Высокий")
        with self.assertRaises(ValueError):
            task.set_priority("Очень высокий")

    def test_priority_values_edge(self):
        """Граничный тест: все возможные приоритеты"""
        task = Task("Тест", "Описание", "Высокий")

        task.set_priority("Низкий")
        self.assertEqual(task.get_priority(), "Низкий")
        self.assertEqual(task.get_priority_value(), 1)

        task.set_priority("Средний")
        self.assertEqual(task.get_priority(), "Средний")
        self.assertEqual(task.get_priority_value(), 2)

        task.set_priority("Высокий")
        self.assertEqual(task.get_priority(), "Высокий")
        self.assertEqual(task.get_priority_value(), 3)

    def test_status_conversion(self):
        """Позитивный тест: конвертация статусов"""
        status = TaskStatus.from_string("Нужно сделать")
        self.assertEqual(status, TaskStatus.TO_DO)
        self.assertEqual(TaskStatus.get_russian(status), "Нужно сделать")

    def test_long_title_edge(self):
        """Граничный тест: длинное название"""
        task = Task("Тест", "Описание", "Высокий")
        long_title = "A" * 1000
        task.set_title(long_title)
        self.assertEqual(len(task.get_title()), 1000)

    def test_to_dict_conversion(self):
        """Позитивный тест: конвертация в словарь"""
        task = Task("Тест", "Описание", "Высокий")
        task_dict = task.to_dict()

        self.assertEqual(task_dict["title"], "Тест")
        self.assertEqual(task_dict["description"], "Описание")
        self.assertEqual(task_dict["priority"], "Высокий")
        self.assertIn("task_id", task_dict)
        self.assertIn("created_at", task_dict)

    def test_from_dict_conversion(self):
        """Позитивный тест: создание из словаря"""
        task_dict = {
            "task_id": "test123",
            "title": "Тест из словаря",
            "description": "Описание",
            "priority": "Средний",
            "status": "In Progress",
            "created_at": "01.01.2024 12:00"
        }
        task = Task.from_dict(task_dict)

        self.assertEqual(task.get_id(), "test123")
        self.assertEqual(task.get_title(), "Тест из словаря")
        self.assertEqual(task.get_status(), TaskStatus.IN_PROGRESS)

class TestPriorityQueue(unittest.TestCase):
    """Тесты для очереди с приоритетом"""

    def setUp(self):
        self.queue = PriorityTaskQueue()
        self.high = Task("High", "", "Высокий")
        self.medium = Task("Medium", "", "Средний")
        self.low = Task("Low", "", "Низкий")

    def test_enqueue_dequeue_order(self):
        """Позитивный тест: порядок извлечения по приоритету"""
        self.queue.enqueue(self.low)
        self.queue.enqueue(self.high)
        self.queue.enqueue(self.medium)

        self.assertEqual(self.queue.dequeue().get_priority(), "Высокий")
        self.assertEqual(self.queue.dequeue().get_priority(), "Средний")
        self.assertEqual(self.queue.dequeue().get_priority(), "Низкий")

    def test_empty_queue_edge(self):
        """Граничный тест: пустая очередь"""
        self.assertTrue(self.queue.is_empty())
        self.assertEqual(self.queue.size(), 0)
        self.assertIsNone(self.queue.dequeue())

    def test_queue_size(self):
        """Позитивный тест: размер очереди"""
        self.assertEqual(self.queue.size(), 0)
        self.queue.enqueue(self.high)
        self.assertEqual(self.queue.size(), 1)
        self.queue.enqueue(self.medium)
        self.assertEqual(self.queue.size(), 2)
        self.queue.dequeue()
        self.assertEqual(self.queue.size(), 1)

    def test_get_all_tasks(self):
        """Позитивный тест: получение всех задач в правильном порядке"""
        self.queue.enqueue(self.low)
        self.queue.enqueue(self.high)
        self.queue.enqueue(self.medium)

        tasks = self.queue.get_all()
        self.assertEqual(len(tasks), 3)
        self.assertEqual(tasks[0].get_priority(), "Высокий")
        self.assertEqual(tasks[1].get_priority(), "Средний")
        self.assertEqual(tasks[2].get_priority(), "Низкий")

    def test_multiple_same_priority(self):
        """Граничный тест: несколько задач с одинаковым приоритетом"""
        high1 = Task("High1", "", "Высокий")
        high2 = Task("High2", "", "Высокий")

        self.queue.enqueue(high1)
        self.queue.enqueue(high2)

        self.assertEqual(self.queue.dequeue().get_title(), "High1")
        self.assertEqual(self.queue.dequeue().get_title(), "High2")

class TestUndoStack(unittest.TestCase):
    """Тесты для стека отмены"""

    def setUp(self):
        self.stack = UndoStack(max_size=3)

    def test_push_pop(self):
        """Позитивный тест: добавление и извлечение"""
        self.stack.push("action1")
        self.stack.push("action2")

        self.assertEqual(self.stack.pop(), "action2")
        self.assertEqual(self.stack.pop(), "action1")

    def test_pop_empty_edge(self):
        """Граничный тест: извлечение из пустого стека"""
        self.assertIsNone(self.stack.pop())

    def test_max_size_limit_edge(self):
        """Граничный тест: ограничение максимального размера"""
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        self.stack.push(4)

        # Должен сохранить только последние 3
        self.assertEqual(self.stack.pop(), 4)
        self.assertEqual(self.stack.pop(), 3)
        self.assertEqual(self.stack.pop(), 2)
        self.assertTrue(self.stack.is_empty())

    def test_clear(self):
        """Позитивный тест: очистка стека"""
        self.stack.push("action1")
        self.stack.push("action2")
        self.stack.clear()
        self.assertTrue(self.stack.is_empty())

class TestTaskManager(unittest.TestCase):
    """Тесты для менеджера задач"""

    def setUp(self):
        self.manager = TaskManager()

    def test_add_task_positive(self):
        """Позитивный тест: добавление задачи"""
        task = self.manager.add_task("Тест", "Описание", "Высокий")
        self.assertEqual(self.manager.get_count(), 1)
        self.assertIsNotNone(self.manager.get_task_by_id(task.get_id()))

    def test_add_empty_title_negative(self):
        """Негативный тест: добавление с пустым названием"""
        with self.assertRaises(ValueError):
            self.manager.add_task("", "Описание", "Высокий")

    def test_delete_task_positive(self):
        """Позитивный тест: удаление задачи"""
        task = self.manager.add_task("Тест", "Описание", "Высокий")
        self.assertTrue(self.manager.delete_task(task.get_id()))
        self.assertEqual(self.manager.get_count(), 0)

    def test_delete_nonexistent_task(self):
        """Негативный тест: удаление несуществующей задачи"""
        self.assertFalse(self.manager.delete_task("nonexistent"))

    def test_update_task_positive(self):
        """Позитивный тест: обновление задачи"""
        task = self.manager.add_task("Старое", "Описание", "Низкий")
        self.manager.update_task(task.get_id(), title="Новое", priority="Высокий")

        updated = self.manager.get_task_by_id(task.get_id())
        self.assertEqual(updated.get_title(), "Новое")
        self.assertEqual(updated.get_priority(), "Высокий")

    def test_undo_add(self):
        """Позитивный тест: отмена добавления"""
        task = self.manager.add_task("Тест", "Описание", "Высокий")
        self.assertEqual(self.manager.get_count(), 1)

        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 0)

    def test_undo_delete(self):
        """Позитивный тест: отмена удаления"""
        task = self.manager.add_task("Тест", "Описание", "Высокий")
        task_id = task.get_id()

        self.manager.delete_task(task_id)
        self.assertEqual(self.manager.get_count(), 0)

        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 1)
        self.assertIsNotNone(self.manager.get_task_by_id(task_id))

    def test_filter_by_status(self):
        """Позитивный тест: фильтрация по статусу"""
        self.manager.add_task("Задача 1", "", "Низкий")
        task2 = self.manager.add_task("Задача 2", "", "Средний")
        self.manager.update_task(task2.get_id(), status="Готово")

        todo_tasks = self.manager.filter_by_status("Нужно сделать")
        self.assertEqual(len(todo_tasks), 1)

        done_tasks = self.manager.filter_by_status("Готово")
        self.assertEqual(len(done_tasks), 1)

    def test_filter_by_priority(self):
        """Позитивный тест: фильтрация по приоритету"""
        self.manager.add_task("Низкая", "", "Низкий")
        self.manager.add_task("Средняя", "", "Средний")
        self.manager.add_task("Высокая", "", "Высокий")

        high_tasks = self.manager.filter_by_priority("Высокий")
        self.assertEqual(len(high_tasks), 1)
        self.assertEqual(high_tasks[0].get_title(), "Высокая")

    def test_search_tasks(self):
        """Позитивный тест: поиск задач"""
        self.manager.add_task("Купить молоко", "Продукты", "Средний")
        self.manager.add_task("Сделать отчет", "Работа", "Высокий")
        self.manager.add_task("Позвонить маме", "Личное", "Низкий")

        results = self.manager.search("молоко")
        self.assertEqual(len(results), 1)

        results = self.manager.search("отчет")
        self.assertEqual(len(results), 1)

    def test_priority_sorting(self):
        """Позитивный тест: сортировка по приоритету"""
        self.manager.add_task("Низкая", "", "Низкий")
        self.manager.add_task("Высокая", "", "Высокий")
        self.manager.add_task("Средняя", "", "Средний")

        sorted_tasks = self.manager.get_tasks_by_priority()
        self.assertEqual(sorted_tasks[0].get_title(), "Высокая")
        self.assertEqual(sorted_tasks[1].get_title(), "Средняя")
        self.assertEqual(sorted_tasks[2].get_title(), "Низкая")

    def test_multiple_undos(self):
        """Граничный тест: множественная отмена"""
        self.manager.add_task("Задача 1", "", "Низкий")
        self.manager.add_task("Задача 2", "", "Средний")
        self.manager.add_task("Задача 3", "", "Высокий")

        self.assertEqual(self.manager.get_count(), 3)

        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 2)
        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 1)
        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 0)
        self.manager.undo()  # Nothing to undo
        self.assertEqual(self.manager.get_count(), 0)

class TestJSONHandler(unittest.TestCase):
    """Тесты для JSON обработчика"""

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.handler = JSONHandler(self.temp_file.name)

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_save_and_load_empty(self):
        """Позитивный тест: сохранение и загрузка пустого списка"""
        self.handler.save([])
        loaded = self.handler.load()
        self.assertEqual(loaded, [])

    def test_save_and_load_tasks(self):
        """Позитивный тест: сохранение и загрузка задач"""
        tasks = [
            Task("Задача 1", "Описание 1", "Высокий"),
            Task("Задача 2", "Описание 2", "Средний")
        ]

        self.handler.save(tasks)
        loaded = self.handler.load()

        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].get_title(), "Задача 1")
        self.assertEqual(loaded[1].get_title(), "Задача 2")

    def test_load_nonexistent_file(self):
        """Граничный тест: загрузка из несуществующего файла"""
        handler = JSONHandler("nonexistent.json")
        tasks = handler.load()
        self.assertEqual(tasks, [])

    def test_save_with_invalid_data(self):
        """Негативный тест: сохранение некорректных данных"""
        with self.assertRaises(Exception):
            self.handler.save(None)

def run_tests():
    """Запуск всех тестов"""
    # Создаем загрузчик тестов
    loader = unittest.TestLoader()

    # Добавляем все тесты
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestTask))
    suite.addTests(loader.loadTestsFromTestCase(TestPriorityQueue))
    suite.addTests(loader.loadTestsFromTestCase(TestUndoStack))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONHandler))

    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Выводим результат
    print("\n" + "="*50)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("="*50)
    print(f"Всего тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Провалено: {len(result.failures)}")
    print(f"Ошибок: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    else:
        print("\n❌ ЕСТЬ ПРОБЛЕМЫ С ТЕСТАМИ!")

    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
