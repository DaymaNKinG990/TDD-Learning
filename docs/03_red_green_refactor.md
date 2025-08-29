# Цикл Red-Green-Refactor: Сердце TDD

## 🎯 Введение

Цикл Red-Green-Refactor — это **основа TDD**. Этот простой трехэтапный процесс кажется элементарным, но его правильное применение требует дисциплины и понимания. В этой главе мы детально разберем каждую фазу на практических примерах.

## 🔄 Обзор цикла

```
🔴 RED → 🟢 GREEN → 🔵 REFACTOR → 🔴 RED → ...
```

### Временные рамки
- **Один цикл:** 2-10 минут
- **RED фаза:** 30 секунд - 2 минуты
- **GREEN фаза:** 1-5 минут  
- **REFACTOR фаза:** 1-3 минуты

### Ключевые принципы
1. **Никогда не пропускайте фазы**
2. **Делайте минимальные шаги**
3. **Запускайте тесты после каждого изменения**
4. **Коммитьте после каждого GREEN**

## 🔴 RED Фаза: Неудачный тест

### Цели RED фазы:
- ✅ Определить **что** должен делать код
- ✅ Создать **спецификацию** в виде теста
- ✅ Убедиться, что тест **действительно падает**
- ✅ Получить **понятное сообщение** об ошибке

### Правила RED фазы:

#### 1. Пишите минимальный тест
```python
# ❌ Слишком много сразу:
def test_user_full_functionality():
    user = User("John", "john@example.com", 25)
    user.change_email("new@example.com")
    user.add_friend("Jane")
    assert user.name == "John"
    assert user.email == "new@example.com"  
    assert len(user.friends) == 1

# ✅ Один аспект за раз:
def test_user_has_name():
    user = User("John")
    assert user.name == "John"
```

#### 2. Убедитесь, что тест падает
```python
def test_add_numbers():
    result = add(2, 3)  # Функции еще нет!
    assert result == 5

# Запуск: pytest test_calculator.py
# NameError: name 'add' is not defined ✅ Тест падает правильно
```

#### 3. Проверьте сообщение об ошибке
```python
def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)  # Функции нет!
        
# Сначала получим NameError, а не ZeroDivisionError
# Это показывает, что нужно создать функцию
```

### Практический пример RED: Банковский счет

**Требование:** Создать класс банковского счета с базовой функциональностью.

#### Тест 1: Создание счета
```python
# test_account.py
def test_new_account_has_zero_balance():
    """Новый счет должен иметь нулевой баланс."""
    account = Account()  # Класса пока нет!
    assert account.balance == 0
```

**Запуск теста:**
```bash
$ uv run pytest test_account.py::test_new_account_has_zero_balance -v

FAILED test_account.py::test_new_account_has_zero_balance
NameError: name 'Account' is not defined
```

✅ **Тест падает с понятной ошибкой — переходим к GREEN!**

## 🟢 GREEN Фаза: Работающий код

### Цели GREEN фазы:
- ✅ Сделать тест **зеленым** любой ценой
- ✅ Написать **минимальный** код
- ✅ **Игнорировать** будущие требования
- ✅ **Не беспокоиться** о красоте кода

### Правила GREEN фазы:

#### 1. Минимальная реализация
```python
# account.py
class Account:
    def __init__(self):
        self.balance = 0  # Просто возвращаем то, что нужно тесту!
```

**Запуск теста:**
```bash
$ uv run pytest test_account.py::test_new_account_has_zero_balance -v

PASSED test_account.py::test_new_account_has_zero_balance ✅
```

#### 2. Хардкод допустим!
```python
# Если тест проверяет add(2, 3) == 5
def add(a, b):
    return 5  # Хардкод проходит тест!

# Только после добавления второго теста нужна общая логика
def test_add_different_numbers():
    assert add(1, 1) == 2  # Теперь хардкод не поможет
```

#### 3. Fake it 'til you make it
```python
# Стратегия "подделки" для сложной логики
class UserValidator:
    def is_valid_email(self, email):
        # Начинаем с простого хардкода
        if email == "test@example.com":
            return True
        return False

# После добавления новых тестов - развиваем логику
```

### Практический пример GREEN: Банковский счет

#### Тест 2: Пополнение счета
```python
def test_deposit_money():
    """Можно пополнить счет."""
    account = Account()
    account.deposit(100)
    assert account.balance == 100
```

**Минимальная реализация:**
```python
class Account:
    def __init__(self):
        self.balance = 0
        
    def deposit(self, amount):
        self.balance = 100  # Хардкод для прохождения теста!
```

#### Тест 3: Разные суммы пополнения  
```python
def test_deposit_different_amount():
    """Можно пополнить на разную сумму."""
    account = Account()
    account.deposit(50)
    assert account.balance == 50
```

**Теперь нужна настоящая логика:**
```python
class Account:
    def __init__(self):
        self.balance = 0
        
    def deposit(self, amount):
        self.balance += amount  # Теперь хардкод не поможет
```

### Стратегии GREEN фазы

#### Стратегия 1: Fake It (Подделка)
```python
# Возвращаем константу
def calculate_tax(income):
    return 1000  # Хардкод

# Постепенно обобщаем
def calculate_tax(income):
    if income <= 50000:
        return income * 0.1
    return 1000  # Частичный хардкод
```

#### Стратегия 2: Use Obvious Implementation
```python
# Если реализация очевидна, пишем сразу
def is_even(number):
    return number % 2 == 0  # Очевидная реализация
```

#### Стратегия 3: Triangulation (Триангуляция)
```python
# Добавляем тесты пока не станет ясна общая закономерность
def test_fibonacci_0():
    assert fibonacci(0) == 0

def test_fibonacci_1():  
    assert fibonacci(1) == 1

def test_fibonacci_2():
    assert fibonacci(2) == 1

# Теперь паттерн ясен - можно писать общую реализацию
```

## 🔵 REFACTOR Фаза: Улучшение кода

### Цели REFACTOR фазы:
- ✅ **Устранить дублирование** кода
- ✅ **Улучшить читаемость** 
- ✅ **Применить паттерны** проектирования
- ✅ **Сохранить зеленые** тесты

### Правила REFACTOR фазы:

#### 1. Тесты всегда зеленые
```python
# После каждого изменения запускайте тесты!
def refactor_step():
    # 1. Изменяем код
    extract_method()
    
    # 2. Запускаем тесты  
    run_tests()  # Должны быть зеленые!
    
    # 3. Продолжаем или откатываемся
```

#### 2. Маленькие шаги
```python
# ❌ Большой рефакторинг:
def calculate_total_price(items):
    # Переписали всю функцию сразу - рискованно!
    
# ✅ Поэтапный рефакторинг:
def calculate_total_price(items):
    # Шаг 1: Извлекли метод
    subtotal = calculate_subtotal(items)
    # Запустили тесты ✅
    
    # Шаг 2: Добавили налог
    tax = calculate_tax(subtotal)  
    # Запустили тесты ✅
    
    return subtotal + tax
```

### Виды рефакторинга

#### 1. Извлечение метода (Extract Method)
```python
# До рефакторинга:
class Account:
    def transfer(self, amount, target_account):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        if target_account is None:
            raise ValueError("Target account required")
            
        self.balance -= amount
        target_account.balance += amount

# После рефакторинга:
class Account:
    def transfer(self, amount, target_account):
        self._validate_transfer(amount, target_account)
        self._execute_transfer(amount, target_account)
    
    def _validate_transfer(self, amount, target_account):
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds") 
        if target_account is None:
            raise ValueError("Target account required")
    
    def _execute_transfer(self, amount, target_account):
        self.balance -= amount
        target_account.balance += amount
```

#### 2. Извлечение класса (Extract Class)
```python
# До рефакторинга:
class User:
    def __init__(self, name, street, city, postal_code):
        self.name = name
        self.street = street
        self.city = city  
        self.postal_code = postal_code
    
    def get_full_address(self):
        return f"{self.street}, {self.city} {self.postal_code}"

# После рефакторинга:
class Address:
    def __init__(self, street, city, postal_code):
        self.street = street
        self.city = city
        self.postal_code = postal_code
    
    def __str__(self):
        return f"{self.street}, {self.city} {self.postal_code}"

class User:
    def __init__(self, name, address):
        self.name = name
        self.address = address
    
    def get_full_address(self):
        return str(self.address)
```

#### 3. Замена условий полиморфизмом
```python
# До рефакторинга:
def calculate_area(shape_type, **kwargs):
    if shape_type == "rectangle":
        return kwargs["width"] * kwargs["height"]
    elif shape_type == "circle":
        return 3.14159 * kwargs["radius"] ** 2
    elif shape_type == "triangle":
        return 0.5 * kwargs["base"] * kwargs["height"]

# После рефакторинга:
class Shape:
    def area(self):
        raise NotImplementedError

class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def area(self):
        return self.width * self.height

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return 3.14159 * self.radius ** 2
```

### Практический пример REFACTOR: Банковский счет

#### Текущий код после GREEN:
```python
class Account:
    def __init__(self):
        self.balance = 0
        
    def deposit(self, amount):
        self.balance += amount
        
    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
```

#### Рефакторинг 1: Добавляем валидацию
```python
class Account:
    def __init__(self):
        self.balance = 0
        
    def deposit(self, amount):
        self._validate_positive_amount(amount)
        self.balance += amount
        
    def withdraw(self, amount):
        self._validate_positive_amount(amount)
        if amount > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount
    
    def _validate_positive_amount(self, amount):
        if amount <= 0:
            raise ValueError("Amount must be positive")
```

#### Рефакторинг 2: Улучшаем типизацию
```python
from decimal import Decimal
from typing import Union

Number = Union[int, float, Decimal]

class Account:
    def __init__(self, initial_balance: Number = 0):
        self._balance = Decimal(str(initial_balance))
        
    @property
    def balance(self) -> Decimal:
        return self._balance
        
    def deposit(self, amount: Number) -> None:
        """Deposit money to account."""
        amount_decimal = self._validate_amount(amount)
        self._balance += amount_decimal
        
    def withdraw(self, amount: Number) -> None:
        """Withdraw money from account."""
        amount_decimal = self._validate_amount(amount)
        if amount_decimal > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount_decimal
    
    def _validate_amount(self, amount: Number) -> Decimal:
        """Валидирует сумму и возвращает Decimal."""
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        return amount_decimal
```

## 🎯 Полный цикл: Практический пример

Создадим систему управления задачами с помощью TDD:

### Цикл 1: Создание задачи

#### 🔴 RED
```python
# test_todo.py  
def test_create_task_with_title():
    """Можно создать задачу с заголовком."""
    task = Task("Buy milk")  # Класса пока нет!
    assert task.title == "Buy milk"
```

#### 🟢 GREEN
```python
# todo.py
class Task:
    def __init__(self, title):
        self.title = title
```

#### 🔵 REFACTOR
```python
# Добавляем типизацию
class Task:
    def __init__(self, title: str) -> None:
        self.title = title
```

### Цикл 2: Статус задачи

#### 🔴 RED
```python
def test_new_task_is_not_completed():
    """Новая задача не завершена."""
    task = Task("Buy milk")
    assert task.is_completed == False
```

#### 🟢 GREEN
```python
class Task:
    def __init__(self, title: str) -> None:
        self.title = title
        self.is_completed = False  # Минимальная реализация
```

### Цикл 3: Завершение задачи

#### 🔴 RED
```python
def test_mark_task_as_completed():
    """Можно пометить задачу как завершенную."""
    task = Task("Buy milk")
    task.complete()  # Метода пока нет!
    assert task.is_completed == True
```

#### 🟢 GREEN
```python
class Task:
    def __init__(self, title: str) -> None:
        self.title = title
        self.is_completed = False
    
    def complete(self) -> None:
        self.is_completed = True  # Минимальная реализация
```

#### 🔵 REFACTOR
```python
class Task:
    def __init__(self, title: str) -> None:
        self._title = title
        self._completed = False
    
    @property 
    def title(self) -> str:
        return self._title
    
    @property
    def is_completed(self) -> bool:
        return self._completed
    
    def complete(self) -> None:
        """Mark task as completed."""
        self._completed = True
    
    def __repr__(self) -> str:
        status = "✓" if self._completed else "○"
        return f"{status} {self._title}"
```

## ⚠️ Типичные ошибки в цикле

### 1. Пропуск RED фазы
```python
# ❌ Сразу пишем код без теста
def add(a, b):
    return a + b

# ✅ Сначала тест
def test_add():
    assert add(2, 3) == 5  # Падает - функции нет
```

### 2. Слишком большие шаги в GREEN
```python
# ❌ Слишком много сразу
class User:
    def __init__(self, name, email, age, address):
        self.name = name
        self.email = email  
        self.age = age
        self.address = address
        self.validate()  # Много логики сразу
    
# ✅ По одному полю за раз
class User:
    def __init__(self, name):
        self.name = name  # Только то, что нужно тесту
```

### 3. Игнорирование REFACTOR
```python
# ❌ Код работает, но ужасен
def process_order(customer_name, items, discount_type, payment_method):
    total = 0
    for item in items:
        total += item["price"] * item["quantity"]
    if discount_type == "percentage":
        total = total * (1 - discount_type / 100)
    elif discount_type == "fixed":
        total = total - discount_type
    # ... 50 строк кода
    
# ✅ Рефакторинг обязателен
class OrderProcessor:
    def process(self, order: Order) -> OrderResult:
        subtotal = self._calculate_subtotal(order.items)
        total = self._apply_discount(subtotal, order.discount)
        return self._create_result(total, order.payment_method)
```

## 🏆 Мастерство TDD

### Признаки опытного TDD практика:

1. **Циклы длятся 2-5 минут**
2. **Тесты падают по правильным причинам**  
3. **Код минимален в GREEN фазе**
4. **Рефакторинг происходит постоянно**
5. **Коммиты частые и осмысленные**

### Ритм TDD:
```
🔴 RED: "Что должен делать код?"
🟢 GREEN: "Как заставить его работать?"  
🔵 REFACTOR: "Как сделать его лучше?"
```

## 🎯 Следующие шаги

В следующей главе мы углубимся в основы тестирования Python и изучим паттерны написания качественных тестов.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="red-green-refactor-quiz">
<script type="application/json">
{
  "title": "Цикл Red-Green-Refactor",
  "description": "Проверьте понимание основного цикла разработки в TDD",
  "icon": "🔄",
  "questions": [
    {
      "question": "Что означает каждая фаза в цикле TDD?",
      "type": "multiple",
      "options": [
        {"text": "🔴 RED: Написать падающий тест", "correct": true},
        {"text": "🟢 GREEN: Написать минимальный код для прохождения теста", "correct": true},
        {"text": "🔵 REFACTOR: Улучшить код без изменения функциональности", "correct": true},
        {"text": "🔴 RED: Исправить ошибки в коде", "correct": false},
        {"text": "🟢 GREEN: Добавить новую функциональность", "correct": false}
      ],
      "explanation": "RED - написание падающего теста, GREEN - минимальный код для прохождения, REFACTOR - улучшение кода при сохранении функциональности.",
      "points": 2
    },
    {
      "question": "Сколько времени должен занимать один полный цикл TDD у опытного разработчика?",
      "type": "single",
      "options": [
        {"text": "30 секунд - 1 минута", "correct": false},
        {"text": "2-5 минут", "correct": true},
        {"text": "15-20 минут", "correct": false},
        {"text": "1-2 часа", "correct": false}
      ],
      "explanation": "Опытные TDD практики выполняют полный цикл Red-Green-Refactor за 2-5 минут, что обеспечивает быстрый фидбек и минимальные риски.",
      "points": 1
    },
    {
      "question": "Какая ошибка допущена в этом коде для GREEN фазы?",
      "type": "single", 
      "code": "class User:\n    def __init__(self, name, email, age, phone, address):\n        self.name = name\n        self.email = email\n        self.age = age\n        self.phone = phone\n        self.address = address\n        self.validate_all_fields()",
      "options": [
        {"text": "Слишком много полей добавлено сразу", "correct": true},
        {"text": "Нет проверки типов", "correct": false},
        {"text": "Отсутствует документация", "correct": false},
        {"text": "Неправильные имена переменных", "correct": false}
      ],
      "explanation": "В GREEN фазе нужно писать минимальный код, который проходит тест. Добавление множества полей и валидации сразу нарушает принцип минимальности.",
      "points": 1
    },
    {
      "question": "Когда нужно выполнять рефакторинг в TDD?",
      "type": "single",
      "options": [
        {"text": "В конце проекта", "correct": false},
        {"text": "Только когда код перестает работать", "correct": false},
        {"text": "После каждого успешного прохождения тестов в GREEN фазе", "correct": true},
        {"text": "Раз в неделю", "correct": false}
      ],
      "explanation": "Рефакторинг выполняется постоянно - после каждого успешного GREEN этапа, пока тесты проходят. Это предотвращает накопление технического долга.",
      "points": 1
    },
    {
      "question": "Что такое 'triangulation' в контексте TDD циклов?",
      "type": "single",
      "options": [
        {"text": "Техника написания трех тестов сразу", "correct": false},
        {"text": "Постепенное обобщение реализации через добавление тестов", "correct": true},
        {"text": "Архитектурный паттерн", "correct": false},
        {"text": "Способ организации файлов тестов", "correct": false}
      ],
      "explanation": "Triangulation - это когда мы постепенно обобщаем код, добавляя новые тесты. Например: сначала return 5, потом return a + b когда появляется второй тест.",
      "points": 1
    },
    {
      "question": "Какой правильный ритм мышления в TDD цикле?",
      "type": "single",
      "options": [
        {"text": "🔴 'Как написать код?' → 🟢 'Что тестировать?' → 🔵 'Где ошибка?'", "correct": false},
        {"text": "🔴 'Что должен делать код?' → 🟢 'Как заставить его работать?' → 🔵 'Как сделать его лучше?'", "correct": true},
        {"text": "🔴 'Где баг?' → 🟢 'Как исправить?' → 🔵 'Что добавить?'", "correct": false},
        {"text": "🔴 'Что протестировать?' → 🟢 'Что реализовать?' → 🔵 'Что удалить?'", "correct": false}
      ],
      "explanation": "Правильный ритм TDD: RED (что должен делать код?), GREEN (как заставить работать?), REFACTOR (как сделать лучше?).",
      "points": 1
    }
  ]
}
</script>
</div>

## 🎯 Интерактивное упражнение: Создание калькулятора с TDD

Пришло время применить цикл Red-Green-Refactor на практике! Создадим простой калькулятор, строго следуя TDD принципам.

### 📋 Задание

Реализуйте класс `Calculator` с методами для основных арифметических операций, используя строгий TDD подход.

**Требования:**
- Сложение двух чисел
- Вычитание двух чисел  
- Умножение двух чисел
- Деление двух чисел (с обработкой деления на ноль)

### 🔴 Этап 1: RED - Первый тест

Начнем с самого простого теста для сложения:

**🔴 RED фаза**: Пишем падающий тест

{{ create_exercise_form(
    "red_test_1",
    "Создание первого RED теста",
    "Напишите тест, который будет падать, потому что класс Calculator еще не существует.",
    """import pytest

def test_calculator_can_add_two_numbers():
    '''Калькулятор может сложить два числа'''
    calc = Calculator()  # Класса еще нет!
    result = calc.add(2, 3)
    assert result == 5""",
    [
        "Тест должен создавать экземпляр Calculator",
        "Тест должен вызывать метод add с параметрами 2 и 3",
        "Тест должен проверять, что результат равен 5"
    ]
) }}

❌ **Ожидаемая ошибка**: `NameError: name 'Calculator' is not defined`

Этот тест определяет, что мы хотим от нашего кода!

### 🟢 Этап 2: GREEN - Минимальная реализация

Теперь создадим минимальный код для прохождения теста:

**🟢 GREEN фаза**: Минимальный код для прохождения

{{ create_exercise_form(
    "green_implementation_1",
    "Создание минимальной GREEN реализации",
    "Напишите минимальный код, который заставит тест проходить. Пока не важно, насколько он правильный - главное, чтобы тест прошел!",
    """class Calculator:
    def add(self, a, b):
        return 5  # Хардкод! Но тест проходит!""",
    [
        "Создать класс Calculator",
        "Добавить метод add",
        "Метод должен возвращать 5 (пока хардкод)",
        "Тест должен проходить"
    ]
) }}

✅ **Тест проходит!**

Да, код возвращает константу, но это нормально в GREEN фазе!

### 🔵 Этап 3: REFACTOR - Добавляем второй тест (Triangulation)

Для устранения хардкода добавим второй тест:

**🔺 Triangulation**: Второй тест ломает хардкод

{{ create_exercise_form(
    "triangulation_test",
    "Добавление второго теста для triangulation",
    "Напишите второй тест с другими числами, чтобы сломать хардкод и заставить написать настоящую реализацию.",
    """def test_calculator_add_different_numbers():
    '''Второй тест для разных чисел'''
    calc = Calculator()
    result = calc.add(5, 7)
    assert result == 12  # Теперь хардкод 5 не подойдет!""",
    [
        "Создать второй тест с числами 5 и 7",
        "Ожидать результат 12",
        "Этот тест должен сломать предыдущий хардкод"
    ]
) }}

**🔄 REFACTOR**: Обобщаем реализацию

{{ create_exercise_form(
    "refactor_implementation",
    "Рефакторинг реализации",
    "Теперь напишите настоящую реализацию, которая работает со всеми тестами, а не только с хардкодом.",
    """class Calculator:
    def add(self, a, b):
        return a + b  # Теперь настоящая логика!""",
    [
        "Заменить хардкод на настоящую логику",
        "Оба теста должны проходить",
        "Код должен быть обобщенным"
    ]
) }}

✅ **Оба теста проходят!**

### 🎮 Интерактивная практика

Теперь ваша очередь! Используйте цикл RED-GREEN-REFACTOR для реализации остальных операций:

```python {marimo}
# Интерактивная зона для практики

# Класс для тестирования
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b  # Реализуйте через TDD!
    
    def multiply(self, a, b):
        return a * b  # Реализуйте через TDD!
    
    def divide(self, a, b):
        if b == 0:
            raise ValueError("Division by zero!")
        return a / b  # Реализуйте через TDD!

# Тестовая зона
calc = Calculator()

# Интерактивные элементы для тестирования
operation = mo.ui.dropdown(
    options=["add", "subtract", "multiply", "divide"],
    value="add",
    label="Выберите операцию:"
)

num1 = mo.ui.number(value=10, label="Первое число:")
num2 = mo.ui.number(value=5, label="Второе число:")

mo.vstack([operation, num1, num2])
```

```python {marimo}
# Выполнение операции и отображение результата
global calc, operation, num1, num2
try:
    if operation.value == "add":
        result = calc.add(num1.value, num2.value)
    elif operation.value == "subtract":
        result = calc.subtract(num1.value, num2.value)
    elif operation.value == "multiply":
        result = calc.multiply(num1.value, num2.value)
    elif operation.value == "divide":
        result = calc.divide(num1.value, num2.value)
    
    mo.md(f"""
    ### 🧮 Результат
    
    **Операция**: {operation.value}  
    **Числа**: {num1.value} и {num2.value}  
    **Результат**: {result}
    
    ✅ Операция выполнена успешно!
    """)
    
except Exception as e:
    mo.md(f"""
    ### ⚠️ Ошибка
    
    **Операция**: {operation.value}  
    **Числа**: {num1.value} и {num2.value}  
    **Ошибка**: {str(e)}
    
    ❌ Проверьте входные данные!
    """)
```

### 🎯 Упражнение для самостоятельной работы

**Задача**: Реализуйте метод `power(base, exponent)` для возведения в степень, строго следуя TDD:

1. **🔴 RED**: Напишите тест для `calc.power(2, 3) == 8`
2. **🟢 GREEN**: Реализуйте минимальный код (можете начать с хардкода)
3. **🔺 Triangulation**: Добавьте второй тест для других чисел
4. **🔵 REFACTOR**: Обобщите реализацию

```python {marimo}
# Место для вашего решения
your_test = mo.ui.text_area(
    placeholder="Напишите здесь ваш тест для power()...",
    label="Ваш тест:",
    rows=5
)

your_implementation = mo.ui.text_area(
    placeholder="Напишите здесь реализацию power()...",
    label="Ваша реализация:",
    rows=5
)

mo.vstack([your_test, your_implementation])
```

```python {marimo}
# Проверка решения
global your_test, your_implementation
if your_test.value and your_implementation.value:
    mo.md(f"""
    ### 📝 Ваше решение
    
    **Тест:**
    
    {your_test.value}
    
    **Реализация:**
    
    {your_implementation.value}
    
    💡 **Совет**: Убедитесь, что тест сначала падает, затем проходит!
    """)
else:
    mo.md("✏️ Напишите ваш тест и реализацию выше...")
```

### 🎉 Ключевые выводы

После выполнения упражнения вы поймете:

✅ **Цикл TDD** работает на практике  
✅ **RED фаза** четко определяет требования  
✅ **GREEN фаза** фокусируется только на прохождении теста  
✅ **REFACTOR фаза** улучшает код без изменения поведения  
✅ **Triangulation** помогает избавиться от хардкода

## 🚀 Дополнительная практика

### 📝 Валидатор строк

Готовы к более сложному заданию? Попробуйте создать валидатор для email, паролей и телефонов:

**[🎯 Интерактивное упражнение: Валидатор строк с TDD](exercises/03_string_validator.md)**

В этом упражнении вы:
- Примените TDD к работе с регулярными выражениями
- Освоите негативное тестирование  
- Поработаете с валидацией реальных данных
- Изучите triangulation на практике

---

**Следующая глава:** [Основы тестирования в Python](04_python_testing_basics.md)

*🔄 Цикл освоен — пора к более сложным примерам!*
