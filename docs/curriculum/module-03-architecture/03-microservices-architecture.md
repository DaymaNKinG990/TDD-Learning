# 🏗 Урок 3: Микросервисная архитектура

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Проектировать микросервисную архитектуру с правильными границами сервисов
- ✅ Выбирать протоколы коммуникации между сервисами
- ✅ Управлять данными в распределенной системе
- ✅ Обеспечивать отказоустойчивость и мониторинг
- ✅ Организовывать развертывание и масштабирование микросервисов

## 📖 Что такое микросервисная архитектура?

!!! quote "Определение микросервисов"
    **Микросервисная архитектура** - это подход к разработке программного обеспечения, при котором приложение строится как набор небольших сервисов, каждый из которых работает в своем собственном процессе и взаимодействует с другими через четко определенные API.

### 💡 Простыми словами

**Аналогия**: Район с отдельными домами
- Каждый дом (сервис) независим и автономен
- У каждого свой адрес (API endpoint)
- Можно перестроить один дом, не трогая другие
- Но нужно строить дороги между домами (сеть, очереди)
- Каждый дом может быть построен по-разному (разные технологии)

**В программировании:**
- Небольшие независимые сервисы
- Каждый сервис - своя база данных
- Коммуникация через API
- Независимое масштабирование

### 📊 Визуализация микросервисов

```mermaid
graph TB
    A[API Gateway] --> B[User Service<br/>Python/FastAPI]
    A --> C[Order Service<br/>Python/FastAPI]
    A --> D[Payment Service<br/>Java/Spring]
    A --> E[Notification Service<br/>Node.js]
    
    B --> F[PostgreSQL]
    C --> G[PostgreSQL]
    D --> H[MongoDB]
    E --> I[Redis]
    
    B -.->|HTTP/gRPC| C
    C -.->|HTTP/gRPC| D
    D -.->|Events| E
    
    style A fill:#4dabf7
    style B fill:#51cf66
    style C fill:#51cf66
    style D fill:#ffd43b
    style E fill:#ff6b6b
```

### Ключевые характеристики

1. **Независимое развертывание** - каждый сервис можно развернуть отдельно
2. **Автономность команд** - разные команды работают над разными сервисами
3. **Технологическая гибкость** - разные сервисы могут использовать разные технологии
4. **Масштабируемость** - сервисы можно масштабировать независимо
5. **Отказоустойчивость** - сбой одного сервиса не влияет на всю систему

## 🎯 Принципы микросервисной архитектуры

### 1. **Единственная ответственность** (Single Responsibility)

```python
# ❌ Плохо: Монолитный сервис
class OrderService:
    def create_order(self, order_data):
        # Валидация
        # Расчет цены
        # Списание средств
        # Отправка уведомлений
        # Обновление инвентаря
        pass

# ✅ Хорошо: Разделение на микросервисы
# Order Service - только создание и управление заказами
# Payment Service - только обработка платежей
# Notification Service - только отправка уведомлений
# Inventory Service - только управление запасами
```

### 2. **Автономность сервисов** (Service Autonomy)

```python
# Каждый сервис:
# - Имеет собственную базу данных
# - Развертывается независимо
# - Масштабируется независимо
# - Имеет собственный жизненный цикл
```

### 3. **API как контракт** (API as Contract)

```python
# API-first подход
# OpenAPI/Swagger спецификации
# Версионирование API
# Документация как часть разработки
```

### 4. **Отказоустойчивость** (Resilience)

```python
# Circuit Breaker паттерн
# Retry логика
# Fallback стратегии
# Graceful degradation
```

## 🔍 Декомпозиция на микросервисы

### Шаг 1: Анализ домена (Domain Analysis)

#### Идентификация бизнес-возможностей (Business Capabilities)

```
📊 E-commerce Domain
├── 🛒 Product Management
│   ├── Product Catalog
│   ├── Product Search
│   ├── Product Reviews
│   └── Product Recommendations
├── 👥 Customer Management
│   ├── Customer Registration
│   ├── Customer Profiles
│   ├── Customer Preferences
│   └── Customer History
├── 🛍️ Order Management
│   ├── Order Creation
│   ├── Order Processing
│   ├── Order Tracking
│   └── Order History
├── 💰 Payment Processing
│   ├── Payment Methods
│   ├── Payment Processing
│   ├── Refunds
│   └── Payment History
└── 📦 Inventory Management
    ├── Stock Tracking
    ├── Stock Reservations
    ├── Stock Alerts
    └── Stock Optimization
```

#### Определение границ сервисов (Bounded Contexts)

```python
# Product Service
class ProductService:
    def create_product(self, product_data):
        # Только продукты
        pass

    def update_product(self, product_id, updates):
        # Только продукты
        pass

    def search_products(self, query):
        # Только продукты
        pass

# Order Service
class OrderService:
    def create_order(self, order_data):
        # Только заказы
        pass

    def get_order(self, order_id):
        # Только заказы
        pass

    def update_order_status(self, order_id, status):
        # Только заказы
        pass
```

### Шаг 2: Техническая декомпозиция

#### Размер сервиса (Service Size)

```python
# Правильный размер микросервиса:
# - 100-1000 строк кода
# - 1-2 разработчика
# - 1-2 недели на разработку
# - Независимое развертывание

# Признаки слишком большого сервиса:
# - Трудно понять весь код
# - Долгое время сборки/тестирования
# - Много зависимостей
# - Редкие изменения в разных частях

# Признаки слишком маленького сервиса:
# - Слишком много сервисов
# - Сложная коммуникация
# - Overhead на инфраструктуру
# - Трудно отслеживать зависимости
```

#### Критерии декомпозиции

1. **Бизнес-логика** - сервисы должны соответствовать бизнес-доменам
2. **Частота изменений** - часто изменяющиеся части в отдельных сервисах
3. **Масштабируемость** - разные требования к нагрузке
4. **Технологии** - разные технологические требования
5. **Команды** - границы владения командами

## 🔗 Коммуникация между сервисами

### Синхронная коммуникация

#### REST API (HTTP)

```python
# Product Service API
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Product Service", version="1.0.0")

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    category: str

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    # Получение продукта из БД
    return ProductResponse(
        id=product_id,
        name="Sample Product",
        price=99.99,
        category="Electronics"
    )

# Order Service вызывает Product Service
import httpx

class OrderService:
    def __init__(self):
        self.client = httpx.AsyncClient()

    async def validate_order_items(self, order_data):
        for item in order_data['items']:
            # Синхронный вызов другого сервиса
            response = await self.client.get(
                f"http://product-service/products/{item['product_id']}"
            )
            if response.status_code != 200:
                raise ValueError(f"Product {item['product_id']} not found")

            product = response.json()
            # Проверка доступности, цены и т.д.
```

#### gRPC

```protobuf
// product.proto
service ProductService {
  rpc GetProduct (GetProductRequest) returns (ProductResponse);
  rpc GetProducts (GetProductsRequest) returns (ProductsResponse);
}

message Product {
  int32 id = 1;
  string name = 2;
  float price = 3;
  string category = 4;
}
```

```python
# Python клиент для gRPC
import grpc
import product_pb2
import product_pb2_grpc

class ProductClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('product-service:50051')
        self.stub = product_pb2_grpc.ProductServiceStub(self.channel)

    def get_product(self, product_id: int):
        request = product_pb2.GetProductRequest(product_id=product_id)
        response = self.stub.GetProduct(request)
        return {
            'id': response.id,
            'name': response.name,
            'price': response.price,
            'category': response.category
        }
```

### Асинхронная коммуникация

#### Message Queue (RabbitMQ, Kafka)

```python
# Publisher (Order Service)
import aio_pika

class OrderPublisher:
    def __init__(self):
        self.connection = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async def publish_order_created(self, order_data):
        async with self.connection.channel() as channel:
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(order_data).encode(),
                    message_id=str(order_data['id'])
                ),
                routing_key="order.created"
            )

# Consumer (Notification Service)
class OrderConsumer:
    def __init__(self):
        self.connection = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")

    async def consume_order_created(self):
        async with self.connection.channel() as channel:
            queue = await channel.declare_queue("order.created")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        order_data = json.loads(message.body.decode())
                        await self.send_order_notification(order_data)

    async def send_order_notification(self, order_data):
        # Отправка email/SMS уведомления
        print(f"📧 Отправка уведомления для заказа {order_data['id']}")
```

#### Event Streaming (Kafka)

```python
# Producer
from aiokafka import AIOKafkaProducer
import json

class EventProducer:
    def __init__(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers='localhost:9092'
        )

    async def start(self):
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def publish_event(self, topic: str, event: dict):
        await self.producer.send_and_wait(
            topic,
            json.dumps(event).encode('utf-8'),
            key=str(event['id']).encode('utf-8')
        )

# Consumer
from aiokafka import AIOKafkaConsumer

class EventConsumer:
    def __init__(self):
        self.consumer = AIOKafkaConsumer(
            'order.created',
            bootstrap_servers='localhost:9092',
            group_id='notification-service'
        )

    async def start(self):
        await self.consumer.start()

    async def consume(self):
        try:
            async for message in self.consumer:
                event = json.loads(message.value.decode('utf-8'))
                await self.handle_order_created(event)
        finally:
            await self.consumer.stop()

    async def handle_order_created(self, event):
        print(f"📧 Обработка события: {event}")
```

## 💾 Управление данными

### Проблемы распределенных данных

1. **Консистентность** - данные в разных сервисах могут быть неконсистентны
2. **Транзакции** - ACID транзакции невозможны между сервисами
3. **Производительность** - сетевые вызовы медленнее локального доступа
4. **Отказоустойчивость** - сбои в сети между сервисами

### Стратегии управления данными

#### 1. Database per Service

```python
# Каждый сервис имеет свою базу данных
# Product Service -> PostgreSQL
# Order Service -> MongoDB
# User Service -> MySQL

# Преимущества:
# - Технологическая независимость
# - Независимое масштабирование
# - Изоляция данных

# Недостатки:
# - Сложность запросов к нескольким сервисам
# - Eventual consistency
# - Сложность транзакций
```

#### 2. Saga Pattern (для транзакций)

```python
# Choreography Saga
class OrderSaga:
    def __init__(self, event_publisher):
        self.publisher = event_publisher

    async def create_order(self, order_data):
        # Шаг 1: Создать заказ
        order = await self.order_repo.save(order_data)
        await self.publisher.publish("order.created", order)

        # Шаг 2: Зарезервировать товары
        await self.publisher.publish("inventory.reserve", {
            'order_id': order.id,
            'items': order.items
        })

        # Шаг 3: Обработать платеж
        await self.publisher.publish("payment.process", {
            'order_id': order.id,
            'amount': order.total
        })

# Inventory Service слушает события
class InventoryService:
    async def handle_inventory_reserve(self, event):
        try:
            # Зарезервировать товары
            await self.inventory_repo.reserve_items(event['items'])
            await self.publisher.publish("inventory.reserved", event)
        except Exception as e:
            # Компенсирующая транзакция
            await self.publisher.publish("inventory.reservation.failed", {
                **event,
                'error': str(e)
            })
```

#### 3. CQRS (Command Query Responsibility Segregation)

```python
# Разделение операций чтения и записи

# Write Model (Commands)
class OrderCommandService:
    async def create_order(self, command: CreateOrderCommand):
        # Валидация и бизнес-логика
        order = Order(command.customer_id, command.items)
        await self.order_repo.save(order)

        # Публикация события для обновления Read Model
        await self.publisher.publish("order.created", {
            'order_id': order.id,
            'customer_id': order.customer_id,
            'items': order.items,
            'total': order.total
        })

# Read Model (Queries)
class OrderQueryService:
    async def get_customer_orders(self, customer_id: int):
        # Чтение из оптимизированной БД для чтения
        return await self.read_repo.get_orders_by_customer(customer_id)

    async def get_order_summary(self, order_id: int):
        # Агрегированные данные для быстрого чтения
        return await self.read_repo.get_order_summary(order_id)
```

#### 4. Event Sourcing

```python
# Хранение состояния как последовательности событий
import uuid

class EventStore:
    async def save_event(self, aggregate_id: str, event: dict):
        event['aggregate_id'] = aggregate_id
        event['timestamp'] = datetime.utcnow()
        event['version'] = await self.get_next_version(aggregate_id)

        await self.events_repo.save(event)

    async def get_events(self, aggregate_id: str) -> List[dict]:
        return await self.events_repo.find_by_aggregate(aggregate_id)

class OrderAggregate:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self.events = []

    async def create_order(self, customer_id: int, items: List[dict]):
        order_id = uuid.uuid4()
        event = {
            'type': 'order.created',
            'order_id': str(order_id),
            'customer_id': customer_id,
            'items': items,
            'total': sum(item['price'] * item['quantity'] for item in items)
        }

        await self.event_store.save_event(f"order_{order_id}", event)
        self.events.append(event)

    async def load_from_events(self, order_id: str):
        self.events = await self.event_store.get_events(order_id)

        # Восстановление состояния из событий
        self.state = {}
        for event in self.events:
            self.apply_event(event)

    def apply_event(self, event: dict):
        if event['type'] == 'order.created':
            self.state.update({
                'order_id': event['order_id'],
                'customer_id': event['customer_id'],
                'items': event['items'],
                'total': event['total'],
                'status': 'created'
            })
```

## 🛡️ Отказоустойчивость и мониторинг

### Circuit Breaker Pattern

```python
from enum import Enum
import asyncio

class CircuitState(Enum):
    CLOSED = "closed"      # Нормальная работа
    OPEN = "open"         # Сбой, запросы блокируются
    HALF_OPEN = "half_open" # Тестирование восстановления

class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self) -> bool:
        if self.last_failure_time is None:
            return False
        return (asyncio.get_event_loop().time() -
                self.last_failure_time) > self.timeout

    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

### Service Mesh (Istio)

```yaml
# Istio VirtualService для маршрутизации
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: product-service
spec:
  http:
  - route:
    - destination:
        host: product-service
        subset: v1
      weight: 90
    - destination:
        host: product-service
        subset: v2
      weight: 10
---
# Istio DestinationRule для версий
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: product-service
spec:
  host: product-service
  subsets:
  - name: v1
    labels:
      version: v1
  - name: v2
    labels:
      version: v2
```

### Мониторинг и Observability

```python
# Метрики с Prometheus
from prometheus_client import Counter, Histogram, Gauge

# Метрики HTTP запросов
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Метрики бизнес-логики
orders_created_total = Counter(
    'orders_created_total',
    'Total number of orders created'
)

active_connections = Gauge(
    'active_connections',
    'Number of active connections'
)

# Middleware для сбора метрик
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    http_requests_total.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    http_request_duration.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response
```

### Распределенная трассировка (Distributed Tracing)

```python
# OpenTelemetry для трассировки
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter

# Настройка трассировки
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)

span_processor = BatchSpanProcessor(jaeger_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Использование в коде
@tracer.start_as_current_span("create_order")
async def create_order(order_data):
    with tracer.start_as_current_span("validate_order") as span:
        span.set_attribute("order.customer_id", order_data['customer_id'])
        # Валидация заказа
        await validate_order_data(order_data)

    with tracer.start_as_current_span("save_order") as span:
        # Сохранение заказа
        order = await order_repo.save(order_data)
        span.set_attribute("order.id", order.id)

    with tracer.start_as_current_span("publish_event") as span:
        # Публикация события
        await event_publisher.publish("order.created", order)

    return order
```

## 🚀 Развертывание и масштабирование

### Container Orchestration (Kubernetes)

```yaml
# Deployment для микросервиса
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:v1.2.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          value: "postgresql://..."
        - name: REDIS_URL
          value: "redis://..."
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service Discovery

```python
# Consul для service discovery
import consul

class ServiceRegistry:
    def __init__(self):
        self.consul = consul.Consul()

    def register_service(self, service_name: str, service_id: str, address: str, port: int):
        self.consul.agent.service.register(
            service_name,
            service_id=service_id,
            address=address,
            port=port,
            check=consul.Check.http(f"http://{address}:{port}/health", "10s")
        )

    def discover_service(self, service_name: str):
        services = self.consul.catalog.service(service_name)[1]
        if services:
            service = services[0]
            return f"http://{service['Address']}:{service['Port']}"
        return None

# Использование
registry = ServiceRegistry()

# Регистрация сервиса
registry.register_service("order-service", "order-1", "10.0.0.1", 8000)

# Обнаружение сервиса
order_service_url = registry.discover_service("order-service")
```

### API Gateway

```python
# API Gateway на FastAPI
from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI(title="API Gateway")

# Service URLs (в продакшене из Service Discovery)
SERVICES = {
    "products": "http://product-service:8001",
    "orders": "http://order-service:8002",
    "users": "http://user-service:8003"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gateway(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    service_url = f"{SERVICES[service]}/{path}"

    # Копирование заголовков и тела запроса
    headers = dict(request.headers)
    headers.pop("host", None)  # Убираем host заголовок

    body = await request.body()

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=service_url,
            headers=headers,
            content=body,
            params=request.query_params
        )

        return response.json()
```

## 🎮 Практические упражнения

### Упражнение 1: Декомпозиция монолита

**Задание:** Разбить монолитное приложение на микросервисы.

### Упражнение 2: Реализация коммуникации

**Задание:** Настроить синхронную и асинхронную коммуникацию между сервисами.

### Упражнение 3: Управление данными

**Задание:** Реализовать Saga паттерн для распределенных транзакций.

## 🎯 Ключевые выводы

1. **Микросервисы - это не серебряная пуля** - они добавляют сложность
2. **Правильная декомпозиция** - ключ к успешной микросервисной архитектуре
3. **Коммуникация через API** - сервисы должны быть автономны
4. **Eventual consistency** - принять и обойти ограничения распределенных систем
5. **Мониторинг и observability** - критически важны в распределенных системах
6. **Организация команд** - важнее, чем технология

## 🚀 Следующие шаги

!!! success "Что вы узнали"
    - ✅ Принципы микросервисной архитектуры и декомпозиции
    - ✅ Протоколы коммуникации между сервисами (HTTP, gRPC, Events)
    - ✅ Управление данными в распределенных системах
    - ✅ Паттерны отказоустойчивости и мониторинга

!!! tip "Практика"
    Попробуйте разбить простое монолитное приложение на 2-3 микросервиса. Это поможет понять сложности распределенных систем.

Теперь вы готовы изучить **[Событийную архитектуру](04-event-driven-architecture.md)** - современный подход к созданию реактивных и масштабируемых систем!

---

!!! tip "Практический совет"
    Начните с монолита и переходите к микросервисам только когда преимущества перевешивают сложности. Используйте Domain-Driven Design для правильной декомпозиции.

!!! info "Дополнительные ресурсы"
    - [Building Microservices by Sam Newman](https://samnewman.io/books/building_microservices/)
    - [Microservices.io](https://microservices.io/)
    - [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🧪 Проверьте свои знания: Микросервисная архитектура

<div class="quiz-container" id="microservices-architecture-quiz">
<script type="application/json">
{
  "title": "Микросервисная архитектура",
  "description": "Проверьте понимание микросервисных принципов и паттернов",
  "icon": "🏗️",
  "questions": [
    {
      "question": "Что является ключевой характеристикой микросервисной архитектуры?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Все сервисы используют одну базу данных", "correct": false},
        {"text": "Каждый сервис имеет собственную базу данных", "correct": true},
        {"text": "Сервисы общаются через общую память", "correct": false},
        {"text": "Все сервисы работают в одном процессе", "correct": false}
      ],
      "explanation": "Database per Service - один из ключевых принципов микросервисов"
    },
    {
      "question": "Какой паттерн используется для управления распределенными транзакциями в микросервисах?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Factory Pattern", "correct": false},
        {"text": "Saga Pattern", "correct": true},
        {"text": "Observer Pattern", "correct": false},
        {"text": "Strategy Pattern", "correct": false}
      ],
      "explanation": "Saga Pattern позволяет реализовать распределенные транзакции через последовательность локальных транзакций"
    },
    {
      "question": "Какие преимущества дает микросервисная архитектура?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Независимое масштабирование сервисов", "correct": true},
        {"text": "Технологическая гибкость", "correct": true},
        {"text": "Упрощенная коммуникация между командами", "correct": true},
        {"text": "Автоматическая консистентность данных", "correct": false},
        {"text": "Упрощенное тестирование", "correct": false}
      ],
      "explanation": "Микросервисы дают преимущества в масштабировании и гибкости, но добавляют сложности"
    },
    {
      "question": "Что такое Circuit Breaker паттерн?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Паттерн для создания цепей наследования", "correct": false},
        {"text": "Паттерн для защиты от каскадных сбоев", "correct": true},
        {"text": "Паттерн для маршрутизации запросов", "correct": false},
        {"text": "Паттерн для кэширования данных", "correct": false}
      ],
      "explanation": "Circuit Breaker предотвращает каскадные сбои в распределенных системах"
    },
    {
      "question": "Какой протокол лучше использовать для синхронной коммуникации между микросервисами?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "HTTP REST", "correct": true},
        {"text": "Email", "correct": false},
        {"text": "FTP", "correct": false},
        {"text": "SMS", "correct": false}
      ],
      "explanation": "HTTP REST - стандарт для синхронной коммуникации в микросервисах"
    },
    {
      "question": "Что такое CQRS?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Command Query Responsibility Segregation", "correct": true},
        {"text": "Create Query Read Service", "correct": false},
        {"text": "Centralized Query Resource System", "correct": false},
        {"text": "Common Query Response Standard", "correct": false}
      ],
      "explanation": "CQRS разделяет операции чтения и записи для лучшей масштабируемости"
    },
    {
      "question": "Какие инструменты используются для Service Discovery?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Consul", "correct": true},
        {"text": "Zookeeper", "correct": true},
        {"text": "Kubernetes DNS", "correct": true},
        {"text": "Git", "correct": false},
        {"text": "Docker", "correct": false}
      ],
      "explanation": "Consul, Zookeeper и Kubernetes DNS используются для обнаружения сервисов"
    },
    {
      "question": "Что такое Eventual Consistency?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Данные всегда консистентны", "correct": false},
        {"text": "Данные становятся консистентными со временем", "correct": true},
        {"text": "Данные никогда не консистентны", "correct": false},
        {"text": "Консистентность проверяется вручную", "correct": false}
      ],
      "explanation": "Eventual Consistency - модель консистентности в распределенных системах"
    },
    {
      "question": "Какой инструмент используется для container orchestration в микросервисах?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Kubernetes", "correct": true},
        {"text": "Apache HTTP Server", "correct": false},
        {"text": "Nginx", "correct": false},
        {"text": "PostgreSQL", "correct": false}
      ],
      "explanation": "Kubernetes - стандарт для оркестрации контейнеров в микросервисах"
    },
    {
      "question": "Что такое API Gateway в микросервисной архитектуре?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "База данных для API", "correct": false},
        {"text": "Точка входа для клиентских запросов", "correct": true},
        {"text": "Инструмент для тестирования API", "correct": false},
        {"text": "Генератор API документации", "correct": false}
      ],
      "explanation": "API Gateway - единая точка входа для всех клиентских запросов к микросервисам"
    }
  ]
}
</script>
</div>

## 💻 Практическое задание: Проектирование микросервисной системы

{{ create_exercise_form(
    "microservices_design",
    "Проектирование микросервисной архитектуры для e-commerce платформы",
    "Спроектируйте микросервисную архитектуру для e-commerce платформы с правильной декомпозицией, коммуникацией и управлением данными.",
    """# Задание: Микросервисная архитектура E-commerce

Разработайте микросервисную архитектуру для крупной e-commerce платформы со следующими требованиями:

## Бизнес-требования

### Функциональность:
- **Каталог товаров** - 10M+ товаров, сложный поиск и фильтры
- **Управление заказами** - 100K+ заказов в день
- **Обработка платежей** - интеграция с 10+ платежными системами
- **Управление пользователями** - 1M+ активных пользователей
- **Рекомендации** - персонализированные предложения
- **Аналитика** - отчеты о продажах и поведении пользователей
- **Уведомления** - email, SMS, push-уведомления
- **Логистика** - интеграция с службами доставки

### Технические требования:
- **Нагрузка**: 10,000+ RPS в пиковые часы
- **Доступность**: 99.99% SLA
- **Время отклика**: < 100ms для основных операций
- **Масштабируемость**: Рост на 500% в ближайшие 2 года
- **Команды**: 15+ команд разработчиков
- **Технологии**: Python, Go, Node.js (по выбору команд)

## Задачи декомпозиции

### 1. Domain Analysis (Анализ домена)

Определите bounded contexts и сервисы на основе бизнес-возможностей:

```
🏪 E-commerce Domain
├── 📦 Product Domain
│   ├── Product Catalog Service
│   ├── Product Search Service
│   ├── Product Recommendation Service
│   └── Product Review Service
├── 👤 Customer Domain
│   ├── Customer Profile Service
│   ├── Customer Authentication Service
│   ├── Customer Preferences Service
│   └── Customer History Service
├── 🛒 Order Domain
│   ├── Order Management Service
│   ├── Order Processing Service
│   ├── Order Tracking Service
│   └── Order Analytics Service
├── 💳 Payment Domain
│   ├── Payment Processing Service
│   ├── Payment Gateway Integration
│   ├── Fraud Detection Service
│   └── Refund Management Service
├── 📬 Notification Domain
│   ├── Email Service
│   ├── SMS Service
│   ├── Push Notification Service
│   └── Notification Template Service
└── 🚚 Logistics Domain
    ├── Shipping Service
    ├── Warehouse Management Service
    ├── Delivery Tracking Service
    └── Returns Management Service
```

### 2. Service Design (Проектирование сервисов)

#### Product Service (Python + FastAPI)
```python
# product_service/src/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Product Service", version="1.0.0")

class Product(BaseModel):
    id: str
    name: str
    description: str
    price: float
    category: str
    images: List[str]
    attributes: dict

class ProductService:
    def __init__(self, product_repo, search_service, cache):
        self.product_repo = product_repo
        self.search_service = search_service
        self.cache = cache

    async def get_product(self, product_id: str) -> Optional[Product]:
        # Получение из кэша
        cached = await self.cache.get(f"product:{product_id}")
        if cached:
            return Product(**cached)

        # Получение из БД
        product = await self.product_repo.get_by_id(product_id)
        if product:
            await self.cache.set(f"product:{product_id}", product.dict(), ttl=3600)

        return product

    async def search_products(self, query: str, filters: dict) -> List[Product]:
        # Делегирование поиска в Search Service
        search_results = await self.search_service.search(query, filters)

        # Получение полных данных товаров
        products = []
        for result in search_results:
            product = await self.get_product(result['id'])
            if product:
                products.append(product)

        return products

# API Endpoints
@app.get("/products/{product_id}")
async def get_product(product_id: str):
    # TODO: Реализовать эндпоинт
    pass

@app.get("/products/search")
async def search_products(q: str, category: Optional[str] = None):
    # TODO: Реализовать поиск
    pass
```

#### Order Service (Go)
```go
// order_service/main.go
package main

import (
    "context"
    "encoding/json"
    "net/http"
    "github.com/gorilla/mux"
)

type Order struct {
    ID         string  `json:"id"`
    CustomerID string  `json:"customer_id"`
    Items      []OrderItem `json:"items"`
    Status     string  `json:"status"`
    Total      float64 `json:"total"`
}

type OrderService struct {
    repo     OrderRepository
    producer EventProducer
}

func (s *OrderService) CreateOrder(ctx context.Context, customerID string, items []OrderItem) (*Order, error) {
    // Валидация товаров через Product Service
    if err := s.validateItems(ctx, items); err != nil {
        return nil, err
    }

    // Расчет общей стоимости
    total := s.calculateTotal(items)

    // Создание заказа
    order := &Order{
        ID:         generateID(),
        CustomerID: customerID,
        Items:      items,
        Status:     "pending",
        Total:      total,
    }

    // Сохранение в БД
    if err := s.repo.Save(order); err != nil {
        return nil, err
    }

    // Публикация события
    event := OrderCreatedEvent{
        OrderID:    order.ID,
        CustomerID: customerID,
        Total:      total,
    }

    if err := s.producer.Publish("order.created", event); err != nil {
        // Обработка ошибки публикации
        log.Printf("Failed to publish event: %v", err)
    }

    return order, nil
}

func main() {
    service := &OrderService{
        repo:     NewPostgresOrderRepository(),
        producer: NewKafkaProducer(),
    }

    r := mux.NewRouter()
    r.HandleFunc("/orders", service.CreateOrderHandler).Methods("POST")
    r.HandleFunc("/orders/{id}", service.GetOrderHandler).Methods("GET")

    http.ListenAndServe(":8080", r)
}
```

#### Payment Service (Node.js)
```javascript
// payment_service/app.js
const express = require('express');
const { Kafka } = require('kafkajs');

class PaymentService {
    constructor() {
        this.kafka = new Kafka({
            clientId: 'payment-service',
            brokers: ['kafka:9092']
        });
        this.consumer = this.kafka.consumer({ groupId: 'payment-group' });
    }

    async processPayment(orderEvent) {
        console.log(`Processing payment for order ${orderEvent.orderId}`);

        try {
            // Интеграция с платежной системой
            const paymentResult = await this.paymentGateway.charge({
                amount: orderEvent.total,
                currency: 'USD',
                orderId: orderEvent.orderId
            });

            if (paymentResult.success) {
                // Публикация события успешной оплаты
                await this.producer.send({
                    topic: 'payment.succeeded',
                    messages: [{
                        value: JSON.stringify({
                            orderId: orderEvent.orderId,
                            paymentId: paymentResult.paymentId,
                            amount: orderEvent.total
                        })
                    }]
                });
            } else {
                // Публикация события неудачной оплаты
                await this.producer.send({
                    topic: 'payment.failed',
                    messages: [{
                        value: JSON.stringify({
                            orderId: orderEvent.orderId,
                            reason: paymentResult.error
                        })
                    }]
                });
            }
        } catch (error) {
            console.error(`Payment failed: ${error.message}`);
            // Обработка ошибки
        }
    }

    async start() {
        await this.consumer.connect();
        await this.consumer.subscribe({ topic: 'order.created' });

        await this.consumer.run({
            eachMessage: async ({ topic, partition, message }) => {
                const orderEvent = JSON.parse(message.value.toString());
                await this.processPayment(orderEvent);
            }
        });
    }
}

const app = express();
const paymentService = new PaymentService();

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

app.listen(3000, () => {
    console.log('Payment Service listening on port 3000');
    paymentService.start();
});
```

### 3. Communication Patterns (Паттерны коммуникации)

#### Synchronous Communication (REST/gRPC)
```python
# API Gateway для маршрутизации
class APIGateway:
    def __init__(self):
        self.service_registry = ServiceRegistry()

    async def route_request(self, service: str, path: str, method: str, data: dict):
        # Обнаружение адреса сервиса
        service_url = await self.service_registry.discover(service)

        # Circuit Breaker для защиты от сбоев
        circuit_breaker = CircuitBreaker()

        # Выполнение запроса с retry
        return await circuit_breaker.call(
            self._make_request,
            service_url,
            path,
            method,
            data
        )

    async def _make_request(self, service_url, path, method, data):
        async with aiohttp.ClientSession() as session:
            url = f"{service_url}/{path}"
            async with session.request(method, url, json=data) as response:
                return await response.json()
```

#### Asynchronous Communication (Events)
```python
# Event Bus для асинхронной коммуникации
class EventBus:
    def __init__(self):
        self.handlers = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        self.handlers[event_type].append(handler)

    async def publish(self, event_type: str, event_data: dict):
        # Публикация события всем подписчикам
        tasks = []
        for handler in self.handlers[event_type]:
            task = asyncio.create_task(handler(event_data))
            tasks.append(task)

        # Ожидание завершения всех обработчиков
        await asyncio.gather(*tasks, return_exceptions=True)

# Saga Pattern для распределенных транзакций
class OrderSaga:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.steps = []
        self.compensations = []

    async def execute(self, order_data: dict):
        try:
            # Шаг 1: Валидация и создание заказа
            await self.create_order(order_data)
            self.compensations.append(self.cancel_order)

            # Шаг 2: Резервирование товаров
            await self.reserve_inventory(order_data)
            self.compensations.append(self.release_inventory)

            # Шаг 3: Обработка платежа
            await self.process_payment(order_data)
            self.compensations.append(self.refund_payment)

            # Шаг 4: Подтверждение заказа
            await self.confirm_order(order_data)

        except Exception as e:
            # Компенсирующие действия при ошибке
            await self.rollback()

    async def rollback(self):
        for compensation in reversed(self.compensations):
            try:
                await compensation()
            except Exception as e:
                logger.error(f"Compensation failed: {e}")
```

### 4. Data Management (Управление данными)

#### CQRS Implementation
```python
# Write Model (Commands)
class OrderCommandService:
    def __init__(self, event_store: EventStore):
        self.event_store = event_store

    async def create_order(self, command: CreateOrderCommand):
        # Валидация бизнес-правил
        await self.validate_business_rules(command)

        # Создание события
        event = OrderCreatedEvent(
            order_id=uuid.uuid4(),
            customer_id=command.customer_id,
            items=command.items,
            total=command.total
        )

        # Сохранение события
        await self.event_store.save_event(event)

        # Публикация для обновления Read Model
        await self.event_publisher.publish("order.created", event)

# Read Model (Queries)
class OrderQueryService:
    def __init__(self, read_repository: OrderReadRepository):
        self.read_repo = read_repository

    async def get_customer_orders(self, customer_id: str) -> List[OrderSummary]:
        # Оптимизированный запрос для чтения
        return await self.read_repo.get_orders_by_customer(customer_id)

    async def get_order_details(self, order_id: str) -> OrderDetails:
        # Детальная информация о заказе
        return await self.read_repo.get_order_details(order_id)

# Event Handler для обновления Read Model
class OrderReadModelHandler:
    def __init__(self, read_repository: OrderReadRepository):
        self.read_repo = read_repository

    async def handle_order_created(self, event: OrderCreatedEvent):
        # Создание записи в Read Model
        order_summary = OrderSummary(
            id=event.order_id,
            customer_id=event.customer_id,
            status="created",
            total=event.total,
            created_at=datetime.utcnow()
        )

        await self.read_repo.save_order_summary(order_summary)

        # Создание записей товаров
        for item in event.items:
            order_item = OrderItem(
                order_id=event.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price
            )
            await self.read_repo.save_order_item(order_item)
```

### 5. Infrastructure and Deployment

#### Kubernetes Manifests
```yaml
# order-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      containers:
      - name: order-service
        image: order-service:v1.0.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: order-db-url
        - name: KAFKA_BROKERS
          value: "kafka-cluster:9092"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
---
# order-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order-service
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

#### Service Mesh Configuration
```yaml
# Istio Virtual Service
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service
spec:
  http:
  - match:
    - uri:
        prefix: "/api/orders"
    route:
    - destination:
        host: order-service
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
---
# Istio Destination Rule
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-service
spec:
  host: order-service
  trafficPolicy:
    loadBalancer:
      simple: ROUND_ROBIN
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 10
```

### 6. Monitoring and Observability

#### Metrics Collection
```python
# Prometheus metrics для Order Service
from prometheus_client import Counter, Histogram, Gauge

# Business metrics
orders_created_total = Counter(
    'orders_created_total',
    'Total number of orders created'
)

order_creation_duration = Histogram(
    'order_creation_duration_seconds',
    'Time spent creating orders',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

active_orders = Gauge(
    'active_orders',
    'Number of currently active orders'
)

# Technical metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

database_connection_pool_size = Gauge(
    'database_connection_pool_size',
    'Current database connection pool size'
)
```

#### Distributed Tracing
```python
# OpenTelemetry tracing
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger import JaegerExporter

trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer("order-service")

jaeger_exporter = JaegerExporter(
    agent_host_name="jaeger-agent",
    agent_port=6831,
)

trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

class OrderService:
    @tracer.start_as_current_span("create_order")
    async def create_order(self, customer_id: str, items: List[dict]):
        with tracer.start_as_current_span("validate_customer") as span:
            span.set_attribute("customer.id", customer_id)
            await self.validate_customer(customer_id)

        with tracer.start_as_current_span("validate_items") as span:
            span.set_attribute("items.count", len(items))
            await self.validate_items(items)

        with tracer.start_as_current_span("calculate_total") as span:
            total = self.calculate_total(items)
            span.set_attribute("order.total", total)

        with tracer.start_as_current_span("save_order") as span:
            order = await self.save_order(customer_id, items, total)
            span.set_attribute("order.id", order.id)

        return order
```

## Ожидаемый результат

Создайте детальный дизайн микросервисной архитектуры с:

1. **Domain Decomposition** - диаграмма сервисов и их ответственности
2. **Service Contracts** - API спецификации для ключевых сервисов
3. **Communication Patterns** - синхронная и асинхронная коммуникация
4. **Data Management** - стратегии управления данными
5. **Infrastructure Design** - Kubernetes manifests, monitoring
6. **Deployment Strategy** - CI/CD, blue-green deployment
7. **Risk Assessment** - потенциальные проблемы и решения

## Продвинутые темы для исследования

### Event Sourcing + CQRS
```python
# Полная реализация Event Sourcing
class EventSourcedAggregate:
    def __init__(self, aggregate_id: str):
        self.aggregate_id = aggregate_id
        self.version = 0
        self.uncommitted_events = []

    def apply_event(self, event: DomainEvent):
        self._apply(event, is_new=False)

    def _apply(self, event: DomainEvent, is_new: bool = True):
        # Применение события к агрегату
        method_name = f"apply_{event.__class__.__name__.lower()}"
        method = getattr(self, method_name, None)
        if method:
            method(event)

        self.version += 1

        if is_new:
            self.uncommitted_events.append(event)

    def mark_events_as_committed(self):
        self.uncommitted_events.clear()

# CQRS Command Handler
class OrderCommandHandler:
    def __init__(self, event_store: EventStore, event_publisher: EventPublisher):
        self.event_store = event_store
        self.event_publisher = event_publisher

    async def handle_create_order(self, command: CreateOrderCommand):
        # Загрузка существующего агрегата или создание нового
        aggregate = await self.load_aggregate(command.order_id)

        # Выполнение бизнес-логики
        aggregate.create_order(command.customer_id, command.items)

        # Сохранение событий
        await self.event_store.save_events(
            aggregate.aggregate_id,
            aggregate.uncommitted_events
        )

        # Публикация событий
        for event in aggregate.uncommitted_events:
            await self.event_publisher.publish(event)

        aggregate.mark_events_as_committed()

    async def load_aggregate(self, aggregate_id: str) -> OrderAggregate:
        events = await self.event_store.get_events(aggregate_id)
        aggregate = OrderAggregate(aggregate_id)

        for event in events:
            aggregate.apply_event(event)

        return aggregate
```

### Service Mesh Patterns
```yaml
# Istio Traffic Management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: order-service-routing
spec:
  http:
  - match:
    - headers:
        x-customer-tier:
          exact: "gold"
    route:
    - destination:
        host: order-service
        subset: gold
  - route:
    - destination:
        host: order-service
        subset: standard

---
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: order-service-subsets
spec:
  host: order-service
  subsets:
  - name: gold
    labels:
      version: gold
  - name: standard
    labels:
      version: standard
```

---

*Помните: Микросервисная архитектура - это инструмент для решения конкретных проблем масштабируемости и организационной сложности. Не используйте ее только потому, что "это современно". Анализируйте свои требования и контекст!*""",
    [
        "Провести domain analysis и декомпозицию на bounded contexts",
        "Спроектировать API контракты для ключевых сервисов",
        "Реализовать паттерны коммуникации (синхронная и асинхронная)",
        "Настроить CQRS + Event Sourcing для управления данными",
        "Создать Kubernetes manifests для развертывания",
        "Настроить мониторинг и distributed tracing",
        "Документировать архитектуру и риски"
    ]
) }}














