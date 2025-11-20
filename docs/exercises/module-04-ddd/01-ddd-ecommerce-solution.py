#!/usr/bin/env python3
"""
Solution for DDD E-commerce Domain Modeling
Module 04: Domain-Driven Design - Complete Implementation

This solution demonstrates comprehensive Domain-Driven Design implementation
for an e-commerce platform, showcasing:
- Strategic Design (Bounded Contexts, Ubiquitous Language)
- Tactical Design (Entities, Value Objects, Aggregates, Domain Services)
- Domain Events and Event Sourcing
- Context Mapping and Integration Patterns

Bounded Contexts:
- Product Catalog Context
- Order Management Context
- Customer Management Context
- Payment Context
- Inventory Context
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal
import uuid
from collections import defaultdict


# =============================================================================
# SHARED KERNEL - Common Domain Elements
# =============================================================================


class DomainEvent(ABC):
    """Base class for all domain events"""

    def __init__(self):
        self.event_id = str(uuid.uuid4())
        self.occurred_at = datetime.now(timezone.utc)
        self.version = 1

    @abstractmethod
    def get_event_type(self) -> str:
        pass


class DomainException(Exception):
    """Base exception for domain-related errors"""

    pass


class BusinessRule(ABC):
    """Base class for business rules validation"""

    def __init__(self, message: str):
        self.message = message

    @abstractmethod
    def is_satisfied(self, **kwargs) -> bool:
        pass


# Value Objects for Shared Kernel
@dataclass(frozen=True)
class Money:
    """
    Money value object with currency support.

    💡 Простыми словами: Это "объект-значение" для денег. Value Object в DDD -
    это объект, который определяется своими значениями, а не идентичностью.
    Два объекта Money с одинаковой суммой и валютой считаются равными.

    Value Object (DDD Tactical Pattern):
    - ✅ Неизменяемый (immutable) - frozen=True
    - ✅ Определяется значениями (amount, currency)
    - ✅ Не имеет идентичности (нет ID)
    - ✅ Может содержать бизнес-логику (add, multiply)

    Example:
        >>> price1 = Money(Decimal('100.00'), 'USD')
        >>> price2 = Money(Decimal('100.00'), 'USD')
        >>> print(price1 == price2)  # True - равны по значениям
        True
        >>> total = price1.add(Money(Decimal('50.00'), 'USD'))
        >>> print(total.amount)
        150.00
    """

    amount: Decimal
    currency: str = "USD"

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("Money amount cannot be negative")
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3-letter ISO code")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)

    def multiply(self, factor: Union[int, Decimal]) -> "Money":
        return Money(self.amount * Decimal(str(factor)), self.currency)

    def is_zero(self) -> bool:
        return self.amount == 0

    def is_positive(self) -> bool:
        return self.amount > 0


@dataclass(frozen=True)
class CustomerId:
    """Customer ID value object"""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Customer ID cannot be empty")


@dataclass(frozen=True)
class ProductId:
    """Product ID value object"""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Product ID cannot be empty")


@dataclass(frozen=True)
class OrderId:
    """Order ID value object"""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) == 0:
            raise ValueError("Order ID cannot be empty")


# =============================================================================
# CUSTOMER MANAGEMENT BOUNDED CONTEXT
# =============================================================================


class CustomerType(Enum):
    REGULAR = "regular"
    PREMIUM = "premium"
    VIP = "vip"


@dataclass(frozen=True)
class Email:
    """Email value object with validation"""

    value: str

    def __post_init__(self):
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email format: {self.value}")

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email.split("@")[1]


@dataclass(frozen=True)
class Address:
    """Address value object"""

    street: str
    city: str
    postal_code: str
    country: str

    def __post_init__(self):
        if not all([self.street, self.city, self.postal_code, self.country]):
            raise ValueError("All address fields are required")


class Customer:
    """
    Customer aggregate root.

    💡 Простыми словами: Это "агрегат" клиента - главный объект, который управляет
    всеми связанными данными клиента. Aggregate в DDD - это группа связанных объектов,
    которые рассматриваются как единое целое.

    Aggregate (DDD Tactical Pattern):
    - ✅ Aggregate Root - единственная точка входа (Customer)
    - ✅ Инкапсулирует бизнес-правила (record_purchase, _update_customer_type)
    - ✅ Управляет доменными событиями (CustomerPurchaseRecorded, CustomerTypeChanged)
    - ✅ Обеспечивает консистентность данных

    Example:
        >>> customer_id = CustomerId("cust-123")
        >>> email = Email("john@example.com")
        >>> customer = Customer(customer_id, email, "John Doe")
        >>> customer.record_purchase(Money(Decimal('5000.00')))
        >>> print(customer.type)  # Может измениться на PREMIUM
    """

    def __init__(self, customer_id: CustomerId, email: Email, name: str):
        self._id = customer_id
        self._email = email
        self._name = name
        self._type = CustomerType.REGULAR
        self._registration_date = datetime.now(timezone.utc)
        self._addresses: List[Address] = []
        self._total_spent = Money(Decimal("0"))
        self._domain_events: List[DomainEvent] = []

    @property
    def id(self) -> CustomerId:
        return self._id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def name(self) -> str:
        return self._name

    @property
    def type(self) -> CustomerType:
        return self._type

    @property
    def total_spent(self) -> Money:
        return self._total_spent

    def add_address(self, address: Address):
        """Add new address to customer"""
        if address not in self._addresses:
            self._addresses.append(address)

    def record_purchase(self, amount: Money):
        """Record customer purchase and potentially upgrade status"""
        self._total_spent = self._total_spent.add(amount)
        self._update_customer_type()

        # Domain event
        self._domain_events.append(
            CustomerPurchaseRecorded(self._id, amount, self._total_spent)
        )

    def _update_customer_type(self):
        """Business rule: Update customer type based on spending"""
        if self._total_spent.amount >= Decimal("10000"):
            if self._type != CustomerType.VIP:
                old_type = self._type
                self._type = CustomerType.VIP
                self._domain_events.append(
                    CustomerTypeChanged(self._id, old_type, self._type)
                )
        elif self._total_spent.amount >= Decimal("1000"):
            if self._type != CustomerType.PREMIUM:
                previous_type: CustomerType = self._type
                self._type = CustomerType.PREMIUM
                self._domain_events.append(
                    CustomerTypeChanged(self._id, previous_type, self._type)
                )

    def get_discount_rate(self) -> Decimal:
        """Business rule: Discount based on customer type"""
        discount_rates = {
            CustomerType.REGULAR: Decimal("0.00"),
            CustomerType.PREMIUM: Decimal("0.05"),
            CustomerType.VIP: Decimal("0.10"),
        }
        return discount_rates[self._type]

    def get_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


class CustomerPurchaseRecorded(DomainEvent):
    def __init__(
        self, customer_id: CustomerId, purchase_amount: Money, total_spent: Money
    ):
        super().__init__()
        self.customer_id = customer_id
        self.purchase_amount = purchase_amount
        self.total_spent = total_spent

    def get_event_type(self) -> str:
        return "CustomerPurchaseRecorded"


class CustomerTypeChanged(DomainEvent):
    def __init__(
        self, customer_id: CustomerId, old_type: CustomerType, new_type: CustomerType
    ):
        super().__init__()
        self.customer_id = customer_id
        self.old_type = old_type
        self.new_type = new_type

    def get_event_type(self) -> str:
        return "CustomerTypeChanged"


# =============================================================================
# PRODUCT CATALOG BOUNDED CONTEXT
# =============================================================================


class ProductCategory(Enum):
    ELECTRONICS = "electronics"
    BOOKS = "books"
    CLOTHING = "clothing"
    HOME = "home"
    SPORTS = "sports"


@dataclass(frozen=True)
class ProductName:
    """Product name value object"""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 3:
            raise ValueError("Product name must be at least 3 characters")


@dataclass(frozen=True)
class ProductDescription:
    """Product description value object"""

    value: str

    def __post_init__(self):
        if len(self.value) > 1000:
            raise ValueError("Product description cannot exceed 1000 characters")


class Product:
    """Product aggregate root"""

    def __init__(
        self,
        product_id: ProductId,
        name: ProductName,
        price: Money,
        category: ProductCategory,
    ):
        self._id = product_id
        self._name = name
        self._price = price
        self._category = category
        self._description: Optional[ProductDescription] = None
        self._is_active = True
        self._created_at = datetime.now(timezone.utc)
        self._domain_events: List[DomainEvent] = []

    @property
    def id(self) -> ProductId:
        return self._id

    @property
    def name(self) -> ProductName:
        return self._name

    @property
    def price(self) -> Money:
        return self._price

    @property
    def category(self) -> ProductCategory:
        return self._category

    @property
    def is_active(self) -> bool:
        return self._is_active

    def update_price(self, new_price: Money):
        """Update product price"""
        if new_price.amount <= 0:
            raise DomainException("Product price must be positive")

        old_price = self._price
        self._price = new_price

        self._domain_events.append(ProductPriceChanged(self._id, old_price, new_price))

    def activate(self):
        """Activate product for sale"""
        if not self._is_active:
            self._is_active = True
            self._domain_events.append(ProductActivated(self._id))

    def deactivate(self):
        """Deactivate product from sale"""
        if self._is_active:
            self._is_active = False
            self._domain_events.append(ProductDeactivated(self._id))

    def set_description(self, description: ProductDescription):
        """Set product description"""
        self._description = description

    def get_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


class ProductPriceChanged(DomainEvent):
    def __init__(self, product_id: ProductId, old_price: Money, new_price: Money):
        super().__init__()
        self.product_id = product_id
        self.old_price = old_price
        self.new_price = new_price

    def get_event_type(self) -> str:
        return "ProductPriceChanged"


class ProductActivated(DomainEvent):
    def __init__(self, product_id: ProductId):
        super().__init__()
        self.product_id = product_id

    def get_event_type(self) -> str:
        return "ProductActivated"


class ProductDeactivated(DomainEvent):
    def __init__(self, product_id: ProductId):
        super().__init__()
        self.product_id = product_id

    def get_event_type(self) -> str:
        return "ProductDeactivated"


# =============================================================================
# ORDER MANAGEMENT BOUNDED CONTEXT
# =============================================================================


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class Quantity:
    """Quantity value object"""

    value: int

    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("Quantity must be positive")

    def multiply(self, factor: int) -> "Quantity":
        return Quantity(self.value * factor)


class OrderItem:
    """Order item entity"""

    def __init__(self, product_id: ProductId, quantity: Quantity, unit_price: Money):
        self._product_id = product_id
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def product_id(self) -> ProductId:
        return self._product_id

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def unit_price(self) -> Money:
        return self._unit_price

    def calculate_total(self) -> Money:
        """Calculate total price for this order item"""
        return self._unit_price.multiply(self._quantity.value)

    def update_quantity(self, new_quantity: Quantity):
        """Update item quantity"""
        self._quantity = new_quantity


class OrderTotalMustBePositiveRule(BusinessRule):
    """Business rule: Order total must be positive"""

    def __init__(self):
        super().__init__("Order total must be positive")

    def is_satisfied(self, **kwargs) -> bool:
        total: Optional[Money] = kwargs.get("total")
        if total is None or not isinstance(total, Money):
            return False
        return total.is_positive()


class MaxOrderItemsRule(BusinessRule):
    """Business rule: Maximum 50 items per order"""

    def __init__(self):
        super().__init__("Order cannot have more than 50 items")

    def is_satisfied(self, **kwargs) -> bool:
        items_count: int = kwargs.get("items_count", 0)
        return items_count <= 50


class Order:
    """Order aggregate root"""

    def __init__(self, order_id: OrderId, customer_id: CustomerId):
        self._id = order_id
        self._customer_id = customer_id
        self._items: List[OrderItem] = []
        self._status = OrderStatus.PENDING
        self._order_date = datetime.now(timezone.utc)
        self._domain_events: List[DomainEvent] = []
        self._shipping_address: Optional[Address] = None
        self._discount_amount = Money(Decimal("0"))

    @property
    def id(self) -> OrderId:
        return self._id

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def items(self) -> List[OrderItem]:
        return self._items.copy()

    def add_item(self, product_id: ProductId, quantity: Quantity, unit_price: Money):
        """Add item to order"""
        # Check business rules
        if not MaxOrderItemsRule().is_satisfied(items_count=len(self._items) + 1):
            raise DomainException("Cannot add more items to order")

        # Check if item already exists
        existing_item = self._find_item(product_id)
        if existing_item:
            new_quantity = Quantity(existing_item.quantity.value + quantity.value)
            existing_item.update_quantity(new_quantity)
        else:
            self._items.append(OrderItem(product_id, quantity, unit_price))

        self._domain_events.append(OrderItemAdded(self._id, product_id, quantity))

    def remove_item(self, product_id: ProductId):
        """Remove item from order"""
        item = self._find_item(product_id)
        if item:
            self._items.remove(item)
            self._domain_events.append(OrderItemRemoved(self._id, product_id))

    def _find_item(self, product_id: ProductId) -> Optional[OrderItem]:
        """Find order item by product ID"""
        for item in self._items:
            if item.product_id.value == product_id.value:
                return item
        return None

    def set_shipping_address(self, address: Address):
        """Set shipping address"""
        self._shipping_address = address

    def apply_discount(self, discount_amount: Money):
        """Apply discount to order"""
        if discount_amount.amount < 0:
            raise DomainException("Discount amount cannot be negative")

        self._discount_amount = discount_amount
        self._domain_events.append(OrderDiscountApplied(self._id, discount_amount))

    def calculate_subtotal(self) -> Money:
        """Calculate order subtotal"""
        if not self._items:
            return Money(Decimal("0"))

        total = Money(Decimal("0"))
        for item in self._items:
            total = total.add(item.calculate_total())

        return total

    def calculate_total(self) -> Money:
        """Calculate final order total"""
        subtotal = self.calculate_subtotal()
        total = Money(subtotal.amount - self._discount_amount.amount)

        # Validate business rule
        if not OrderTotalMustBePositiveRule().is_satisfied(total=total):
            raise DomainException("Order total must be positive after discount")

        return total

    def confirm(self):
        """Confirm the order"""
        if self._status != OrderStatus.PENDING:
            raise DomainException("Only pending orders can be confirmed")

        if not self._items:
            raise DomainException("Cannot confirm order without items")

        if not self._shipping_address:
            raise DomainException("Shipping address is required")

        self._status = OrderStatus.CONFIRMED
        self._domain_events.append(OrderConfirmed(self._id, self.calculate_total()))

    def mark_as_paid(self):
        """Mark order as paid"""
        if self._status != OrderStatus.CONFIRMED:
            raise DomainException("Only confirmed orders can be marked as paid")

        self._status = OrderStatus.PAID
        self._domain_events.append(OrderPaid(self._id, self.calculate_total()))

    def ship(self):
        """Ship the order"""
        if self._status != OrderStatus.PAID:
            raise DomainException("Only paid orders can be shipped")

        self._status = OrderStatus.SHIPPED
        self._domain_events.append(OrderShipped(self._id))

    def cancel(self, reason: str):
        """Cancel the order"""
        if self._status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise DomainException("Cannot cancel shipped or delivered orders")

        self._status = OrderStatus.CANCELLED
        self._domain_events.append(OrderCancelled(self._id, reason))

    def get_domain_events(self) -> List[DomainEvent]:
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


# Order Domain Events
class OrderItemAdded(DomainEvent):
    def __init__(self, order_id: OrderId, product_id: ProductId, quantity: Quantity):
        super().__init__()
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity

    def get_event_type(self) -> str:
        return "OrderItemAdded"


class OrderItemRemoved(DomainEvent):
    def __init__(self, order_id: OrderId, product_id: ProductId):
        super().__init__()
        self.order_id = order_id
        self.product_id = product_id

    def get_event_type(self) -> str:
        return "OrderItemRemoved"


class OrderConfirmed(DomainEvent):
    def __init__(self, order_id: OrderId, total_amount: Money):
        super().__init__()
        self.order_id = order_id
        self.total_amount = total_amount

    def get_event_type(self) -> str:
        return "OrderConfirmed"


class OrderPaid(DomainEvent):
    def __init__(self, order_id: OrderId, amount: Money):
        super().__init__()
        self.order_id = order_id
        self.amount = amount

    def get_event_type(self) -> str:
        return "OrderPaid"


class OrderShipped(DomainEvent):
    def __init__(self, order_id: OrderId):
        super().__init__()
        self.order_id = order_id

    def get_event_type(self) -> str:
        return "OrderShipped"


class OrderCancelled(DomainEvent):
    def __init__(self, order_id: OrderId, reason: str):
        super().__init__()
        self.order_id = order_id
        self.reason = reason

    def get_event_type(self) -> str:
        return "OrderCancelled"


class OrderDiscountApplied(DomainEvent):
    def __init__(self, order_id: OrderId, discount_amount: Money):
        super().__init__()
        self.order_id = order_id
        self.discount_amount = discount_amount

    def get_event_type(self) -> str:
        return "OrderDiscountApplied"


# =============================================================================
# DOMAIN SERVICES
# =============================================================================


class PricingService:
    """Domain service for pricing calculations"""

    def __init__(self, customer_repository):
        self._customer_repository = customer_repository

    def calculate_discounted_price(
        self, customer_id: CustomerId, original_price: Money
    ) -> Money:
        """Calculate price with customer-specific discount"""
        customer = self._customer_repository.find_by_id(customer_id)
        if not customer:
            return original_price

        discount_rate = customer.get_discount_rate()
        discount_amount = original_price.multiply(discount_rate)

        return Money(original_price.amount - discount_amount.amount)


class OrderProcessingService:
    """Domain service for complex order processing"""

    def __init__(self, customer_repository, product_repository, pricing_service):
        self._customer_repository = customer_repository
        self._product_repository = product_repository
        self._pricing_service = pricing_service

    def create_order_from_cart(
        self, customer_id: CustomerId, cart_items: List[Dict[str, Any]]
    ) -> Order:
        """Create order from shopping cart items"""
        order = Order(OrderId(str(uuid.uuid4())), customer_id)

        for cart_item in cart_items:
            product_id = ProductId(cart_item["product_id"])
            quantity = Quantity(cart_item["quantity"])

            # Get product to verify price
            product = self._product_repository.find_by_id(product_id)
            if not product or not product.is_active:
                continue

            # Calculate discounted price
            unit_price = self._pricing_service.calculate_discounted_price(
                customer_id, product.price
            )

            order.add_item(product_id, quantity, unit_price)

        return order

    def apply_automatic_discounts(self, order: Order):
        """Apply automatic discounts based on business rules"""
        subtotal = order.calculate_subtotal()

        # Business rule: $50 discount for orders over $1000 (check higher threshold first)
        if subtotal.amount >= Decimal("1000"):
            discount = Money(Decimal("50"))
            order.apply_discount(discount)

        # Business rule: 5% discount for orders over $500
        elif subtotal.amount >= Decimal("500"):
            discount = subtotal.multiply(Decimal("0.05"))
            order.apply_discount(discount)


# =============================================================================
# REPOSITORIES (Interfaces)
# =============================================================================


class ICustomerRepository(ABC):
    @abstractmethod
    def find_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        pass

    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[Customer]:
        pass

    @abstractmethod
    def save(self, customer: Customer) -> None:
        pass


class IProductRepository(ABC):
    @abstractmethod
    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        pass

    @abstractmethod
    def find_by_category(self, category: ProductCategory) -> List[Product]:
        pass

    @abstractmethod
    def save(self, product: Product) -> None:
        pass


class IOrderRepository(ABC):
    @abstractmethod
    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        pass

    @abstractmethod
    def find_by_customer(self, customer_id: CustomerId) -> List[Order]:
        pass

    @abstractmethod
    def save(self, order: Order) -> None:
        pass


# =============================================================================
# EVENT SOURCING AND DOMAIN EVENT HANDLING
# =============================================================================


class DomainEventStore:
    """Simple in-memory event store for demonstration"""

    def __init__(self):
        self._events: List[DomainEvent] = []
        self._streams: Dict[str, List[DomainEvent]] = defaultdict(list)

    def append_event(self, stream_id: str, event: DomainEvent):
        """Append event to stream"""
        self._events.append(event)
        self._streams[stream_id].append(event)
        print(f"📝 Event stored: {event.get_event_type()} for stream {stream_id}")

    def get_events_for_stream(self, stream_id: str) -> List[DomainEvent]:
        """Get all events for a specific stream"""
        return self._streams[stream_id].copy()

    def get_all_events(self) -> List[DomainEvent]:
        """Get all events across all streams"""
        return self._events.copy()


class DomainEventPublisher:
    """Domain event publisher for handling domain events"""

    def __init__(self, event_store: DomainEventStore):
        self._event_store = event_store
        self._handlers: Dict[str, List[Callable[[DomainEvent], None]]] = defaultdict(
            list
        )

    def register_handler(self, event_type: str, handler: Callable[[DomainEvent], None]):
        """Register event handler"""
        self._handlers[event_type].append(handler)
        print(f"📋 Registered handler for {event_type}")

    def publish(self, aggregate_id: str, events: List[DomainEvent]):
        """Publish domain events"""
        for event in events:
            # Store event
            self._event_store.append_event(aggregate_id, event)

            # Handle event
            event_type = event.get_event_type()
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    print(f"❌ Error handling {event_type}: {e}")


# Event Handlers
class CustomerEventHandler:
    """Handler for customer-related events"""

    def handle_customer_purchase_recorded(self, event: CustomerPurchaseRecorded) -> None:
        """Handle customer purchase recorded event"""
        print(
            f"📊 Customer {event.customer_id.value} purchased ${event.purchase_amount.amount}"
        )
        print(f"📈 Total spent: ${event.total_spent.amount}")

    def handle_customer_type_changed(self, event: CustomerTypeChanged) -> None:
        """Handle customer type change event"""
        print(
            f"🎉 Customer {event.customer_id.value} upgraded: {event.old_type.value} → {event.new_type.value}"
        )


class OrderEventHandler:
    """Handler for order-related events"""

    def handle_order_confirmed(self, event: OrderConfirmed) -> None:
        """Handle order confirmed event"""
        print(
            f"✅ Order {event.order_id.value} confirmed - Total: ${event.total_amount.amount}"
        )

    def handle_order_paid(self, event: OrderPaid) -> None:
        """Handle order paid event"""
        print(
            f"💳 Payment received for order {event.order_id.value} - Amount: ${event.amount.amount}"
        )

    def handle_order_shipped(self, event: OrderShipped) -> None:
        """Handle order shipped event"""
        print(f"📦 Order {event.order_id.value} has been shipped")


# =============================================================================
# IN-MEMORY REPOSITORY IMPLEMENTATIONS (FOR DEMO)
# =============================================================================


class InMemoryCustomerRepository(ICustomerRepository):
    """In-memory customer repository for demonstration"""

    def __init__(self):
        self._customers: Dict[str, Customer] = {}

    def find_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        return self._customers.get(customer_id.value)

    def find_by_email(self, email: Email) -> Optional[Customer]:
        for customer in self._customers.values():
            if customer.email.value == email.value:
                return customer
        return None

    def save(self, customer: Customer) -> None:
        self._customers[customer.id.value] = customer


class InMemoryProductRepository(IProductRepository):
    """In-memory product repository for demonstration"""

    def __init__(self):
        self._products: Dict[str, Product] = {}

    def find_by_id(self, product_id: ProductId) -> Optional[Product]:
        return self._products.get(product_id.value)

    def find_by_category(self, category: ProductCategory) -> List[Product]:
        return [p for p in self._products.values() if p.category == category]

    def save(self, product: Product) -> None:
        self._products[product.id.value] = product


class InMemoryOrderRepository(IOrderRepository):
    """In-memory order repository for demonstration"""

    def __init__(self):
        self._orders: Dict[str, Order] = {}

    def find_by_id(self, order_id: OrderId) -> Optional[Order]:
        return self._orders.get(order_id.value)

    def find_by_customer(self, customer_id: CustomerId) -> List[Order]:
        return [
            o for o in self._orders.values() if o.customer_id.value == customer_id.value
        ]

    def save(self, order: Order) -> None:
        self._orders[order.id.value] = order


# =============================================================================
# APPLICATION SERVICE (Use Case Layer)
# =============================================================================


class ECommerceService:
    """Application service orchestrating domain operations"""

    def __init__(
        self,
        customer_repo: ICustomerRepository,
        product_repo: IProductRepository,
        order_repo: IOrderRepository,
        event_publisher: DomainEventPublisher,
    ):
        self._customer_repo = customer_repo
        self._product_repo = product_repo
        self._order_repo = order_repo
        self._event_publisher = event_publisher

        # Domain services
        self._pricing_service = PricingService(customer_repo)
        self._order_processing_service = OrderProcessingService(
            customer_repo, product_repo, self._pricing_service
        )

    def register_customer(self, email_str: str, name: str) -> CustomerId:
        """Register new customer"""
        customer_id = CustomerId(str(uuid.uuid4()))
        email = Email(email_str)

        # Check if customer exists
        existing = self._customer_repo.find_by_email(email)
        if existing:
            raise DomainException(f"Customer with email {email_str} already exists")

        customer = Customer(customer_id, email, name)
        self._customer_repo.save(customer)

        print(f"👤 Customer registered: {name} ({email_str})")
        return customer_id

    def create_product(
        self, name_str: str, price_amount: str, category_str: str
    ) -> ProductId:
        """Create new product"""
        product_id = ProductId(str(uuid.uuid4()))
        name = ProductName(name_str)
        price = Money(Decimal(price_amount))
        category = ProductCategory(category_str)

        product = Product(product_id, name, price, category)
        self._product_repo.save(product)

        # Publish events
        events = product.get_domain_events()
        self._event_publisher.publish(product_id.value, events)

        print(f"📦 Product created: {name_str} - ${price_amount}")
        return product_id

    def place_order(
        self,
        customer_id: CustomerId,
        cart_items: List[Dict[str, Any]],
        shipping_address: Dict[str, str],
    ) -> OrderId:
        """Place new order"""
        # Create order from cart
        order = self._order_processing_service.create_order_from_cart(
            customer_id, cart_items
        )

        # Set shipping address
        address = Address(
            street=shipping_address["street"],
            city=shipping_address["city"],
            postal_code=shipping_address["postal_code"],
            country=shipping_address["country"],
        )
        order.set_shipping_address(address)

        # Apply automatic discounts
        self._order_processing_service.apply_automatic_discounts(order)

        # Confirm order
        order.confirm()

        # Save order
        self._order_repo.save(order)

        # Publish events
        events = order.get_domain_events()
        self._event_publisher.publish(order.id.value, events)

        print(
            f"🛒 Order placed: {order.id.value} - Total: ${order.calculate_total().amount}"
        )
        return order.id

    def process_payment(self, order_id: OrderId) -> bool:
        """Process order payment"""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise DomainException("Order not found")

        try:
            # Simulate payment processing
            order.mark_as_paid()

            # Record customer purchase for loyalty tracking
            customer = self._customer_repo.find_by_id(order.customer_id)
            if customer:
                customer.record_purchase(order.calculate_total())
                self._customer_repo.save(customer)

                # Publish customer events
                customer_events = customer.get_domain_events()
                self._event_publisher.publish(customer.id.value, customer_events)

            # Save order
            self._order_repo.save(order)

            # Publish order events
            events = order.get_domain_events()
            self._event_publisher.publish(order.id.value, events)

            return True

        except Exception as e:
            print(f"❌ Payment failed: {e}")
            return False

    def ship_order(self, order_id: OrderId) -> bool:
        """Ship order"""
        order = self._order_repo.find_by_id(order_id)
        if not order:
            raise DomainException("Order not found")

        try:
            order.ship()
            self._order_repo.save(order)

            # Publish events
            events = order.get_domain_events()
            self._event_publisher.publish(order.id.value, events)

            return True

        except Exception as e:
            print(f"❌ Shipping failed: {e}")
            return False


# =============================================================================
# DEMONSTRATION AND TESTING
# =============================================================================


def main():
    """Demonstrate comprehensive DDD implementation"""
    print("🏪 DDD E-commerce Platform Demo")
    print("=" * 60)

    # Initialize infrastructure
    event_store = DomainEventStore()
    event_publisher = DomainEventPublisher(event_store)

    # Initialize repositories
    customer_repo = InMemoryCustomerRepository()
    product_repo = InMemoryProductRepository()
    order_repo = InMemoryOrderRepository()

    # Initialize event handlers
    customer_handler = CustomerEventHandler()
    order_handler = OrderEventHandler()

    # Register event handlers
    # Specific event types are subtypes of DomainEvent, so handlers are compatible
    event_publisher.register_handler(
        "CustomerPurchaseRecorded", customer_handler.handle_customer_purchase_recorded  # type: ignore[arg-type]
    )
    event_publisher.register_handler(
        "CustomerTypeChanged", customer_handler.handle_customer_type_changed  # type: ignore[arg-type]
    )
    event_publisher.register_handler(
        "OrderConfirmed", order_handler.handle_order_confirmed  # type: ignore[arg-type]
    )
    event_publisher.register_handler("OrderPaid", order_handler.handle_order_paid)  # type: ignore[arg-type]
    event_publisher.register_handler("OrderShipped", order_handler.handle_order_shipped)  # type: ignore[arg-type]

    # Initialize application service
    app_service = ECommerceService(
        customer_repo, product_repo, order_repo, event_publisher
    )

    print("\n👤 Customer Management Context")
    print("-" * 40)

    # Register customers
    customer1_id = app_service.register_customer("john@example.com", "John Doe")
    app_service.register_customer("jane@example.com", "Jane Smith")

    print("\n📦 Product Catalog Context")
    print("-" * 40)

    # Create products
    laptop_id = app_service.create_product("Gaming Laptop", "1500.00", "electronics")
    book_id = app_service.create_product("Python Guide", "45.99", "books")
    shirt_id = app_service.create_product("Cotton Shirt", "29.99", "clothing")

    print("\n🛒 Order Management Context")
    print("-" * 40)

    # Place order
    cart_items = [
        {"product_id": laptop_id.value, "quantity": 1},
        {"product_id": book_id.value, "quantity": 2},
    ]

    shipping_address = {
        "street": "123 Main St",
        "city": "New York",
        "postal_code": "10001",
        "country": "USA",
    }

    order1_id = app_service.place_order(customer1_id, cart_items, shipping_address)

    # Process payment
    print("\n💳 Processing payment...")
    payment_success = app_service.process_payment(order1_id)

    if payment_success:
        print("✅ Payment processed successfully")

        # Ship order
        print("\n📦 Shipping order...")
        ship_success = app_service.ship_order(order1_id)

        if ship_success:
            print("✅ Order shipped successfully")

    # Place large order to trigger customer upgrade
    print("\n🔄 Testing Customer Loyalty System")
    print("-" * 40)

    large_cart = [
        {"product_id": laptop_id.value, "quantity": 3},
        {"product_id": shirt_id.value, "quantity": 10},
    ]

    order2_id = app_service.place_order(customer1_id, large_cart, shipping_address)
    app_service.process_payment(order2_id)

    # Another large order to trigger VIP
    order3_id = app_service.place_order(customer1_id, large_cart, shipping_address)
    app_service.process_payment(order3_id)

    print("\n📊 Event Sourcing Demonstration")
    print("-" * 40)

    # Show all events
    all_events = event_store.get_all_events()
    print(f"📝 Total events stored: {len(all_events)}")

    for i, event in enumerate(all_events[-5:], 1):  # Show last 5 events
        print(
            f"  {i}. {event.get_event_type()} at {event.occurred_at.strftime('%H:%M:%S')}"
        )

    print("\n🏆 Domain-Driven Design Features Demonstrated:")
    print("✅ Strategic Design - Bounded Contexts (Customer, Product, Order)")
    print("✅ Tactical Design - Entities, Value Objects, Aggregates")
    print("✅ Domain Events - Event publishing and handling")
    print("✅ Business Rules - Validation and constraints")
    print("✅ Domain Services - Complex business logic")
    print("✅ Repository Pattern - Data access abstraction")
    print("✅ Event Sourcing - Event storage and replay")
    print("✅ Ubiquitous Language - Domain-specific terminology")

    print("\n" + "=" * 60)
    print("🎉 DDD E-commerce Demo Complete!")

    print("\nKey DDD Benefits Shown:")
    print("🚀 Clear domain boundaries and contexts")
    print("🚀 Rich domain models with behavior")
    print("🚀 Event-driven architecture")
    print("🚀 Scalable and maintainable design")
    print("🚀 Business logic centralized in domain")


if __name__ == "__main__":
    main()
