# 🏦 Интерактивное упражнение: Банковская система с TDD

Создадим полноценную банковскую систему, применяя все принципы TDD на комплексном примере.

## 📋 Техническое задание

**Реализуйте банковскую систему** с следующей функциональностью:

### **Базовые операции:**
- ✅ Создание счета с начальным балансом
- ✅ Пополнение счета (депозит)
- ✅ Снятие средств (с проверкой баланса)
- ✅ Получение текущего баланса

### **Продвинутые функции:**
- 🔄 Перевод между счетами
- 🔄 История операций
- 🔄 Разные типы счетов (сберегательный, текущий)
- 🔄 Комиссии и лимиты

## 🎯 Этап 1: Базовый банковский счет

Начнем с создания простого банковского счета.

### 🔴 RED: Создание счета

**🔴 RED фаза**: Пишем первый тест

{{ create_exercise_form(
    "bank_account_red_1",
    "Создание первого RED теста для банковского счета",
    "Напишите тест, который будет падать, потому что класс BankAccount еще не существует.",
    """import pytest
from decimal import Decimal

def test_new_account_has_zero_balance():
    '''Новый счет имеет нулевой баланс'''
    account = BankAccount("ACC123")
    assert account.balance == Decimal("0.00")
    assert account.account_number == "ACC123"

def test_new_account_with_initial_balance():
    '''Новый счет может быть создан с начальным балансом'''
    initial_balance = Decimal("100.00")
    account = BankAccount("ACC456", initial_balance)
    assert account.balance == initial_balance
    assert account.account_number == "ACC456" """,
    [
        "Тест должен проверять создание счета с нулевым балансом",
        "Тест должен проверять создание счета с начальным балансом",
        "Тест должен проверять корректность номера счета"
    ]
) }}

❌ **Ожидаемая ошибка**: `NameError: name 'BankAccount' is not defined`

### 🟢 GREEN: Минимальная реализация

**🟢 GREEN фаза**: Создаем базовый класс

{{ create_exercise_form(
    "bank_account_green_1",
    "Создание минимальной GREEN реализации BankAccount",
    "Напишите минимальный код, который заставит тесты проходить. Начните с простейшей реализации.",
    """from decimal import Decimal

class BankAccount:
    def __init__(self, account_number: str, initial_balance: Decimal = Decimal("0.00")):
        self.account_number = account_number
        self.balance = initial_balance""",
    [
        "Создать класс BankAccount",
        "Добавить конструктор с account_number и initial_balance",
        "Установить начальный баланс (по умолчанию 0.00)"
    ]
) }}

✅ **Тесты проходят!** У нас есть базовая структура счета.

## 🎯 Этап 2: Операции с балансом

### 🔴 RED: Пополнение счета

**🔴 RED фаза**: Тест для депозита

{{ create_exercise_form(
    "bank_account_deposit_red",
    "Создание теста для пополнения счета",
    "Напишите тест для метода deposit, который должен увеличивать баланс на указанную сумму.",
    """def test_deposit_increases_balance():
    '''Пополнение счета увеличивает баланс'''
    account = BankAccount("ACC123")
    initial_balance = account.balance

    deposit_amount = Decimal("50.00")
    account.deposit(deposit_amount)

    assert account.balance == initial_balance + deposit_amount

def test_deposit_negative_amount_raises_error():
    '''Пополнение отрицательной суммой вызывает ошибку'''
    account = BankAccount("ACC123")

    with pytest.raises(ValueError, match="Amount must be positive"):
        account.deposit(Decimal("-10.00"))""",
    [
        "Тест должен проверять увеличение баланса после депозита",
        "Тест должен проверять обработку отрицательных сумм"
    ]
) }}

### 🟢 GREEN: Реализация депозита

**🟢 GREEN фаза**: Добавляем метод deposit

{{ create_exercise_form(
    "bank_account_deposit_green",
    "Реализация метода deposit",
    "Добавьте метод deposit в класс BankAccount с валидацией входных данных.",
    """from decimal import Decimal
from typing import Union

MoneyType = Union[int, float, str, Decimal]

class BankAccount:
    def __init__(self, account_number: str, initial_balance: Decimal = Decimal("0.00")):
        self.account_number = account_number
        self.balance = initial_balance

    def deposit(self, amount: MoneyType) -> None:
        '''Пополнение счета'''
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount_decimal""",
    [
        "Добавить метод deposit",
        "Конвертировать amount в Decimal",
        "Проверить что сумма положительная",
        "Увеличить баланс на указанную сумму"
    ]
) }}

## 🎯 Этап 3: Снятие средств

### 🔴 RED: Тест для снятия

**🔴 RED фаза**: Тест для метода withdraw

{{ create_exercise_form(
    "bank_account_withdraw_red",
    "Создание теста для снятия средств",
    "Напишите тест для метода withdraw, который должен уменьшать баланс и проверять достаточность средств.",
    """def test_withdraw_decreases_balance():
    '''Снятие средств уменьшает баланс'''
    account = BankAccount("ACC123", Decimal("100.00"))
    initial_balance = account.balance

    withdraw_amount = Decimal("30.00")
    account.withdraw(withdraw_amount)

    assert account.balance == initial_balance - withdraw_amount

def test_withdraw_insufficient_funds_raises_error():
    '''Снятие суммы больше баланса вызывает ошибку'''
    account = BankAccount("ACC123", Decimal("50.00"))

    with pytest.raises(ValueError, match="Insufficient funds"):
        account.withdraw(Decimal("100.00"))

def test_withdraw_negative_amount_raises_error():
    '''Снятие отрицательной суммы вызывает ошибку'''
    account = BankAccount("ACC123", Decimal("100.00"))

    with pytest.raises(ValueError, match="Amount must be positive"):
        account.withdraw(Decimal("-10.00"))""",
    [
        "Тест должен проверять уменьшение баланса",
        "Тест должен проверять недостаток средств",
        "Тест должен проверять отрицательные суммы"
    ]
) }}

### 🟢 GREEN: Реализация снятия

**🟢 GREEN фаза**: Добавляем метод withdraw

{{ create_exercise_form(
    "bank_account_withdraw_green",
    "Реализация метода withdraw",
    "Добавьте метод withdraw в класс BankAccount с полной валидацией.",
    """from decimal import Decimal
from typing import Union

MoneyType = Union[int, float, str, Decimal]

class BankAccount:
    def __init__(self, account_number: str, initial_balance: Decimal = Decimal("0.00")):
        self.account_number = account_number
        self.balance = initial_balance

    def deposit(self, amount: MoneyType) -> None:
        '''Пополнение счета'''
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount_decimal

    def withdraw(self, amount: MoneyType) -> None:
        '''Снятие средств со счета'''
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        if amount_decimal > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount_decimal""",
    [
        "Добавить метод withdraw",
        "Конвертировать amount в Decimal",
        "Проверить что сумма положительная",
        "Проверить достаточность средств",
        "Уменьшить баланс на указанную сумму"
    ]
) }}

## 🎯 Этап 4: Переводы между счетами

### 🔴 RED: Тест для переводов

**🔴 RED фаза**: Тест для метода transfer

{{ create_exercise_form(
    "bank_account_transfer_red",
    "Создание теста для переводов между счетами",
    "Напишите тест для метода transfer, который должен переводить деньги между двумя счетами.",
    """def test_transfer_between_accounts():
    '''Перевод денег между счетами'''
    account1 = BankAccount("ACC001", Decimal("200.00"))
    account2 = BankAccount("ACC002", Decimal("50.00"))

    transfer_amount = Decimal("75.00")
    account1.transfer(account2, transfer_amount)

    assert account1.balance == Decimal("125.00")  # 200 - 75
    assert account2.balance == Decimal("125.00")  # 50 + 75

def test_transfer_insufficient_funds_raises_error():
    '''Перевод при недостатке средств вызывает ошибку'''
    account1 = BankAccount("ACC001", Decimal("50.00"))
    account2 = BankAccount("ACC002", Decimal("100.00"))

    with pytest.raises(ValueError, match="Insufficient funds"):
        account1.transfer(account2, Decimal("100.00"))

def test_transfer_to_same_account_raises_error():
    '''Перевод на тот же счет вызывает ошибку'''
    account = BankAccount("ACC001", Decimal("100.00"))

    with pytest.raises(ValueError, match="Cannot transfer to same account"):
        account.transfer(account, Decimal("50.00"))""",
    [
        "Тест должен проверять успешный перевод",
        "Тест должен проверять недостаток средств",
        "Тест должен проверять перевод на тот же счет"
    ]
) }}

### 🟢 GREEN: Реализация переводов

**🟢 GREEN фаза**: Добавляем метод transfer

{{ create_exercise_form(
    "bank_account_transfer_green",
    "Реализация метода transfer",
    "Добавьте метод transfer в класс BankAccount для переводов между счетами.",
    """from decimal import Decimal
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

MoneyType = Union[int, float, str, Decimal]

class BankAccount:
    def __init__(self, account_number: str, initial_balance: Decimal = Decimal("0.00")):
        self.account_number = account_number
        self.balance = initial_balance

    def deposit(self, amount: MoneyType) -> None:
        '''Пополнение счета'''
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        self.balance += amount_decimal

    def withdraw(self, amount: MoneyType) -> None:
        '''Снятие средств со счета'''
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            raise ValueError("Amount must be positive")
        if amount_decimal > self.balance:
            raise ValueError("Insufficient funds")
        self.balance -= amount_decimal

    def transfer(self, to_account: 'Self', amount: MoneyType) -> None:
        '''Перевод средств на другой счет'''
        if to_account.account_number == self.account_number:
            raise ValueError("Cannot transfer to same account")

        # Используем существующий метод withdraw для валидации
        self.withdraw(amount)
        # Используем существующий метод deposit для пополнения
        to_account.deposit(amount)""",
    [
        "Добавить метод transfer",
        "Проверить что получатель не тот же счет",
        "Использовать существующие методы withdraw и deposit",
        "Обеспечить атомарность операции"
    ]
) }}

## 🎯 Этап 5: История операций (опционально)

Для тех, кто хочет углубить навыки TDD, добавим историю операций.

### 🔴 RED: Тест для истории

**🔴 RED фаза**: Тест для отслеживания операций

{{ create_exercise_form(
    "bank_account_history_red",
    "Создание теста для истории операций",
    "Напишите тест для отслеживания операций счета (депозиты, снятия, переводы).",
    """def test_account_tracks_deposit_history():
    '''Счет отслеживает операции депозита'''
    account = BankAccount("ACC123")

    account.deposit(Decimal("100.00"))
    account.deposit(Decimal("50.00"))

    history = account.get_transaction_history()
    assert len(history) == 2

    assert history[0]['type'] == 'deposit'
    assert history[0]['amount'] == Decimal("100.00")
    assert history[1]['type'] == 'deposit'
    assert history[1]['amount'] == Decimal("50.00")

def test_account_tracks_withdrawal_history():
    '''Счет отслеживает операции снятия'''
    account = BankAccount("ACC123", Decimal("100.00"))

    account.withdraw(Decimal("30.00"))

    history = account.get_transaction_history()
    assert len(history) == 1
    assert history[0]['type'] == 'withdrawal'
    assert history[0]['amount'] == Decimal("30.00")""",
    [
        "Тест должен проверять историю депозитов",
        "Тест должен проверять историю снятий",
        "Тест должен проверять корректность данных операций"
    ]
) }}

## 🎯 Резюме упражнения

В этом упражнении вы:

✅ **Применяли Red-Green-Refactor** на комплексном примере
✅ **Разрабатывали систему итеративно** от простого к сложному
✅ **Тестировали edge cases** (недостаток средств, отрицательные суммы)
✅ **Реализовали SOLID принципы** (single responsibility, dependency inversion)
✅ **Создавали поддерживаемый код** с помощью TDD

### 🔄 Следующие шаги для продвинутых:
- Добавьте разные типы счетов (SavingsAccount, CheckingAccount)
- Реализуйте комиссию за переводы
- Добавьте лимиты на операции
- Создайте Bank класс для управления счетами
- Добавьте многопоточную безопасность

### 📊 Итоговый результат:
У вас должна получиться система вроде этой:

```python
# Пример использования
account1 = BankAccount("ACC001", Decimal("1000.00"))
account2 = BankAccount("ACC002", Decimal("500.00"))

# Операции
account1.deposit(Decimal("200.00"))      # Баланс: 1200.00
account1.withdraw(Decimal("150.00"))     # Баланс: 1050.00
account1.transfer(account2, Decimal("300.00"))  # ACC001: 750.00, ACC002: 800.00

print(f"Account 1 balance: {account1.balance}")
print(f"Account 2 balance: {account2.balance}")
```

---

**[🏠 Вернуться к практическим примерам](../07_practical_examples.md)**
