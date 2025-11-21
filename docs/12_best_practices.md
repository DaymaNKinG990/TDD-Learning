# Лучшие практики и антипаттерны TDD

## 🎯 Цели главы

В этой главе мы рассмотрим проверенные временем лучшие практики TDD, типичные ошибки и антипаттерны, которых следует избегать. Эти знания помогут вам эффективно применять TDD в реальных проектах.

## ✅ Лучшие практики TDD

### 1. 🚀 Начинайте с простейшего теста

#### ✅ Правильно:
```python
def test_user_has_name():
    """Пользователь имеет имя."""
    user = User("John")
    assert user.name == "John"
```

#### ❌ Неправильно:
```python
def test_complete_user_lifecycle():
    """Полный жизненный цикл пользователя."""
    user = User("John", "john@example.com", 25, ["admin", "user"])
    user.login("password123")
    user.update_profile({"bio": "Developer"})
    user.add_friend(another_user)
    user.logout()
    assert user.last_login is not None
    # Слишком много в одном тесте!
```

### 2. 📝 Пишите выразительные имена тестов

#### ✅ Отличные имена:
```python
def test_withdraw_amount_greater_than_balance_raises_insufficient_funds_error():
    """Снятие суммы больше баланса вызывает ошибку недостатка средств."""
    pass

def test_new_shopping_cart_is_empty():
    """Новая корзина покупок пуста."""
    pass

def test_sending_email_to_invalid_address_raises_validation_error():
    """Отправка email на невалидный адрес вызывает ошибку валидации."""
    pass
```

#### ❌ Плохие имена:
```python
def test_user():  # Что именно тестируем?
    pass

def test_1():  # Неинформативно
    pass

def test_edge_case():  # Какой именно edge case?
    pass
```

### 3. 🏗 Следуйте структуре AAA

```python
def test_bank_transfer_between_accounts():
    """Перевод средств между банковскими счетами."""
    # Arrange (Подготовка)
    from_account = Account("ACC001", initial_balance=1000)
    to_account = Account("ACC002", initial_balance=500)
    transfer_amount = 250
    
    # Act (Действие)
    from_account.transfer(transfer_amount, to_account)
    
    # Assert (Проверка)
    assert from_account.balance == 750
    assert to_account.balance == 750
```

### 4. 🎯 Один тест = одна концепция

#### ✅ Правильно:
```python
def test_valid_email_passes_validation():
    """Валидный email проходит валидацию."""
    assert is_valid_email("user@example.com") == True

def test_email_without_at_symbol_fails_validation():
    """Email без символа @ не проходит валидацию."""
    assert is_valid_email("userexample.com") == False

def test_email_without_domain_fails_validation():
    """Email без домена не проходит валидацию."""
    assert is_valid_email("user@") == False
```

#### ❌ Неправильно:
```python
def test_email_validation():
    """Валидация email."""
    # Тестируем несколько концепций одновременно
    assert is_valid_email("user@example.com") == True
    assert is_valid_email("userexample.com") == False
    assert is_valid_email("user@") == False
    assert is_valid_email("@example.com") == False
    # Если один assert падает, мы не узнаем о других
```

### 5. ⚡ Быстрые и независимые тесты

#### ✅ Быстрые тесты:
```python
def test_calculate_discount():
    """Расчет скидки выполняется мгновенно."""
    price = 100
    discount_percent = 10
    
    result = calculate_discount(price, discount_percent)
    
    assert result == 90
```

#### ❌ Медленные тесты:
```python
def test_user_registration():
    """Медленный тест с реальной БД."""
    # Подключение к реальной БД
    db = connect_to_production_database()
    
    # Реальный HTTP запрос
    response = requests.post("https://api.example.com/users", {
        "email": "test@example.com"
    })
    
    # Ожидание ответа от внешнего сервиса
    time.sleep(2)
    
    assert response.status_code == 201
```

### 6. 🔬 Тестируйте поведение, а не реализацию

#### ✅ Тестируем поведение:
```python
def test_user_can_change_password():
    """Пользователь может изменить пароль."""
    user = User("john@example.com")
    old_password = "old_password"
    new_password = "new_password"
    
    user.set_password(old_password)
    user.change_password(old_password, new_password)
    
    # Проверяем поведение, а не реализацию
    assert user.verify_password(new_password) == True
    assert user.verify_password(old_password) == False
```

#### ❌ Тестируем реализацию:
```python
def test_password_hashing_implementation():
    """Тест конкретной реализации хеширования."""
    user = User("john@example.com")
    password = "test_password"
    
    user.set_password(password)
    
    # Тестируем внутреннюю реализацию
    assert user._password_hash.startswith("$2b$")  # Проверяем алгоритм bcrypt
    assert len(user._salt) == 32  # Проверяем длину соли
    # Тест сломается при изменении алгоритма хеширования
```

### 7. 🏷 Используйте маркеры для организации

```python
import pytest

@pytest.mark.unit
def test_calculate_tax():
    """Unit тест расчета налога."""
    assert calculate_tax(100) == 13

@pytest.mark.integration
def test_user_registration_flow():
    """Интеграционный тест регистрации."""
    pass

@pytest.mark.slow
def test_data_migration():
    """Медленный тест миграции данных."""
    pass

@pytest.mark.smoke
def test_application_starts():
    """Дымовой тест запуска приложения."""
    pass
```

### 8. 🧪 Используйте параметризацию для покрытия edge cases

```python
@pytest.mark.parametrize("age,expected", [
    (17, False),  # Несовершеннолетний
    (18, True),   # Граница
    (25, True),   # Взрослый
    (65, True),   # Пожилой
    (150, False), # Нереальный возраст
])
def test_is_adult(age, expected):
    """Проверка совершеннолетия для различных возрастов."""
    assert is_adult(age) == expected

@pytest.mark.parametrize("email", [
    "user@example.com",
    "test.email+tag@domain.co.uk",
    "user123@test-domain.org",
])
def test_valid_emails(email):
    """Валидные email адреса проходят валидацию."""
    assert is_valid_email(email) == True
```

## ❌ Антипаттерны TDD

### 1. 🚫 The Liar (Лжец)

Тест, который проходит по неправильным причинам.

#### ❌ Проблема:
```python
def test_user_authentication():
    """Тест аутентификации пользователя."""
    user = User("john@example.com", "password")
    
    # Тест проходит, но не по той причине!
    result = user.authenticate("wrong_password")
    assert result == True  # Всегда возвращает True из-за бага
```

#### ✅ Решение:
```python
def test_user_authentication_with_correct_password():
    """Аутентификация с правильным паролем успешна."""
    user = User("john@example.com", "password")
    
    result = user.authenticate("password")
    assert result == True

def test_user_authentication_with_wrong_password():
    """Аутентификация с неправильным паролем неуспешна."""
    user = User("john@example.com", "password")
    
    result = user.authenticate("wrong_password")
    assert result == False
```

### 2. 🚫 The Mockery (Передразнивание)

Чрезмерное использование моков.

#### ❌ Проблема:
```python
def test_user_service_create_user(mocker):
    """Перемокированный тест."""
    # Мокируем все зависимости
    mock_email_validator = mocker.Mock()
    mock_password_hasher = mocker.Mock() 
    mock_database = mocker.Mock()
    mock_logger = mocker.Mock()
    mock_event_bus = mocker.Mock()
    
    # Тест ничего не проверяет из реальной логики
    service = UserService(
        mock_email_validator,
        mock_password_hasher,
        mock_database,
        mock_logger,
        mock_event_bus
    )
    
    service.create_user("test@example.com", "password")
    
    # Проверяем только взаимодействие с моками
    mock_database.save.assert_called_once()
```

#### ✅ Решение:
```python
def test_user_service_create_user():
    """Тест с минимальным мокированием."""
    # Мокируем только внешние зависимости
    with patch('userservice.send_welcome_email') as mock_email:
        service = UserService()
        
        user = service.create_user("test@example.com", "password")
        
        # Проверяем реальное поведение
        assert user.email == "test@example.com"
        assert user.password_hash is not None
        mock_email.assert_called_once_with(user)
```

### 3. 🚫 The Inspector (Инспектор)

Тест, который знает слишком много о внутренней реализации.

#### ❌ Проблема:
```python
def test_shopping_cart_implementation_details():
    """Тест внутренней реализации корзины."""
    cart = ShoppingCart()
    product = Product("Laptop", 1000)
    
    cart.add_item(product)
    
    # Тестируем внутреннюю структуру данных
    assert len(cart._items) == 1
    assert cart._items[product] == 1
    assert cart._total_calculated == False
```

#### ✅ Решение:
```python
def test_shopping_cart_add_item():
    """Тест добавления товара в корзину."""
    cart = ShoppingCart()
    product = Product("Laptop", 1000)
    
    cart.add_item(product)
    
    # Тестируем публичное поведение
    assert cart.item_count == 1
    assert cart.total_price == 1000
    assert product in cart.items
```

### 4. 🚫 The Greedy Catcher (Жадный ловец)

Тест, который ловит слишком общие исключения.

#### ❌ Проблема:
```python
def test_invalid_user_data_raises_exception():
    """Невалидные данные пользователя вызывают исключение."""
    with pytest.raises(Exception):  # Слишком общее исключение
        User(email="invalid", age=-5)
```

#### ✅ Решение:
```python
def test_invalid_email_raises_validation_error():
    """Невалидный email вызывает ошибку валидации."""
    with pytest.raises(ValidationError, match="Invalid email format"):
        User(email="invalid", age=25)

def test_negative_age_raises_value_error():
    """Отрицательный возраст вызывает ValueError."""
    with pytest.raises(ValueError, match="Age cannot be negative"):
        User(email="user@example.com", age=-5)
```

### 5. 🚫 The Giant (Гигант)

Слишком большой тест, который проверяет множество вещей.

#### ❌ Проблема:
```python
def test_complete_e_commerce_flow():
    """Полный процесс электронной коммерции."""
    # 200+ строк кода
    user = create_user()
    product = create_product()
    cart = ShoppingCart()
    cart.add_item(product)
    order = place_order(cart, user)
    payment = process_payment(order)
    shipment = create_shipment(order)
    # ... много других проверок
    assert shipment.status == "shipped"
```

#### ✅ Решение:
```python
def test_user_can_add_product_to_cart():
    """Пользователь может добавить товар в корзину."""
    user = create_user()
    product = create_product()
    cart = user.get_cart()
    
    cart.add_item(product)
    
    assert product in cart.items

def test_user_can_place_order_from_cart():
    """Пользователь может создать заказ из корзины."""
    user = create_user()
    cart = create_cart_with_items()
    
    order = user.place_order(cart)
    
    assert order.status == "pending"
    assert order.items == cart.items
```

### 6. 🚫 The Sleeper (Соня)

Тест, который использует sleep или зависит от времени.

#### ❌ Проблема:
```python
def test_cache_expiration():
    """Тест истечения кеша."""
    cache = Cache(ttl=1)  # 1 секунда
    cache.set("key", "value")
    
    time.sleep(1.1)  # Ждем истечения кеша
    
    assert cache.get("key") is None
```

#### ✅ Решение:
```python
def test_cache_expiration(mocker):
    """Тест истечения кеша с мокированием времени."""
    with patch('time.time') as mock_time:
        mock_time.return_value = 1000
        
        cache = Cache(ttl=1)
        cache.set("key", "value")
        
        mock_time.return_value = 1002  # +2 секунды
        
        assert cache.get("key") is None
```

## 🏆 Практические рекомендации

### 1. 📊 Метрики качества тестов

```python
# Хорошие метрики:
# - Покрытие кода: 80-90%
# - Время выполнения unit тестов: < 10ms каждый
# - Соотношение тестов: 70% unit, 20% integration, 10% e2e
# - Количество моков в тесте: < 3

def test_fast_unit_test():
    """Быстрый unit тест."""
    start = time.time()
    result = calculate_discount(100, 10)
    end = time.time()
    
    assert result == 90
    assert (end - start) < 0.01  # Менее 10ms
```

### 2. 🔄 Рефакторинг тестов

```python
# До рефакторинга: дублирование
def test_valid_user_creation():
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "age": 25
    }
    user = User(**user_data)
    assert user.email == "test@example.com"

def test_user_with_invalid_email():
    user_data = {
        "email": "invalid-email",
        "name": "Test User", 
        "age": 25
    }
    with pytest.raises(ValidationError):
        User(**user_data)

# После рефакторинга: извлечение фикстуры
@pytest.fixture
def valid_user_data():
    return {
        "email": "test@example.com",
        "name": "Test User",
        "age": 25
    }

def test_valid_user_creation(valid_user_data):
    user = User(**valid_user_data)
    assert user.email == "test@example.com"

def test_user_with_invalid_email(valid_user_data):
    valid_user_data["email"] = "invalid-email"
    with pytest.raises(ValidationError):
        User(**valid_user_data)
```

### 3. 📝 Документирование тестов

```python
def test_bank_account_overdraft_protection():
    """
    Тест защиты от овердрафта.
    
    Given: Банковский счет с балансом $100
    When: Попытка снять $150
    Then: Возникает исключение InsufficientFundsError
    And: Баланс остается неизменным
    """
    account = BankAccount(initial_balance=100)
    
    with pytest.raises(InsufficientFundsError):
        account.withdraw(150)
    
    assert account.balance == 100
```

### 4. 🎯 Тестирование граничных условий

```python
@pytest.mark.parametrize("value,expected", [
    # Граничные условия
    (0, "zero"),
    (1, "positive"),
    (-1, "negative"),
    
    # Крайние значения
    (sys.maxsize, "positive"),
    (-sys.maxsize, "negative"),
    
    # Особые случаи
    (float('inf'), "infinite"),
    (float('nan'), "not_a_number"),
])
def test_number_classification_edge_cases(value, expected):
    """Тест классификации чисел для граничных случаев."""
    result = classify_number(value)
    assert result == expected
```

## 🎯 Чек-лист качественного теста

### ✅ Хороший тест должен быть:

- [ ] **Fast** - выполняется быстро (< 10ms для unit тестов)
- [ ] **Independent** - не зависит от других тестов
- [ ] **Repeatable** - дает одинаковый результат при повторных запусках
- [ ] **Self-validating** - четко показывает pass/fail
- [ ] **Timely** - написан до или одновременно с кодом

### ✅ Дополнительные критерии:

- [ ] Тестирует одну концепцию
- [ ] Имеет понятное имя
- [ ] Следует структуре AAA
- [ ] Не зависит от внешних ресурсов
- [ ] Использует минимум моков
- [ ] Тестирует поведение, а не реализацию

## 🎯 Следующие шаги

В следующей главе мы рассмотрим инструменты и фреймворки, которые помогут вам эффективно применять TDD в различных проектах.

## 🧪 Проверьте свои знания

<div class="quiz-container" id="best-practices-quiz">
<script type="application/json">
{
  "title": "Лучшие практики TDD",
  "description": "Проверьте знание лучших практик и антипаттернов в TDD",
  "icon": "🏆",
  "questions": [
    {
      "question": "Какие принципы включает аббревиатура F.I.R.S.T. для хороших тестов?",
      "type": "multiple",
      "options": [
        {"text": "Fast - тесты выполняются быстро", "correct": true},
        {"text": "Independent - тесты независимы друг от друга", "correct": true},
        {"text": "Repeatable - тесты воспроизводимы", "correct": true},
        {"text": "Self-validating - тесты самопроверяющиеся", "correct": true},
        {"text": "Timely - тесты своевременны", "correct": true}
      ],
      "explanation": "F.I.R.S.T. включает все пять принципов: Fast, Independent, Repeatable, Self-validating, Timely. Это основа качественных unit тестов.",
      "points": 2
    },
    {
      "question": "Что такое 'Ice Cream Cone' антипаттерн?",
      "type": "single",
      "options": [
        {"text": "Слишком много unit тестов", "correct": false},
        {"text": "Слишком много E2E тестов, мало unit тестов", "correct": true},
        {"text": "Отсутствие интеграционных тестов", "correct": false},
        {"text": "Тестирование только UI компонентов", "correct": false}
      ],
      "explanation": "Ice Cream Cone - антипаттерн, когда основной упор делается на E2E тесты (медленные, хрупкие), а unit тестов мало. Это противоположность Test Pyramid.",
      "points": 1
    },
    {
      "question": "Какие проблемы создают Fragile Tests?",
      "type": "multiple",
      "options": [
        {"text": "Падают при любых изменениях кода", "correct": true},
        {"text": "Создают ложное чувство безопасности", "correct": true},
        {"text": "Замедляют разработку", "correct": true},
        {"text": "Снижают доверие к тестам", "correct": true},
        {"text": "Ускоряют выполнение тестов", "correct": false}
      ],
      "explanation": "Fragile Tests падают от малейших изменений, создают ложную безопасность, замедляют разработку и снижают доверие. Ускорение выполнения не является их проблемой.",
      "points": 2
    },
    {
      "question": "Что означает 'тестировать поведение, а не реализацию'?",
      "type": "single",
      "options": [
        {"text": "Тестировать private методы вместо public", "correct": false},
        {"text": "Проверять результат работы, а не внутреннюю логику", "correct": true},
        {"text": "Писать больше интеграционных тестов", "correct": false},
        {"text": "Использовать только black-box тестирование", "correct": false}
      ],
      "explanation": "Тестирование поведения означает проверку того, что делает код (результат), а не того, как он это делает (внутренняя реализация). Это делает тесты более устойчивыми к рефакторингу.",
      "points": 1
    },
    {
      "question": "Какие техники помогают создавать читаемые тесты?",
      "type": "multiple",
      "options": [
        {"text": "Описательные имена тестов", "correct": true},
        {"text": "Структура AAA (Arrange-Act-Assert)", "correct": true},
        {"text": "Тестирование одной концепции в тесте", "correct": true},
        {"text": "Использование helper методов", "correct": true},
        {"text": "Максимальное количество assertions", "correct": false}
      ],
      "explanation": "Читаемость обеспечивают описательные имена, структура AAA, фокус на одной концепции и helper методы. Много assertions ухудшает читаемость.",
      "points": 2
    },
    {
      "question": "Что НЕ рекомендуется делать в unit тестах?",
      "type": "single",
      "options": [
        {"text": "Использовать параметризацию", "correct": false},
        {"text": "Тестировать private методы напрямую", "correct": true},
        {"text": "Применять fixtures для настройки", "correct": false},
        {"text": "Проверять граничные условия", "correct": false}
      ],
      "explanation": "Тестирование private методов напрямую нарушает инкапсуляцию и делает тесты хрупкими. Private методы должны тестироваться через public API.",
      "points": 1
    }
  ]
}
</script>
</div>

---

## 🔗 Связанные темы

- **[Основы TDD](01_tdd_basics.md)** - фундаментальные принципы
- **[Цикл Red-Green-Refactor](03_red_green_refactor.md)** - применение лучших практик
- **[Практические примеры](07_practical_examples.md)** - примеры хороших и плохих практик
- **[Mock объекты](08_mocking.md)** - лучшие практики мокирования
- **[Продвинутые техники](11_advanced_tdd.md)** - когда нарушать правила
- **[Инструменты и фреймворки](13_tools_frameworks.md)** - инструменты для соблюдения практик
- **[TDD и архитектура](19_tdd_architecture.md)** - архитектурные практики

**Следующая глава:** [Инструменты и фреймворки](13_tools_frameworks.md)

*🏆 Знание лучших практик — путь к мастерству TDD!*
