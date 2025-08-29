# 🌐 Интерактивное упражнение: Flask API с TDD

Создадим полноценный RESTful API используя Flask и TDD подход для всех эндпоинтов и бизнес-логики.

## 📋 Техническое задание

**Реализуйте RESTful API** для управления задачами (TODO API) со следующими эндпоинтами:

### **Основные эндпоинты:**
- `GET /tasks` - получение всех задач
- `POST /tasks` - создание новой задачи
- `GET /tasks/<id>` - получение задачи по ID
- `PUT /tasks/<id>` - обновление задачи
- `DELETE /tasks/<id>` - удаление задачи

### **Требования:**
- ✅ Валидация данных
- ✅ Обработка ошибок
- ✅ JSON ответы
- ✅ HTTP статус коды
- ✅ TDD подход

## 🎯 Этап 1: Проектирование API

### Архитектура приложения

{{ create_exercise_form(
    "api_architecture_design",
    "Проектирование архитектуры API",
    "Спроектируйте структуру приложения с разделением на слои для эффективного тестирования.",
    """# Структура проекта для TDD-friendly API
todo_api/
├── domain/              # Бизнес-логика
│   ├── models.py       # Модели данных (Task)
│   └── services.py     # Бизнес-сервисы
├── infrastructure/     # Внешние зависимости
│   ├── repositories.py # Репозитории данных
│   └── database.py     # Настройки БД
├── web/                # Веб-слой
│   ├── api/           # Flask API routes
│   ├── schemas.py     # Сериализация/валидация
│   └── app.py         # Flask приложение
└── tests/
    ├── unit/          # Unit тесты
    ├── integration/   # Интеграционные тесты
    └── conftest.py    # Фикстуры pytest""",
    [
        "Определите основные слои приложения",
        "Опишите назначение каждой директории",
        "Объясните, почему такая структура хороша для TDD"
    ]
) }}

### Модель данных Task

{{ create_exercise_form(
    "task_model_design",
    "Проектирование модели Task",
    "Создайте модель данных для задачи с необходимыми полями и методами.",
    """from datetime import datetime
from typing import Optional
import uuid

class Task:
    '''Модель задачи для TODO API'''

    def __init__(self, title: str, description: str = "", status: str = "pending"):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.status = status  # pending, in_progress, completed
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update(self, title: Optional[str] = None, description: Optional[str] = None,
               status: Optional[str] = None):
        '''Обновление задачи'''
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        if status is not None:
            self.status = status
        self.updated_at = datetime.now()

    def to_dict(self) -> dict:
        '''Преобразование в словарь для JSON'''
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        '''Создание задачи из словаря'''
        task = cls(
            title=data["title"],
            description=data.get("description", ""),
            status=data.get("status", "pending")
        )
        if "id" in data:
            task.id = data["id"]
        return task""",
    [
        "Добавьте все необходимые поля для задачи",
        "Реализуйте методы update, to_dict, from_dict",
        "Добавьте валидацию данных",
        "Обеспечьте типизацию"
    ]
) }}

## 🎯 Этап 2: Репозиторий данных

### Интерфейс репозитория

{{ create_exercise_form(
    "repository_interface_design",
    "Проектирование интерфейса репозитория",
    "Создайте абстрактный интерфейс для репозитория задач.",
    """from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models import Task

class TaskRepository(ABC):
    '''Абстрактный интерфейс репозитория задач'''

    @abstractmethod
    def save(self, task: Task) -> Task:
        '''Сохранить задачу'''
        pass

    @abstractmethod
    def find_by_id(self, task_id: str) -> Optional[Task]:
        '''Найти задачу по ID'''
        pass

    @abstractmethod
    def find_all(self, status_filter: Optional[str] = None) -> List[Task]:
        '''Найти все задачи с опциональным фильтром по статусу'''
        pass

    @abstractmethod
    def update(self, task_id: str, updates: dict) -> Optional[Task]:
        '''Обновить задачу'''
        pass

    @abstractmethod
    def delete(self, task_id: str) -> bool:
        '''Удалить задачу'''
        pass""",
    [
        "Создайте абстрактный базовый класс",
        "Определите все необходимые методы CRUD",
        "Добавьте типизацию для всех методов",
        "Обеспечьте возможность фильтрации"
    ]
) }}

### Реализация In-Memory репозитория

{{ create_exercise_form(
    "in_memory_repository_implementation",
    "Реализация In-Memory репозитория",
    "Создайте конкретную реализацию репозитория с хранением в памяти.",
    """from typing import List, Optional, Dict
from domain.models import Task
from infrastructure.repositories import TaskRepository

class InMemoryTaskRepository(TaskRepository):
    '''In-Memory реализация репозитория задач'''

    def __init__(self):
        self._tasks: Dict[str, Task] = {}

    def save(self, task: Task) -> Task:
        '''Сохранить задачу'''
        self._tasks[task.id] = task
        return task

    def find_by_id(self, task_id: str) -> Optional[Task]:
        '''Найти задачу по ID'''
        return self._tasks.get(task_id)

    def find_all(self, status_filter: Optional[str] = None) -> List[Task]:
        '''Найти все задачи с опциональным фильтром'''
        tasks = list(self._tasks.values())
        if status_filter:
            tasks = [task for task in tasks if task.status == status_filter]
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    def update(self, task_id: str, updates: dict) -> Optional[Task]:
        '''Обновить задачу'''
        task = self.find_by_id(task_id)
        if not task:
            return None

        task.update(**updates)
        return task

    def delete(self, task_id: str) -> bool:
        '''Удалить задачу'''
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False""",
    [
        "Реализуйте все методы абстрактного класса",
        "Используйте словарь для хранения задач",
        "Добавьте сортировку по дате создания",
        "Обеспечьте корректную обработку ошибок"
    ]
) }}

## 🎯 Этап 3: Сервис бизнес-логики

### Сервис задач

{{ create_exercise_form(
    "task_service_implementation",
    "Реализация сервиса задач",
    "Создайте сервис для бизнес-логики работы с задачами.",
    """from typing import List, Optional, Dict, Any
from domain.models import Task
from infrastructure.repositories import TaskRepository

class TaskService:
    '''Сервис для бизнес-логики задач'''

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    def create_task(self, title: str, description: str = "") -> Dict[str, Any]:
        '''Создать новую задачу'''
        # Валидация
        if not title or not title.strip():
            return {"error": "Title is required", "status_code": 400}

        if len(title) > 100:
            return {"error": "Title too long (max 100 characters)", "status_code": 400}

        # Создание задачи
        task = Task(title.strip(), description.strip())
        saved_task = self.repository.save(task)

        return {"task": saved_task.to_dict(), "status_code": 201}

    def get_task(self, task_id: str) -> Dict[str, Any]:
        '''Получить задачу по ID'''
        task = self.repository.find_by_id(task_id)
        if not task:
            return {"error": "Task not found", "status_code": 404}

        return {"task": task.to_dict(), "status_code": 200}

    def get_all_tasks(self, status: Optional[str] = None) -> Dict[str, Any]:
        '''Получить все задачи'''
        if status and status not in ["pending", "in_progress", "completed"]:
            return {"error": "Invalid status filter", "status_code": 400}

        tasks = self.repository.find_all(status)
        return {"tasks": [task.to_dict() for task in tasks], "status_code": 200}

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        '''Обновить задачу'''
        # Проверяем существование задачи
        existing_task = self.repository.find_by_id(task_id)
        if not existing_task:
            return {"error": "Task not found", "status_code": 404}

        # Валидация обновлений
        if "title" in updates and (not updates["title"] or not updates["title"].strip()):
            return {"error": "Title cannot be empty", "status_code": 400}

        if "status" in updates and updates["status"] not in ["pending", "in_progress", "completed"]:
            return {"error": "Invalid status", "status_code": 400}

        # Обновление
        updated_task = self.repository.update(task_id, updates)
        return {"task": updated_task.to_dict(), "status_code": 200}

    def delete_task(self, task_id: str) -> Dict[str, Any]:
        '''Удалить задачу'''
        # Проверяем существование задачи
        existing_task = self.repository.find_by_id(task_id)
        if not existing_task:
            return {"error": "Task not found", "status_code": 404}

        # Удаление
        success = self.repository.delete(task_id)
        if success:
            return {"message": "Task deleted successfully", "status_code": 200}
        else:
            return {"error": "Failed to delete task", "status_code": 500}""",
    [
        "Добавьте все методы CRUD с бизнес-логикой",
        "Реализуйте валидацию входных данных",
        "Добавьте обработку ошибок",
        "Обеспечьте корректные HTTP статус коды"
    ]
) }}

## 🎯 Этап 4: Flask API Routes

### API Routes

{{ create_exercise_form(
    "flask_api_routes",
    "Реализация Flask API routes",
    "Создайте Flask routes для всех операций CRUD с задачами.",
    """from flask import Flask, request, jsonify, Blueprint
from typing import Optional
from domain.services import TaskService
from infrastructure.repositories import InMemoryTaskRepository

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__)

def create_api_blueprint(repository=None) -> Blueprint:
    '''Фабрика для создания API Blueprint с dependency injection'''

    if repository is None:
        repository = InMemoryTaskRepository()

    service = TaskService(repository)

    @api_bp.route('/tasks', methods=['GET'])
    def get_tasks():
        '''Получить все задачи'''
        status = request.args.get('status')
        result = service.get_all_tasks(status)

        if result["status_code"] == 400:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["tasks"]), 200

    @api_bp.route('/tasks', methods=['POST'])
    def create_task():
        '''Создать новую задачу'''
        data = request.get_json()

        if not data or "title" not in data:
            return jsonify({"error": "Title is required"}), 400

        result = service.create_task(
            title=data["title"],
            description=data.get("description", "")
        )

        if result["status_code"] == 400:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["task"]), 201

    @api_bp.route('/tasks/<task_id>', methods=['GET'])
    def get_task(task_id):
        '''Получить задачу по ID'''
        result = service.get_task(task_id)

        if result["status_code"] == 404:
            return jsonify({"error": result["error"]}), 404

        return jsonify(result["task"]), 200

    @api_bp.route('/tasks/<task_id>', methods=['PUT'])
    def update_task(task_id):
        '''Обновить задачу'''
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        result = service.update_task(task_id, data)

        if result["status_code"] == 404:
            return jsonify({"error": result["error"]}), 404
        elif result["status_code"] == 400:
            return jsonify({"error": result["error"]}), 400

        return jsonify(result["task"]), 200

    @api_bp.route('/tasks/<task_id>', methods=['DELETE'])
    def delete_task(task_id):
        '''Удалить задачу'''
        result = service.delete_task(task_id)

        if result["status_code"] == 404:
            return jsonify({"error": result["error"]}), 404

        return jsonify({"message": result["message"]}), 200

    return api_bp""",
    [
        "Создайте Blueprint для API",
        "Реализуйте все HTTP методы (GET, POST, PUT, DELETE)",
        "Добавьте обработку JSON данных",
        "Обеспечьте корректные HTTP статус коды",
        "Добавьте dependency injection для тестирования"
    ]
) }}

### Flask приложение

{{ create_exercise_form(
    "flask_app_creation",
    "Создание Flask приложения",
    "Создайте основное Flask приложение с настройками для тестирования.",
    """from flask import Flask
from web.api import create_api_blueprint

def create_app(testing=False):
    '''Фабрика для создания Flask приложения'''
    app = Flask(__name__)

    if testing:
        app.config['TESTING'] = True

    # Регистрируем API blueprint
    api_blueprint = create_api_blueprint()
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.route('/')
    def index():
        return {'message': 'TODO API', 'version': '1.0'}

    return app

# Для разработки
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)""",
    [
        "Создайте фабрику приложений",
        "Добавьте настройки для тестирования",
        "Зарегистрируйте API blueprint",
        "Добавьте базовый endpoint для проверки"
    ]
) }}

## 🎯 Этап 5: Тестирование API

### Интеграционные тесты

{{ create_exercise_form(
    "api_integration_tests",
    "Написание интеграционных тестов для API",
    "Создайте интеграционные тесты для проверки работы всего API.",
    """import pytest
import json
from web.app import create_app
from infrastructure.repositories import InMemoryTaskRepository

@pytest.fixture
def app():
    '''Создание тестового приложения'''
    app = create_app(testing=True)
    return app

@pytest.fixture
def client(app):
    '''Тестовый клиент'''
    return app.test_client()

@pytest.fixture
def repository():
    '''Чистый репозиторий для каждого теста'''
    return InMemoryTaskRepository()

def test_create_task_api(client):
    '''Тест создания задачи через API'''
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }

    response = client.post(
        '/api/tasks',
        data=json.dumps(task_data),
        content_type='application/json'
    )

    assert response.status_code == 201
    response_data = json.loads(response.data)

    assert response_data["title"] == "Test Task"
    assert response_data["description"] == "Test Description"
    assert response_data["status"] == "pending"
    assert "id" in response_data

def test_get_task_api(client):
    '''Тест получения задачи по ID'''
    # Сначала создаем задачу
    task_data = {"title": "Test Task"}
    create_response = client.post(
        '/api/tasks',
        data=json.dumps(task_data),
        content_type='application/json'
    )

    task_id = json.loads(create_response.data)["id"]

    # Получаем задачу
    response = client.get(f'/api/tasks/{task_id}')

    assert response.status_code == 200
    response_data = json.loads(response.data)

    assert response_data["id"] == task_id
    assert response_data["title"] == "Test Task"

def test_update_task_api(client):
    '''Тест обновления задачи'''
    # Создаем задачу
    task_data = {"title": "Original Title"}
    create_response = client.post(
        '/api/tasks',
        data=json.dumps(task_data),
        content_type='application/json'
    )

    task_id = json.loads(create_response.data)["id"]

    # Обновляем задачу
    update_data = {
        "title": "Updated Title",
        "status": "completed"
    }

    response = client.put(
        f'/api/tasks/{task_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )

    assert response.status_code == 200
    response_data = json.loads(response.data)

    assert response_data["title"] == "Updated Title"
    assert response_data["status"] == "completed"

def test_delete_task_api(client):
    '''Тест удаления задачи'''
    # Создаем задачу
    task_data = {"title": "Task to Delete"}
    create_response = client.post(
        '/api/tasks',
        data=json.dumps(task_data),
        content_type='application/json'
    )

    task_id = json.loads(create_response.data)["id"]

    # Удаляем задачу
    response = client.delete(f'/api/tasks/{task_id}')

    assert response.status_code == 200

    # Проверяем что задача удалена
    get_response = client.get(f'/api/tasks/{task_id}')
    assert get_response.status_code == 404

def test_get_all_tasks_api(client):
    '''Тест получения всех задач'''
    # Создаем несколько задач
    tasks_data = [
        {"title": "Task 1", "status": "pending"},
        {"title": "Task 2", "status": "completed"},
        {"title": "Task 3", "status": "in_progress"}
    ]

    for task_data in tasks_data:
        client.post(
            '/api/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )

    # Получаем все задачи
    response = client.get('/api/tasks')
    assert response.status_code == 200

    response_data = json.loads(response.data)
    assert len(response_data) == 3

def test_filter_tasks_by_status_api(client):
    '''Тест фильтрации задач по статусу'''
    # Создаем задачи с разными статусами
    tasks_data = [
        {"title": "Pending Task", "status": "pending"},
        {"title": "Completed Task", "status": "completed"},
        {"title": "In Progress Task", "status": "in_progress"}
    ]

    for task_data in tasks_data:
        client.post(
            '/api/tasks',
            data=json.dumps(task_data),
            content_type='application/json'
        )

    # Фильтруем по статусу completed
    response = client.get('/api/tasks?status=completed')
    assert response.status_code == 200

    response_data = json.loads(response.data)
    assert len(response_data) == 1
    assert response_data[0]["title"] == "Completed Task"
    assert response_data[0]["status"] == "completed" """,
    [
        "Создайте тесты для всех CRUD операций",
        "Добавьте тесты для фильтрации",
        "Протестируйте валидацию данных",
        "Проверьте обработку ошибок"
    ]
) }}

## 🎯 Этап 6: Расширенные возможности

### Валидация данных

{{ create_exercise_form(
    "data_validation",
    "Добавление валидации данных",
    "Создайте систему валидации для входных данных API.",
    """import re
from typing import List, Dict, Any, Optional

class ValidationError(Exception):
    '''Исключение для ошибок валидации'''
    pass

class TaskValidator:
    '''Валидатор данных для задач'''

    @staticmethod
    def validate_title(title: str) -> str:
        '''Валидация заголовка задачи'''
        if not title or not isinstance(title, str):
            raise ValidationError("Title is required and must be a string")

        title = title.strip()
        if not title:
            raise ValidationError("Title cannot be empty")

        if len(title) > 100:
            raise ValidationError("Title too long (max 100 characters)")

        return title

    @staticmethod
    def validate_description(description: Optional[str]) -> str:
        '''Валидация описания задачи'''
        if description is None:
            return ""

        if not isinstance(description, str):
            raise ValidationError("Description must be a string")

        if len(description) > 500:
            raise ValidationError("Description too long (max 500 characters)")

        return description.strip()

    @staticmethod
    def validate_status(status: Optional[str]) -> str:
        '''Валидация статуса задачи'''
        valid_statuses = ["pending", "in_progress", "completed"]

        if status is None:
            return "pending"

        if status not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {valid_statuses}")

        return status

    @classmethod
    def validate_task_data(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        '''Валидация полных данных задачи'''
        if not isinstance(data, dict):
            raise ValidationError("Data must be a dictionary")

        validated_data = {}

        # Обязательные поля
        if "title" not in data:
            raise ValidationError("Title is required")

        validated_data["title"] = cls.validate_title(data["title"])

        # Опциональные поля
        validated_data["description"] = cls.validate_description(data.get("description"))
        validated_data["status"] = cls.validate_status(data.get("status"))

        return validated_data""",
    [
        "Создайте класс валидации с методами для каждого поля",
        "Добавьте проверки типов и длин строк",
        "Реализуйте кастомные исключения",
        "Создайте метод комплексной валидации"
    ]
) }}

## 🎯 Этап 7: Обработка ошибок

### Глобальная обработка ошибок

{{ create_exercise_form(
    "error_handling",
    "Реализация обработки ошибок",
    "Создайте систему глобальной обработки ошибок для API.",
    """from flask import Flask, jsonify
from web.api import api_bp
from web.validation import ValidationError

def register_error_handlers(app: Flask):
    '''Регистрация обработчиков ошибок'''

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        '''Обработка ошибок валидации'''
        return jsonify({
            "error": "Validation Error",
            "message": str(error)
        }), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        '''Обработка 404 ошибок'''
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found"
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        '''Обработка ошибок метода'''
        return jsonify({
            "error": "Method Not Allowed",
            "message": "The method is not allowed for this endpoint"
        }), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        '''Обработка внутренних ошибок сервера'''
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500

    @app.errorhandler(Exception)
    def handle_generic_error(error):
        '''Обработка всех остальных исключений'''
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500

# Обновляем создание приложения
def create_app(testing=False):
    '''Фабрика для создания Flask приложения'''
    app = Flask(__name__)

    if testing:
        app.config['TESTING'] = True

    # Регистрируем обработчики ошибок
    register_error_handlers(app)

    # Регистрируем API blueprint
    from web.api import create_api_blueprint
    api_blueprint = create_api_blueprint()
    app.register_blueprint(api_blueprint, url_prefix='/api')

    @app.route('/')
    def index():
        return {'message': 'TODO API', 'version': '1.0'}

    return app""",
    [
        "Создайте функцию для регистрации обработчиков ошибок",
        "Добавьте обработку валидационных ошибок",
        "Добавьте обработку стандартных HTTP ошибок",
        "Обновите фабрику приложения"
    ]
) }}

## 🎉 Ключевые выводы

В этом упражнении вы:

✅ **Освоили TDD в веб-разработке** - от моделей до API
✅ **Создали RESTful API** - все CRUD операции
✅ **Реализовали архитектурные паттерны** - Repository, Service, Dependency Injection
✅ **Добавили валидацию данных** - комплексная проверка входных данных
✅ **Организовали обработку ошибок** - глобальные обработчики исключений
✅ **Написали интеграционные тесты** - полное покрытие API

### 💡 Лучшие практики Flask API с TDD:

1. **Разделение слоев** - Domain/Repository/Service/Web
2. **Dependency Injection** - легкость тестирования
3. **Валидация данных** - на уровне сервиса, не контроллера
4. **Обработка ошибок** - централизованная система
5. **HTTP статус коды** - правильные коды для каждого случая
6. **JSON API** - consistent формат ответов

### 🎯 Следующие шаги:

- **База данных** - замените InMemoryRepository на SQLAlchemy
- **Аутентификация** - добавьте JWT токены
- **Документация** - создайте OpenAPI/Swagger
- **Docker** - контейнеризируйте приложение
- **Мониторинг** - добавьте логирование и метрики
- **E2E тесты** - Selenium или Playwright для UI

---

**[🏠 Вернуться к практическим примерам](../10_web_development_tdd.md)**
