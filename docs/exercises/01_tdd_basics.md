# 🎯 Интерактивное упражнение: Основы TDD

## 📋 Задание

В этом упражнении вы будете применять основы TDD на практике. Вам предстоит создать простой калькулятор с использованием подхода Test-Driven Development.

### 🎯 Цели упражнения:
- Научиться писать тесты **до** написания кода
- Освоить цикл **Red-Green-Refactor**
- Применить принципы **чистого кода** в тестах
- Понять важность **минимальной реализации**

## 🏗 Шаг 1: Настройка проекта

### 1.1 Создайте структуру проекта
```bash
# Создайте новый проект
uv init calculator-tdd
cd calculator-tdd

# Добавьте необходимые зависимости
uv add pytest pytest-cov

# Создайте структуру директорий
mkdir -p src/calculator tests
touch src/calculator/__init__.py
touch tests/__init__.py
```

### 1.2 Создайте базовый класс Calculator
```python
# src/calculator/calculator.py
class Calculator:
    """Простой калькулятор с базовыми операциями."""

    pass  # Пока пустой класс
```

## 🧪 Шаг 2: Первый тест (RED)

### 2.1 Напишите падающий тест
```python
# tests/test_calculator.py
import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """Тесты для калькулятора."""

    def test_add_positive_numbers(self):
        """Тест сложения двух положительных чисел."""
        calc = Calculator()

        # Когда складываем 2 + 3
        result = calc.add(2, 3)

        # Тогда результат должен быть 5
        assert result == 5

    def test_add_negative_numbers(self):
        """Тест сложения отрицательных чисел."""
        calc = Calculator()

        # Когда складываем -2 + (-3)
        result = calc.add(-2, -3)

        # Тогда результат должен быть -5
        assert result == -5

    def test_add_mixed_numbers(self):
        """Тест сложения положительного и отрицательного числа."""
        calc = Calculator()

        # Когда складываем 5 + (-3)
        result = calc.add(5, -3)

        # Тогда результат должен быть 2
        assert result == 2
```

### 2.2 Запустите тест
```bash
# Запустите тесты - они должны провалиться
uv run pytest tests/test_calculator.py::TestCalculator::test_add_positive_numbers -v
```

**Ожидаемый результат:**
```
AttributeError: 'Calculator' object has no attribute 'add'
```

## 🟢 Шаг 3: Минимальная реализация (GREEN)

### 3.1 Добавьте метод add
```python
# src/calculator/calculator.py
class Calculator:
    """Простой калькулятор с базовыми операциями."""

    def add(self, a: int, b: int) -> int:
        """Складывает два числа.

        Args:
            a: Первое число
            b: Второе число

        Returns:
            Сумма двух чисел
        """
        return a + b
```

### 3.2 Запустите тесты снова
```bash
uv run pytest tests/test_calculator.py -v
```

**Ожидаемый результат:**
```
============================= test session starts ==============================
collected 3 items

tests/test_calculator.py::TestCalculator::test_add_positive_numbers PASSED
tests/test_calculator.py::TestCalculator::test_add_negative_numbers PASSED
tests/test_calculator.py::TestCalculator::test_add_mixed_numbers PASSED

============================== 3 passed in 0.01s ===============================
```

## 🔵 Шаг 4: Рефакторинг

### 4.1 Улучшите код
```python
# src/calculator/calculator.py
class Calculator:
    """Простой калькулятор с базовыми математическими операциями."""

    def add(self, a: float, b: float) -> float:
        """Складывает два числа.

        Args:
            a: Первое число (int или float)
            b: Второе число (int или float)

        Returns:
            Сумма двух чисел

        Examples:
            >>> calc = Calculator()
            >>> calc.add(2, 3)
            5
            >>> calc.add(2.5, 3.5)
            6.0
        """
        return a + b
```

### 4.2 Добавьте больше тестов
```python
# tests/test_calculator.py
import pytest
from calculator.calculator import Calculator


class TestCalculator:
    """Тесты для калькулятора."""

    def test_add_positive_numbers(self):
        """Тест сложения двух положительных чисел."""
        calc = Calculator()
        assert calc.add(2, 3) == 5

    def test_add_negative_numbers(self):
        """Тест сложения отрицательных чисел."""
        calc = Calculator()
        assert calc.add(-2, -3) == -5

    def test_add_mixed_numbers(self):
        """Тест сложения положительного и отрицательного числа."""
        calc = Calculator()
        assert calc.add(5, -3) == 2

    def test_add_with_zero(self):
        """Тест сложения с нулем."""
        calc = Calculator()
        assert calc.add(0, 5) == 5
        assert calc.add(5, 0) == 5

    def test_add_float_numbers(self):
        """Тест сложения чисел с плавающей точкой."""
        calc = Calculator()
        assert calc.add(2.5, 3.5) == 6.0
        assert calc.add(1.1, 2.2) == 3.3

    def test_add_large_numbers(self):
        """Тест сложения больших чисел."""
        calc = Calculator()
        assert calc.add(1000000, 2000000) == 3000000
```

### 4.3 Запустите все тесты
```bash
uv run pytest tests/test_calculator.py -v
```

## 🧪 Шаг 5: Добавление новых функций

### 5.1 Напишите тест для вычитания (RED)
```python
def test_subtract_positive_numbers(self):
    """Тест вычитания двух положительных чисел."""
    calc = Calculator()

    # Когда вычитаем 5 - 3
    result = calc.subtract(5, 3)

    # Тогда результат должен быть 2
    assert result == 2
```

### 5.2 Добавьте минимальную реализацию (GREEN)
```python
# src/calculator/calculator.py
def subtract(self, a: float, b: float) -> float:
    """Вычитает второе число из первого.

    Args:
        a: Уменьшаемое
        b: Вычитаемое

    Returns:
        Разность чисел
    """
    return a - b
```

### 5.3 Добавьте больше тестов для вычитания
```python
def test_subtract_negative_numbers(self):
    """Тест вычитания отрицательных чисел."""
    calc = Calculator()
    assert calc.subtract(-2, -3) == 1

def test_subtract_mixed_numbers(self):
    """Тест вычитания смешанных чисел."""
    calc = Calculator()
    assert calc.subtract(5, -3) == 8

def test_subtract_with_zero(self):
    """Тест вычитания с нулем."""
    calc = Calculator()
    assert calc.subtract(5, 0) == 5
    assert calc.subtract(0, 5) == -5
```

## 📊 Шаг 6: Измерение покрытия кода

### 6.1 Запустите тесты с покрытием
```bash
uv run pytest --cov=src --cov-report=html
```

### 6.2 Откройте отчет о покрытии
```bash
# Откройте файл htmlcov/index.html в браузере
open htmlcov/index.html
```

## 🎯 Дополнительные задания

### Задание 1: Добавьте метод умножения
- Напишите тесты для `multiply(a, b)`
- Реализуйте метод
- Добавьте edge cases (умножение на 0, отрицательные числа)

### Задание 2: Добавьте метод деления
- Напишите тесты для `divide(a, b)`
- Обработайте деление на 0 (ZeroDivisionError)
- Добавьте тесты для проверки исключений

### Задание 3: Добавьте валидацию входных данных
- Добавьте проверки типов
- Обработайте некорректные входные данные
- Напишите тесты для валидации

## 📋 Контрольный список

- [ ] Структура проекта создана
- [ ] Базовый класс Calculator создан
- [ ] Тесты написаны **до** реализации
- [ ] Метод add реализован и протестирован
- [ ] Метод subtract реализован и протестирован
- [ ] Покрытие кода измерено
- [ ] Код отрефакторен
- [ ] Дополнительные методы добавлены

## 💡 Советы

1. **Всегда пишите тест сначала** - это суть TDD
2. **Делайте маленькие шаги** - не пишите много кода сразу
3. **Запускайте тесты часто** - проверяйте прогресс
4. **Рефакторите постепенно** - улучшайте код небольшими изменениями
5. **Покрывайте edge cases** - тестируйте граничные случаи

### 🔴 Интерактивная практика: Ваш первый TDD тест

{{ create_exercise_form(
    "first_tdd_test",
    "Создание первого TDD теста",
    "Напишите простой тест для функции сложения, следуя принципам TDD. Тест должен сначала падать, а затем проходить.",
    """import pytest

def test_add_two_positive_numbers():
    '''Тест сложения двух положительных чисел'''
    # Arrange - подготовка данных
    a = 5
    b = 3
    expected = 8

    # Act - выполнение действия
    result = add(a, b)

    # Assert - проверка результата
    assert result == expected

def test_add_with_zero():
    '''Тест сложения с нулем'''
    # Arrange
    a = 10
    b = 0
    expected = 10

    # Act
    result = add(a, b)

    # Assert
    assert result == expected""",
    [
        "Создайте функцию test_add_two_positive_numbers",
        "Добавьте тест test_add_with_zero",
        "Используйте структуру AAA (Arrange-Act-Assert)",
        "Добавьте понятные комментарии и докстринги"
    ]
) }}

### 🟢 Интерактивная практика: Минимальная реализация

{{ create_exercise_form(
    "minimal_implementation",
    "Создание минимальной реализации",
    "Напишите самую простую функцию add(), которая заставит ваши тесты проходить.",
    """def add(a, b):
    '''Складывает два числа и возвращает результат'''
    return a + b""",
    [
        "Создайте функцию add с двумя параметрами",
        "Верните сумму параметров",
        "Убедитесь что оба теста проходят"
    ]
) }}

### 🔵 Интерактивная практика: Рефакторинг

{{ create_exercise_form(
    "refactoring_practice",
    "Улучшение кода через рефакторинг",
    "Добавьте типизацию, документацию и проверки для функции add, сохраняя прохождение всех тестов.",
    """def add(a: float, b: float) -> float:
    '''Складывает два числа и возвращает результат.

    Args:
        a: Первое число (int или float)
        b: Второе число (int или float)

    Returns:
        Сумма двух чисел

    Examples:
        >>> add(2, 3)
        5
        >>> add(2.5, 3.5)
        6.0
    '''
    return a + b""",
    [
        "Добавьте типизацию параметров и возвращаемого значения",
        "Добавьте подробную документацию с примерами",
        "Убедитесь что все тесты по-прежнему проходят"
    ]
) }}

## 🔍 Вопросы для размышления

1. Почему важно писать тесты до кода?
2. Что такое "минимальная реализация"?
3. Почему мы не должны добавлять лишний код?
4. Как измерять качество тестов?
5. Что такое "технический долг" и как его избежать?

---

**[🏠 Вернуться к основам TDD](../01_tdd_basics.md)**

## 🎊 Поздравляем!

Вы успешно применили TDD на практике! Теперь вы знаете:

- ✅ Как писать тесты **до** кода
- ✅ Как следовать циклу **Red-Green-Refactor**
- ✅ Как создавать **чистый и понятный** код
- ✅ Как измерять **покрытие тестами**

*Помните: TDD — это навык, который развивается с практикой. Продолжайте писать тесты!*
