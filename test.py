#!/usr/bin/env python3
"""
Модульное тестирование Random Task Generator
"""

import unittest
import tempfile
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import TaskType, Difficulty, WorkTask, SportTask, StudyTask
from factories import TaskFactory, TaskGenerator
from controllers import TaskManagerController
from utils import TaskHistoryQueue, JSONHandler


class TestTaskTypes(unittest.TestCase):
    """Тесты для различных типов задач"""
    
    def test_work_task_creation(self):
        """Позитивный тест: создание рабочей задачи"""
        task = WorkTask("Сделать отчет", Difficulty.MEDIUM, TaskType.WORK)
        self.assertEqual(task.get_description(), "Сделать отчет")
        self.assertEqual(task.get_difficulty(), Difficulty.MEDIUM)
        self.assertEqual(task.get_estimated_time(), 60)
        self.assertEqual(task.get_icon(), "💼")
    
    def test_sport_task_creation(self):
        """Позитивный тест: создание спортивной задачи"""
        task = SportTask("Пробежка", Difficulty.EASY, TaskType.SPORT)
        self.assertEqual(task.get_estimated_time(), 20)
        self.assertEqual(task.get_icon(), "🏃")
    
    def test_study_task_creation(self):
        """Позитивный тест: создание учебной задачи"""
        task = StudyTask("Изучить Python", Difficulty.HARD, TaskType.STUDY)
        self.assertEqual(task.get_estimated_time(), 100)
        self.assertEqual(task.get_icon(), "📚")
    
    def test_empty_description_negative(self):
        """Негативный тест: пустое описание"""
        task = WorkTask("Описание", Difficulty.MEDIUM, TaskType.WORK)
        with self.assertRaises(ValueError):
            task.set_description("")
    
    def test_description_too_long_edge(self):
        """Граничный тест: слишком длинное описание"""
        task = WorkTask("Описание", Difficulty.MEDIUM, TaskType.WORK)
        with self.assertRaises(ValueError):
            task.set_description("a" * 300)
    
    def test_complete_task(self):
        """Позитивный тест: отметка задачи выполненной"""
        task = WorkTask("Задача", Difficulty.MEDIUM, TaskType.WORK)
        self.assertFalse(task.is_completed())
        task.complete()
        self.assertTrue(task.is_completed())
    
    def test_to_dict_conversion(self):
        """Позитивный тест: конвертация в словарь"""
        task = WorkTask("Тест", Difficulty.MEDIUM, TaskType.WORK)
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict["description"], "Тест")
        self.assertEqual(task_dict["difficulty"], "Средняя")
        self.assertEqual(task_dict["task_type"], "Работа")
        self.assertFalse(task_dict["completed"])
        self.assertIn("task_id", task_dict)
    
    def test_from_dict_conversion(self):
        """Позитивный тест: создание из словаря"""
        task_dict = {
            "task_id": "test123",
            "description": "Тестовая задача",
            "difficulty": "Сложная",
            "task_type": "Спорт",
            "created_at": "01.01.2024 12:00:00",
            "completed": True
        }
        task = Task.from_dict(task_dict)
        
        self.assertEqual(task.get_id(), "test123")
        self.assertEqual(task.get_description(), "Тестовая задача")
        self.assertEqual(task.get_difficulty(), Difficulty.HARD)
        self.assertEqual(task.get_task_type(), TaskType.SPORT)
        self.assertTrue(task.is_completed())


class TestTaskFactory(unittest.TestCase):
    """Тесты для фабрики задач"""
    
    def test_create_work_task(self):
        """Позитивный тест: создание рабочей задачи через фабрику"""
        task = TaskFactory.create_task("Работа", "Написать код", "Средняя")
        self.assertIsInstance(task, WorkTask)
        self.assertEqual(task.get_description(), "Написать код")
    
    def test_create_sport_task(self):
        """Позитивный тест: создание спортивной задачи"""
        task = TaskFactory.create_task(TaskType.SPORT, "Пробежка", Difficulty.EASY)
        self.assertIsInstance(task, SportTask)
    
    def test_create_study_task(self):
        """Позитивный тест: создание учебной задачи"""
        task = TaskFactory.create_task("Учеба", "Повторить материал", "Легкая")
        self.assertIsInstance(task, StudyTask)
    
    def test_invalid_task_type_negative(self):
        """Негативный тест: неверный тип задачи"""
        with self.assertRaises(ValueError):
            TaskFactory.create_task("Несуществующий", "Описание", "Средняя")
    
    def test_invalid_difficulty_negative(self):
        """Негативный тест: неверная сложность"""
        with self.assertRaises(ValueError):
            TaskFactory.create_task("Работа", "Описание", "Сверхсложная")
    
    def test_get_task_examples(self):
        """Позитивный тест: получение примеров задач"""
        examples = TaskFactory.get_task_examples()
        self.assertIn(TaskType.WORK, examples)
        self.assertTrue(len(examples[TaskType.WORK]) > 0)


class TestTaskGenerator(unittest.TestCase):
    """Тесты для генератора задач"""
    
    def setUp(self):
        self.generator = TaskGenerator()
    
    def test_generate_random_task(self):
        """Позитивный тест: генерация случайной задачи"""
        task = self.generator.generate_random_task()
        self.assertIsNotNone(task)
        self.assertIsNotNone(task.get_id())
        self.assertIsNotNone(task.get_description())
    
    def test_generate_task_by_type(self):
        """Позитивный тест: генерация задачи указанного типа"""
        task = self.generator.generate_random_task(task_type=TaskType.WORK)
        self.assertEqual(task.get_task_type(), TaskType.WORK)
    
    def test_generate_task_by_difficulty(self):
        """Позитивный тест: генерация задачи указанной сложности"""
        task = self.generator.generate_random_task(difficulty=Difficulty.HARD)
        self.assertEqual(task.get_difficulty(), Difficulty.HARD)
    
    def test_generate_task_by_template(self):
        """Позитивный тест: создание задачи по шаблону"""
        task = self.generator.generate_task_by_template(
            TaskType.WORK, "Особая задача", Difficulty.HARD
        )
        self.assertEqual(task.get_description(), "Особая задача")
        self.assertEqual(task.get_task_type(), TaskType.WORK)
        self.assertEqual(task.get_difficulty(), Difficulty.HARD)


class TestTaskHistoryQueue(unittest.TestCase):
    """Тесты для очереди истории"""
    
    def setUp(self):
        self.queue = TaskHistoryQueue(max_size=3)
        self.generator = TaskGenerator()
    
    def test_add_task(self):
        """Позитивный тест: добавление задачи"""
        task = self.generator.generate_random_task()
        self.queue.add(task)
        self.assertEqual(self.queue.size(), 1)
    
    def test_max_size_limit_edge(self):
        """Граничный тест: ограничение размера очереди"""
        for i in range(5):
            task = self.generator.generate_random_task()
            self.queue.add(task)
        
        self.assertEqual(self.queue.size(), 3)  # Должно сохранить только 3
    
    def test_get_all(self):
        """Позитивный тест: получение всех задач"""
        tasks = []
        for i in range(3):
            task = self.generator.generate_random_task()
            self.queue.add(task)
            tasks.append(task)
        
        all_tasks = self.queue.get_all()
        self.assertEqual(len(all_tasks), 3)
    
    def test_get_last(self):
        """Позитивный тест: получение последних задач"""
        for i in range(5):
            task = self.generator.generate_random_task()
            self.queue.add(task)
        
        last_tasks = self.queue.get_last(2)
        self.assertEqual(len(last_tasks), 2)
    
    def test_filter_by_type(self):
        """Позитивный тест: фильтрация по типу"""
        work_task = self.generator.generate_random_task(task_type=TaskType.WORK)
        sport_task = self.generator.generate_random_task(task_type=TaskType.SPORT)
        
        self.queue.add(work_task)
        self.queue.add(sport_task)
        
        work_tasks = self.queue.get_by_type(TaskType.WORK)
        self.assertEqual(len(work_tasks), 1)
        self.assertEqual(work_tasks[0].get_task_type(), TaskType.WORK)
    
    def test_filter_by_difficulty(self):
        """Позитивный тест: фильтрация по сложности"""
        easy_task = self.generator.generate_random_task(difficulty=Difficulty.EASY)
        hard_task = self.generator.generate_random_task(difficulty=Difficulty.HARD)
        
        self.queue.add(easy_task)
        self.queue.add(hard_task)
        
        easy_tasks = self.queue.get_by_difficulty(Difficulty.EASY)
        self.assertEqual(len(easy_tasks), 1)
    
    def test_clear_queue(self):
        """Позитивный тест: очистка очереди"""
        task = self.generator.generate_random_task()
        self.queue.add(task)
        self.assertFalse(self.queue.is_empty())
        
        self.queue.clear()
        self.assertTrue(self.queue.is_empty())


class TestTaskManagerController(unittest.TestCase):
    """Тесты для контроллера"""
    
    def setUp(self):
        self.controller = TaskManagerController()
    
    def test_generate_random_task(self):
        """Позитивный тест: генерация случайной задачи через контроллер"""
        task = self.controller.generate_random_task()
        self.assertIsNotNone(task)
        self.assertEqual(len(self.controller.get_all_tasks()), 1)
    
    def test_add_custom_task(self):
        """Позитивный тест: добавление пользовательской задачи"""
        task = self.controller.add_custom_task(
            TaskType.WORK, "Моя задача", Difficulty.MEDIUM
        )
        self.assertEqual(task.get_description(), "Моя задача")
        self.assertEqual(len(self.controller.get_all_tasks()), 1)
    
    def test_filter_by_type(self):
        """Позитивный тест: фильтрация по типу"""
        self.controller.generate_random_task(task_type=TaskType.WORK)
        self.controller.generate_random_task(task_type=TaskType.SPORT)
        
        work_tasks = self.controller.filter_by_type(TaskType.WORK)
        self.assertEqual(len(work_tasks), 1)
    
    def test_mark_completed(self):
        """Позитивный тест: отметка выполненной задачи"""
        task = self.controller.generate_random_task()
        task_id = task.get_id()
        
        result = self.controller.mark_task_completed(task_id)
        self.assertTrue(result)
        
        # Проверяем, что задача отмечена
        tasks = self.controller.get_all_tasks()
        self.assertTrue(tasks[0].is_completed())
    
    def test_mark_nonexistent_completed(self):
        """Негативный тест: отметка несуществующей задачи"""
        result = self.controller.mark_task_completed("nonexistent")
        self.assertFalse(result)
    
    def test_statistics(self):
        """Позитивный тест: получение статистики"""
        self.controller.generate_random_task()
        stats = self.controller.get_statistics()
        self.assertEqual(stats['total'], 1)
        self.assertIn('by_type', stats)
    
    def test_clear_history(self):
        """Позитивный тест: очистка истории"""
        self.controller.generate_random_task()
        self.assertEqual(len(self.controller.get_all_tasks()), 1)
        
        self.controller.clear_history()
        self.assertEqual(len(self.controller.get_all_tasks()), 0)


class TestJSONHandler(unittest.TestCase):
    """Тесты для JSON обработчика"""
    
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.handler = JSONHandler(self.temp_file.name)
        self.generator = TaskGenerator()
    
    def tearDown(self):
        os.unlink(self.temp_file.name)
    
    def test_save_and_load_empty(self):
        """Позитивный тест: сохранение и загрузка пустого списка"""
        self.handler.save_history([])
        loaded = self.handler.load_history()
        self.assertEqual(loaded, [])
    
    def test_save_and_load_tasks(self):
        """Позитивный тест: сохранение и загрузка задач"""
        tasks = [
            self.generator.generate_random_task(),
            self.generator.generate_random_task()
        ]
        
        self.handler.save_history(tasks)
        loaded = self.handler.load_history()
        
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].get_description(), tasks[0].get_description())
        self.assertEqual(loaded[1].get_description(), tasks[1].get_description())
    
    def test_load_nonexistent_file(self):
        """Граничный тест: загрузка из несуществующего файла"""
        handler = JSONHandler("nonexistent.json")
        tasks = handler.load_history()
        self.assertEqual(tasks, [])


def run_tests():
    """Запуск всех тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestTaskTypes))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskFactory))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskHistoryQueue))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskManagerController))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONHandler))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 70)
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
