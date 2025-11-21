# 🎯 Модуль 5: Практический Проект

## 🎯 Обзор модуля

**Финальный модуль курса** - интеграция всех концепций в реальном проекте.

## 🏗️ Финальный проект: E-commerce Platform

### 🎯 Архитектура системы

```
🎯 E-commerce Platform Architecture
├── 🏪 Sales Service (DDD Core)
│   ├── Domain Layer (Entities, Value Objects, Aggregates)
│   ├── Application Layer (Use Cases, Commands, Queries)
│   ├── Infrastructure Layer (Repositories, External APIs)
│   └── Presentation Layer (REST API, Event Publishing)
├── 📦 Inventory Service (Supporting)
│   ├── Stock Management & Reservation System
├── 💳 Payment Service (Generic)
│   ├── Payment Processing & Fraud Detection
├── 🚚 Shipping Service (Supporting)
│   ├── Delivery Management & Tracking
├── 👥 Customer Service (Core)
│   ├── Profile Management & Loyalty Program
├── 📊 Analytics Service (Generic)
│   ├── Business Intelligence & Reporting
└── 🗄️ Shared Infrastructure
    ├── Event Bus (Kafka)
    ├── API Gateway
    └── Monitoring Stack
```

## 📚 Структура модуля

### Теоретическая подготовка
1. **[Планирование проекта](01-project-planning.md)** - анализ требований, архитектура
2. **[Подготовка инфраструктуры](02-infrastructure-setup.md)** - Docker, БД, message broker
3. **[Domain modeling](03-domain-modeling.md)** - DDD анализ домена

### Практическая реализация
4. **[Sales Service](04-sales-service.md)** - ядро системы (DDD)
5. **[Inventory Service](05-inventory-service.md)** - управление запасами
6. **[Payment Service](06-payment-service.md)** - обработка платежей
7. **[Shipping Service](07-shipping-service.md)** - доставка

### Интеграция и оптимизация
8. **[Service Integration](08-service-integration.md)** - event-driven коммуникация
9. **[API Gateway](09-api-gateway.md)** - единая точка входа
10. **[Testing & Deployment](10-testing-deployment.md)** - тестирование и развертывание

## 🎮 Практические задания

- **Архитектурное проектирование** - bounded contexts и context mapping
- **Domain modeling** - создание доменной модели
- **Service implementation** - реализация микросервисов
- **Event-driven integration** - асинхронная коммуникация
- **API design** - RESTful API
- **Testing strategy** - unit, integration, e2e
- **Deployment automation** - CI/CD
- **Monitoring setup** - observability

## 🎯 Цели обучения

1. **Проектировать** масштабируемые микросервисные системы
2. **Применять** DDD в реальных проектах
3. **Реализовывать** event-driven архитектуру
4. **Организовывать** CI/CD pipeline
5. **Оптимизировать** производительность систем

---

!!! success "Это кульминация всего курса!"
    Здесь теория превращается в практику, а знания становятся навыками. Вы создадите систему корпоративного уровня!

!!! tip "Рекомендации"
    - Не спешите - уделяйте время каждому уроку
    - Практикуйте - пишите код, тестируйте
    - Документируйте - ведите техническую документацию
    - Итеративно улучшайте - постоянно рефакторьте

## 🔐 Переменные окружения

**⚠️ ВАЖНО: Никогда не храните секреты в исходном коде!**

Решение проекта использует переменные окружения для всех чувствительных данных через pydantic BaseSettings.

### Обязательные переменные:

```bash
# Database URLs
export DATABASE_URL="postgresql+asyncpg://user:password@localhost/ecommerce"
export DATABASE_SYNC_URL="postgresql://user:password@localhost/ecommerce"

# Redis
export REDIS_URL="redis://localhost:6379"

# JWT Secret (минимум 32 символа)
export JWT_SECRET_KEY="your-super-secret-jwt-key-minimum-32-characters-long"
```

### Опциональные переменные (имеют безопасные значения по умолчанию):

```bash
export JWT_ALGORITHM="HS256"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export API_V1_PREFIX="/api/v1"
export PROJECT_NAME="E-commerce Platform"
export VERSION="1.0.0"
export PROMETHEUS_METRICS_PATH="/metrics"
export MAX_ORDER_ITEMS=50
export FREE_SHIPPING_THRESHOLD="100.00"
export LOYALTY_POINTS_RATE="0.01"

# Metrics Authentication (for production)
# Default values: all auth variables default to empty strings (""), which means disabled/unset
# Empty values are treated as "not configured" - the corresponding auth method is not used
export METRICS_AUTH_ENABLED=false  # Default: false (set to true in production)
export METRICS_BEARER_TOKEN=""  # Default: "" (empty = disabled, set token string to enable bearer auth)
export METRICS_BASIC_AUTH_USERNAME=""  # Default: "" (empty = disabled, set username to enable basic auth)
export METRICS_BASIC_AUTH_PASSWORD=""  # Default: "" (empty = disabled, set password to enable basic auth)
export METRICS_ALLOWED_IPS=""  # Default: "" (empty = disabled, comma-separated IP list to enable IP allowlist, e.g., "127.0.0.1,10.0.0.1")
```

### Использование .env файла:

Создайте `.env` файл (но **не коммитьте его!**):

```bash
# Добавьте в .gitignore!
DATABASE_URL=postgresql+asyncpg://user:password@localhost/ecommerce
DATABASE_SYNC_URL=postgresql://user:password@localhost/ecommerce
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-long

# Metrics Authentication (for production - optional for local/dev)
# METRICS_AUTH_ENABLED=false  # Leave disabled for local development
# METRICS_BEARER_TOKEN=your-metrics-bearer-token-here  # For bearer token auth
# METRICS_BASIC_AUTH_USERNAME=prometheus  # For basic auth
# METRICS_BASIC_AUTH_PASSWORD=secure-password-here  # For basic auth
# METRICS_ALLOWED_IPS=127.0.0.1,10.0.0.1  # For IP allowlist (internal scraping)
```

**⚠️ Безопасность:**
- Добавьте `.env` в `.gitignore`
- Никогда не коммитьте реальные пароли или секретные ключи
- Используйте разные секреты для разных окружений
- Для production используйте секретные менеджеры

### 🔒 Настройка аутентификации метрик (для production)

Эндпоинт метрик Prometheus защищен аутентификацией, которая по умолчанию отключена для удобства локальной разработки.

#### Для production окружения:

**Вариант 1: Bearer Token (рекомендуется)**
```bash
export METRICS_AUTH_ENABLED=true
export METRICS_BEARER_TOKEN="your-secure-bearer-token-here"
```

**Вариант 2: Basic Authentication**
```bash
export METRICS_AUTH_ENABLED=true
export METRICS_BASIC_AUTH_USERNAME="prometheus"
export METRICS_BASIC_AUTH_PASSWORD="secure-password-here"
```

**Вариант 3: IP Allowlist (для внутреннего scraping)**
```bash
export METRICS_AUTH_ENABLED=true
export METRICS_ALLOWED_IPS="127.0.0.1,10.0.0.1,192.168.1.0/24"
```

**Примечание о формате METRICS_ALLOWED_IPS:**
- Формат: comma-separated список IP адресов (например, `"127.0.0.1,10.0.0.1"`)
- Пустое значение (`""`) означает, что IP allowlist отключен
- Значение по умолчанию: `""` (отключено)
- IP адреса проверяются напрямую; при использовании за прокси/load balancer учитывается заголовок `X-Forwarded-For`

**Комбинированный вариант (IP + Bearer Token):**
```bash
export METRICS_AUTH_ENABLED=true
export METRICS_ALLOWED_IPS="10.0.0.1"  # Prometheus server IP
export METRICS_BEARER_TOKEN="backup-token"  # Fallback для внешних запросов
```

#### Настройка Prometheus для scraping с аутентификацией:

**С Bearer Token:**
```yaml
scrape_configs:
  - job_name: 'ecommerce-service'
    static_configs:
      - targets: ['service:8000']
    bearer_token: 'your-secure-bearer-token-here'
```

**С Basic Auth:**
```yaml
scrape_configs:
  - job_name: 'ecommerce-service'
    static_configs:
      - targets: ['service:8000']
    basic_auth:
      username: 'prometheus'
      password: 'secure-password-here'
```

#### Для локальной разработки:

Оставьте `METRICS_AUTH_ENABLED=false` (значение по умолчанию) для упрощения разработки и тестирования.