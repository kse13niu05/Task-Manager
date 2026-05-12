"""
Фабрика для создания задач различных типов
"""

from models import (
    TaskType, Difficulty, Task,
    WorkTask, SportTask, StudyTask, 
    HobbyTask, HealthTask, SocialTask
)

class TaskFactory:
    """Фабрика для создания задач"""
    
    @staticmethod
    def create_task(task_type, description, difficulty):
        """Создает задачу указанного типа"""
        if not isinstance(task_type, TaskType):
            task_type = TaskType.from_string(task_type)
        
        if not isinstance(difficulty, Difficulty):
            difficulty = Difficulty.from_string(difficulty)
        
        task_classes = {
            TaskType.WORK: WorkTask,
            TaskType.SPORT: SportTask,
            TaskType.STUDY: StudyTask,
            TaskType.HOBBY: HobbyTask,
            TaskType.HEALTH: HealthTask,
            TaskType.SOCIAL: SocialTask
        }
        
        task_class = task_classes.get(task_type)
        if not task_class:
            raise ValueError(f"Неизвестный тип задачи: {task_type}")
        
        return task_class(description, difficulty, task_type)
    
    @staticmethod
    def get_task_examples():
        """Возвращает примеры задач для каждого типа"""
        examples = {
            TaskType.WORK: [
                "Написать отчет по проекту",
                "Провести встречу с командой",
                "Закончить презентацию",
                "Оптимизировать код",
                "Составить план на неделю"
            ],
            TaskType.SPORT: [
                "Пробежка 5 км",
                "Тренировка в зале",
                "Йога утром",
                "Плавание в бассейне",
                "Велосипедная прогулка"
            ],
            TaskType.STUDY: [
                "Изучить новую технологию",
                "Прочитать главу из книги",
                "Просмотреть онлайн-курс",
                "Сделать домашнее задание",
                "Повторить материал"
            ],
            TaskType.HOBBY: [
                "Поиграть на гитаре",
                "Нарисовать скетч",
                "Почитать книгу",
                "Поиграть в настольную игру",
                "Позаниматься фотографией"
            ],
            TaskType.HEALTH: [
                "Сделать зарядку",
                "Провести медитацию",
                "Сходить к врачу",
                "Приготовить полезный ужин",
                "Выпить 2 литра воды"
            ],
            TaskType.SOCIAL: [
                "Позвонить друзьям",
                "Встретиться с семьей",
                "Сходить на свидание",
                "Помочь соседу",
                "Сходить на мероприятие"
            ]
        }
        return examples


class TaskGenerator:
    """Генератор случайных задач"""
    
    def __init__(self, task_factory=TaskFactory):
        self.factory = task_factory
        self.examples = self.factory.get_task_examples()
    
    def generate_random_task(self, task_type=None, difficulty=None):
        """Генерирует случайную задачу"""
        import random
        
        # Случайный выбор типа, если не указан
        if task_type is None:
            task_type = random.choice(list(self.examples.keys()))
        elif isinstance(task_type, str):
            task_type = TaskType.from_string(task_type)
        
        # Случайный выбор сложности, если не указана
        if difficulty is None:
            difficulty = random.choice([Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD])
        elif isinstance(difficulty, str):
            difficulty = Difficulty.from_string(difficulty)
        
        # Случайный выбор описания из примеров
        description = random.choice(self.examples[task_type])
        
        return self.factory.create_task(task_type, description, difficulty)
    
    def generate_task_by_template(self, task_type, description, difficulty):
        """Создает задачу по заданным параметрам"""
        return self.factory.create_task(task_type, description, difficulty)
