# Метрики покрытия кода в TDD

## 🎯 Введение

Покрытие кода тестами — это ключевая метрика качества в TDD, показывающая, какая часть вашего кода исполняется при запуске тестов. Правильное понимание и использование метрик покрытия помогает выявить неисследованные участки кода и повысить качество тестового набора.

## 🧠 Что такое покрытие кода?

### Определение

**Покрытие кода (Code Coverage)** — метрика, показывающая процент исходного кода программы, который был выполнен во время запуска тестов.

### Важные принципы

- **Покрытие НЕ гарантирует отсутствие ошибок**, но указывает на потенциальные проблемы
- **Высокое покрытие** не всегда означает качественные тесты
- **Покрытие** — это инструмент для выявления пробелов, а не самоцель
- **100% покрытие** редко достижимо и экономически нецелесообразно

## 📊 Виды покрытия кода

### 1. Statement Coverage (Покрытие инструкций)

Процент выполненных строк кода.

**Формула:** `Statement Coverage = (Выполненные строки / Общее количество строк) × 100%`

```python
def calculate_grade(score):
    if score >= 90:        # Строка 1
        return "A"         # Строка 2
    elif score >= 80:      # Строка 3
        return "B"         # Строка 4
    else:                  # Строка 5
        return "C"         # Строка 6

# Тест покрывает только часть строк
def test_grade_a():
    assert calculate_grade(95) == "A"
    # Покрыты строки: 1, 2
    # Statement Coverage = 2/6 = 33.3%

# Полное покрытие инструкций
def test_all_statements():
    assert calculate_grade(95) == "A"  # Строки 1, 2
    assert calculate_grade(85) == "B"  # Строки 3, 4
    assert calculate_grade(75) == "C"  # Строки 5, 6
    # Statement Coverage = 6/6 = 100%
```

### 2. Branch Coverage (Покрытие ветвей)

Процент выполненных ветвей условных операторов.

**Формула:** `Branch Coverage = (Выполненные ветви / Общее количество ветвей) × 100%`

```python
def is_valid_age(age):
    if age >= 0 and age <= 150:  # 2 условия = 4 ветви
        return True
    return False

# Неполное покрытие ветвей
def test_valid_age():
    assert is_valid_age(25) == True
    # Покрыта только одна ветвь: age >= 0 (True) and age <= 150 (True)
    # Branch Coverage = 1/4 = 25%

# Полное покрытие ветвей
def test_all_branches():
    assert is_valid_age(25) == True    # age >= 0 (True) and age <= 150 (True)
    assert is_valid_age(-5) == False   # age >= 0 (False)
    assert is_valid_age(200) == False  # age >= 0 (True) and age <= 150 (False)
    # Branch Coverage = 4/4 = 100%
```

### 3. Function Coverage (Покрытие функций)

Процент вызванных функций или методов.

**Формула:** `Function Coverage = (Вызванные функции / Общее количество функций) × 100%`

```python
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
    
    def divide(self, a, b):
        return a / b

def test_partial_functions():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.subtract(5, 2) == 3
    # Function Coverage = 2/4 = 50%

def test_all_functions():
    calc = Calculator()
    assert calc.add(2, 3) == 5
    assert calc.subtract(5, 2) == 3
    assert calc.multiply(3, 4) == 12
    assert calc.divide(10, 2) == 5
    # Function Coverage = 4/4 = 100%
```

### 4. Path Coverage (Покрытие путей)

Процент выполненных уникальных путей через код.

```python
def complex_logic(a, b, c):
    result = 0
    
    if a > 0:           # Условие 1
        result += 10
    
    if b > 0:           # Условие 2
        result += 20
    
    if c > 0:           # Условие 3
        result += 30
    
    return result

# Возможные пути: 2^3 = 8 комбинаций
def test_all_paths():
    assert complex_logic(1, 1, 1) == 60   # Path: T,T,T
    assert complex_logic(1, 1, 0) == 30   # Path: T,T,F
    assert complex_logic(1, 0, 1) == 40   # Path: T,F,T
    assert complex_logic(1, 0, 0) == 10   # Path: T,F,F
    assert complex_logic(0, 1, 1) == 50   # Path: F,T,T
    assert complex_logic(0, 1, 0) == 20   # Path: F,T,F
    assert complex_logic(0, 0, 1) == 30   # Path: F,F,T
    assert complex_logic(0, 0, 0) == 0    # Path: F,F,F
    # Path Coverage = 8/8 = 100%
```

### 5. Condition Coverage (Покрытие условий)

Процент протестированных булевых подвыражений.

```python
def validate_user(email, age):
    if email and "@" in email and age >= 18:  # 3 условия
        return True
    return False

def test_condition_coverage():
    # Тестируем каждое условие отдельно
    assert validate_user("", 20) == False         # email = False
    assert validate_user("test", 20) == False     # "@" in email = False  
    assert validate_user("test@test.com", 16) == False  # age >= 18 = False
    assert validate_user("test@test.com", 20) == True   # Все True
    # Condition Coverage = 100%
```

### 6. Multiple Condition Coverage (MC/DC)

Все комбинации условий в сложных булевых выражениях.

```python
def access_granted(is_admin, is_owner, has_permission):
    # Сложное условие
    return is_admin or (is_owner and has_permission)

def test_multiple_condition_coverage():
    # Тестируем все значимые комбинации
    assert access_granted(True, False, False) == True   # admin = True
    assert access_granted(False, True, True) == True    # owner AND permission
    assert access_granted(False, True, False) == False  # owner but no permission
    assert access_granted(False, False, True) == False  # permission but not owner
    assert access_granted(False, False, False) == False # nothing
    # MC/DC Coverage учитывает влияние каждого условия на результат
```

## 🛠 Инструменты измерения покрытия в Python

### 1. Coverage.py - основной инструмент

#### Установка и базовое использование

```bash
# Установка
uv add coverage pytest-cov

# Запуск с coverage
uv run coverage run -m pytest
uv run coverage report
uv run coverage html

# Или через pytest-cov
uv run pytest --cov=myapp --cov-report=html --cov-report=term
```

#### Конфигурация .coveragerc

```ini
# .coveragerc
[run]
source = src/
omit = 
    */tests/*
    */venv/*
    */virtualenv/*
    */__pycache__/*
    */site-packages/*
    */migrations/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

show_missing = True
skip_covered = False

[html]
directory = htmlcov
```

#### Практический пример

```python
# src/calculator.py
class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def divide(self, a, b):
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self):  # pragma: no cover
        """Debug method, excluded from coverage."""
        return self.history

# tests/test_calculator.py
import pytest
from src.calculator import Calculator

class TestCalculator:
    def test_add(self):
        calc = Calculator()
        result = calc.add(2, 3)
        assert result == 5
        assert "2 + 3 = 5" in calc.history
    
    def test_divide_success(self):
        calc = Calculator()
        result = calc.divide(10, 2)
        assert result == 5.0
    
    def test_divide_by_zero(self):
        calc = Calculator()
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            calc.divide(10, 0)
```

#### Запуск и анализ

```bash
# Запуск тестов с покрытием
uv run pytest --cov=src --cov-report=html --cov-report=term-missing

# Результат в терминале:
# Name                    Stmts   Miss  Cover   Missing
# ----------------------------------------------------- 
# src/calculator.py          12      1    92%   25
# ----------------------------------------------------- 
# TOTAL                      12      1    92%

# HTML отчет создается в htmlcov/index.html
```

### 2. Продвинутые конфигурации

#### Покрытие ветвей (Branch Coverage)

```bash
# Включение измерения покрытия ветвей
uv run pytest --cov=src --cov-branch --cov-report=html

# В .coveragerc
[run]
branch = True
```

#### Разные форматы отчетов

```bash
# XML отчет (для CI/CD)
uv run pytest --cov=src --cov-report=xml

# JSON отчет
uv run pytest --cov=src --cov-report=json

# Отчет в терминале с деталями
uv run pytest --cov=src --cov-report=term-missing
```

### 3. Интеграция с CI/CD

#### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
    
    - name: Set up Python
      run: uv python install 3.12
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests with coverage
      run: |
        uv run pytest --cov=src --cov-report=xml --cov-report=term
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
        token: ${{ secrets.CODECOV_TOKEN }}
```

## 📏 Интерпретация метрик покрытия

### Разумные границы покрытия

```python
# pyproject.toml конфигурация для минимального покрытия
[tool.coverage.report]
fail_under = 80  # Минимальное покрытие 80%

[tool.coverage.run]
branch = true

# Разные уровни покрытия для разных компонентов
[tool.coverage.paths]
source = ["src", "*/site-packages/mypackage"]
```

#### Рекомендуемые уровни

- **70-80%**: Минимальный уровень для большинства проектов
- **80-90%**: Хороший уровень для критически важного кода
- **90-95%**: Высокий уровень для системных компонентов
- **95-100%**: Для критически важных алгоритмов (финансы, медицина)

### Анализ качества покрытия

```python
# Плохое покрытие - высокий процент, но тест ничего не проверяет
def bad_test():
    calculator = Calculator()
    calculator.add(2, 3)  # Выполняется код, но нет проверок!
    # Coverage = 100%, но тест бесполезен

# Хорошее покрытие - проверяются результаты и поведение
def good_test():
    calculator = Calculator()
    result = calculator.add(2, 3)
    
    assert result == 5  # Проверяем результат
    assert len(calculator.history) == 1  # Проверяем побочные эффекты
    assert "2 + 3 = 5" in calculator.history[0]  # Проверяем содержимое
```

## 🎯 Практические стратегии

### 1. Выявление непокрытых участков

```python
def complex_function(data, mode="normal"):
    if not data:
        return []  # Строка не покрыта тестами!
    
    result = []
    for item in data:
        if mode == "strict":
            if not item.is_valid():  # Ветвь не покрыта!
                raise ValueError(f"Invalid item: {item}")
        
        processed = process_item(item)
        result.append(processed)
    
    return result

def test_uncover_missing_paths():
    """Тест для покрытия пропущенных путей."""
    
    # Покрываем пустые данные
    assert complex_function([]) == []
    
    # Покрываем strict режим с невалидными данными
    invalid_item = Mock()
    invalid_item.is_valid.return_value = False
    
    with pytest.raises(ValueError, match="Invalid item"):
        complex_function([invalid_item], mode="strict")
```

### 2. Mutation Testing - проверка качества тестов

```bash
# Установка mutmut для mutation testing
uv add mutmut

# Запуск mutation testing
uv run mutmut run

# Просмотр результатов
uv run mutmut results
uv run mutmut show
```

```python
# Пример: mutation testing выявляет слабые тесты
def calculate_discount(price, percent):
    if percent > 100:  # Mutmut изменит на >=, ==, <, etc.
        return 0
    return price * (1 - percent / 100)

# Слабый тест - не поймает мутацию > на >=
def weak_test():
    assert calculate_discount(100, 50) == 50

# Сильный тест - поймает мутации
def strong_test():
    assert calculate_discount(100, 50) == 50
    assert calculate_discount(100, 100) == 0   # Граничный случай
    assert calculate_discount(100, 101) == 0   # За границей
    assert calculate_discount(100, 99) > 0     # Перед границей
```

### 3. Дифференциальное покрытие

```bash
# Покрытие только для изменившихся файлов (в CI)
uv run pytest --cov=src --cov-report=xml
coverage xml --compare-branch=main  # Сравнение с main веткой
```

### 4. Исключение кода из покрытия

```python
def debug_function():  # pragma: no cover
    """Отладочная функция, исключенная из покрытия."""
    print("Debug information")

def production_function():
    try:
        return risky_operation()
    except Exception:  # pragma: no cover
        # Обработка ошибок исключена из покрытия
        logger.critical("Critical error occurred")
        raise

class ConfigurationError(Exception):
    def __str__(self):  # pragma: no cover
        # __str__ методы часто исключают
        return f"Configuration error: {self.args[0]}"
```

## ⚠️ Проблемы и ограничения покрытия

### 1. Ложное чувство безопасности

```python
# 100% покрытие, но тест не проверяет корректность
def misleading_coverage():
    def divide(a, b):
        return a / b  # Может упасть при b=0
    
    def test_divide():
        result = divide(10, 2)  # Покрытие 100%, но не тестирует b=0
        # Нет assert! Тест ничего не проверяет
    
    # Правильный тест
    def proper_test():
        assert divide(10, 2) == 5
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)
```

### 2. Непокрытый код может быть мертвым

```python
def outdated_function():
    # Старая функция, которая больше не используется
    return "legacy code"  # Показывает в покрытии как непокрытый

# Решение: удалить мертвый код
# Инструменты: vulture, unimport
```

### 3. Покрытие не гарантирует отсутствие багов

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)  # Баг: нет проверки на пустой список

def test_average():
    assert calculate_average([1, 2, 3]) == 2  # 100% покрытие
    # Но не тестирует пустой список - calculate_average([]) упадет!

def comprehensive_test():
    assert calculate_average([1, 2, 3]) == 2
    assert calculate_average([5]) == 5
    
    # Тестируем граничные случаи
    with pytest.raises(ZeroDivisionError):
        calculate_average([])  # Выявляем баг!
```

## 📊 Мониторинг покрытия в команде

### 1. Настройка minimum coverage

```python
# pyproject.toml
[tool.coverage.report]
fail_under = 85
show_missing = true
skip_covered = false

# Падение CI при низком покрытии
[tool.coverage.run]
branch = true
source = ["src"]
```

### 2. Отчеты для code review

```bash
# Генерация diff coverage для PR
uv run coverage xml
diff-cover coverage.xml --compare-branch=main --fail-under=80
```

### 3. Badges и дашборды

```markdown
<!-- README.md -->
[![Coverage Status](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

## 🎯 Продвинутые техники

### 1. Покрытие интеграционных тестов

```python
# Измерение покрытия для разных типов тестов
def test_unit_with_coverage():
    """Unit тест с собственным покрытием."""
    # pytest --cov=src --cov-config=.coveragerc-unit
    pass

def test_integration_with_coverage():
    """Integration тест с покрытием."""
    # pytest --cov=src --cov-config=.coveragerc-integration  
    pass
```

### 2. Conditional coverage

```python
import sys

def platform_specific_function():
    if sys.platform == "win32":  # pragma: no cover
        return "Windows implementation"
    else:
        return "Unix implementation"

# Покрытие будет различаться на разных платформах
```

### 3. Асинхронный код и покрытие

```python
import asyncio
import pytest

async def async_function():
    await asyncio.sleep(0.1)
    return "async result"

@pytest.mark.asyncio
async def test_async_coverage():
    """Тест покрытия асинхронного кода."""
    result = await async_function()
    assert result == "async result"

# Запуск: pytest --cov=src --cov-branch test_async.py
```

## 📈 Метрики команды

### Трекинг покрытия во времени

```python
# coverage-history.py - скрипт для отслеживания изменений
import json
import subprocess
from datetime import datetime

def track_coverage():
    # Запускаем тесты и получаем покрытие
    result = subprocess.run([
        "uv", "run", "pytest", "--cov=src", "--cov-report=json"
    ], capture_output=True, text=True)
    
    with open("coverage.json") as f:
        coverage_data = json.load(f)
    
    # Сохраняем исторические данные
    history = {
        "date": datetime.now().isoformat(),
        "coverage_percent": coverage_data["totals"]["percent_covered"],
        "lines_total": coverage_data["totals"]["num_statements"],
        "lines_covered": coverage_data["totals"]["covered_lines"]
    }
    
    with open("coverage_history.json", "a") as f:
        json.dump(history, f)
        f.write("\n")

if __name__ == "__main__":
    track_coverage()
```

## 🏆 Лучшие практики

### ✅ Рекомендации

1. **Стремитесь к 80-90% покрытию** для большинства проектов
2. **Измеряйте branch coverage**, не только statement
3. **Используйте mutation testing** для проверки качества тестов
4. **Исключайте нерелевантный код** (debug, __repr__, etc.)
5. **Настройте fail_under** в CI для поддержания уровня
6. **Анализируйте непокрытые участки** регулярно
7. **Не гонитесь за 100%** - фокусируйтесь на качестве тестов

### ❌ Что избегать

1. **Не делайте покрытие самоцелью**
2. **Не игнорируйте качество ради процентов**
3. **Не исключайте важный код без обоснования**
4. **Не полагайтесь только на покрытие** - используйте другие метрики
5. **Не забывайте про boundary и error cases**

## 🔮 Следующие шаги

В следующей главе мы изучим **стратегии работы с Legacy Code** — как применять TDD к существующему коду без тестов.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="code-coverage-quiz">
<script type="application/json">
{
  "title": "Метрики покрытия кода",
  "description": "Проверьте знание различных типов покрытия и их применения",
  "icon": "📊",
  "questions": [
    {
      "question": "Какие типы покрытия кода существуют? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "Line Coverage - покрытие строк кода", "correct": true},
        {"text": "Branch Coverage - покрытие ветвей условий", "correct": true},
        {"text": "Function Coverage - покрытие функций", "correct": true},
        {"text": "Condition Coverage - покрытие условий", "correct": true},
        {"text": "Class Coverage - покрытие классов", "correct": false}
      ],
      "explanation": "Основные типы: Line (строки), Branch (ветви if/else), Function (вызовы функций), Condition (булевы выражения). Class Coverage не является стандартным типом.",
      "points": 2
    },
    {
      "question": "Какой минимальный процент покрытия рекомендуется для production кода?",
      "type": "single",
      "options": [
        {"text": "60-70%", "correct": false},
        {"text": "80-90%", "correct": true},
        {"text": "95-100%", "correct": false},
        {"text": "50-60%", "correct": false}
      ],
      "explanation": "Рекомендуемый минимум 80-90%. Меньше 80% - недостаточно, 95-100% часто нереалистично и может включать тривиальный код.",
      "points": 1
    },
    {
      "question": "Что показывает Mutation Testing?",
      "type": "single",
      "options": [
        {"text": "Процент покрытых строк кода", "correct": false},
        {"text": "Качество тестов через внесение изменений в код", "correct": true},
        {"text": "Скорость выполнения тестов", "correct": false},
        {"text": "Количество тестовых случаев", "correct": false}
      ],
      "explanation": "Mutation Testing вносит небольшие изменения (мутации) в код и проверяет, обнаруживают ли тесты эти изменения, показывая реальное качество тестов.",
      "points": 1
    },
    {
      "question": "Какие проблемы есть у метрики покрытия кода?",
      "type": "multiple",
      "options": [
        {"text": "Высокое покрытие не гарантирует отсутствие багов", "correct": true},
        {"text": "Покрытие не проверяет качество assertions", "correct": true},
        {"text": "Покрытие может включать мертвый код", "correct": true},
        {"text": "Не покрывает граничные случаи автоматически", "correct": true},
        {"text": "Замедляет выполнение тестов", "correct": false}
      ],
      "explanation": "Основные проблемы: не гарантирует отсутствие багов, не проверяет качество assertions, включает мертвый код, не покрывает edge cases. Замедление не является концептуальной проблемой.",
      "points": 2
    },
    {
      "question": "Как правильно настроить coverage.py для исключения файлов?",
      "type": "single",
      "options": [
        {"text": "Использовать .coveragerc с [run] omit", "correct": true},
        {"text": "Добавить # pragma: no cover ко всем строкам", "correct": false},
        {"text": "Настроить исключения в pytest.ini", "correct": false},
        {"text": "Использовать --ignore флаг", "correct": false}
      ],
      "explanation": "Правильный способ - создать .coveragerc файл с секцией [run] и параметром omit для указания исключаемых файлов и паттернов.",
      "points": 1
    },
    {
      "question": "Что означает 'Branch Coverage'?",
      "type": "single",
      "options": [
        {"text": "Покрытие всех веток git репозитория", "correct": false},
        {"text": "Проверка всех путей выполнения в условных конструкциях", "correct": true},
        {"text": "Покрытие всех функций в модуле", "correct": false},
        {"text": "Тестирование исключительных ситуаций", "correct": false}
      ],
      "explanation": "Branch Coverage проверяет, что все возможные пути выполнения в условных конструкциях (if/else, try/except) были протестированы.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Настройка окружения](02_environment_setup.md)** - настройка инструментов покрытия
- **[Pytest фреймворк](06_pytest.md)** - использование pytest-cov
- **[CI/CD и автоматизация](14_ci_cd_automation.md)** - метрики в CI/CD
- **[Тестирование обработки ошибок](15_error_handling_tdd.md)** - покрытие обработки ошибок
- **[Стратегии работы с Legacy Code](17_legacy_code_strategies.md)** - покрытие legacy кода
- **[Инструменты и фреймворки](13_tools_frameworks.md)** - инструменты для метрик

**Следующая глава:** [Стратегии работы с Legacy Code](17_legacy_code_strategies.md)

*📊 Помните: покрытие — это компас, а не пункт назначения!*
