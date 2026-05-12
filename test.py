#!/usr/bin/env python3
"""
Модульное тестирование Password Manager
"""

import unittest
import tempfile
import os
import sys

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import PasswordRecord, PasswordCategory
from controllers import PasswordManager
from utils import PasswordGenerator, UndoStack, JSONHandler


class TestPasswordRecord(unittest.TestCase):
    """Тесты для класса PasswordRecord"""
    
    def setUp(self):
        self.record = PasswordRecord("Google", "user@example.com", "SecurePass123!", "email")
    
    def test_create_valid_record(self):
        """Позитивный тест: создание корректной записи"""
        self.assertEqual(self.record.get_service(), "Google")
        self.assertEqual(self.record.get_username(), "user@example.com")
        self.assertEqual(self.record.get_password(), "SecurePass123!")
        self.assertEqual(self.record.get_category(), "email")
        self.assertIsNotNone(self.record.get_id())
    
    def test_empty_service_negative(self):
        """Негативный тест: пустое название сервиса"""
        with self.assertRaises(ValueError):
            self.record.set_service("")
    
    def test_whitespace_service_edge(self):
        """Граничный тест: пробелы в названии сервиса"""
        with self.assertRaises(ValueError):
            self.record.set_service("   ")
    
    def test_empty_username_negative(self):
        """Негативный тест: пустое имя пользователя"""
        with self.assertRaises(ValueError):
            self.record.set_username("")
    
    def test_empty_password_negative(self):
        """Негативный тест: пустой пароль"""
        with self.assertRaises(ValueError):
            self.record.set_password("")
    
    def test_short_password_edge(self):
        """Граничный тест: слишком короткий пароль"""
        with self.assertRaises(ValueError):
            self.record.set_password("123")
    
    def test_long_password_edge(self):
        """Граничный тест: слишком длинный пароль"""
        with self.assertRaises(ValueError):
            self.record.set_password("a" * 200)
    
    def test_long_service_edge(self):
        """Граничный тест: длинное название сервиса"""
        with self.assertRaises(ValueError):
            self.record.set_service("a" * 200)
    
    def test_long_username_edge(self):
        """Граничный тест: длинное имя пользователя"""
        with self.assertRaises(ValueError):
            self.record.set_username("a" * 200)
    
    def test_invalid_category_negative(self):
        """Негативный тест: неверная категория"""
        with self.assertRaises(ValueError):
            self.record.set_category("invalid_category")
    
    def test_valid_category(self):
        """Позитивный тест: верная категория"""
        self.record.set_category("social")
        self.assertEqual(self.record.get_category(), "social")
    
    def test_mask_password(self):
        """Позитивный тест: маскирование пароля"""
        password = "SecurePass123!"
        self.record.set_password(password)
        masked = self.record.get_masked_password()
        
        if len(password) <= 8:
            self.assertEqual(len(masked), len(password))
            self.assertTrue(all(c == '*' for c in masked))
        else:
            self.assertEqual(masked[:4], password[:4])
            self.assertEqual(masked[-4:], password[-4:])
    
    def test_to_dict_conversion(self):
        """Позитивный тест: конвертация в словарь"""
        record_dict = self.record.to_dict()
        self.assertEqual(record_dict["service"], "Google")
        self.assertEqual(record_dict["username"], "user@example.com")
        self.assertEqual(record_dict["password"], "SecurePass123!")
        self.assertEqual(record_dict["category"], "email")
        self.assertIn("record_id", record_dict)
        self.assertIn("created_at", record_dict)
        self.assertIn("updated_at", record_dict)
    
    def test_from_dict_conversion(self):
        """Позитивный тест: создание из словаря"""
        record_dict = {
            "record_id": "test123",
            "service": "Test Service",
            "username": "testuser",
            "password": "TestPass123!",
            "category": "work",
            "notes": "Test notes",
            "created_at": "01.01.2024 12:00",
            "updated_at": "01.01.2024 12:00"
        }
        record = PasswordRecord.from_dict(record_dict)
        self.assertEqual(record.get_id(), "test123")
        self.assertEqual(record.get_service(), "Test Service")
        self.assertEqual(record.get_username(), "testuser")
        self.assertEqual(record.get_password(), "TestPass123!")


class TestPasswordGenerator(unittest.TestCase):
    """Тесты для генератора паролей"""
    
    def test_generate_default_length(self):
        """Позитивный тест: генерация пароля по умолчанию"""
        password = PasswordGenerator.generate()
        self.assertEqual(len(password), 12)
    
    def test_generate_custom_length(self):
        """Позитивный тест: генерация с заданной длиной"""
        lengths = [8, 16, 24, 32]
        for length in lengths:
            password = PasswordGenerator.generate(length=length)
            self.assertEqual(len(password), length)
    
    def test_generate_too_short_edge(self):
        """Граничный тест: слишком короткий пароль"""
        with self.assertRaises(ValueError):
            PasswordGenerator.generate(length=3)
    
    def test_generate_too_long_edge(self):
        """Граничный тест: слишком длинный пароль"""
        with self.assertRaises(ValueError):
            PasswordGenerator.generate(length=200)
    
    def test_generate_only_uppercase(self):
        """Позитивный тест: только заглавные буквы"""
        password = PasswordGenerator.generate(length=20, use_lowercase=False, 
                                              use_digits=False, use_special=False)
        self.assertTrue(all(c.isupper() for c in password))
    
    def test_generate_only_lowercase(self):
        """Позитивный тест: только строчные буквы"""
        password = PasswordGenerator.generate(length=20, use_uppercase=False,
                                              use_digits=False, use_special=False)
        self.assertTrue(all(c.islower() for c in password))
    
    def test_generate_with_digits(self):
        """Позитивный тест: с цифрами"""
        password = PasswordGenerator.generate(length=20, use_uppercase=False,
                                              use_lowercase=False, use_special=False)
        self.assertTrue(all(c.isdigit() for c in password))
    
    def test_calculate_strength(self):
        """Позитивный тест: оценка сложности пароля"""
        weak_pass = "123"
        medium_pass = "Password123"
        strong_pass = "S#r0ngP@ssw0rd!2024"
        
        weak_score = PasswordGenerator.calculate_strength(weak_pass)
        medium_score = PasswordGenerator.calculate_strength(medium_pass)
        strong_score = PasswordGenerator.calculate_strength(strong_pass)
        
        self.assertLess(weak_score, 40)
        self.assertLess(medium_score, 80)
        self.assertGreaterEqual(strong_score, 80)
    
    def test_empty_password_strength(self):
        """Граничный тест: пустой пароль"""
        score = PasswordGenerator.calculate_strength("")
        self.assertEqual(score, 0)
    
    def test_get_strength_label(self):
        """Позитивный тест: текстовые метки сложности"""
        self.assertEqual(PasswordGenerator.get_strength_label(90), "Очень надежный")
        self.assertEqual(PasswordGenerator.get_strength_label(70), "Надежный")
        self.assertEqual(PasswordGenerator.get_strength_label(50), "Средний")
        self.assertEqual(PasswordGenerator.get_strength_label(30), "Слабый")
        self.assertEqual(PasswordGenerator.get_strength_label(10), "Очень слабый")


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
        """Граничный тест: ограничение размера"""
        self.stack.push(1)
        self.stack.push(2)
        self.stack.push(3)
        self.stack.push(4)
        
        self.assertEqual(self.stack.size(), 3)
        self.assertEqual(self.stack.pop(), 4)
        self.assertEqual(self.stack.pop(), 3)
        self.assertEqual(self.stack.pop(), 2)
        self.assertTrue(self.stack.is_empty())
    
    def test_peek(self):
        """Позитивный тест: просмотр последнего действия"""
        self.stack.push("action1")
        self.stack.push("action2")
        self.assertEqual(self.stack.peek(), "action2")
        self.assertEqual(self.stack.size(), 2)
    
    def test_clear(self):
        """Позитивный тест: очистка стека"""
        self.stack.push("action1")
        self.stack.push("action2")
        self.stack.clear()
        self.assertTrue(self.stack.is_empty())


class TestPasswordManager(unittest.TestCase):
    """Тесты для менеджера паролей"""
    
    def setUp(self):
        self.manager = PasswordManager()
        self.record = self.manager.add_record("Google", "user@gmail.com", "Pass123!", "email")
    
    def test_add_record_positive(self):
        """Позитивный тест: добавление записи"""
        count = self.manager.get_count()
        self.assertEqual(count, 1)
        self.assertIsNotNone(self.manager.get_record_by_id(self.record.get_id()))
    
    def test_add_empty_service_negative(self):
        """Негативный тест: добавление с пустым сервисом"""
        with self.assertRaises(ValueError):
            self.manager.add_record("", "user", "pass", "other")
    
    def test_delete_record_positive(self):
        """Позитивный тест: удаление записи"""
        self.assertTrue(self.manager.delete_record(self.record.get_id()))
        self.assertEqual(self.manager.get_count(), 0)
    
    def test_delete_nonexistent_record(self):
        """Негативный тест: удаление несуществующей записи"""
        self.assertFalse(self.manager.delete_record("nonexistent"))
    
    def test_update_record(self):
        """Позитивный тест: обновление записи"""
        self.manager.update_record(self.record.get_id(), service="YouTube", username="newuser@gmail.com")
        updated = self.manager.get_record_by_id(self.record.get_id())
        self.assertEqual(updated.get_service(), "YouTube")
        self.assertEqual(updated.get_username(), "newuser@gmail.com")
    
    def test_search_by_service(self):
        """Позитивный тест: поиск по сервису"""
        self.manager.add_record("Facebook", "user@fb.com", "pass1", "social")
        self.manager.add_record("Twitter", "user@tw.com", "pass2", "social")
        
        results = self.manager.search_by_service("face")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get_service(), "Facebook")
    
    def test_search_by_username(self):
        """Позитивный тест: поиск по имени пользователя"""
        self.manager.add_record("Service1", "alice@test.com", "pass1", "email")
        self.manager.add_record("Service2", "bob@test.com", "pass2", "email")
        
        results = self.manager.search_by_username("alice")
        self.assertEqual(len(results), 1)
    
    def test_filter_by_category(self):
        """Позитивный тест: фильтрация по категории"""
        self.manager.add_record("GitHub", "dev@github.com", "pass1", "work")
        self.manager.add_record("Spotify", "user@spotify.com", "pass2", "entertainment")
        
        work_records = self.manager.filter_by_category("work")
        self.assertEqual(len(work_records), 1)
        self.assertEqual(work_records[0].get_service(), "GitHub")
    
    def test_undo_add(self):
        """Позитивный тест: отмена добавления"""
        initial_count = self.manager.get_count()
        self.manager.undo()
        self.assertEqual(self.manager.get_count(), initial_count - 1)
    
    def test_undo_delete(self):
        """Позитивный тест: отмена удаления"""
        record_id = self.record.get_id()
        self.manager.delete_record(record_id)
        self.assertEqual(self.manager.get_count(), 0)
        self.manager.undo()
        self.assertEqual(self.manager.get_count(), 1)
    
    def test_undo_update(self):
        """Позитивный тест: отмена обновления"""
        original_service = self.record.get_service()
        self.manager.update_record(self.record.get_id(), service="NewService")
        self.assertEqual(self.record.get_service(), "NewService")
        self.manager.undo()
        self.assertEqual(self.record.get_service(), original_service)
    
    def test_get_statistics(self):
        """Позитивный тест: получение статистики"""
        stats = self.manager.get_statistics()
        self.assertEqual(stats['total'], 1)
        self.assertIn('email', stats['by_category'])


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
    
    def test_save_and_load_records(self):
        """Позитивный тест: сохранение и загрузка записей"""
        records = [
            PasswordRecord("Google", "user1@test.com", "pass123", "email"),
            PasswordRecord("GitHub", "user2@github.com", "pass456", "work")
        ]
        
        self.handler.save(records)
        loaded = self.handler.load()
        
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0].get_service(), "Google")
        self.assertEqual(loaded[1].get_service(), "GitHub")
    
    def test_load_nonexistent_file(self):
        """Граничный тест: загрузка из несуществующего файла"""
        handler = JSONHandler("nonexistent.json")
        records = handler.load()
        self.assertEqual(records, [])


def run_tests():
    """Запуск всех тестов"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordRecord))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestUndoStack))
    suite.addTests(loader.loadTestsFromTestCase(TestPasswordManager))
    suite.addTests(loader.loadTestsFromTestCase(TestJSONHandler))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print("=" * 60)
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
