# 🏗️ Урок 2: Подготовка инфраструктуры

## 🎯 Цели урока

После изучения этого урока вы сможете:
- ✅ Настраивать Docker-контейнеризацию для микросервисов
- ✅ Развертывать PostgreSQL и Redis базы данных
- ✅ Настраивать Apache Kafka для event-driven архитектуры
- ✅ Создавать docker-compose файлы для локальной разработки
- ✅ Организовывать инфраструктуру как код

## 🐳 Docker и контейнеризация

### 💡 Простыми словами

**Аналогия**: Контейнеры для перевозки грузов
- **Docker контейнер** = стандартный контейнер (одинаковый размер, одинаковые крепления)
- **Изоляция** = каждый контейнер отделен от других (не мешают друг другу)
- **Портативность** = контейнер работает везде одинаково (на корабле, поезде, грузовике)
- **Масштабируемость** = можно добавить больше контейнеров при необходимости

**В программировании:**
- Docker = способ упаковать приложение со всеми зависимостями
- Контейнер работает одинаково на любой машине
- Легко масштабировать - запустить больше копий

### 📊 Визуализация Docker архитектуры

```mermaid
graph TB
    A[Docker Host] --> B[Container 1<br/>Sales Service]
    A --> C[Container 2<br/>Inventory Service]
    A --> D[Container 3<br/>PostgreSQL]
    A --> E[Container 4<br/>Kafka]
    
    B -->|Network| C
    B -->|Database| D
    B -->|Events| E
    
    F[Docker Compose] --> A
    
    style A fill:#4dabf7
    style F fill:#51cf66
    style B fill:#ffd43b
    style C fill:#ff6b6b
    style D fill:#74c0fc
    style E fill:#f783ac
```

### 🎯 Зачем Docker?

Docker обеспечивает:
- **Консистентность** - одинаковое окружение на всех этапах
- **Изоляция** - сервисы не конфликтуют друг с другом
- **Масштабируемость** - легкое копирование и развертывание
- **Dev/Prod parity** - разработка = продакшен
- **Быстрое развертывание** - минуты вместо часов

### 📁 Структура проекта

```
📁 e-commerce-platform/
├── 📁 docker/
│   ├── 📄 docker-compose.yml          # Основной compose файл
│   ├── 📄 docker-compose.override.yml # Переопределения для разработки
│   ├── 📄 Dockerfile                  # Dockerfile для Python сервисов
│   └── 📄 .env                        # Переменные окружения
├── 📁 services/
│   ├── 📁 sales-service/
│   │   ├── 📄 Dockerfile
│   │   ├── 📄 requirements.txt
│   │   └── 📄 src/
│   ├── 📁 inventory-service/
│   └── 📁 payment-service/
├── 📁 infrastructure/
│   ├── 📄 init-db.sql                 # Инициализация БД
│   ├── 📄 kafka-setup.sh             # Настройка Kafka
│   └── 📄 monitoring/                 # Конфигурация мониторинга
└── 📁 docs/
    └── 📄 infrastructure.md          # Документация инфраструктуры
```

### 🐳 Dockerfile для Python сервисов

```dockerfile
# 📄 services/sales-service/Dockerfile
FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создание пользователя
RUN useradd --create-home --shell /bin/bash app
USER app

# Рабочая директория
WORKDIR /home/app

# Копирование файлов зависимостей
COPY requirements.txt .
COPY pyproject.toml .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ .

# Переменные окружения
ENV PYTHONPATH=/home/app
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Запуск приложения
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 📋 docker-compose.yml

```yaml
# 📄 docker/docker-compose.yml
version: '3.8'

services:
  # PostgreSQL база данных
  postgres:
    image: postgres:15-alpine
    container_name: e-commerce-postgres
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: ecommerce_user
      POSTGRES_PASSWORD: ecommerce_pass
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ecommerce_user -d ecommerce"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis для кэширования
  redis:
    image: redis:7-alpine
    container_name: e-commerce-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ecommerce-network
    command: redis-server --appendonly yes
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Zookeeper для Kafka
  zookeeper:
    image: confluentinc/cp-zookeeper:7.4.0
    container_name: e-commerce-zookeeper
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    networks:
      - ecommerce-network

  # Apache Kafka
  kafka:
    image: confluentinc/cp-kafka:7.4.0
    container_name: e-commerce-kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "9093:9093"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_INTERNAL:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092,PLAINTEXT_INTERNAL://kafka:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_JMX_PORT: 9101
      KAFKA_JMX_HOSTNAME: localhost
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD", "/opt/confluent/bin/kafka-broker-api-versions.sh", "--bootstrap-server", "localhost:9092"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Sales Service
  sales-service:
    build:
      context: ../services/sales-service
      dockerfile: Dockerfile
    container_name: e-commerce-sales
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8001:8000"
    environment:
      - DATABASE_URL=postgresql://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce
      - REDIS_URL=redis://redis:6379
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - SERVICE_NAME=sales-service
    networks:
      - ecommerce-network
    volumes:
      - ../services/sales-service/src:/home/app/src
    develop:
      watch:
        - action: sync
          path: ../services/sales-service/src
          target: /home/app/src

  # Inventory Service
  inventory-service:
    build:
      context: ../services/inventory-service
      dockerfile: Dockerfile
    container_name: e-commerce-inventory
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
    ports:
      - "8002:8000"
    environment:
      - DATABASE_URL=postgresql://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - SERVICE_NAME=inventory-service
    networks:
      - ecommerce-network
    volumes:
      - ../services/inventory-service/src:/home/app/src

  # Payment Service
  payment-service:
    build:
      context: ../services/payment-service
      dockerfile: Dockerfile
    container_name: e-commerce-payment
    depends_on:
      postgres:
        condition: service_healthy
      kafka:
        condition: service_healthy
    ports:
      - "8003:8000"
    environment:
      - DATABASE_URL=postgresql://ecommerce_user:ecommerce_pass@postgres:5432/ecommerce
      - KAFKA_BOOTSTRAP_SERVERS=kafka:29092
      - SERVICE_NAME=payment-service
      - PAYMENT_GATEWAY_URL=https://api.payment-gateway.com
      - PAYMENT_GATEWAY_KEY=${PAYMENT_GATEWAY_KEY}
    networks:
      - ecommerce-network
    volumes:
      - ../services/payment-service/src:/home/app/src

  # API Gateway
  api-gateway:
    image: nginx:alpine
    container_name: e-commerce-api-gateway
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - sales-service
      - inventory-service
      - payment-service
    networks:
      - ecommerce-network

volumes:
  postgres_data:
  redis_data:

networks:
  ecommerce-network:
    driver: bridge
```

### 🔧 Переменные окружения

```bash
# 📄 docker/.env
# Database
POSTGRES_DB=ecommerce
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=ecommerce_pass

# Redis
REDIS_URL=redis://localhost:6379

# Kafka
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Services
SALES_SERVICE_URL=http://localhost:8001
INVENTORY_SERVICE_URL=http://localhost:8002
PAYMENT_SERVICE_URL=http://localhost:8003

# External APIs
PAYMENT_GATEWAY_URL=https://api.payment-gateway.com
PAYMENT_GATEWAY_KEY=your-secret-key

# Monitoring
PROMETHEUS_URL=http://localhost:9090
GRAFANA_URL=http://localhost:3000

# Security
JWT_SECRET_KEY=your-super-secret-jwt-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

## 🐘 PostgreSQL настройка

### 📄 Инициализация базы данных

```sql
-- 📄 infrastructure/init-db.sql
-- Создание базы данных и пользователя
CREATE DATABASE ecommerce;
CREATE USER ecommerce_user WITH PASSWORD 'ecommerce_pass';
GRANT ALL PRIVILEGES ON DATABASE ecommerce TO ecommerce_user;

-- Подключение к базе данных
\c ecommerce;

-- Создание схем для разных bounded contexts
CREATE SCHEMA common;
CREATE SCHEMA sales;
CREATE SCHEMA inventory;
CREATE SCHEMA payment;
CREATE SCHEMA shipping;
CREATE SCHEMA customer;

-- Предоставление прав
GRANT USAGE ON SCHEMA common TO ecommerce_user;
GRANT USAGE ON SCHEMA sales TO ecommerce_user;
GRANT USAGE ON SCHEMA inventory TO ecommerce_user;
GRANT USAGE ON SCHEMA payment TO ecommerce_user;
GRANT USAGE ON SCHEMA shipping TO ecommerce_user;
GRANT USAGE ON SCHEMA customer TO ecommerce_user;

-- Создание общих типов
CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'paid', 'shipped', 'delivered', 'cancelled');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded');
CREATE TYPE shipping_status AS ENUM ('pending', 'processing', 'shipped', 'delivered', 'returned');

-- Создание общих таблиц
CREATE TABLE common.products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'RUB',
    category VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE common.customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    loyalty_points INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Индексы для производительности
CREATE INDEX idx_products_category ON common.products(category);
CREATE INDEX idx_products_active ON common.products(is_active);
CREATE INDEX idx_customers_email ON common.customers(email);
CREATE INDEX idx_customers_active ON common.customers(is_active);
```

### 🏗️ Миграции базы данных

```python
# 📄 infrastructure/migrations/env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from src.infrastructure.database import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_file_name),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

## 📨 Apache Kafka настройка

### 🎯 Зачем Kafka?

Kafka обеспечивает:
- **Event-driven architecture** - асинхронная коммуникация
- **Scalability** - обработка миллионов событий
- **Reliability** - гарантия доставки сообщений
- **Decoupling** - сервисы не зависят друг от друга
- **Replay capability** - повторная обработка событий

### 📋 Настройка топиков

```bash
# 📄 infrastructure/kafka-setup.sh
#!/bin/bash

# Ожидание запуска Kafka
sleep 30

# Создание топиков для domain events
kafka-topics --create --topic order-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic payment-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic inventory-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic shipping-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic customer-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Создание топиков для команд
kafka-topics --create --topic order-commands --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic payment-commands --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Создание топиков для интеграционных событий
kafka-topics --create --topic saga-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1
kafka-topics --create --topic notification-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

echo "Kafka topics created successfully"
```

### 🔧 Event Store на базе Kafka

```python
# 📄 services/sales-service/src/infrastructure/event_store.py
import json
from typing import List, Optional
from datetime import datetime
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from domain.events import DomainEvent

class KafkaEventStore:
    """Event Store на базе Apache Kafka"""

    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Запуск producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        """Остановка producer"""
        if self.producer:
            await self.producer.stop()

    async def save_event(self, event: DomainEvent, topic: str) -> None:
        """Сохранение события в Kafka"""
        event_data = {
            "event_id": event.event_id,
            "aggregate_id": event.aggregate_id,
            "event_type": event.__class__.__name__,
            "event_data": event.__dict__,
            "occurred_at": event.occurred_at.isoformat(),
            "event_version": event.event_version
        }

        await self.producer.send_and_wait(
            topic=topic,
            value=event_data,
            key=event.aggregate_id.encode('utf-8')
        )

    async def get_events_for_aggregate(self, aggregate_id: str, topic: str) -> List[DomainEvent]:
        """Получение событий для агрегата"""
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=f"event-store-{aggregate_id}",
            auto_offset_reset='earliest',
            value_deserializer=lambda v: json.loads(v.decode('utf-8'))
        )

        await consumer.start()

        events = []
        try:
            # Получение всех сообщений с заданным ключом
            async for message in consumer:
                if message.key.decode('utf-8') == aggregate_id:
                    event_data = message.value
                    # Преобразование обратно в DomainEvent
                    # (упрощенная реализация)
                    events.append(event_data)
        finally:
            await consumer.stop()

        return events
```

## 🔍 Мониторинг и логирование

### 📊 Prometheus и Grafana

```yaml
# 📄 docker/docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: e-commerce-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    networks:
      - ecommerce-network

  grafana:
    image: grafana/grafana:latest
    container_name: e-commerce-grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - ecommerce-network

  node-exporter:
    image: prom/node-exporter:latest
    container_name: e-commerce-node-exporter
    ports:
      - "9100:9100"
    networks:
      - ecommerce-network

volumes:
  prometheus_data:
  grafana_data:
```

### 📋 Конфигурация Prometheus

```yaml
# 📄 monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'sales-service'
    static_configs:
      - targets: ['sales-service:8000']
    # Optional: Add authentication if METRICS_AUTH_ENABLED=true
    # bearer_token: 'your-metrics-bearer-token-here'  # For bearer token auth
    # basic_auth:
    #   username: 'prometheus'
    #   password: 'secure-password-here'  # For basic auth

  - job_name: 'inventory-service'
    static_configs:
      - targets: ['inventory-service:8000']
    # Optional: Add authentication if METRICS_AUTH_ENABLED=true
    # bearer_token: 'your-metrics-bearer-token-here'
    # basic_auth:
    #   username: 'prometheus'
    #   password: 'secure-password-here'

  - job_name: 'payment-service'
    static_configs:
      - targets: ['payment-service:8000']
    # Optional: Add authentication if METRICS_AUTH_ENABLED=true
    # bearer_token: 'your-metrics-bearer-token-here'
    # basic_auth:
    #   username: 'prometheus'
    #   password: 'secure-password-here'

## 🚀 Запуск инфраструктуры

### 📋 Команды для запуска

```bash
# Запуск всей инфраструктуры
docker-compose -f docker/docker-compose.yml up -d

# Запуск с мониторингом
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.monitoring.yml up -d

# Просмотр логов
docker-compose logs -f

# Остановка сервисов
docker-compose down

# Очистка volumes
docker-compose down -v
```

### 🧪 Проверка работоспособности

```bash
# Проверка PostgreSQL
docker exec -it e-commerce-postgres psql -U ecommerce_user -d ecommerce -c "SELECT version();"

# Проверка Redis
docker exec -it e-commerce-redis redis-cli ping

# Проверка Kafka
docker exec -it e-commerce-kafka kafka-topics --list --bootstrap-server localhost:9092

# Проверка API
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## 🎮 Практическое задание

{{ create_exercise_form(
    "infrastructure_setup_exercise",
    "Настройка Docker-инфраструктуры для микросервисов",
    "Создайте docker-compose файлы, настройте PostgreSQL, Redis, Kafka и API Gateway.",
    """# Задание: Настройка инфраструктуры

## Шаг 1: Docker Compose

Создайте docker-compose.yml с сервисами:

1. **PostgreSQL** - основная база данных
2. **Redis** - кэширование и сессии
3. **Kafka + Zookeeper** - event streaming
4. **3 микросервиса** - sales, inventory, payment
5. **API Gateway** - единая точка входа

## Шаг 2: Переменные окружения

Создайте .env файл с:

1. **Database credentials**
2. **Redis connection**
3. **Kafka bootstrap servers**
4. **Service URLs**
5. **External API keys**
6. **Security settings**

## Шаг 3: Инициализация БД

Создайте SQL скрипт для:

1. **Создания пользователя и БД**
2. **Создания схем** для bounded contexts
3. **Создания общих таблиц** (products, customers)
4. **Создания индексов** для производительности

## Шаг 4: Настройка Kafka

Создайте скрипт для:

1. **Создания топиков** для domain events
2. **Создания топиков** для команд
3. **Создания топиков** для интеграционных событий

## Шаг 5: API Gateway

Настройте Nginx как API Gateway:

1. **Маршрутизация** запросов к сервисам
2. **Load balancing** для нескольких инстансов
3. **Rate limiting** для защиты от перегрузки
4. **CORS headers** для веб-клиентов

## Ожидаемый результат

Полная инфраструктура проекта:

1. **docker-compose.yml** - все сервисы
2. **.env** - переменные окружения
3. **init-db.sql** - инициализация БД
4. **kafka-setup.sh** - настройка Kafka
5. **nginx.conf** - конфигурация API Gateway
6. **Dockerfile** - для Python сервисов

## Критерии оценки

- **Docker Compose**: Правильная конфигурация сервисов и зависимостей
- **Переменные окружения**: Безопасность и организация настроек
- **База данных**: Правильная структура схем и индексов
- **Kafka**: Корректная настройка топиков и конфигурации
- **API Gateway**: Правильная маршрутизация и безопасность
- **Работоспособность**: Все сервисы запускаются и работают вместе

---

*Инфраструктура - это фундамент вашего приложения. Качественная настройка сэкономит время на разработку и поддержку!*""",
    [
        "Создать docker-compose.yml с сервисами",
        "Настроить переменные окружения",
        "Создать скрипт инициализации БД",
        "Настроить Kafka топики",
        "Создать Dockerfile для сервисов",
        "Настроить API Gateway"
    ]
) }}

## 🧪 Квиз

<div class="quiz-container" id="infrastructure-quiz">
<script type="application/json">
  "title": "Инфраструктура",
  "description": "Проверьте понимание Docker, баз данных и message broker",
  "questions": [
    {
      "question": "Зачем нужен Docker в микросервисах?",
      "type": "multiple",
      "points": 2,
      "options": [
        {"text": "Консистентность окружения", "correct": true},
        {"text": "Изоляция сервисов", "correct": true},
        {"text": "Быстрое развертывание", "correct": true},
        {"text": "Увеличение производительности", "correct": false}
      ],
      "explanation": "Docker обеспечивает консистентность, изоляцию и быстрое развертывание"
    },
    {
      "question": "Что такое health check в Docker?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Проверка готовности контейнера", "correct": true},
        {"text": "Проверка безопасности", "correct": false},
        {"text": "Проверка производительности", "correct": false}
      ],
      "explanation": "Health check проверяет готовность контейнера к работе"
    },
    {
      "question": "Зачем нужен Apache Kafka?",
      "type": "single",
      "points": 1,
      "options": [
        {"text": "Для event-driven архитектуры", "correct": true},
        {"text": "Для хранения файлов", "correct": false},
        {"text": "Для кэширования данных", "correct": false}
      ],
      "explanation": "Kafka обеспечивает асинхронную коммуникацию в event-driven архитектуре"
    }
  ]
</script>
</div>

## 🚀 Следующие шаги

!!! success "Что вы узнали"
    - ✅ Как настраивать Docker-контейнеризацию для микросервисов
    - ✅ Как развертывать PostgreSQL и Redis базы данных
    - ✅ Как настраивать Apache Kafka для event-driven архитектуры
    - ✅ Как создавать docker-compose файлы для локальной разработки

!!! tip "Практика"
    Попробуйте создать свой docker-compose файл для простого проекта (например, веб-приложение с БД). Это поможет закрепить знания.

Теперь вы готовы перейти к **[Domain Modeling](03-domain-modeling.md)** - созданию доменной модели с использованием DDD паттернов!

---













