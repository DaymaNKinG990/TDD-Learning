# Настройка окружения для TDD в Python

## 🎯 Цели главы

В этой главе мы настроим полноценное окружение для разработки через тестирование в Python. Вы узнаете:

- Как настроить Python и виртуальные окружения
- Какие инструменты тестирования выбрать
- Как конфигурировать IDE для эффективной работы с TDD
- Как настроить автоматизацию тестирования

## 🐍 Установка Python

### Проверка версии Python
```bash
python --version  # Должно быть Python 3.12+
python3 --version # На некоторых системах
```

### Рекомендуемые версии:
- **Минимум:** Python 3.12
- **Рекомендовано:** Python 3.12+
- **Новейшая стабильная:** Python 3.13+

### Установка Python (если нужно)

#### Windows:
1. Скачайте с [python.org](https://python.org)
2. Установите с опцией "Add to PATH"
3. Проверьте установку: `python --version`

#### macOS:
```bash
# Через Homebrew (рекомендовано)
brew install python

# Или скачайте с python.org
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 🏗 Управление зависимостями с uv

Согласно правилам проекта, используем `uv` для управления зависимостями:

### Установка uv
```bash
# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Создание проекта
```bash
# Создание нового проекта с uv
uv init tdd-project
cd tdd-project
```

### Основные зависимости для TDD
```bash
# Добавление основных инструментов тестирования
uv add pytest
uv add pytest-cov        # Покрытие кода
uv add pytest-mock       # Мокирование
uv add pytest-xdist      # Параллельные тесты
uv add pytest-benchmark  # Тесты производительности

# Дополнительные инструменты
uv add mypy              # Статическая типизация
uv add ruff              # Линтер + форматтер + сортировка импортов (замена black/isort/flake8)
```

### Структура проекта с uv
```
tdd-project/
├── pyproject.toml       # Конфигурация проекта
├── README.md
├── src/
│   └── tdd_project/
│       ├── __init__.py
│       └── main.py
└── tests/
    ├── __init__.py
    └── test_main.py
```

## 🧪 Выбор фреймворка тестирования

### pytest vs unittest

| Критерий | pytest | unittest |
|----------|---------|----------|
| **Синтаксис** | Простой, Pythonic | Verbose, Java-style |
| **Assertions** | `assert x == y` | `self.assertEqual(x, y)` |
| **Fixtures** | Гибкие декораторы | setUp/tearDown методы |
| **Плагины** | Богатая экосистема | Ограниченные возможности |
| **Параметризация** | Встроенная | Требует дополнительного кода |
| **Совместимость** | Запускает unittest тесты | Не запускает pytest тесты |

### Рекомендация: pytest
**Для TDD лучше использовать pytest** благодаря его простоте и мощности.

## ⚙️ Конфигурация pytest

### Создание pytest.ini
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_functions = test_*
python_classes = Test*

# Опции по умолчанию
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

# Маркеры для организации тестов
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    smoke: Smoke tests
```

### Альтернативно: pyproject.toml (рекомендовано для uv)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_functions = ["test_*"]
python_classes = ["Test*"]

addopts = [
    "--verbose",
    "--tb=short",
    "--strict-markers",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing",
    "--cov-fail-under=80"
]

markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "slow: Slow tests",
    "smoke: Smoke tests"
]
```

## 🔧 Конфигурация инструментов качества кода

### Ruff (линтер + форматтер)
```toml
# pyproject.toml
[tool.ruff]
line-length = 88
target-version = "py38"

[tool.ruff.lint]
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "UP",  # pyupgrade
]
ignore = ["E501"]  # line too long (handled by formatter)

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
```

### mypy (статическая типизация)
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 🔄 Настройка автоматизации

### pre-commit хуки
```bash
# Установка pre-commit
uv add pre-commit --dev

# Создание .pre-commit-config.yaml
```

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      # Линтер
      - id: ruff
        args: [--fix]
      # Форматтер
      - id: ruff-format

  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: uv run pytest
        language: system
        pass_filenames: false
        always_run: true
```

### Активация pre-commit
```bash
uv run pre-commit install
```

## 💻 Настройка IDE

### VS Code
Установите расширения:
- **Python** - основная поддержка Python
- **Python Test Explorer** - интеграция с pytest
- **Coverage Gutters** - показ покрытия кода
- **Python Docstring Generator** - автогенерация докстрингов

#### settings.json для VS Code:
```json
{
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "python.testing.autoTestDiscoverOnSaveEnabled": true,
    "python.linting.enabled": true,
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    },
    "editor.formatOnSave": true
}
```

### PyCharm
1. **File → Settings → Python Integrated Tools**
2. Выберите pytest как тестирующий фреймворк
3. Настройте автозапуск тестов при изменениях
4. Включите покрытие кода в настройках

## 📁 Структура проекта для TDD

### Рекомендуемая структура:
```
my_project/
├── pyproject.toml           # Конфигурация проекта
├── pytest.ini              # Конфигурация pytest (альтернатива)
├── .pre-commit-config.yaml  # Хуки pre-commit
├── .gitignore               # Игнорируемые файлы
├── README.md                # Документация проекта
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── calculator.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── services/
│           ├── __init__.py
│           └── user_service.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Общие фикстуры
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_calculator.py
│   │   └── models/
│   │       └── test_user.py
│   └── integration/
│       ├── __init__.py
│       └── test_user_service.py
└── docs/                    # Документация (опционально)
```

## 🚀 Первый тест

Создадим простой пример для проверки настройки:

### src/my_project/calculator.py
```python
"""Simple calculator module."""

def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b
```

### tests/unit/test_calculator.py
```python
"""Tests for calculator module."""

from my_project.calculator import add


def test_add_positive_numbers():
    """Test addition of positive numbers."""
    result = add(2, 3)
    assert result == 5


def test_add_negative_numbers():
    """Test addition of negative numbers."""
    result = add(-1, -2)
    assert result == -3


def test_add_zero():
    """Test addition with zero."""
    result = add(5, 0)
    assert result == 5
```

### Запуск тестов
```bash
# Запуск всех тестов
uv run pytest

# Запуск с покрытием
uv run pytest --cov

# Запуск только unit тестов
uv run pytest tests/unit/

# Запуск в watch режиме (требует pytest-watch)
uv add pytest-watch
uv run ptw
```

## 🔍 Отладка и профилирование

### Отладка с pdb
```python
def test_complex_logic():
    data = prepare_complex_data()
    
    import pdb; pdb.set_trace()  # Точка останова
    
    result = process_data(data)
    assert result is not None
```

### Профилирование тестов
```bash
# Время выполнения тестов
uv run pytest --durations=10

# Медленные тесты
uv run pytest -m "not slow"
```

## 📊 Мониторинг качества

### Покрытие кода
```bash
# HTML отчет
uv run pytest --cov-report=html
# Откройте htmlcov/index.html в браузере

# Проверка покрытия
uv run pytest --cov-fail-under=90
```

### Continuous Integration
Пример GitHub Actions:

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Install uv
      uses: astral-sh/setup-uv@v1
      
    - name: Set up Python ${{ python_version_matrix }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ python_version_matrix }}
      
    - name: Install dependencies
      run: |
        uv venv
        source .venv/bin/activate
        uv pip install pytest pytest-cov ruff mypy
      
    - name: Run linting
      run: |
        source .venv/bin/activate
        uv run ruff check .
        uv run mypy src/ --ignore-missing-imports
      
    - name: Run tests
      run: |
        source .venv/bin/activate
        uv run pytest --cov=src --cov-report=xml --cov-report=term
      
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v4
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## 🚀 Интерактивная практика

### 🔧 Проверка настроенного окружения

Давайте убедимся, что ваше окружение настроено правильно! Выполните следующие команды и проверьте результаты:

{{ create_exercise_form(
    "environment_check",
    "Проверка настроенного окружения TDD",
    "Выполните команды проверки окружения и убедитесь, что все работает корректно.",
    """# Шаг 1: Проверьте версию Python
python --version

# Шаг 2: Проверьте uv
uv --version

# Шаг 3: Создайте простой тест
# Создайте файл test_example.py
def test_simple():
    assert 2 + 2 == 4

# Шаг 4: Запустите тест
uv run pytest test_example.py -v

# Шаг 5: Проверьте покрытие
uv run pytest test_example.py --cov=test_example --cov-report=term

# Шаг 6: Очистите тестовый файл
# rm test_example.py""",
    [
        "Python версия должна быть 3.8+",
        "uv должен быть установлен и работать",
        "Тест должен выполняться без ошибок",
        "Отчет о покрытии должен показывать 100%",
        "Все команды должны выполняться успешно"
    ]
) }}

## ✅ Проверка настройки

Выполните следующие команды для проверки:

```bash
# 1. Проверка Python
python --version

# 2. Проверка uv
uv --version

# 3. Синхронизация зависимостей
uv sync

# 4. Запуск тестов
uv run pytest

# 5. Проверка покрытия
uv run pytest --cov

# 6. Проверка линтера
uv run ruff check src/ tests/

# 7. Форматирование
uv run ruff format src/ tests/
```

## 🎯 Следующие шаги

Теперь у вас есть полноценное окружение для TDD! В следующей главе мы подробно разберем цикл Red-Green-Refactor на практических примерах.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="environment-setup-quiz">
<script type="application/json">
{
  "title": "Настройка окружения для TDD",
  "description": "Проверьте знание инструментов и настройки среды разработки",
  "icon": "🔧",
  "questions": [
    {
      "question": "Какой менеджер пакетов рекомендуется для современных Python проектов?",
      "type": "single",
      "options": [
        {"text": "pip", "correct": false},
        {"text": "conda", "correct": false},
        {"text": "uv", "correct": true},
        {"text": "poetry", "correct": false}
      ],
      "explanation": "uv — это современный, быстрый и надежный менеджер пакетов Python, который заменяет pip-tools и значительно ускоряет установку зависимостей.",
      "points": 1
    },
    {
      "question": "Какие инструменты входят в современный стек Python разработки? (выберите все правильные)",
      "type": "multiple",
      "options": [
        {"text": "pytest для тестирования", "correct": true},
        {"text": "ruff для линтинга и форматирования", "correct": true},
        {"text": "mypy для проверки типов", "correct": true},
        {"text": "pylint для анализа кода", "correct": false},
        {"text": "pytest-cov для покрытия кода", "correct": true}
      ],
      "explanation": "Современный стек включает: pytest (тестирование), ruff (линтинг/форматирование), mypy (типы), pytest-cov (покрытие). pylint уже не так актуален благодаря ruff.",
      "points": 2
    },
    {
      "question": "Что делает команда 'uv sync'?",
      "type": "single",
      "options": [
        {"text": "Устанавливает новые пакеты", "correct": false},
        {"text": "Переустанавливает все зависимости согласно lock файлу", "correct": true},
        {"text": "Обновляет все пакеты до последних версий", "correct": false},
        {"text": "Синхронизирует код с GitHub", "correct": false}
      ],
      "explanation": "uv sync переустанавливает все зависимости точно согласно uv.lock файлу, обеспечивая воспроизводимые сборки.",
      "points": 1
    },
    {
      "question": "Какой правильный способ запуска тестов с покрытием кода?",
      "type": "single",
      "options": [
        {"text": "python -m pytest --cov", "correct": false},
        {"text": "uv run pytest --cov=src --cov-report=term", "correct": true},
        {"text": "pytest --coverage", "correct": false},
        {"text": "uv test --coverage", "correct": false}
      ],
      "explanation": "Правильная команда: 'uv run pytest --cov=src --cov-report=term' запускает тесты с покрытием кода и выводит отчет в терминал.",
      "points": 1
    },
    {
      "question": "Для чего используется pre-commit?",
      "type": "single",
      "options": [
        {"text": "Для автоматической отправки кода в репозиторий", "correct": false},
        {"text": "Для запуска проверок кода перед коммитом", "correct": true},
        {"text": "Для создания backup'ов кода", "correct": false},
        {"text": "Для управления версиями Python", "correct": false}
      ],
      "explanation": "pre-commit автоматически запускает линтеры, форматеры и тесты перед каждым коммитом, предотвращая попадание некачественного кода в репозиторий.",
      "points": 1
    },
    {
      "question": "Какая структура проекта рекомендуется для TDD?",
      "type": "single",
      "options": [
        {"text": "Все файлы в корне проекта", "correct": false},
        {"text": "src/ для кода, tests/ для тестов", "correct": true},
        {"text": "app/ для кода, test/ для тестов", "correct": false},
        {"text": "lib/ для кода, spec/ для тестов", "correct": false}
      ],
      "explanation": "Рекомендуемая структура: src/ для исходного кода и tests/ для тестов. Это обеспечивает четкое разделение и соответствует современным стандартам Python.",
      "points": 1
    }
  ]
}
</script>
</div>

---

**Следующая глава:** [Цикл Red-Green-Refactor](03_red_green_refactor.md)

*🔧 Окружение настроено — пора писать тесты!*
