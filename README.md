graph TD
    %% Стиль для элементов
    classDef users fill:#f9f,stroke:#333,stroke-width:2px;
    classDef infra fill:#bbf,stroke:#333,stroke-width:1px;
    classDef db fill:#fbf,stroke:#333,stroke-width:1px;
    
    %% Пользователь и внешние сущности
    Client([Пользователь / Клиент]):::users
    CA[Внутренний CA / Центр сертификации]:::infra

    %% Внутри периметра Nginx/Сервера
    subgraph ИНФРАСТРУКТУРА СЕРВЕРА
        Nginx[Nginx Reverse Proxy]:::infra
        Backend[Backend API Сервис]:::infra
        
        %% Базы данных
        PostgreSQL[(PostgreSQL)]:::db
        Redis[(Redis)]:::db
        
        %% Мониторинг
        Prometheus[Prometheus]:::infra
        Exporter[Blackbox Exporter]:::infra
    end

    %% Потоки бизнес-логики (Регистрация и генерация ключа)
    CA -. Выпускает mTLS сертификаты .-> Client
    CA -. Выпускает TLS сертификат .-> Nginx
    
    Client -- 1. Данные карты + mTLS сертификат / HTTPS:443 --> Nginx
    Nginx -- 2. Проверяет mTLS клиента и проксирует / HTTP:8080 --> Backend
    
    Backend -- 3. Проверяет кэш / TCP:6379 --> Redis
    Backend -- 4. Генерирует ключ и сохраняет пару / TCP:5432 --> PostgreSQL
    Backend -- 5. Возвращает сгенерированный ключ --> Nginx --> Client

    %% Потоки мониторинга (Проверка сертификатов)
    Prometheus -- Сбор метрик / HTTP:9115 --> Exporter
    Exporter -- Проверка срока действия TLS / mTLS --> Nginx
