# 🎯 Интерактивное упражнение: Валидатор строк с TDD

Создадим валидатор для различных типов строк, применяя принципы TDD и треугольного тестирования.

## 📋 Задание

**Реализуйте класс `StringValidator`** с методами для валидации:
- **Email адресов** - проверка формата email
- **Паролей** - минимум 8 символов, должен содержать буквы и цифры
- **Телефонных номеров** - российский формат (+7XXXXXXXXXX или 8XXXXXXXXXX)

## 🎯 Цели упражнения:
- Применить **Red-Green-Refactor** цикл
- Освоить **триангуляцию** (triangulation)
- Научиться писать **информативные имена тестов**
- Понять **постепенное развитие** функциональности

## 📚 Что вы узнаете:
- Как писать минимальные тесты
- Как развивать код через добавление тестов
- Как рефакторить код без изменения поведения
- Как тестировать edge cases

## 🔴 Этап 1: RED - Email валидация

Начнем с простейшего случая - валидации email адресов.

**🔴 RED фаза**: Пишем падающий тест

{{ create_exercise_form(
    "email_validator_red_1",
    "Создание первого RED теста для email валидации",
    "Напишите тест, который будет падать, потому что класс StringValidator еще не существует.",
    """import pytest

def test_valid_email_returns_true():
    '''Валидный email должен проходить проверку'''
    validator = StringValidator()  # Класса еще нет!
    result = validator.is_valid_email('test@example.com')
    assert result is True""",
    [
        "Тест должен создавать экземпляр StringValidator",
        "Тест должен вызывать метод is_valid_email с валидным email",
        "Тест должен проверять, что результат равен True"
    ]
) }}

❌ **Ожидаемая ошибка**: `NameError: name 'StringValidator' is not defined`

Этот тест определяет, что мы хотим от нашего кода!

## 🟢 Этап 2: GREEN - Минимальная реализация

Теперь создадим минимальный код для прохождения теста.

**🟢 GREEN фаза**: Минимальный код для прохождения

{{ create_exercise_form(
    "email_validator_green_1",
    "Создание минимальной GREEN реализации",
    "Напишите минимальный код, который заставит тест проходить. Пока не важно, насколько он правильный - главное, чтобы тест прошел!",
    """class StringValidator:
    def is_valid_email(self, email):
        return True  # Хардкод! Но тест проходит!""",
    [
        "Создать класс StringValidator",
        "Добавить метод is_valid_email",
        "Метод должен возвращать True (пока хардкод)"
    ]
) }}

✅ **Тест проходит!** Но это очевидно неправильно... Мы сделали только первый шаг в правильном направлении.

## 🔺 Этап 3: Triangulation - Развиваем функциональность

**🔴 RED фаза**: Добавляем тест для невалидного email

{{ create_exercise_form(
    "email_validator_triangulation_1",
    "Добавление теста для невалидного email",
    "Напишите тест, который проверит, что невалидный email возвращает False. Этот тест сломает наш хардкод!",
    """def test_invalid_email_returns_false():
    '''Невалидный email должен НЕ проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_email('invalid_email')
    assert result is False  # Теперь хардкод True не подойдет!""",
    [
        "Тест должен проверять невалидный email без @",
        "Тест должен ожидать False как результат",
        "Тест должен ломать наш текущий хардкод"
    ]
) }}

❌ **Этот тест будет падать** с нашим хардкодом, который всегда возвращает True!

**🔄 REFACTOR**: Реализуем настоящую логику валидации

{{ create_exercise_form(
    "email_validator_refactor_1",
    "Реализация правильной email валидации",
    "Замените хардкод на настоящую логику валидации email с использованием регулярных выражений.",
    """import re

class StringValidator:
    def is_valid_email(self, email):
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))""",
    [
        "Добавить проверку типа и пустой строки",
        "Использовать регулярное выражение для валидации",
        "Вернуть результат re.match()"
    ]
) }}

✅ **Теперь оба теста проходят!** Мы применили triangulation - добавили тест, который заставил нас написать настоящую реализацию.

## 🎮 Интерактивная практика: Продолжаем развитие

Теперь, когда у нас есть базовая email валидация, давайте расширим функциональность и применим те же принципы TDD к остальным методам.

### 📝 Задание: Валидация паролей

**🔴 RED фаза**: Пишем тест для валидации паролей

{{ create_exercise_form(
    "password_validator_red_1",
    "Создание теста для валидации паролей",
    "Напишите тест для метода is_valid_password, который проверяет пароль на минимальную длину 8 символов и наличие букв и цифр.",
    """def test_password_too_short_returns_false():
    '''Пароль короче 8 символов должен быть невалиден'''
    validator = StringValidator()
    result = validator.is_valid_password('short')
    assert result is False

def test_password_without_letters_returns_false():
    '''Пароль без букв должен быть невалиден'''
    validator = StringValidator()
    result = validator.is_valid_password('12345678')
    assert result is False

def test_password_without_digits_returns_false():
    '''Пароль без цифр должен быть невалиден'''
    validator = StringValidator()
    result = validator.is_valid_password('password')
    assert result is False

def test_valid_password_returns_true():
    '''Валидный пароль должен проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_password('password123')
    assert result is True""",
    [
        "Тест должен проверять минимальную длину",
        "Тест должен проверять наличие букв",
        "Тест должен проверять наличие цифр",
        "Тест должен проверять валидный пароль"
    ]
) }}

### 🔧 GREEN реализация для паролей

{{ create_exercise_form(
    "password_validator_green_1",
    "Реализация валидации паролей",
    "Добавьте метод is_valid_password в класс StringValidator с правильной логикой валидации.",
    """import re

class StringValidator:
    def is_valid_email(self, email):
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def is_valid_password(self, password):
        # Реализуйте через TDD!
        if not password or len(password) < 8:
            return False
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_letter and has_digit""",
    [
        "Проверить длину пароля (>= 8 символов)",
        "Проверить наличие букв (используйте isalpha())",
        "Проверить наличие цифр (используйте isdigit())",
        "Вернуть True только если все условия выполнены"
    ]
) }}

### 📞 Задание: Валидация телефонных номеров

**🔴 RED фаза**: Пишем тест для валидации телефонов

{{ create_exercise_form(
    "phone_validator_red_1",
    "Создание теста для валидации телефонных номеров",
    "Напишите тест для метода is_valid_phone, который проверяет российский формат номеров (+7XXXXXXXXXX или 8XXXXXXXXXX).",
    """def test_valid_russian_phone_with_plus_returns_true():
    '''Валидный российский номер с +7 должен проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_phone('+71234567890')
    assert result is True

def test_valid_russian_phone_with_8_returns_true():
    '''Валидный российский номер с 8 должен проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_phone('81234567890')
    assert result is True

def test_invalid_phone_returns_false():
    '''Невалидный номер должен не проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_phone('1234567890')
    assert result is False

def test_empty_phone_returns_false():
    '''Пустой номер должен не проходить проверку'''
    validator = StringValidator()
    result = validator.is_valid_phone("")
    assert result is False""",
    [
        "Тест должен проверять формат +7XXXXXXXXXX",
        "Тест должен проверять формат 8XXXXXXXXXX",
        "Тест должен проверять невалидные форматы",
        "Тест должен проверять пустую строку"
    ]
) }}

### 🔧 GREEN реализация для телефонов

{{ create_exercise_form(
    "phone_validator_green_1",
    "Реализация валидации телефонных номеров",
    "Добавьте метод is_valid_phone в класс StringValidator с правильной логикой валидации российских номеров.",
    """import re

class StringValidator:
    def is_valid_email(self, email):
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def is_valid_password(self, password):
        if not password or len(password) < 8:
            return False
        has_letter = any(c.isalpha() for c in password)
        has_digit = any(c.isdigit() for c in password)
        return has_letter and has_digit

    def is_valid_phone(self, phone):
        # Реализуйте через TDD!
        if not phone:
            return False
        # Российский формат: +7XXXXXXXXXX или 8XXXXXXXXXX
        pattern = r'^(\+7|8)\d{10}$'
        return bool(re.match(pattern, phone))""",
    [
        "Проверить что номер не пустой",
        "Использовать регулярное выражение для российских форматов",
        "Поддержать форматы +7XXXXXXXXXX и 8XXXXXXXXXX",
        "Вернуть результат re.match()"
    ]
) }}

## 🎯 Резюме упражнения

В этом упражнении вы:

✅ **Освоили цикл Red-Green-Refactor** - писали тесты до кода
✅ **Применили triangulation** - развивали код через добавление тестов
✅ **Научились писать информативные имена** для тестов
✅ **Реализовали валидацию email, паролей и телефонов** через TDD
✅ **Поняли постепенное развитие** функциональности

### 🔄 Следующие шаги:
- Добавьте больше edge cases для каждого типа валидации
- Создайте интеграционные тесты, которые используют все три метода
- Добавьте валидацию других типов данных (URL, даты, etc.)
- Создайте веб-API, которое использует ваш StringValidator

---

**[🏠 Вернуться к практическим примерам](../07_practical_examples.md)**
