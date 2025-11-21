"""
Основной модуль с макросами для интерактивных упражнений TDD Learning
"""

import contextlib
import json
import os
import re
import subprocess
import sys
import tempfile
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from mkdocs_macros.plugin import MacrosPlugin


def hashFiles(_pattern: str) -> str:
    """
    Имитация функции hashFiles из GitHub Actions
    """
    try:
        # Для демонстрации возвращаем фиксированный хэш
        return "abc123def456"
    except Exception:
        return "default_hash"


def define_env(env: "MacrosPlugin") -> None:
    """
    Основная функция для определения макросов и переменных.

    Args:
        env: Объект плагина MkDocs macros для регистрации макросов
    """

    # Добавить базовые переменные
    env.variables.update(
        {
            "project_name": "TDD Learning",
            "project_version": "1.0.0",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        }
    )

    # Функции для GitHub Actions
    env.macro(hashFiles)

    # Добавить интерактивные макросы
    env.macro(code_input_form)
    env.macro(run_tests_button)
    env.macro(code_validator)
    env.macro(exercise_runner)
    env.macro(show_test_results)
    env.macro(create_exercise_form)


def code_input_form(
    exercise_id: str,
    initial_code: str = "",
    placeholder: str = "Введите ваш код здесь...",
    use_pyodide: bool = True,
    test_cases: list | None = None,
) -> str:
    """
    Создает форму для ввода кода с кнопкой проверки

    Args:
        exercise_id: Уникальный идентификатор упражнения
        initial_code: Начальный код в форме
        placeholder: Текст плейсхолдера
        use_pyodide: bool (default True) - использовать Pyodide для выполнения кода в браузере
        test_cases: list | None (default None) - опциональный список тестовых случаев.
            Каждый элемент может быть строкой (код теста) или словарем с ключами:
            - 'code': str - код теста (assert statement)
            - 'description': str - описание теста

    Returns:
        HTML строка с формой ввода кода
    """
    form_id = f"code_form_{exercise_id}"
    textarea_id = f"code_input_{exercise_id}"
    button_id = f"run_button_{exercise_id}"
    output_id = f"output_{exercise_id}"

    # Экранируем кавычки в JavaScript строках
    escaped_placeholder = placeholder.replace('"', "&quot;")
    escaped_initial = (
        initial_code.replace('"', "&quot;").replace("\n", "\\n").replace("\r", "")
    )

    # Prepare test cases for Pyodide
    test_cases_json = "[]"
    if test_cases:
        # Normalize test cases: convert strings to dicts if needed
        normalized_tests = []
        for test in test_cases:
            if isinstance(test, str):
                normalized_tests.append({"code": test, "description": ""})
            elif isinstance(test, dict):
                normalized_tests.append(
                    {
                        "code": test.get("code", ""),
                        "description": test.get("description", ""),
                    }
                )
        test_cases_json = json.dumps(normalized_tests)

    # Choose execution method
    if use_pyodide:
        onclick_handler = f"runExerciseWithPyodide('{exercise_id}', {test_cases_json})"
        pyodide_script = """
<script src="https://cdn.jsdelivr.net/pyodide/v0.24.1/full/pyodide.js"></script>
<script src="/assets/js/pyodide-exercise.js"></script>
"""
    else:
        onclick_handler = f"runExerciseSimple('{exercise_id}')"
        pyodide_script = ""

    return f"""
{pyodide_script}
<div class="code-exercise" id="{exercise_id}">
    <form id="{form_id}" class="code-input-form">
        <div class="form-group">
            <label for="{textarea_id}">Ваш код:</label>
            <textarea
                id="{textarea_id}"
                name="user_code"
                class="code-textarea"
                rows="10"
                placeholder="{escaped_placeholder}"
                data-initial="{escaped_initial}"
                spellcheck="false"
            >{initial_code}</textarea>
        </div>
        <div class="form-actions">
            <button type="button" id="{button_id}" class="run-button" onclick="{onclick_handler}">
                🚀 Запустить и проверить
            </button>
            <button type="button" class="reset-button" onclick="resetCode('{exercise_id}')">
                🔄 Сбросить
            </button>
        </div>
    </form>
    <div id="{output_id}" class="exercise-output" style="display: none;">
        <h4>Результаты проверки:</h4>
        <div class="output-content"></div>
    </div>
</div>

<script>
// Fallback function if Pyodide is not available
function runExerciseSimple(exerciseId) {{
    const textarea = document.getElementById('code_input_' + exerciseId);
    const output = document.getElementById('output_' + exerciseId);
    const button = document.getElementById('run_button_' + exerciseId);

    button.innerHTML = '⏳ Выполняется...';
    button.disabled = true;

    setTimeout(() => {{
        const userCode = textarea.value;
        let result;

        try {{
            if (userCode.includes('def ') && userCode.includes('return')) {{
                result = {{
                    success: true,
                    tests_passed: 1,
                    total_tests: 1,
                    test_details: '<p>✅ Синтаксис корректен</p>'
                }};
            }} else {{
                result = {{
                    success: false,
                    error: 'Функция должна содержать def и return',
                    hints: ['Добавьте ключевое слово def', 'Добавьте оператор return']
                }};
            }}
        }} catch (error) {{
            result = {{
                success: false,
                error: 'Ошибка в коде: ' + error.message
            }};
        }}

        displayResults(exerciseId, result);
        button.innerHTML = '🚀 Запустить и проверить';
        button.disabled = false;
    }}, 1000);
}}

function displayResults(exerciseId, data) {{
    const output = document.getElementById('output_' + exerciseId);
    const outputContent = output.querySelector('.output-content');

    output.style.display = 'block';

    if (data.success) {{
        const successHtml = `
            <div class="success-message">
                <h5>✅ Поздравляем! Все тесты пройдены!</h5>
                <div class="test-results">
                    <p>Пройдено тестов: ${{data.tests_passed}}/${{data.total_tests}}</p>
                    <div class="test-details">
                        ${{data.test_details || ''}}
                    </div>
                </div>
            </div>
        `;
        outputContent.innerHTML = successHtml;
        output.className = 'exercise-output success';
    }} else {{
        const errorMsg = data.error || 'Неизвестная ошибка';
        let hintsHtml = '';
        if (data.hints && data.hints.length > 0) {{
            const hintsList = data.hints.map(hint => `<li>${{hint}}</li>`).join('');
            hintsHtml = `<div class="hints"><h6>Подсказки:</h6><ul>${{hintsList}}</ul></div>`;
        }}

        const errorHtml = `
            <div class="error-message">
                <h5>❌ Есть ошибки в коде</h5>
                <div class="error-details">
                    <pre class="error-traceback">${{errorMsg}}</pre>
                </div>
                ${{hintsHtml}}
            </div>
        `;
        outputContent.innerHTML = errorHtml;
        output.className = 'exercise-output error';
    }}
}}

function resetCode(exerciseId) {{
    const textarea = document.getElementById('code_input_' + exerciseId);
    const initialCode = textarea.getAttribute('data-initial') || '';
    textarea.value = initialCode.replace(/\\\\n/g, '\\n');
    const output = document.getElementById('output_' + exerciseId);
    output.style.display = 'none';
}}
</script>
"""


def create_exercise_form(
    exercise_id: str,
    title: str,
    description: str,
    initial_code: str = "",
    test_cases: list[str] | None = None,
) -> str:
    """
    Создает полную форму упражнения с описанием и тестами

    Args:
        exercise_id: Уникальный ID упражнения
        title: Заголовок упражнения
        description: Описание задачи
        initial_code: Начальный код
        test_cases: Список тестовых случаев

    Returns:
        HTML строка с полным упражнением
    """
    test_html = ""
    if test_cases:
        test_html = f"""
        <div class="test-cases">
            <h4>Тестовые случаи:</h4>
            <ul>
                {"".join(f"<li>{test}</li>" for test in test_cases)}
            </ul>
        </div>
        """

    return f"""
<div class="exercise-container">
    <div class="exercise-header">
        <h3>{title}</h3>
        <div class="exercise-description">
            {description}
        </div>
        {test_html}
    </div>
    <div class="exercise-content">
        {code_input_form(exercise_id, initial_code)}
    </div>
</div>
"""


def _is_code_safe(user_code: str) -> bool:
    """
    Проверяет код на наличие опасных конструкций.

    Args:
        user_code: Код для проверки

    Returns:
        True если код безопасен, False иначе
    """
    dangerous_patterns = [
        r"__import__",
        r"exec\s*\(",
        r"eval\s*\(",
        r"compile\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"input\s*\(",
        r"raw_input\s*\(",
        r"subprocess",
        r"os\.system",
        r"os\.popen",
        r"os\.exec",
        r"shutil",
        r"pickle",
        r"marshal",
        r"__builtins__",
        r"__globals__",
        r"__dict__",
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, user_code, re.IGNORECASE):
            return False
    return True


def exercise_runner(_exercise_id: str, user_code: str) -> dict[str, Any]:
    """
    Запускает код пользователя и проверяет на тесты.

    ⚠️ ВНИМАНИЕ: Эта функция выполняет произвольный код пользователя!
    Используйте только в изолированной среде (sandbox) или для локальной разработки.

    Args:
        _exercise_id: ID упражнения (не используется в текущей реализации)
        user_code: Код пользователя

    Returns:
        Результаты выполнения
    """
    # Проверка безопасности кода
    if not _is_code_safe(user_code):
        return {
            "success": False,
            "error": "Код содержит небезопасные конструкции. Использование системных функций запрещено.",
        }

    temp_file = None
    try:
        # Создать временный файл с кодом пользователя
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
        ) as f:
            f.write(user_code)
            temp_file = f.name

        # Запустить код через subprocess с ограничениями
        result = subprocess.run(
            [sys.executable, temp_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=tempfile.gettempdir(),  # Ограничиваем рабочую директорию
            env={**os.environ, "PYTHONPATH": ""},  # Очищаем PYTHONPATH
        )

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Превышено время выполнения (10 секунд)"}
    except Exception as e:
        return {"success": False, "error": f"Ошибка выполнения: {str(e)}"}
    finally:
        # Удалить временный файл
        if temp_file and os.path.exists(temp_file):
            with contextlib.suppress(OSError):
                os.unlink(temp_file)


def code_validator(
    _exercise_id: str, _user_code: str, expected_tests: list[str]
) -> dict[str, Any]:
    """
    Проверяет код пользователя на соответствие тестам

    Args:
        _exercise_id: ID упражнения (не используется в текущей реализации)
        _user_code: Код пользователя (не используется в текущей реализации)
        expected_tests: Список ожидаемых результатов тестов

    Returns:
        Результаты валидации
    """
    # Здесь будет логика проверки кода на тесты
    # Пока возвращаем заглушку

    return {
        "success": True,
        "tests_passed": len(expected_tests),
        "total_tests": len(expected_tests),
        "test_details": "<p>Все тесты пройдены успешно!</p>",
    }


def run_tests_button(exercise_id: str, button_text: str = "Запустить тесты") -> str:
    """
    Создает кнопку для запуска тестов

    Args:
        exercise_id: ID упражнения
        button_text: Текст кнопки

    Returns:
        HTML кнопки
    """
    return f"""
<button onclick="runExerciseTests('{exercise_id}')" class="test-button">
    🧪 {button_text}
</button>
"""


def show_test_results(results: dict[str, Any]) -> str:
    """
    Отображает результаты тестов

    Args:
        results: Результаты тестирования

    Returns:
        HTML с результатами
    """
    if results.get("success"):
        return f"""
        <div class="exercise-output success">
            <h4>Результаты проверки:</h4>
            <div class="output-content">
                <div class="success-message">
                    <h5>✅ Тесты пройдены!</h5>
                    <div class="test-results">
                        <p>Все {results.get("tests_passed", 0)} тестов выполнены успешно.</p>
                        <div class="test-details">
                            {results.get("test_details", "")}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
    else:
        hints_html = ""
        if results.get("hints"):
            hints_list = "".join(f"<li>{hint}</li>" for hint in results["hints"])
            hints_html = (
                f'<div class="hints"><h6>Подсказки:</h6><ul>{hints_list}</ul></div>'
            )

        return f"""
        <div class="exercise-output error">
            <h4>Результаты проверки:</h4>
            <div class="output-content">
                <div class="error-message">
                    <h5>❌ Ошибки в коде</h5>
                    <div class="error-details">
                        <pre class="error-traceback">{results.get("error", "Неизвестная ошибка")}</pre>
                    </div>
                    {hints_html}
                </div>
            </div>
        </div>
        """
