#!/usr/bin/env python3
"""
Solution for E-commerce System Refactoring with Design Patterns
Module 02: Design Patterns - Complete Implementation

This solution demonstrates the application of multiple design patterns
to refactor a monolithic OrderManager class into a flexible, maintainable system.

Applied Patterns:
- Strategy Pattern (payment processing)
- Observer Pattern (notifications)
- Factory Pattern (order creation)
- Command Pattern (order operations)
- Decorator Pattern (order enhancements)
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Protocol, Optional
from datetime import datetime
from enum import Enum
import uuid
from dataclasses import dataclass, field
from decimal import Decimal


# =============================================================================
# DOMAIN MODELS
# =============================================================================


@dataclass
class Product:
    """Product domain model"""

    id: str
    name: str
    price: Decimal
    category: str
    stock_quantity: int = 0

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")


@dataclass
class OrderItem:
    """Order item domain model"""

    product: Product
    quantity: int
    unit_price: Decimal

    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.unit_price < 0:
            raise ValueError("Unit price cannot be negative")

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


class OrderStatus(Enum):
    """Order status enumeration"""

    CREATED = "created"
    CONFIRMED = "confirmed"
    PAID = "paid"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass
class Order:
    """Order domain model"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str = ""
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    total_amount: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")

    def add_item(self, item: OrderItem):
        """Add item to order"""
        self.items.append(item)
        self._recalculate_total()

    def _recalculate_total(self):
        """Recalculate order total"""
        subtotal = sum(item.subtotal for item in self.items)
        self.total_amount = subtotal - self.discount_amount + self.tax_amount

    def get_total_amount(self) -> Decimal:
        """Get total amount of the order"""
        return self.total_amount

    def get_description(self) -> str:
        """Get description of the order"""
        return f"Order {self.id}"


@dataclass
class Customer:
    """Customer domain model"""

    id: str
    name: str
    email: str
    phone: str = ""
    address: str = ""


# =============================================================================
# STRATEGY PATTERN - Payment Processing
# =============================================================================


class PaymentStrategy(ABC):
    """
    Abstract strategy for payment processing.

    💡 Простыми словами: Это интерфейс для разных способов оплаты.
    Strategy Pattern позволяет легко добавлять новые способы оплаты
    (карта, PayPal, криптовалюта) без изменения основного кода.

    Strategy Pattern:
    - ✅ Определяет семейство алгоритмов (способы оплаты)
    - ✅ Инкапсулирует каждый алгоритм
    - ✅ Делает их взаимозаменяемыми

    Example:
        >>> strategy = CreditCardPayment("1234-5678", 12, 2025)
        >>> result = strategy.process_payment(Decimal('100.00'), order, cvv="123")
        >>> print(result)
        True
    """

    @abstractmethod
    def process_payment(self, amount: Decimal, order: Order) -> bool:
        """
        Process payment for given amount.

        💡 Простыми словами: Обрабатывает платеж выбранным способом.
        Каждый способ оплаты реализует этот метод по-своему.

        Args:
            amount: Сумма платежа
            order: Заказ для оплаты

        Returns:
            bool: True если платеж успешен, False иначе
        """
        pass

    @abstractmethod
    def get_payment_method_name(self) -> str:
        """Get human-readable payment method name"""
        pass


class CreditCardPayment(PaymentStrategy):
    """Credit card payment strategy"""

    # PCI-DSS Compliance: CVV must never be persisted to comply with PCI-DSS requirements
    # CVV should only be used transiently during payment processing and never stored

    def __init__(self, card_number: str, expiry_month: int, expiry_year: int):
        # In production, these would be properly validated and secured
        self.card_number = self._mask_card_number(card_number)
        self.expiry_month = expiry_month
        self.expiry_year = expiry_year

    def process_payment(
        self, amount: Decimal, order: Order, cvv: str | None = None
    ) -> bool:
        """Process credit card payment"""
        print(f"💳 Processing credit card payment of ${amount}")
        print(f"💳 Card ending in: {self.card_number[-4:]}")
        print(f"💳 Order ID: {order.id}")

        # Simulate payment gateway API call
        try:
            # In production, integrate with real payment gateway
            if amount > 0:
                print(f"✅ Credit card payment successful: ${amount}")
                return True
            else:
                print(f"❌ Invalid payment amount: ${amount}")
                return False
        except Exception as e:
            print(f"❌ Credit card payment failed: {e}")
            return False

    def get_payment_method_name(self) -> str:
        return f"Credit Card ending in {self.card_number[-4:]}"

    def _mask_card_number(self, card_number: str) -> str:
        """Mask credit card number for security"""
        if len(card_number) < 4:
            return "****"
        return "*" * (len(card_number) - 4) + card_number[-4:]


class PayPalPayment(PaymentStrategy):
    """PayPal payment strategy"""

    def __init__(self, email: str):
        self.email = email

    def process_payment(self, amount: Decimal, order: Order) -> bool:
        """Process PayPal payment"""
        print(f"💰 Processing PayPal payment of ${amount}")
        print(f"💰 PayPal account: {self.email}")
        print(f"💰 Order ID: {order.id}")

        try:
            # Simulate PayPal API integration
            if amount > 0:
                print(f"✅ PayPal payment successful: ${amount}")
                return True
            else:
                print(f"❌ Invalid payment amount: ${amount}")
                return False
        except Exception as e:
            print(f"❌ PayPal payment failed: {e}")
            return False

    def get_payment_method_name(self) -> str:
        return f"PayPal ({self.email})"


class CryptocurrencyPayment(PaymentStrategy):
    """Cryptocurrency payment strategy"""

    def __init__(self, wallet_address: str, currency: str = "BTC"):
        self.wallet_address = wallet_address
        self.currency = currency

    def process_payment(self, amount: Decimal, order: Order) -> bool:
        """Process cryptocurrency payment"""
        print(f"₿ Processing {self.currency} payment of ${amount}")
        print(f"₿ Wallet: {self.wallet_address}")
        print(f"₿ Order ID: {order.id}")

        try:
            # Simulate blockchain API integration
            if amount > 0:
                print(f"✅ {self.currency} payment successful: ${amount}")
                return True
            else:
                print(f"❌ Invalid payment amount: ${amount}")
                return False
        except Exception as e:
            print(f"❌ {self.currency} payment failed: {e}")
            return False

    def get_payment_method_name(self) -> str:
        return f"{self.currency} ({self.wallet_address[:8]}...)"


# =============================================================================
# OBSERVER PATTERN - Notifications
# =============================================================================


class OrderObserver(ABC):
    """
    Abstract observer for order events.

    💡 Простыми словами: Это интерфейс для "подписчиков" на события заказа.
    Observer Pattern позволяет уведомлять разные сервисы (email, SMS, push)
    о событиях заказа без жесткой связи между ними.

    Observer Pattern:
    - ✅ Заказ (Subject) уведомляет всех наблюдателей
    - ✅ Наблюдатели (Observers) реагируют на события
    - ✅ Легко добавлять новых наблюдателей

    Example:
        >>> notifier = EmailNotifier()
        >>> order.add_observer(notifier)
        >>> order.confirm()  # Все наблюдатели получат уведомление
    """

    @abstractmethod
    def on_order_created(self, order: Order) -> None:
        """
        Handle order creation event.

        💡 Простыми словами: Вызывается, когда создается новый заказ.
        Каждый наблюдатель реагирует по-своему (отправляет email, SMS и т.д.).

        Args:
            order: Созданный заказ
        """
        pass

    @abstractmethod
    def on_order_confirmed(self, order: Order) -> None:
        """Handle order confirmation event"""
        pass

    @abstractmethod
    def on_order_paid(self, order: Order) -> None:
        """Handle payment confirmation event"""
        pass

    @abstractmethod
    def on_order_shipped(self, order: Order) -> None:
        """Handle order shipment event"""
        pass

    @abstractmethod
    def on_order_delivered(self, order: Order) -> None:
        """Handle order delivery event"""
        pass


class EmailNotifier(OrderObserver):
    """Email notification observer"""

    def __init__(self, customer_repository):
        self.customer_repository = customer_repository

    def on_order_created(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer:
            print(f"📧 Email sent to {customer.email}: Order {order.id} created")

    def on_order_confirmed(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer:
            print(f"📧 Email sent to {customer.email}: Order {order.id} confirmed")

    def on_order_paid(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer:
            print(
                f"📧 Email sent to {customer.email}: Payment confirmed for order {order.id}"
            )

    def on_order_shipped(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer:
            print(
                f"📧 Email sent to {customer.email}: Order {order.id} has been shipped"
            )

    def on_order_delivered(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer:
            print(
                f"📧 Email sent to {customer.email}: Order {order.id} has been delivered"
            )


class SMSNotifier(OrderObserver):
    """SMS notification observer"""

    def __init__(self, customer_repository):
        self.customer_repository = customer_repository

    def on_order_created(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer and customer.phone:
            print(f"📱 SMS sent to {customer.phone}: Order {order.id} created")

    def on_order_confirmed(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer and customer.phone:
            print(f"📱 SMS sent to {customer.phone}: Order {order.id} confirmed")

    def on_order_paid(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer and customer.phone:
            print(
                f"📱 SMS sent to {customer.phone}: Payment confirmed for order {order.id}"
            )

    def on_order_shipped(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer and customer.phone:
            print(f"📱 SMS sent to {customer.phone}: Order {order.id} shipped")

    def on_order_delivered(self, order: Order) -> None:
        customer = self.customer_repository.find_by_id(order.customer_id)
        if customer and customer.phone:
            print(f"📱 SMS sent to {customer.phone}: Order {order.id} delivered")


class PushNotifier(OrderObserver):
    """Push notification observer"""

    def __init__(self, customer_repository):
        self.customer_repository = customer_repository

    def on_order_created(self, order: Order) -> None:
        print(f"🔔 Push notification: Order {order.id} created")

    def on_order_confirmed(self, order: Order) -> None:
        print(f"🔔 Push notification: Order {order.id} confirmed")

    def on_order_paid(self, order: Order) -> None:
        print(f"🔔 Push notification: Payment confirmed for order {order.id}")

    def on_order_shipped(self, order: Order) -> None:
        print(f"🔔 Push notification: Order {order.id} shipped")

    def on_order_delivered(self, order: Order) -> None:
        print(f"🔔 Push notification: Order {order.id} delivered")


# =============================================================================
# FACTORY PATTERN - Order Creation
# =============================================================================


class OrderFactory:
    """
    Factory for creating different types of orders.

    💡 Простыми словами: Это "фабрика заказов" - создает заказы с нужными настройками.
    Factory Pattern скрывает сложность создания объектов и позволяет
    создавать разные типы заказов (обычный, VIP, оптовый) единым способом.

    Factory Pattern:
    - ✅ Инкапсулирует логику создания объектов
    - ✅ Упрощает создание сложных объектов
    - ✅ Централизует правила создания

    Example:
        >>> factory = OrderFactory()
        >>> order = factory.create_standard_order("customer-123", items)
        >>> print(order.id)
        'order-uuid-...'
    """

    @staticmethod
    def create_standard_order(customer_id: str, items: List[Dict[str, Any]]) -> Order:
        """Create a standard order"""
        order = Order(customer_id=customer_id)

        for item_data in items:
            product = Product(**item_data["product"])
            order_item = OrderItem(
                product=product,
                quantity=item_data["quantity"],
                unit_price=product.price,
            )
            order.add_item(order_item)

        return order

    @staticmethod
    def create_bulk_order(
        customer_id: str, items: List[Dict[str, Any]], bulk_discount: float = 0.1
    ) -> Order:
        """Create a bulk order with automatic discount"""
        order = OrderFactory.create_standard_order(customer_id, items)

        # Apply bulk discount
        subtotal = sum(item.subtotal for item in order.items)
        order.discount_amount = subtotal * Decimal(str(bulk_discount))
        order._recalculate_total()

        return order

    @staticmethod
    def create_subscription_order(
        customer_id: str,
        items: List[Dict[str, Any]],
        subscription_discount: float = 0.15,
    ) -> Order:
        """Create a subscription order with recurring billing"""
        order = OrderFactory.create_standard_order(customer_id, items)

        # Apply subscription discount
        subtotal = sum(item.subtotal for item in order.items)
        order.discount_amount = subtotal * Decimal(str(subscription_discount))
        order._recalculate_total()

        return order


# =============================================================================
# COMMAND PATTERN - Order Operations
# =============================================================================


class OrderCommand(ABC):
    """Abstract command for order operations"""

    @abstractmethod
    def execute(self) -> bool:
        """Execute the command"""
        pass

    @abstractmethod
    def undo(self) -> bool:
        """Undo the command (if possible)"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get command description"""
        pass


class ConfirmOrderCommand(OrderCommand):
    """Command to confirm an order"""

    def __init__(self, order: Order, inventory_service):
        self.order = order
        self.inventory_service = inventory_service
        self.previous_status: Optional[OrderStatus] = None

    def execute(self) -> bool:
        """Execute order confirmation"""
        if self.order.status != OrderStatus.CREATED:
            print(
                f"❌ Cannot confirm order {self.order.id}: Invalid status {self.order.status}"
            )
            return False

        # Check inventory availability
        for item in self.order.items:
            if not self.inventory_service.is_available(item.product.id, item.quantity):
                print(
                    f"❌ Cannot confirm order {self.order.id}: Insufficient stock for {item.product.name}"
                )
                return False

        # Reserve inventory
        for item in self.order.items:
            self.inventory_service.reserve_stock(item.product.id, item.quantity)

        self.previous_status = self.order.status
        self.order.status = OrderStatus.CONFIRMED
        print(f"✅ Order {self.order.id} confirmed")
        return True

    def undo(self) -> bool:
        """Undo order confirmation"""
        if self.previous_status:
            # Release reserved inventory
            for item in self.order.items:
                self.inventory_service.release_reserved_stock(
                    item.product.id, item.quantity
                )

            self.order.status = self.previous_status
            print(f"↩️ Order {self.order.id} confirmation undone")
            return True
        return False

    def get_description(self) -> str:
        return f"Confirm order {self.order.id}"


class CancelOrderCommand(OrderCommand):
    """Command to cancel an order"""

    def __init__(self, order: Order, inventory_service, refund_service):
        self.order = order
        self.inventory_service = inventory_service
        self.refund_service = refund_service
        self.previous_status: Optional[OrderStatus] = None

    def execute(self) -> bool:
        """Execute order cancellation"""
        if self.order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            print(
                f"❌ Cannot cancel order {self.order.id}: Order already shipped or delivered"
            )
            return False

        self.previous_status = self.order.status

        # Release inventory if order was confirmed
        if self.order.status in [
            OrderStatus.CONFIRMED,
            OrderStatus.PAID,
            OrderStatus.PROCESSING,
        ]:
            for item in self.order.items:
                self.inventory_service.release_reserved_stock(
                    item.product.id, item.quantity
                )

        # Process refund if order was paid
        if self.order.status in [OrderStatus.PAID, OrderStatus.PROCESSING]:
            self.refund_service.process_refund(self.order)

        self.order.status = OrderStatus.CANCELLED
        print(f"🚫 Order {self.order.id} cancelled")
        return True

    def undo(self) -> bool:
        """Undo order cancellation (may not always be possible)"""
        if self.previous_status and self.previous_status != OrderStatus.CANCELLED:
            self.order.status = self.previous_status
            print(f"↩️ Order {self.order.id} cancellation undone")
            return True
        return False

    def get_description(self) -> str:
        return f"Cancel order {self.order.id}"


class ShipOrderCommand(OrderCommand):
    """Command to ship an order"""

    def __init__(self, order: Order, shipping_service):
        self.order = order
        self.shipping_service = shipping_service
        self.previous_status = None
        self.tracking_number = None

    def execute(self) -> bool:
        """Execute order shipping"""
        if self.order.status != OrderStatus.PROCESSING:
            print(
                f"❌ Cannot ship order {self.order.id}: Invalid status {self.order.status}"
            )
            return False

        # Create shipment
        self.tracking_number = self.shipping_service.create_shipment(self.order)
        if not self.tracking_number:
            print(f"❌ Failed to create shipment for order {self.order.id}")
            return False

        self.previous_status = self.order.status
        self.order.status = OrderStatus.SHIPPED
        print(f"📦 Order {self.order.id} shipped. Tracking: {self.tracking_number}")
        return True

    def undo(self) -> bool:
        """Undo order shipping (if possible)"""
        if self.previous_status and self.tracking_number:
            if self.shipping_service.cancel_shipment(self.tracking_number):
                self.order.status = self.previous_status
                print(f"↩️ Order {self.order.id} shipping undone")
                return True
        return False

    def get_description(self) -> str:
        return f"Ship order {self.order.id}"


# =============================================================================
# DECORATOR PATTERN - Order Enhancements
# =============================================================================


class OrderComponent(Protocol):
    """Protocol for objects that can be decorated (Order or OrderDecorator)"""

    def get_total_amount(self) -> Decimal:
        """Get total amount"""
        ...

    def get_description(self) -> str:
        """Get description"""
        ...


class OrderDecorator(ABC):
    """Abstract decorator for order enhancements"""

    def __init__(self, wrapped: Order | "OrderDecorator"):
        self.wrapped = wrapped

    @abstractmethod
    def get_total_amount(self) -> Decimal:
        """Get total amount with decorations applied"""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get description of applied enhancements"""
        pass


class DiscountDecorator(OrderDecorator):
    """Decorator that applies discount to order"""

    def __init__(
        self,
        wrapped: Order | OrderDecorator,
        discount_percentage: float,
        description: str = "Discount",
    ):
        super().__init__(wrapped)
        self.discount_percentage = discount_percentage
        self.description = description

    def get_total_amount(self) -> Decimal:
        """Get total with discount applied"""
        base_total = self.wrapped.get_total_amount()
        discount = base_total * Decimal(str(self.discount_percentage))
        return base_total - discount

    def get_description(self) -> str:
        return f"{self.wrapped.get_description()} + {self.description} ({self.discount_percentage:.1%})"


class TaxDecorator(OrderDecorator):
    """Decorator that applies tax to order"""

    def __init__(
        self, wrapped: Order | OrderDecorator, tax_rate: float, tax_name: str = "Tax"
    ):
        super().__init__(wrapped)
        self.tax_rate = tax_rate
        self.tax_name = tax_name

    def get_total_amount(self) -> Decimal:
        """Get total with tax applied"""
        base_total = self.wrapped.get_total_amount()
        tax = base_total * Decimal(str(self.tax_rate))
        return base_total + tax

    def get_description(self) -> str:
        return (
            f"{self.wrapped.get_description()} + {self.tax_name} ({self.tax_rate:.1%})"
        )


class ShippingDecorator(OrderDecorator):
    """Decorator that applies shipping cost to order"""

    def __init__(
        self,
        wrapped: Order | OrderDecorator,
        shipping_cost: Decimal,
        shipping_method: str = "Standard",
    ):
        super().__init__(wrapped)
        self.shipping_cost = shipping_cost
        self.shipping_method = shipping_method

    def get_total_amount(self) -> Decimal:
        """Get total with shipping cost applied"""
        return self.wrapped.get_total_amount() + self.shipping_cost

    def get_description(self) -> str:
        return f"{self.wrapped.get_description()} + {self.shipping_method} Shipping (${self.shipping_cost})"


class InsuranceDecorator(OrderDecorator):
    """Decorator that applies insurance to order"""

    def __init__(self, wrapped: Order | OrderDecorator, insurance_rate: float = 0.02):
        super().__init__(wrapped)
        self.insurance_rate = insurance_rate

    def get_total_amount(self) -> Decimal:
        """Get total with insurance applied"""
        base_total = self.wrapped.get_total_amount()
        insurance_cost = base_total * Decimal(str(self.insurance_rate))
        return base_total + insurance_cost

    def get_description(self) -> str:
        return (
            f"{self.wrapped.get_description()} + Insurance ({self.insurance_rate:.1%})"
        )


# =============================================================================
# SERVICE LAYER - Orchestration
# =============================================================================


class CustomerRepository:
    """Simple in-memory customer repository"""

    def __init__(self):
        self.customers: Dict[str, Customer] = {}

    def save(self, customer: Customer) -> Customer:
        self.customers[customer.id] = customer
        return customer

    def find_by_id(self, customer_id: str) -> Customer | None:
        return self.customers.get(customer_id)


class InventoryService:
    """Simple inventory management service"""

    def __init__(self):
        self.stock: Dict[str, int] = {}
        self.reserved: Dict[str, int] = {}

    def set_stock(self, product_id: str, quantity: int):
        self.stock[product_id] = quantity
        if product_id not in self.reserved:
            self.reserved[product_id] = 0

    def is_available(self, product_id: str, quantity: int) -> bool:
        available = self.stock.get(product_id, 0) - self.reserved.get(product_id, 0)
        return available >= quantity

    def reserve_stock(self, product_id: str, quantity: int):
        if product_id not in self.reserved:
            self.reserved[product_id] = 0
        self.reserved[product_id] += quantity

    def release_reserved_stock(self, product_id: str, quantity: int):
        if product_id in self.reserved:
            self.reserved[product_id] = max(0, self.reserved[product_id] - quantity)


class ShippingService:
    """Simple shipping service"""

    def create_shipment(self, order: Order) -> str:
        """Create shipment and return tracking number"""
        tracking_number = f"TRACK{order.id[:8].upper()}"
        print(f"📦 Shipment created: {tracking_number}")
        return tracking_number

    def cancel_shipment(self, tracking_number: str) -> bool:
        """Cancel shipment"""
        print(f"🚫 Shipment cancelled: {tracking_number}")
        return True


class RefundService:
    """Simple refund service"""

    def process_refund(self, order: Order):
        """Process refund for order"""
        print(f"💰 Refund processed for order {order.id}: ${order.total_amount}")


class OrderService:
    """Enhanced order service using all design patterns"""

    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.observers: List[OrderObserver] = []
        self.command_history: List[OrderCommand] = []

        # Dependencies
        self.customer_repository = CustomerRepository()
        self.inventory_service = InventoryService()
        self.shipping_service = ShippingService()
        self.refund_service = RefundService()

    def add_observer(self, observer: OrderObserver):
        """Add order observer"""
        self.observers.append(observer)

    def remove_observer(self, observer: OrderObserver):
        """Remove order observer"""
        if observer in self.observers:
            self.observers.remove(observer)

    def _notify_observers(self, event_method: str, order: Order):
        """Notify all observers of order event"""
        for observer in self.observers:
            getattr(observer, event_method)(order)

    def create_order(
        self, order_type: str, customer_id: str, items: List[Dict[str, Any]], **kwargs
    ) -> Order:
        """Create order using Factory pattern"""
        if order_type == "standard":
            order = OrderFactory.create_standard_order(customer_id, items)
        elif order_type == "bulk":
            order = OrderFactory.create_bulk_order(
                customer_id, items, kwargs.get("bulk_discount", 0.1)
            )
        elif order_type == "subscription":
            order = OrderFactory.create_subscription_order(
                customer_id, items, kwargs.get("subscription_discount", 0.15)
            )
        else:
            raise ValueError(f"Unknown order type: {order_type}")

        self.orders[order.id] = order
        self._notify_observers("on_order_created", order)
        return order

    def apply_decorators(
        self, order: Order, decorators: List[Dict[str, Any]]
    ) -> Decimal:
        """Apply order decorations and return final total"""
        component: Order | OrderDecorator = order

        for decorator_config in decorators:
            decorator_type = decorator_config["type"]

            if decorator_type == "discount":
                component = DiscountDecorator(
                    component,
                    decorator_config["percentage"],
                    decorator_config.get("description", "Discount"),
                )
            elif decorator_type == "tax":
                component = TaxDecorator(
                    component,
                    decorator_config["rate"],
                    decorator_config.get("name", "Tax"),
                )
            elif decorator_type == "shipping":
                component = ShippingDecorator(
                    component,
                    Decimal(str(decorator_config["cost"])),
                    decorator_config.get("method", "Standard"),
                )
            elif decorator_type == "insurance":
                component = InsuranceDecorator(
                    component, decorator_config.get("rate", 0.02)
                )
            else:
                continue

        description = component.get_description()
        print(f"📋 Applied decorations to order {order.id}: {description}")
        return component.get_total_amount()

    def process_payment(
        self,
        order: Order,
        payment_strategy: PaymentStrategy,
        final_total: Decimal | None = None,
    ) -> bool:
        """Process payment using Strategy pattern"""
        amount = final_total or order.total_amount

        print(f"💳 Processing payment for order {order.id}")
        print(f"💳 Payment method: {payment_strategy.get_payment_method_name()}")
        print(f"💳 Amount: ${amount}")

        if payment_strategy.process_payment(amount, order):
            order.status = OrderStatus.PAID
            self._notify_observers("on_order_paid", order)
            return True
        return False

    def execute_command(self, command: OrderCommand) -> bool:
        """Execute order command using Command pattern"""
        print(f"🔧 Executing: {command.get_description()}")

        if command.execute():
            self.command_history.append(command)

            # Notify observers based on command type
            if isinstance(command, ConfirmOrderCommand):
                self._notify_observers("on_order_confirmed", command.order)
            elif isinstance(command, ShipOrderCommand):
                self._notify_observers("on_order_shipped", command.order)

            return True
        return False

    def undo_last_command(self) -> bool:
        """Undo the last executed command"""
        if self.command_history:
            last_command = self.command_history.pop()
            print(f"↩️ Undoing: {last_command.get_description()}")
            return last_command.undo()
        print("❌ No commands to undo")
        return False


# =============================================================================
# DEMONSTRATION
# =============================================================================


def main():
    """Demonstrate the refactored e-commerce system with design patterns"""
    print("🛒 E-commerce System with Design Patterns")
    print("=" * 60)

    # Initialize services
    order_service = OrderService()

    # Add observers (Observer Pattern)
    email_notifier = EmailNotifier(order_service.customer_repository)
    sms_notifier = SMSNotifier(order_service.customer_repository)
    push_notifier = PushNotifier(order_service.customer_repository)

    order_service.add_observer(email_notifier)
    order_service.add_observer(sms_notifier)
    order_service.add_observer(push_notifier)

    # Create test customer
    customer = Customer(
        id="customer_001",
        name="John Doe",
        email="john@example.com",
        phone="+1234567890",
        address="123 Main St",
    )
    order_service.customer_repository.save(customer)

    # Set up inventory
    order_service.inventory_service.set_stock("product_001", 100)
    order_service.inventory_service.set_stock("product_002", 50)

    # Create order items
    order_items = [
        {
            "product": {
                "id": "product_001",
                "name": "Laptop",
                "price": 1200.00,
                "category": "Electronics",
                "stock_quantity": 10,
            },
            "quantity": 1,
        },
        {
            "product": {
                "id": "product_002",
                "name": "Mouse",
                "price": 25.00,
                "category": "Electronics",
                "stock_quantity": 5,
            },
            "quantity": 2,
        },
    ]

    print("\n📦 Creating Order (Factory Pattern)")
    print("-" * 40)

    # Create order using Factory Pattern
    order = order_service.create_order("standard", customer.id, order_items)
    print(f"✅ Created order {order.id} with {len(order.items)} items")
    print(f"📊 Subtotal: ${order.total_amount}")

    print("\n🎨 Applying Decorators (Decorator Pattern)")
    print("-" * 40)

    # Apply decorators (Decorator Pattern)
    decorators = [
        {"type": "discount", "percentage": 0.1, "description": "New Customer Discount"},
        {"type": "tax", "rate": 0.08, "name": "Sales Tax"},
        {"type": "shipping", "cost": 15.99, "method": "Express"},
        {"type": "insurance", "rate": 0.02},
    ]

    final_total = order_service.apply_decorators(order, decorators)
    print(f"💰 Final total: ${final_total}")

    print("\n🔧 Executing Commands (Command Pattern)")
    print("-" * 40)

    # Confirm order using Command Pattern
    confirm_command = ConfirmOrderCommand(order, order_service.inventory_service)
    order_service.execute_command(confirm_command)

    print("\n💳 Processing Payment (Strategy Pattern)")
    print("-" * 40)

    # Process payment using Strategy Pattern
    payment_strategies = [
        CreditCardPayment("1234567890123456", 12, 2025),
        PayPalPayment("john@example.com"),
        CryptocurrencyPayment("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa", "BTC"),
    ]

    # Use credit card for this demo
    payment_strategy = payment_strategies[0]
    success = order_service.process_payment(order, payment_strategy, final_total)

    if success:
        # Move to processing
        order.status = OrderStatus.PROCESSING

        # Ship order using Command Pattern
        ship_command = ShipOrderCommand(order, order_service.shipping_service)
        order_service.execute_command(ship_command)

    print("\n📊 Order Summary")
    print("-" * 40)
    print(f"Order ID: {order.id}")
    print(f"Customer: {customer.name}")
    print(f"Status: {order.status.value}")
    print(f"Items: {len(order.items)}")
    print(f"Final Total: ${final_total}")

    print("\n🔄 Testing Command Undo")
    print("-" * 40)

    # Demonstrate command undo
    order_service.undo_last_command()  # Undo shipping

    print(f"Order status after undo: {order.status.value}")

    print("\n" + "=" * 60)
    print("🎉 Design Patterns Demonstration Complete!")
    print("\nPatterns Applied:")
    print("✅ Strategy Pattern - Multiple payment methods")
    print("✅ Observer Pattern - Event-driven notifications")
    print("✅ Factory Pattern - Order creation")
    print("✅ Command Pattern - Order operations with undo")
    print("✅ Decorator Pattern - Order enhancements")
    print("\nBenefits Achieved:")
    print("🚀 Flexible payment processing")
    print("🚀 Decoupled notification system")
    print("🚀 Standardized order creation")
    print("🚀 Reversible operations")
    print("🚀 Composable order modifications")


if __name__ == "__main__":
    main()
