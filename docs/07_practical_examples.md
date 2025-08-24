# Практические примеры TDD

## 🎯 Цели главы

В этой главе мы применим все изученные принципы TDD на практических примерах. Мы создадим несколько проектов с нуля, следуя циклу Red-Green-Refactor и демонстрируя различные техники и паттерны.

## 🏦 Проект 1: Банковская система

Создадим простую банковскую систему, используя строгий TDD подход.

### Требования:
- Создание банковского счета
- Пополнение и снятие средств
- Перевод между счетами
- История операций
- Различные типы счетов

### Итерация 1: Создание счета

#### 🔴 RED: Первый тест
```python
# test_bank_account.py
import pytest
from decimal import Decimal

def test_new_account_has_zero_balance():
    """Новый счет имеет нулевой баланс."""
    account = BankAccount("ACC123")  # Класса пока нет!
    assert account.balance == Decimal("0.00")
```

#### 🟢 GREEN: Минимальная реализация
```python
# bank_account.py
from decimal import Decimal

class BankAccount:
    def __init__(self, account_number: str):
        self.account_number = account_number
        self.balance = Decimal("0.00")
```

#### 🔵 REFACTOR: Улучшения
```python
from decimal import Decimal
from typing import Union

MoneyType = Union[int, float, str, Decimal]

class BankAccount:
    """Банковский счет с базовой функциональностью."""
    
    def __init__(self, account_number: str):
        if not account_number:
            raise ValueError("Account number cannot be empty")
        self._account_number = account_number
        self._balance = Decimal("0.00")
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property 
    def balance(self) -> Decimal:
        return self._balance
```

### Итерация 2: Пополнение счета

#### 🔴 RED
```python
def test_deposit_positive_amount():
    """Пополнение счета положительной суммой."""
    account = BankAccount("ACC123")
    account.deposit(Decimal("100.00"))  # Метода пока нет!
    assert account.balance == Decimal("100.00")
```

#### 🟢 GREEN
```python
class BankAccount:
    # ... предыдущий код ...
    
    def deposit(self, amount: MoneyType) -> None:
        self._balance += Decimal(str(amount))
```

#### 🔴 RED: Валидация
```python
def test_deposit_negative_amount_raises_error():
    """Пополнение отрицательной суммой вызывает ошибку."""
    account = BankAccount("ACC123")
    with pytest.raises(ValueError, match="Amount must be positive"):
        account.deposit(Decimal("-10.00"))

def test_deposit_zero_raises_error():
    """Пополнение нулевой суммой вызывает ошибку."""
    account = BankAccount("ACC123")
    with pytest.raises(ValueError, match="Amount must be positive"):
        account.deposit(Decimal("0.00"))
```

#### 🟢 GREEN: Добавляем валидацию
```python
class BankAccount:
    # ... предыдущий код ...
    
    def deposit(self, amount: MoneyType) -> None:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        self._balance += amount_decimal
```

### Итерация 3: Снятие средств

#### 🔴 RED
```python
def test_withdraw_valid_amount():
    """Снятие допустимой суммы."""
    account = BankAccount("ACC123")
    account.deposit(Decimal("100.00"))
    account.withdraw(Decimal("30.00"))  # Метода пока нет!
    assert account.balance == Decimal("70.00")

def test_withdraw_more_than_balance_raises_error():
    """Снятие суммы больше баланса вызывает ошибку."""
    account = BankAccount("ACC123")
    account.deposit(Decimal("50.00"))
    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(Decimal("100.00"))
```

#### 🟢 GREEN
```python
class BankAccount:
    # ... предыдущий код ...
    
    def withdraw(self, amount: MoneyType) -> None:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        if amount_decimal > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount_decimal
```

#### 🔵 REFACTOR: Извлечение общей валидации
```python
class BankAccount:
    """Банковский счет с базовой функциональностью."""
    
    def __init__(self, account_number: str):
        if not account_number:
            raise ValueError("Account number cannot be empty")
        self._account_number = account_number
        self._balance = Decimal("0.00")
    
    @property
    def account_number(self) -> str:
        return self._account_number
    
    @property 
    def balance(self) -> Decimal:
        return self._balance
    
    def deposit(self, amount: MoneyType) -> None:
        """Пополнить счет."""
        amount_decimal = self._validate_amount(amount)
        self._balance += amount_decimal
    
    def withdraw(self, amount: MoneyType) -> None:
        """Снять средства со счета."""
        amount_decimal = self._validate_amount(amount)
        if amount_decimal > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount_decimal
    
    def _validate_amount(self, amount: MoneyType) -> Decimal:
        """Валидация суммы операции."""
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        return amount_decimal
```

### Итерация 4: История операций

#### 🔴 RED
```python
from datetime import datetime

def test_new_account_has_empty_transaction_history():
    """Новый счет имеет пустую историю операций."""
    account = BankAccount("ACC123")
    assert len(account.transaction_history) == 0  # Свойства пока нет!

def test_deposit_creates_transaction_record():
    """Пополнение создает запись в истории."""
    account = BankAccount("ACC123")
    account.deposit(Decimal("100.00"))
    
    history = account.transaction_history
    assert len(history) == 1
    assert history[0].amount == Decimal("100.00")
    assert history[0].type == "deposit"
    assert isinstance(history[0].timestamp, datetime)
```

#### 🟢 GREEN: Добавляем Transaction и историю
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Transaction:
    """Запись о банковской операции."""
    amount: Decimal
    type: str
    timestamp: datetime
    balance_after: Decimal

class BankAccount:
    """Банковский счет с базовой функциональностью."""
    
    def __init__(self, account_number: str):
        if not account_number:
            raise ValueError("Account number cannot be empty")
        self._account_number = account_number
        self._balance = Decimal("0.00")
        self._transactions: List[Transaction] = []
    
    @property
    def transaction_history(self) -> List[Transaction]:
        return self._transactions.copy()  # Возвращаем копию
    
    def deposit(self, amount: MoneyType) -> None:
        """Пополнить счет."""
        amount_decimal = self._validate_amount(amount)
        self._balance += amount_decimal
        self._add_transaction(amount_decimal, "deposit")
    
    def withdraw(self, amount: MoneyType) -> None:
        """Снять средства со счета."""
        amount_decimal = self._validate_amount(amount)
        if amount_decimal > self._balance:
            raise ValueError("Insufficient funds")
        self._balance -= amount_decimal
        self._add_transaction(amount_decimal, "withdrawal")
    
    def _add_transaction(self, amount: Decimal, transaction_type: str) -> None:
        """Добавить запись о транзакции."""
        transaction = Transaction(
            amount=amount,
            type=transaction_type,
            timestamp=datetime.now(),
            balance_after=self._balance
        )
        self._transactions.append(transaction)
    
    # ... остальные методы ...
```

### Итерация 5: Переводы между счетами

#### 🔴 RED
```python
def test_transfer_between_accounts():
    """Перевод средств между счетами."""
    from_account = BankAccount("ACC123")
    to_account = BankAccount("ACC456")
    
    from_account.deposit(Decimal("100.00"))
    from_account.transfer(Decimal("30.00"), to_account)  # Метода пока нет!
    
    assert from_account.balance == Decimal("70.00")
    assert to_account.balance == Decimal("30.00")

def test_transfer_to_same_account_raises_error():
    """Перевод на тот же счет вызывает ошибку."""
    account = BankAccount("ACC123")
    account.deposit(Decimal("100.00"))
    
    with pytest.raises(ValueError, match="Cannot transfer to the same account"):
        account.transfer(Decimal("30.00"), account)
```

#### 🟢 GREEN
```python
class BankAccount:
    # ... предыдущий код ...
    
    def transfer(self, amount: MoneyType, to_account: 'BankAccount') -> None:
        """Перевести средства на другой счет."""
        if to_account is self:
            raise ValueError("Cannot transfer to the same account")
        
        amount_decimal = self._validate_amount(amount)
        if amount_decimal > self._balance:
            raise ValueError("Insufficient funds")
        
        # Выполняем перевод
        self._balance -= amount_decimal
        to_account._balance += amount_decimal
        
        # Записываем транзакции
        self._add_transaction(amount_decimal, f"transfer_out_to_{to_account.account_number}")
        to_account._add_transaction(amount_decimal, f"transfer_in_from_{self.account_number}")
```

## 🛒 Проект 2: Система корзины покупок

Создадим систему корзины покупок для интернет-магазина.

### Требования:
- Добавление товаров в корзину
- Удаление товаров
- Подсчет общей стоимости
- Применение скидок
- Различные типы товаров

### Итерация 1: Товар и корзина

#### 🔴 RED
```python
# test_shopping_cart.py
def test_create_empty_cart():
    """Создание пустой корзины."""
    cart = ShoppingCart()  # Класса пока нет!
    assert cart.is_empty() == True
    assert cart.total_items == 0

def test_create_product():
    """Создание товара."""
    product = Product("Laptop", Decimal("999.99"))  # Класса пока нет!
    assert product.name == "Laptop"
    assert product.price == Decimal("999.99")
```

#### 🟢 GREEN
```python
# shopping_cart.py
from decimal import Decimal

class Product:
    """Товар в магазине."""
    
    def __init__(self, name: str, price: Decimal):
        self.name = name
        self.price = price

class ShoppingCart:
    """Корзина покупок."""
    
    def __init__(self):
        self._items = []
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    @property
    def total_items(self) -> int:
        return len(self._items)
```

### Итерация 2: Добавление товаров

#### 🔴 RED
```python
def test_add_product_to_cart():
    """Добавление товара в корзину."""
    cart = ShoppingCart()
    product = Product("Laptop", Decimal("999.99"))
    
    cart.add_item(product)  # Метода пока нет!
    
    assert cart.is_empty() == False
    assert cart.total_items == 1

def test_add_multiple_same_products():
    """Добавление нескольких одинаковых товаров."""
    cart = ShoppingCart()
    product = Product("Laptop", Decimal("999.99"))
    
    cart.add_item(product, quantity=2)
    
    assert cart.total_items == 2
    assert cart.get_item_quantity(product) == 2  # Метода пока нет!
```

#### 🟢 GREEN
```python
from typing import Dict

class ShoppingCart:
    """Корзина покупок."""
    
    def __init__(self):
        self._items: Dict[Product, int] = {}
    
    def is_empty(self) -> bool:
        return len(self._items) == 0
    
    @property
    def total_items(self) -> int:
        return sum(self._items.values())
    
    def add_item(self, product: Product, quantity: int = 1) -> None:
        """Добавить товар в корзину."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if product in self._items:
            self._items[product] += quantity
        else:
            self._items[product] = quantity
    
    def get_item_quantity(self, product: Product) -> int:
        """Получить количество товара в корзине."""
        return self._items.get(product, 0)
```

### Итерация 3: Подсчет стоимости

#### 🔴 RED
```python
def test_calculate_total_price():
    """Подсчет общей стоимости корзины."""
    cart = ShoppingCart()
    laptop = Product("Laptop", Decimal("999.99"))
    mouse = Product("Mouse", Decimal("29.99"))
    
    cart.add_item(laptop)
    cart.add_item(mouse, quantity=2)
    
    expected_total = Decimal("999.99") + (Decimal("29.99") * 2)
    assert cart.total_price == expected_total  # Свойства пока нет!

def test_empty_cart_total_is_zero():
    """Общая стоимость пустой корзины равна нулю."""
    cart = ShoppingCart()
    assert cart.total_price == Decimal("0.00")
```

#### 🟢 GREEN
```python
class ShoppingCart:
    # ... предыдущий код ...
    
    @property
    def total_price(self) -> Decimal:
        """Общая стоимость товаров в корзине."""
        total = Decimal("0.00")
        for product, quantity in self._items.items():
            total += product.price * quantity
        return total
```

### Итерация 4: Система скидок

#### 🔴 RED
```python
def test_apply_percentage_discount():
    """Применение процентной скидки."""
    cart = ShoppingCart()
    product = Product("Laptop", Decimal("1000.00"))
    cart.add_item(product)
    
    discount = PercentageDiscount(Decimal("10"))  # Класса пока нет!
    cart.apply_discount(discount)  # Метода пока нет!
    
    assert cart.total_price == Decimal("900.00")

def test_apply_fixed_discount():
    """Применение фиксированной скидки."""
    cart = ShoppingCart()
    product = Product("Laptop", Decimal("1000.00"))
    cart.add_item(product)
    
    discount = FixedDiscount(Decimal("100"))
    cart.apply_discount(discount)
    
    assert cart.total_price == Decimal("900.00")
```

#### 🟢 GREEN: Создаем систему скидок
```python
from abc import ABC, abstractmethod

class Discount(ABC):
    """Абстрактная скидка."""
    
    @abstractmethod
    def apply(self, amount: Decimal) -> Decimal:
        """Применить скидку к сумме."""
        pass

class PercentageDiscount(Discount):
    """Процентная скидка."""
    
    def __init__(self, percentage: Decimal):
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100")
        self.percentage = percentage
    
    def apply(self, amount: Decimal) -> Decimal:
        discount_amount = amount * (self.percentage / 100)
        return amount - discount_amount

class FixedDiscount(Discount):
    """Фиксированная скидка."""
    
    def __init__(self, amount: Decimal):
        if amount < 0:
            raise ValueError("Discount amount cannot be negative")
        self.amount = amount
    
    def apply(self, amount: Decimal) -> Decimal:
        return max(amount - self.amount, Decimal("0.00"))

class ShoppingCart:
    # ... предыдущий код ...
    
    def __init__(self):
        self._items: Dict[Product, int] = {}
        self._discount: Optional[Discount] = None
    
    def apply_discount(self, discount: Discount) -> None:
        """Применить скидку к корзине."""
        self._discount = discount
    
    @property
    def subtotal(self) -> Decimal:
        """Стоимость без скидки."""
        total = Decimal("0.00")
        for product, quantity in self._items.items():
            total += product.price * quantity
        return total
    
    @property
    def total_price(self) -> Decimal:
        """Общая стоимость с учетом скидки."""
        subtotal = self.subtotal
        if self._discount:
            return self._discount.apply(subtotal)
        return subtotal
```

## 📝 Проект 3: Система управления задачами

Создадим систему управления задачами (TODO приложение).

### Итерация 1: Базовая задача

#### 🔴 RED
```python
# test_todo.py
from datetime import datetime, date

def test_create_task():
    """Создание задачи с заголовком."""
    task = Task("Buy groceries")  # Класса пока нет!
    assert task.title == "Buy groceries"
    assert task.is_completed == False
    assert isinstance(task.created_at, datetime)

def test_complete_task():
    """Завершение задачи."""
    task = Task("Buy groceries")
    task.complete()  # Метода пока нет!
    
    assert task.is_completed == True
    assert isinstance(task.completed_at, datetime)
```

#### 🟢 GREEN
```python
# todo.py
from datetime import datetime
from typing import Optional

class Task:
    """Задача в системе управления задачами."""
    
    def __init__(self, title: str):
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        self.title = title.strip()
        self.is_completed = False
        self.created_at = datetime.now()
        self.completed_at: Optional[datetime] = None
    
    def complete(self) -> None:
        """Отметить задачу как выполненную."""
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.now()
```

### Итерация 2: Список задач

#### 🔴 RED
```python
def test_create_empty_todo_list():
    """Создание пустого списка задач."""
    todo_list = TodoList()  # Класса пока нет!
    assert len(todo_list) == 0
    assert todo_list.is_empty() == True

def test_add_task_to_list():
    """Добавление задачи в список."""
    todo_list = TodoList()
    task = Task("Buy groceries")
    
    todo_list.add_task(task)  # Метода пока нет!
    
    assert len(todo_list) == 1
    assert task in todo_list.tasks  # Свойства пока нет!
```

#### 🟢 GREEN
```python
from typing import List

class TodoList:
    """Список задач."""
    
    def __init__(self):
        self._tasks: List[Task] = []
    
    def __len__(self) -> int:
        return len(self._tasks)
    
    def is_empty(self) -> bool:
        return len(self._tasks) == 0
    
    @property
    def tasks(self) -> List[Task]:
        return self._tasks.copy()
    
    def add_task(self, task: Task) -> None:
        """Добавить задачу в список."""
        if task in self._tasks:
            raise ValueError("Task already exists in the list")
        self._tasks.append(task)
```

### Итерация 3: Фильтрация и статистика

#### 🔴 RED
```python
def test_filter_completed_tasks():
    """Фильтрация завершенных задач."""
    todo_list = TodoList()
    task1 = Task("Buy groceries")
    task2 = Task("Walk the dog")
    task3 = Task("Read a book")
    
    todo_list.add_task(task1)
    todo_list.add_task(task2) 
    todo_list.add_task(task3)
    
    task1.complete()
    task3.complete()
    
    completed = todo_list.get_completed_tasks()  # Метода пока нет!
    assert len(completed) == 2
    assert task1 in completed
    assert task3 in completed

def test_get_completion_percentage():
    """Получение процента выполнения."""
    todo_list = TodoList()
    task1 = Task("Task 1")
    task2 = Task("Task 2")
    task3 = Task("Task 3")
    task4 = Task("Task 4")
    
    todo_list.add_task(task1)
    todo_list.add_task(task2)
    todo_list.add_task(task3)
    todo_list.add_task(task4)
    
    task1.complete()
    task2.complete()
    
    assert todo_list.completion_percentage == 50.0  # Свойства пока нет!
```

#### 🟢 GREEN
```python
class TodoList:
    # ... предыдущий код ...
    
    def get_completed_tasks(self) -> List[Task]:
        """Получить список завершенных задач."""
        return [task for task in self._tasks if task.is_completed]
    
    def get_pending_tasks(self) -> List[Task]:
        """Получить список незавершенных задач."""
        return [task for task in self._tasks if not task.is_completed]
    
    @property
    def completion_percentage(self) -> float:
        """Процент выполнения задач."""
        if len(self._tasks) == 0:
            return 0.0
        
        completed_count = len(self.get_completed_tasks())
        return (completed_count / len(self._tasks)) * 100
```

## 🎯 Ключевые уроки из примеров

### 1. Начинайте с простого
```python
# ❌ Не пытайтесь сразу создать сложную иерархию
class AdvancedBankAccount(AbstractAccount, Auditable, Serializable):
    pass

# ✅ Начните с минимального
class BankAccount:
    def __init__(self, account_number):
        self.account_number = account_number
        self.balance = 0
```

### 2. Один тест = одна концепция
```python
# ❌ Слишком много проверок в одном тесте
def test_user_management():
    user = User("John")
    assert user.name == "John"
    user.change_email("new@email.com")
    assert user.email == "new@email.com"
    user.deactivate()
    assert not user.is_active

# ✅ Разделите на отдельные тесты
def test_user_creation():
    user = User("John")
    assert user.name == "John"

def test_user_email_change():
    user = User("John")
    user.change_email("new@email.com") 
    assert user.email == "new@email.com"
```

### 3. Рефакторинг — обязательная часть цикла
```python
# После зеленой фазы — всегда ищите возможности улучшения:
# - Дублирование кода
# - Магические числа
# - Длинные методы
# - Неясные имена
```

### 4. Тесты как документация
```python
def test_transfer_to_account_with_insufficient_funds_raises_error():
    """
    При попытке перевода суммы, превышающей баланс счета,
    должно возникать исключение ValueError с сообщением 
    'Insufficient funds'.
    """
    # Тест сам документирует поведение системы
```

## 🎯 Следующие шаги

В следующей главе мы изучим мокирование и изоляцию тестов — ключевые техники для тестирования сложных систем с внешними зависимостями.

---

**Следующая глава:** [Mock объекты и изоляция тестов](08_mocking.md)

*🛠 Практика — лучший учитель TDD!*
