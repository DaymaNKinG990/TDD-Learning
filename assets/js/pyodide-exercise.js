/**
 * 🐍 Pyodide Exercise Runner for TDD Learning
 * Executes Python code in the browser using Pyodide with test validation
 */

let pyodideInstance = null;
let pyodideLoading = false;
let pyodideLoadPromise = null;

/**
 * Load Pyodide instance (singleton pattern)
 * @returns {Promise<Pyodide>} Pyodide instance
 */
async function loadPyodide() {
    if (pyodideInstance) {
        return pyodideInstance;
    }

    if (pyodideLoading && pyodideLoadPromise) {
        return pyodideLoadPromise;
    }

    pyodideLoading = true;
    pyodideLoadPromise = (async () => {
        try {
            // Check if Pyodide is available
            if (typeof loadPyodide === 'undefined') {
                throw new Error('Pyodide library not loaded. Make sure pyodide.js is included before this script.');
            }

            pyodideInstance = await loadPyodide({
                indexURL: "https://cdn.jsdelivr.net/pyodide/v0.24.1/full/"
            });

            console.log('Pyodide loaded successfully');
            return pyodideInstance;
        } catch (error) {
            console.error('Failed to load Pyodide:', error);
            pyodideLoading = false;
            pyodideLoadPromise = null;
            throw error;
        }
    })();

    return pyodideLoadPromise;
}

/**
 * Check if code is safe to execute (security validation)
 * @param {string} code - Python code to check
 * @returns {Object} - {safe: boolean, reason: string}
 */
function isCodeSafe(code) {
    // Dangerous patterns that should be blocked
    const dangerousPatterns = [
        /__import__/gi,
        /exec\s*\(/gi,
        /eval\s*\(/gi,
        /compile\s*\(/gi,
        /open\s*\(/gi,
        /file\s*\(/gi,
        /input\s*\(/gi,
        /raw_input\s*\(/gi,
        /subprocess/gi,
        /os\.system/gi,
        /os\.popen/gi,
        /os\.exec/gi,
        /shutil/gi,
        /pickle/gi,
        /marshal/gi,
        /__builtins__/gi,
        /__globals__/gi,
        /__dict__/gi,
        /import\s+sys/gi,
        /sys\.exit/gi,
        /import\s+ctypes/gi,
        /import\s+os/gi,
        /import\s+subprocess/gi,
    ];

    // Check for dangerous patterns
    for (const pattern of dangerousPatterns) {
        if (pattern.test(code)) {
            const match = code.match(pattern);
            return {
                safe: false,
                reason: `Dangerous code detected: "${match[0]}" is not allowed for security reasons.`
            };
        }
    }

    // Check for suspicious import statements
    const importPattern = /import\s+(\w+)/gi;
    const suspiciousModules = ['sys', 'os', 'subprocess', 'ctypes', 'socket', 'urllib'];
    let match;
    while ((match = importPattern.exec(code)) !== null) {
        if (suspiciousModules.includes(match[1].toLowerCase())) {
            return {
                safe: false,
                reason: `Import of "${match[1]}" is not allowed for security reasons.`
            };
        }
    }

    return { safe: true, reason: '' };
}

/**
 * Run exercise with Pyodide execution and test validation
 * @param {string} exerciseId - Unique exercise identifier
 * @param {Array} testCases - Array of test case objects with 'code' and 'description'
 */
async function runExerciseWithPyodide(exerciseId, testCases = []) {
    const textarea = document.getElementById(`code_input_${exerciseId}`);
    const output = document.getElementById(`output_${exerciseId}`);
    const button = document.getElementById(`run_button_${exerciseId}`);

    if (!textarea || !output || !button) {
        console.error(`Exercise elements not found for ID: ${exerciseId}`);
        return;
    }

    const originalButtonText = button.innerHTML;
    button.innerHTML = '⏳ Загружается Pyodide...';
    button.disabled = true;

    // Show output area
    output.style.display = 'block';
    const outputContent = output.querySelector('.output-content');
    outputContent.innerHTML = '<p>⏳ Инициализация Pyodide...</p>';

    try {
        // Load Pyodide
        const pyodide = await loadPyodide();
        
        button.innerHTML = '⏳ Выполняется...';
        outputContent.innerHTML = '<p>⏳ Выполнение кода...</p>';

        const userCode = textarea.value.trim();

        if (!userCode) {
            displayResults(exerciseId, {
                success: false,
                error: 'Код не может быть пустым. Пожалуйста, введите код.',
                hints: ['Начните с написания функции', 'Используйте начальный код как основу']
            });
            return;
        }

        // Security check
        const safetyCheck = isCodeSafe(userCode);
        if (!safetyCheck.safe) {
            displayResults(exerciseId, {
                success: false,
                error: `Безопасность: ${safetyCheck.reason}`,
                hints: [
                    'Использование системных функций запрещено',
                    'Используйте только стандартные библиотеки Python',
                    'Избегайте операций с файловой системой и процессами'
                ]
            });
            return;
        }

        // Execute user code
        let executionError = null;
        try {
            pyodide.runPython(userCode);
        } catch (error) {
            executionError = error;
        }

        // If there's an execution error, show it immediately
        if (executionError) {
            displayResults(exerciseId, {
                success: false,
                error: `Ошибка выполнения: ${executionError.message}`,
                hints: [
                    'Проверьте синтаксис Python',
                    'Убедитесь, что все переменные определены',
                    'Проверьте отступы (используйте пробелы, а не табы)'
                ]
            });
            return;
        }

        // Run tests if provided
        if (testCases && testCases.length > 0) {
            let testsPassed = 0;
            let totalTests = testCases.length;
            let testDetails = [];
            let testErrors = [];

            for (let i = 0; i < testCases.length; i++) {
                const testCase = testCases[i];
                const testCode = testCase.code || testCase;
                const testDescription = testCase.description || `Тест ${i + 1}`;

                try {
                    pyodide.runPython(testCode);
                    testsPassed++;
                    testDetails.push(`<p>✅ ${testDescription}</p>`);
                } catch (error) {
                    testErrors.push({
                        description: testDescription,
                        error: error.message
                    });
                    testDetails.push(`<p>❌ ${testDescription}: ${error.message}</p>`);
                }
            }

            const success = testsPassed === totalTests;
            displayResults(exerciseId, {
                success: success,
                tests_passed: testsPassed,
                total_tests: totalTests,
                test_details: testDetails.join(''),
                error: testErrors.length > 0 ? `Не пройдено тестов: ${testErrors.length}` : null,
                hints: success ? [] : [
                    'Проверьте логику вашей функции',
                    'Убедитесь, что функция возвращает правильные значения',
                    'Проверьте граничные случаи'
                ]
            });
        } else {
            // No tests provided, just check if code executed successfully
            displayResults(exerciseId, {
                success: true,
                tests_passed: 0,
                total_tests: 0,
                test_details: '<p>✅ Код выполнен успешно</p><p>💡 Добавьте тесты для проверки корректности</p>'
            });
        }

    } catch (error) {
        console.error('Pyodide execution error:', error);
        displayResults(exerciseId, {
            success: false,
            error: `Ошибка: ${error.message}`,
            hints: [
                'Проверьте подключение к интернету (Pyodide загружается с CDN)',
                'Обновите страницу и попробуйте снова',
                'Убедитесь, что используете поддерживаемые библиотеки Python'
            ]
        });
    } finally {
        button.innerHTML = originalButtonText;
        button.disabled = false;
    }
}

/**
 * Display results in the exercise output area
 * @param {string} exerciseId - Exercise identifier
 * @param {Object} data - Result data with success, error, test details, etc.
 */
function displayResults(exerciseId, data) {
    const output = document.getElementById(`output_${exerciseId}`);
    const outputContent = output.querySelector('.output-content');

    output.style.display = 'block';

    if (data.success) {
        const successHtml = `
            <div class="success-message">
                <h5>✅ Поздравляем! Все тесты пройдены!</h5>
                ${data.total_tests > 0 ? `
                <div class="test-results">
                    <p><strong>Пройдено тестов:</strong> ${data.tests_passed}/${data.total_tests}</p>
                    <div class="test-details">
                        ${data.test_details || ''}
                    </div>
                </div>
                ` : ''}
                ${data.test_details || ''}
            </div>
        `;
        outputContent.innerHTML = successHtml;
        output.className = 'exercise-output success';
    } else {
        const errorMsg = data.error || 'Неизвестная ошибка';
        let hintsHtml = '';
        
        if (data.hints && data.hints.length > 0) {
            const hintsList = data.hints.map(hint => `<li>${hint}</li>`).join('');
            hintsHtml = `
                <div class="hints">
                    <h6>💡 Подсказки:</h6>
                    <ul>${hintsList}</ul>
                </div>
            `;
        }

        const errorHtml = `
            <div class="error-message">
                <h5>❌ Есть ошибки в коде</h5>
                <div class="error-details">
                    <pre class="error-traceback">${escapeHtml(errorMsg)}</pre>
                </div>
                ${hintsHtml}
                ${data.total_tests > 0 ? `
                <div class="test-results">
                    <p><strong>Пройдено тестов:</strong> ${data.tests_passed || 0}/${data.total_tests}</p>
                    <div class="test-details">
                        ${data.test_details || ''}
                    </div>
                </div>
                ` : ''}
            </div>
        `;
        outputContent.innerHTML = errorHtml;
        output.className = 'exercise-output error';
    }
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Reset code to initial state
 * @param {string} exerciseId - Exercise identifier
 */
function resetCode(exerciseId) {
    const textarea = document.getElementById(`code_input_${exerciseId}`);
    const output = document.getElementById(`output_${exerciseId}`);
    
    if (textarea) {
        const initialCode = textarea.getAttribute('data-initial') || '';
        textarea.value = initialCode.replace(/\\n/g, '\n');
    }
    
    if (output) {
        output.style.display = 'none';
        output.className = 'exercise-output';
    }
}

// Export functions to global scope for use in HTML
window.runExerciseWithPyodide = runExerciseWithPyodide;
window.resetCode = resetCode;
window.displayResults = displayResults;

