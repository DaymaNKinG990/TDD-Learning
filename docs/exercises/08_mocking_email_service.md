# 🎭 Интерактивное упражнение: Email сервис с Mock объектами

Изучим мокирование на практике, создав email сервис с внешними зависимостями и научившись их изолировать в тестах.

## 📋 Техническое задание

Создадим систему уведомлений, которая:
- Отправляет email через внешний SMTP сервер
- Логирует все операции
- Работает с базой данных пользователей
- Обрабатывает различные типы ошибок

**Цель**: Научиться тестировать код с внешними зависимостями, не затрагивая реальные сервисы.

## 🎯 Этап 1: Понимание проблемы

### Почему нужно мокирование?

{{ create_exercise_form(
    "mocking_problem_analysis",
    "Анализ проблем тестирования без моков",
    "Проанализируйте код ниже и опишите проблемы тестирования этого подхода.",
    """class EmailService:
    def send_email(self, to_email, subject, body):
        # ПРОБЛЕМА: Отправляет реальные email!
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_server.send_message(to_email, subject, body)

        # ПРОБЛЕМА: Записывает в реальную БД!
        db.save_email_log(to_email, subject, datetime.now())

        # ПРОБЛЕМА: Реальное API логирования!
        logger.log_to_external_service(f'Email sent to {to_email}')""",
    [
        "Найдите все внешние зависимости",
        "Опишите риски тестирования этого кода",
        "Предложите решения для каждой проблемы"
    ]
) }}

### 🔄 Решение с Mock объектами

{{ create_exercise_form(
    "mocking_solution_design",
    "Проектирование решения с моками",
    "Напишите тест, который изолирует все внешние зависимости с помощью моков.",
    """def test_email_service_sends_email():
    # Мокируем внешние зависимости
    mock_smtp = Mock()
    mock_db = Mock()
    mock_logger = Mock()

    email_service = EmailService(mock_smtp, mock_db, mock_logger)

    # Выполняем операцию
    email_service.send_notification('test@example.com', 'Hello', 'Test body')

    # Проверяем, что зависимости были вызваны правильно
    mock_smtp.send_email.assert_called_once_with('test@example.com', 'Hello', 'Test body')
    mock_db.save_email_log.assert_called_once()
    mock_logger.log_info.assert_called_once()""",
    [
        "Создайте мок объекты для каждой зависимости",
        "Покажите как передавать моки в конструктор",
        "Напишите assertions для проверки вызовов"
    ]
) }}

## 🏗 Этап 2: Архитектура с Dependency Injection

Создадим правильную архитектуру для тестируемого кода:

### Абстракции для внешних зависимостей

{{ create_exercise_form(
    "dependency_injection_design",
    "Проектирование интерфейсов для DI",
    "Создайте абстрактные интерфейсы для каждой внешней зависимости.",
    """from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional

# Абстракции для внешних зависимостей
class EmailProvider(ABC):
    @abstractmethod
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        pass

class DatabaseRepository(ABC):
    @abstractmethod
    def save_email_log(self, to_email: str, subject: str, timestamp: datetime) -> None:
        pass

    @abstractmethod
    def get_user_preferences(self, email: str) -> Dict:
        pass

class Logger(ABC):
    @abstractmethod
    def log_info(self, message: str) -> None:
        pass

    @abstractmethod
    def log_error(self, message: str) -> None:
        pass""",
    [
        "Создайте абстрактный базовый класс EmailProvider",
        "Создайте абстрактный базовый класс DatabaseRepository",
        "Создайте абстрактный базовый класс Logger",
        "Определите необходимые методы для каждой абстракции"
    ]
) }}

### Реализации зависимостей

{{ create_exercise_form(
    "real_implementations",
    "Создание реальных реализаций",
    "Напишите конкретные реализации для каждой абстракции.",
    """# Реализации (в реальном проекте были бы в отдельных файлах)
class SMTPEmailProvider(EmailProvider):
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        # В реальности здесь был бы настоящий SMTP
        print(f'Отправка email на {to_email}: {subject}')
        return True

class DatabaseEmailRepository(DatabaseRepository):
    def save_email_log(self, to_email: str, subject: str, timestamp: datetime) -> None:
        # В реальности здесь была бы настоящая БД
        print(f'Сохранение в БД: {to_email} - {subject} - {timestamp}')

    def get_user_preferences(self, email: str) -> Dict:
        # Симуляция получения настроек пользователя
        return {'language': 'ru', 'notifications': True}

class FileLogger(Logger):
    def log_info(self, message: str) -> None:
        print(f'INFO: {message}')

    def log_error(self, message: str) -> None:
        print(f'ERROR: {message}')""",
    [
        "Реализуйте SMTPEmailProvider с методом send_email",
        "Реализуйте DatabaseEmailRepository с методами save_email_log и get_user_preferences",
        "Реализуйте FileLogger с методами log_info и log_error",
        "Добавьте логику симуляции реальных операций"
    ]
) }}

## 🎮 Интерактивная реализация: Email сервис

### Основной класс Email сервиса

{{ create_exercise_form(
    "email_service_implementation",
    "Реализация EmailService с DI",
    "Создайте класс EmailService, который использует dependency injection.",
    """from datetime import datetime
from typing import List, Dict, Any

class EmailService:
    def __init__(self, email_provider: EmailProvider,
                 database: DatabaseRepository,
                 logger: Logger):
        self.email_provider = email_provider
        self.database = database
        self.logger = logger

    def send_notification(self, to_email: str, subject: str, body: str) -> bool:
        \"\"\"Отправка уведомления с логированием\"\"\"
        try:
            self.logger.log_info(f'Попытка отправки email на {to_email}')

            # Получаем настройки пользователя
            user_prefs = self.database.get_user_preferences(to_email)

            if not user_prefs.get('notifications', True):
                self.logger.log_info(f'Пользователь {to_email} отключил уведомления')
                return False

            # Отправляем email
            success = self.email_provider.send_email(to_email, subject, body)

            if success:
                # Сохраняем лог в БД
                self.database.save_email_log(to_email, subject, datetime.now())
                self.logger.log_info(f'Email успешно отправлен на {to_email}')
                return True
            else:
                self.logger.log_error(f'Не удалось отправить email на {to_email}')
                return False

        except Exception as e:
            self.logger.log_error(f'Ошибка при отправке email на {to_email}: {str(e)}')
            return False

    def send_bulk_notifications(self, recipients: List[str], subject: str, body: str) -> Dict[str, bool]:
        \"\"\"Массовая рассылка\"\"\"
        results = {}

        for email in recipients:
            results[email] = self.send_notification(email, subject, body)

        successful = sum(1 for success in results.values() if success)
        self.logger.log_info(f'Массовая рассылка завершена. Успешно: {successful}/{len(recipients)}')

        return results""",
    [
        "Добавьте конструктор с dependency injection",
        "Реализуйте метод send_notification с полной логикой",
        "Добавьте метод send_bulk_notifications для массовой рассылки",
        "Обработайте все edge cases и исключения"
    ]
) }}

## 🧪 Интерактивное тестирование с моками

Протестируем сервис с различными Mock сценариями:

### Тестирование успешной отправки

{{ create_exercise_form(
    "mock_test_successful",
    "Тест успешной отправки email",
    "Напишите тест для сценария успешной отправки email с использованием моков.",
    """import pytest
from unittest.mock import Mock

def test_send_notification_success():
    '''Тест успешной отправки уведомления'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # Настраиваем поведение моков
    mock_database.get_user_preferences.return_value = {'notifications': True}
    mock_email_provider.send_email.return_value = True

    # Создаем сервис с моками
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Выполняем операцию
    result = email_service.send_notification('test@example.com', 'Hello', 'Test body')

    # Проверяем результат
    assert result is True

    # Проверяем вызовы моков
    mock_database.get_user_preferences.assert_called_once_with('test@example.com')
    mock_email_provider.send_email.assert_called_once_with('test@example.com', 'Hello', 'Test body')
    mock_database.save_email_log.assert_called_once()
    mock_logger.log_info.assert_called()""",
    [
        "Создайте моки для всех зависимостей",
        "Настройте успешное поведение моков",
        "Выполните операцию отправки",
        "Проверьте корректные вызовы всех моков"
    ]
) }}

### Тестирование отключенных уведомлений

{{ create_exercise_form(
    "mock_test_disabled_notifications",
    "Тест отключенных уведомлений",
    "Напишите тест для сценария, когда пользователь отключил уведомления.",
    """def test_send_notification_disabled():
    '''Тест отправки уведомления с отключенными уведомлениями'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # Пользователь отключил уведомления
    mock_database.get_user_preferences.return_value = {'notifications': False}

    # Создаем сервис с моками
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Выполняем операцию
    result = email_service.send_notification('test@example.com', 'Hello', 'Test body')

    # Проверяем результат
    assert result is False

    # Проверяем, что email НЕ был отправлен
    mock_email_provider.send_email.assert_not_called()
    mock_database.save_email_log.assert_not_called()

    # Проверяем логирование отключения
    mock_logger.log_info.assert_called_with('Пользователь test@example.com отключил уведомления')""",
    [
        "Настройте мок БД для возврата отключенных уведомлений",
        "Проверьте что результат равен False",
        "Убедитесь что email не отправлялся",
        "Проверьте корректное логирование"
    ]
) }}

### Тестирование ошибки отправки

{{ create_exercise_form(
    "mock_test_send_failure",
    "Тест ошибки отправки email",
    "Напишите тест для сценария, когда провайдер email возвращает ошибку.",
    """def test_send_notification_email_failure():
    '''Тест ошибки отправки email'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # Настраиваем успешное получение настроек
    mock_database.get_user_preferences.return_value = {'notifications': True}
    # Но провайдер возвращает ошибку
    mock_email_provider.send_email.return_value = False

    # Создаем сервис с моками
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Выполняем операцию
    result = email_service.send_notification('test@example.com', 'Hello', 'Test body')

    # Проверяем результат
    assert result is False

    # Проверяем что лог НЕ был сохранен
    mock_database.save_email_log.assert_not_called()

    # Проверяем логирование ошибки
    mock_logger.log_error.assert_called_with('Не удалось отправить email на test@example.com')""",
    [
        "Настройте провайдер для возврата False",
        "Проверьте что результат равен False",
        "Убедитесь что лог не сохранился",
        "Проверьте логирование ошибки"
    ]
) }}

### Тестирование исключений

{{ create_exercise_form(
    "mock_test_exceptions",
    "Тест обработки исключений",
    "Напишите тест для сценария, когда возникает исключение в одной из зависимостей.",
    """def test_send_notification_database_error():
    '''Тест ошибки базы данных'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # БД выбрасывает исключение
    mock_database.get_user_preferences.side_effect = Exception('Database connection failed')

    # Создаем сервис с моками
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Выполняем операцию
    result = email_service.send_notification('test@example.com', 'Hello', 'Test body')

    # Проверяем результат
    assert result is False

    # Проверяем что email не отправлялся
    mock_email_provider.send_email.assert_not_called()

    # Проверяем логирование ошибки
    mock_logger.log_error.assert_called_with('Ошибка при отправке email на test@example.com: Database connection failed')""",
    [
        "Настройте мок БД для выбрасывания исключения",
        "Проверьте корректную обработку исключения",
        "Убедитесь что email не отправлялся",
        "Проверьте логирование исключения"
    ]
) }}

## 🎯 Продвинутые техники мокирования

### Side Effects с последовательностью

{{ create_exercise_form(
    "advanced_side_effects",
    "Продвинутые side effects",
    "Напишите тест, демонстрирующий использование side_effect с последовательностью значений.",
    """def test_bulk_send_mixed_results():
    '''Тест массовой рассылки со смешанными результатами'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # Разные пользователи имеют разные настройки
    mock_database.get_user_preferences.side_effect = [
        {'notifications': True},   # Первый пользователь
        {'notifications': False},  # Второй отключил уведомления
        {'notifications': True},   # Третий пользователь
    ]

    # Провайдер возвращает разные результаты
    mock_email_provider.send_email.side_effect = [True, True, False]

    # Создаем сервис с моками
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Выполняем массовую рассылку
    recipients = ['user1@test.com', 'user2@test.com', 'user3@test.com']
    results = email_service.send_bulk_notifications(recipients, 'Bulk message', 'Test body')

    # Проверяем результаты
    assert results['user1@test.com'] is True   # Отправлено успешно
    assert results['user2@test.com'] is False  # Отключены уведомления
    assert results['user3@test.com'] is False  # Ошибка отправки

    # Проверяем статистику
    assert mock_logger.log_info.called
    log_calls = [call for call in mock_logger.log_info.call_args_list
                 if 'Массовая рассылка завершена' in str(call)]
    assert len(log_calls) == 1""",
    [
        "Настройте side_effect для разных пользователей",
        "Настройте side_effect для разных результатов отправки",
        "Проверьте корректность результатов",
        "Проверьте логирование статистики"
    ]
) }}

### Mock с функцией-валидатором

{{ create_exercise_form(
    "mock_with_validator_function",
    "Mock с функцией валидации",
    "Напишите тест с использованием side_effect в виде функции для сложной логики.",
    """def dynamic_email_validator(to_email, subject, body):
    '''Динамическая функция валидации email'''
    if '@invalid.com' in to_email:
        return False
    elif len(subject) > 50:
        raise Exception('Subject too long')
    elif not body.strip():
        raise Exception('Body is empty')
    else:
        return True

def test_email_validation_with_complex_logic():
    '''Тест email валидации со сложной логикой'''
    # Создаем моки
    mock_email_provider = Mock(spec=EmailProvider)
    mock_database = Mock(spec=DatabaseRepository)
    mock_logger = Mock(spec=Logger)

    # Используем функцию для side_effect
    mock_email_provider.send_email.side_effect = dynamic_email_validator

    # Настраиваем БД
    mock_database.get_user_preferences.return_value = {'notifications': True}

    # Создаем сервис
    email_service = EmailService(mock_email_provider, mock_database, mock_logger)

    # Тест различных сценариев
    test_cases = [
        ('valid@test.com', 'Valid subject', 'Valid body', True),
        ('user@invalid.com', 'Subject', 'Body', False),
        ('valid@test.com', 'Very long subject that exceeds the fifty character limit', 'Body', False),
    ]

    for email, subject, body, expected in test_cases:
        if expected:
            # Ожидаем успешный результат
            result = email_service.send_notification(email, subject, body)
            assert result is True
        else:
            # Ожидаем исключение или False
            try:
                result = email_service.send_notification(email, subject, body)
                assert result is False
            except Exception:
                # Исключение тоже приемлемо
                pass""",
    [
        "Создайте функцию dynamic_email_validator",
        "Настройте side_effect с этой функцией",
        "Протестируйте разные сценарии",
        "Проверьте обработку исключений"
    ]
) }}

## 🎉 Ключевые выводы

В этом упражнении вы освоили:

✅ **Dependency Injection** - правильная архитектура для тестируемости
✅ **Mock объекты** - изоляция внешних зависимостей
✅ **side_effect** - симуляция сложного поведения и ошибок
✅ **Assertions на моках** - проверка корректности вызовов
✅ **Архитектурные паттерны** - Interface Segregation, DI Container

### 💡 Лучшие практики мокирования:

1. **Мокируйте только то, что вы не контролируете** - внешние API, БД, файлы
2. **Не мокируйте свой код** - тестируйте реальную логику
3. **Используйте spec** - `Mock(spec=Interface)` для типобезопасности
4. **Проверяйте вызовы** - `assert_called_with()`, `assert_called_once()`
5. **Симулируйте ошибки** - `side_effect` для тестирования обработки исключений

### 🎯 Когда использовать моки:

- 🌐 **Внешние API** и веб-сервисы
- 💾 **Базы данных** и файловые системы
- 📧 **Email, SMS** и другие коммуникации
- ⏰ **Время и дата** (`datetime.now()`)
- 🎲 **Случайные значения** (`random.random()`)
- 💰 **Платежные системы** и банковские API

---

**[🏠 Вернуться к практическим примерам](../08_mocking.md)**
