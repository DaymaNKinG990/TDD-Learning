# CI/CD и автоматизация тестирования в TDD

## 🎯 Цели главы

В этой главе мы рассмотрим интеграцию TDD с системами непрерывной интеграции и непрерывного развертывания (CI/CD). Вы узнаете:

- Как интегрировать автоматическое тестирование в CI/CD пайплайны
- Лучшие практики автоматизации тестирования
- Инструменты для CI/CD в Python проектах
- Стратегии параллельного выполнения тестов
- Мониторинг и отчетность результатов тестирования

## 🔄 Непрерывная интеграция (CI)

### Что такое CI?

**Continuous Integration (CI)** — это практика, при которой разработчики регулярно интегрируют изменения в общий репозиторий, и каждая интеграция автоматически проверяется сборкой и тестами.

### Преимущества CI в TDD

```mermaid
graph TD
    A[Разработчик] --> B[Коммит в Git]
    B --> C[Автоматический запуск CI]
    C --> D[Установка зависимостей]
    D --> E[Запуск тестов]
    E --> F[Анализ покрытия]
    F --> G[Статический анализ]
    G --> H[Отчет о качестве]
```

### Настройка GitHub Actions для Python проекта

Создайте файл `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12", "3.13"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ python_version_matrix }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ python_version_matrix }}

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: uv sync

    - name: Run tests
      run: uv run pytest --cov=src --cov-report=xml

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
        fail_ci_if_error: true
```

## 🚀 Непрерывное развертывание (CD)

### Стратегии развертывания

#### 1. Автоматическое развертывание (Automatic Deployment)

```yaml
# Продолжение ci.yml
  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - name: Deploy to production
      run: |
        echo "Deploying to production..."
        # Ваши команды развертывания
```

#### 2. Ручное одобрение (Manual Approval)

```yaml
# staging-deployment.yml
name: Deploy to Staging

on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'

jobs:
  deploy:
    runs-on: ubuntu-latest

    environment: ${{ github.event.inputs.environment }}

    steps:
    - name: Manual approval required
      run: echo "Waiting for manual approval..."

    - name: Deploy
      run: echo "Deploying to ${{ github.event.inputs.environment }}"
```

## 🧪 Стратегии тестирования в CI/CD

### Пирамида тестирования

```mermaid
graph TD
    A[End-to-End Tests] --> B[Integration Tests]
    B --> C[Unit Tests]
    C --> D[1000+ тестов]
    E[Минуты] --> F[Секунды]
    G[Часы] --> H[Минуты]
```

### Параллельное выполнение тестов

#### Настройка pytest-xdist

```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --cov=src
    --cov-report=term-missing
    --cov-report=xml
    -n auto  # Автоматическое определение количества процессов
```

#### Разделение тестов по типам

```python
# tests/conftest.py
def pytest_collection_modifyitems(config, items):
    """Разделение тестов на группы для параллельного выполнения."""

    for item in items:
        # Быстрые unit тесты
        if "unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)

        # Медленные интеграционные тесты
        elif "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)

        # E2E тесты
        elif "e2e" in item.nodeid:
            item.add_marker(pytest.mark.e2e)
```

### Тестовые окружения

#### Локальное тестирование

```bash
# Быстрые тесты для разработки
uv run pytest tests/unit/ -v

# Полный набор тестов
uv run pytest

# С покрытием
uv run pytest --cov=src --cov-report=html
```

#### Стадийное тестирование

```yaml
# .github/workflows/staging.yml
name: Staging Tests

on:
  push:
    branches: [ staging ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4

    - name: Test with database
      run: |
        uv sync
        uv run pytest tests/integration/
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
```

## 📊 Мониторинг и отчетность

### Отчеты о покрытии кода

#### Codecov интеграция

```yaml
# codecov.yml
coverage:
  status:
    project:
      default:
        target: 80%
        threshold: 1%
    patch:
      default:
        target: 80%
      branches: null

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false
```

#### Локальные отчеты

```bash
# HTML отчет о покрытии
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html

# Терминальный отчет
uv run pytest --cov=src --cov-report=term-missing
```

### Качественные метрики

#### Статический анализ

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.12"

    - name: Install uv
      run: curl -LsSf https://astral.sh/uv/install.sh | sh

    - name: Install dependencies
      run: uv sync

    - name: Run ruff (linting)
      run: uv run ruff check src/

    - name: Run mypy (type checking)
      run: uv run mypy src/

    - name: Run bandit (security)
      run: uv run bandit -r src/
```

### Мониторинг производительности

#### Тесты производительности

```python
# tests/performance/test_performance.py
import pytest
import time
from src.calculator import Calculator

@pytest.mark.benchmark
def test_calculator_speed(benchmark):
    """Тест производительности калькулятора."""

    calc = Calculator()

    def operation():
        return calc.add(1000, 2000)

    # Измеряем время выполнения
    result = benchmark(operation)
    assert result == 3000

    # Проверяем, что выполняется достаточно быстро
    assert benchmark.stats.mean < 0.001  # Менее 1мс
```

## 🛠 Инструменты CI/CD

### Популярные платформы

| Платформа | Преимущества | Недостатки |
|-----------|-------------|-----------|
| **GitHub Actions** | Бесплатно, интегрировано | Ограничения по времени |
| **GitLab CI** | Полный контроль | Сложность настройки |
| **Jenkins** | Гибкость, плагины | Требует обслуживания |
| **CircleCI** | Простота, скорость | Платные минуты |

### Конфигурация для разных платформ

#### GitLab CI (.gitlab-ci.yml)

```yaml
stages:
  - test
  - deploy

test:
  stage: test
  image: python:3.12
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - uv sync
  script:
    - uv run pytest --cov=src
  coverage: '/TOTAL.*\s+(\d+%)$/'

deploy:
  stage: deploy
  script:
    - echo "Deploy to production"
  only:
    - main
```

#### Jenkins (Jenkinsfile)

```groovy
pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh '''
                    curl -LsSf https://astral.sh/uv/install.sh | sh
                    uv sync
                    uv run pytest --cov=src --junitxml=results.xml
                '''
            }
            post {
                always {
                    junit 'results.xml'
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                sh 'echo "Deploying..."'
            }
        }
    }
}
```

## 📈 Продвинутые стратегии

### Feature Flags

```python
# src/features.py
import os

class FeatureFlags:
    @property
    def enable_new_feature(self) -> bool:
        return os.getenv("ENABLE_NEW_FEATURE", "false").lower() == "true"

# tests/test_features.py
def test_new_feature_enabled(feature_flags):
    feature_flags.enable_new_feature = True
    # Тест новой функциональности

def test_new_feature_disabled(feature_flags):
    feature_flags.enable_new_feature = False
    # Тест старой функциональности
```

### Blue-Green Deployment

```yaml
# blue-green-deployment.yml
name: Blue-Green Deployment

on:
  workflow_dispatch:
    inputs:
      traffic_percentage:
        description: 'Percentage of traffic to new version'
        required: true
        default: '10'

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Deploy blue version
      run: |
        echo "Deploying to blue environment..."

    - name: Run smoke tests
      run: |
        echo "Running smoke tests on blue..."

    - name: Gradual traffic shift
      run: |
        echo "Shifting ${{ github.event.inputs.traffic_percentage }}% traffic to blue..."

    - name: Full deployment
      if: github.event.inputs.traffic_percentage == '100'
      run: |
        echo "Full deployment to blue, shutting down green..."
```

## 🎯 Лучшие практики

### 1. Fail Fast принцип

```yaml
# Быстрая отбраковка
jobs:
  quick-checks:
    runs-on: ubuntu-latest
    steps:
    - name: Quick syntax check
      run: python -m py_compile src/
    - name: Quick import check
      run: python -c "import src"
```

### 2. Кэширование зависимостей

```yaml
steps:
- uses: actions/cache@v3
  with:
    path: ~/.cache/uv
    key: ${{ runner.os }}-uv-${{ hashFiles('**/uv.lock') }}
    restore-keys: |
      ${{ runner.os }}-uv-
```

### 3. Матричные сборки

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ["3.11", "3.12", "3.13"]
    exclude:
      # Исключаем некоторые комбинации
      - os: macos-latest
        python-version: "3.11"
```

### 4. Условные развертывания

```yaml
deploy:
  if: |
    github.ref == 'refs/heads/main' &&
    contains(github.event.head_commit.modified, 'src/')
```

## 🚨 Обработка ошибок и откаты

### Автоматические откаты

```yaml
jobs:
  rollback:
    if: failure() && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Rollback deployment
      run: |
        echo "Rolling back to previous version..."
```

### Мониторинг здоровья

```python
# health_check.py
import requests
import time

def wait_for_service(url: str, timeout: int = 300) -> bool:
    """Ожидание готовности сервиса."""
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass

        time.sleep(10)

    return False
```

---

**Предыдущая глава:** [Инструменты и фреймворки](13_tools_frameworks.md)  
**Следующая глава:** [Тестирование обработки ошибок](15_error_handling_tdd.md)

## 🎓 Практические упражнения

### Упражнение 1: Настройка CI для простого проекта

Создайте CI пайплайн для существующего проекта с:
- Автоматическим запуском тестов
- Проверкой покрытия кода
- Статическим анализом

### Упражнение 2: Стратегия развертывания

Разработайте стратегию развертывания для веб-приложения с:
- Автоматическими тестами
- Ручным одобрением для production
- Возможностью отката

### Упражнение 3: Мониторинг качества кода

Настройте систему мониторинга качества кода с:
- Метриками покрытия
- Статическим анализом
- Отчетами о техническом долге

## 🧪 Проверьте свои знания

<div class="quiz-container" id="ci-cd-quiz">
<script type="application/json">
{
  "title": "CI/CD и автоматизация тестирования",
  "description": "Проверьте понимание принципов непрерывной интеграции и развертывания",
  "icon": "🚀",
  "questions": [
    {
      "question": "Что такое Continuous Integration (CI)?",
      "type": "single",
      "options": [
        {"text": "Автоматическое развертывание кода в production", "correct": false},
        {"text": "Регулярное объединение изменений кода в главную ветку", "correct": true},
        {"text": "Непрерывное написание тестов", "correct": false},
        {"text": "Мониторинг производительности приложения", "correct": false}
      ],
      "explanation": "CI — это практика регулярного объединения изменений кода в главную ветку с автоматическим запуском тестов и проверок качества.",
      "points": 1
    },
    {
      "question": "Какие инструменты используются для параллельного запуска тестов?",
      "type": "multiple",
      "options": [
        {"text": "pytest-xdist", "correct": true},
        {"text": "uv run pytest -n auto", "correct": true},
        {"text": "GitHub Actions matrix", "correct": true},
        {"text": "mypy", "correct": false},
        {"text": "ruff", "correct": false}
      ],
      "explanation": "pytest-xdist, -n auto и GitHub Actions matrix позволяют распределять тесты по нескольким процессорам или машинам.",
      "points": 2
    },
    {
      "question": "Что делает команда 'uv sync'?",
      "type": "single",
      "options": [
        {"text": "Запускает тесты", "correct": false},
        {"text": "Переустанавливает зависимости согласно uv.lock", "correct": true},
        {"text": "Создает виртуальное окружение", "correct": false},
        {"text": "Обновляет все пакеты до последних версий", "correct": false}
      ],
      "explanation": "uv sync обеспечивает воспроизводимые сборки, переустанавливая все зависимости точно согласно файлу uv.lock.",
      "points": 1
    },
    {
      "question": "Какая стратегия развертывания позволяет постепенный переход на новую версию?",
      "type": "single",
      "options": [
        {"text": "Big Bang Deployment", "correct": false},
        {"text": "Blue-Green Deployment", "correct": true},
        {"text": "Rolling Update", "correct": false},
        {"text": "Canary Deployment", "correct": false}
      ],
      "explanation": "Blue-Green Deployment позволяет поддерживать две идентичные среды (blue и green) и постепенно переключать трафик.",
      "points": 1
    },
    {
      "question": "Для чего используется кэширование зависимостей в CI?",
      "type": "multiple",
      "options": [
        {"text": "Ускорение сборки", "correct": true},
        {"text": "Снижение сетевого трафика", "correct": true},
        {"text": "Экономия минут CI", "correct": true},
        {"text": "Улучшение качества кода", "correct": false},
        {"text": "Повышение безопасности", "correct": false}
      ],
      "explanation": "Кэширование зависимостей значительно ускоряет сборки и экономит ресурсы CI систем.",
      "points": 2
    },
    {
      "question": "Что проверяет health check после развертывания?",
      "type": "single",
      "options": [
        {"text": "Синтаксис кода", "correct": false},
        {"text": "Доступность и работоспособность сервиса", "correct": true},
        {"text": "Покрытие тестами", "correct": false},
        {"text": "Безопасность кода", "correct": false}
      ],
      "explanation": "Health check проверяет, что развернутое приложение отвечает на запросы и работает корректно.",
      "points": 1
    }
  ]
}
</script>
</div>

---

**Предыдущая глава:** [Инструменты и фреймворки](13_tools_frameworks.md)
**Следующая глава:** [Тестирование обработки ошибок](15_error_handling_tdd.md)

## 📚 Дополнительные ресурсы

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest-xdist](https://pypi.org/project/pytest-xdist/)
- [Codecov](https://codecov.io/)
- [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/)

*Помните: Хорошая CI/CD система — это инвестиция в надежность и скорость разработки!*
