# Шпаргалка по миграциям базы данных

## 🚀 Быстрый старт

```bash
# Первоначальная настройка (один раз)
bash quick_start.sh

# Создать первую миграцию
python3 migrate_db.py --generate -m "Initial migration"
```

## 📝 Ежедневные команды

### Полная миграция (рекомендуется)
```bash
# После изменения database.py
python3 migrate_db.py --full -m "Описание изменений"
```

### Пошаговая миграция
```bash
# 1. Бэкап
python3 migrate_db.py --backup

# 2. Генерация
python3 migrate_db.py --generate -m "Описание"

# 3. Применение
python3 migrate_db.py --apply

# 4. Откат (если что-то пошло не так)
python3 migrate_db.py --rollback
```

## 💾 Резервное копирование

### Ручное создание бэкапа
```bash
python3 backup_db.py backup
```

### Список бэкапов
```bash
python3 backup_db.py list
```

### Восстановление
```bash
# Просмотр доступных бэкапов
python3 backup_db.py list

# Восстановление
python3 backup_db.py restore --file backups/medical_db_backup_YYYYMMDD_HHMMSS.sql

# Полное восстановление (удаление и пересоздание БД)
python3 backup_db.py restore --file backups/backup.sql --drop
```

### Автоматическое резервное копирование
```bash
# Каждый день в 3:00
python3 backup_scheduler.py --schedule daily --time 03:00

# Каждый час
python3 backup_scheduler.py --schedule hourly

# Каждое воскресенье в 3:00
python3 backup_scheduler.py --schedule weekly --time 03:00
```

## 🔍 Проверка и сравнение

### Сравнить схему БД с моделями
```bash
# Полное сравнение
python3 compare_schemas.py

# Быстрая проверка (нужна ли миграция?)
python3 compare_schemas.py --quick
```

## 🔄 Работа с Alembic напрямую

### Информация о миграциях
```bash
# Текущая версия БД
python3 -m alembic current

# История всех миграций
python3 -m alembic history

# Детальная история
python3 -m alembic history --verbose
```

### Применение миграций
```bash
# Применить все миграции
python3 -m alembic upgrade head

# Применить до конкретной версии
python3 -m alembic upgrade <revision_id>

# Применить следующую миграцию
python3 -m alembic upgrade +1
```

### Откат миграций
```bash
# Откатить одну миграцию назад
python3 -m alembic downgrade -1

# Откатить все миграции
python3 -m alembic downgrade base

# Откатить до конкретной версии
python3 -m alembic downgrade <revision_id>
```

### Создание миграций
```bash
# Автогенерация на основе изменений в моделях
python3 -m alembic revision --autogenerate -m "Описание"

# Пустая миграция (для ручного редактирования)
python3 -m alembic revision -m "Custom migration"
```

## 🐳 Docker команды

### Бэкап из контейнера
```bash
# Через скрипт
docker exec -it medical_backend python3 backup_db.py backup

# Напрямую через pg_dump
docker exec medical_db pg_dump -U medical_user -F c medical_db > backup.sql
```

### Восстановление в контейнер
```bash
# Копируем бэкап
docker cp backup.sql medical_db:/tmp/

# Восстанавливаем
docker exec medical_db pg_restore -U medical_user -d medical_db /tmp/backup.sql
```

### Миграция в Docker
```bash
# Запуск миграции
docker exec -it medical_backend python3 migrate_db.py --full -m "Описание"

# Проверка статуса
docker exec -it medical_backend python3 -m alembic current
```

## 🆘 Экстренное восстановление

### Если миграция провалилась
```bash
# Вариант 1: Откат миграции
python3 migrate_db.py --rollback

# Вариант 2: Восстановление из бэкапа
python3 backup_db.py list
python3 backup_db.py restore --file backups/последний_бэкап.sql --drop
```

### Если данные повреждены
```bash
# Полное восстановление
python3 backup_db.py restore --file backups/backup.sql --drop

# Проверка целостности
python3 -c "
from database import SessionLocal
db = SessionLocal()
from sqlalchemy import text
result = db.execute(text('SELECT COUNT(*) FROM patients'))
print(f'Patients: {result.scalar()}')
"
```

## 📊 Полезные SQL команды

```sql
-- Количество записей в таблицах
SELECT 
    schemaname,
    tablename,
    (SELECT COUNT(*) FROM quote_ident(schemaname) || '.' || quote_ident(tablename)) as count
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

-- Размер таблиц
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Проверка внешних ключей
SELECT
    tc.table_name, 
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY';
```

## ⚙️ Переменные окружения

```bash
# Основная переменная
export DATABASE_URL="postgresql://medical_user:medical_pass@localhost:5432/medical_db"

# Для продакшн
export DATABASE_URL="postgresql://prod_user:prod_pass@prod-host:5432/medical_db"

# Для тестов
export DATABASE_URL="postgresql://test_user:test_pass@localhost:5432/medical_db_test"
```

## 📁 Структура директорий

```
.
├── database.py                 # Модели SQLAlchemy
├── backup_db.py               # Скрипт бэкапирования
├── migrate_db.py              # Основной скрипт миграции
├── setup_migrations.py        # Настройка Alembic
├── backup_scheduler.py        # Автоматические бэкапы
├── compare_schemas.py         # Сравнение схем
├── quick_start.sh            # Быстрый старт
├── requirements_migration.txt # Зависимости
├── alembic.ini               # Конфиг Alembic
├── alembic/
│   ├── env.py
│   └── versions/             # Миграции
├── backups/                  # Резервные копии
└── logs/                     # Логи
```

## 🎯 Частые сценарии

### Добавление нового поля
1. Добавьте поле в модель в `database.py`
2. `python3 migrate_db.py --full -m "Add field X to table Y"`

### Создание новой таблицы
1. Добавьте класс модели в `database.py`
2. `python3 migrate_db.py --full -m "Add table Z"`

### Изменение типа колонки
1. Измените тип в `database.py`
2. `python3 migrate_db.py --full -m "Change type of column X"`

### Переименование колонки
1. Создайте ручную миграцию: `alembic revision -m "Rename column"`
2. Отредактируйте файл миграции
3. `python3 migrate_db.py --apply`

## 🔐 Безопасность

### Шифрование бэкапов
```bash
# Создать зашифрованный бэкап
python3 backup_db.py backup
gpg --symmetric --cipher-algo AES256 backups/backup.sql

# Расшифровать
gpg --decrypt backups/backup.sql.gpg > backup.sql
```

### Удаление старых бэкапов
```bash
# Автоматически (через scheduler с retention_days=30)
python3 backup_scheduler.py --retention-days 30

# Вручную
find backups/ -name "*.sql" -mtime +30 -delete
```

## 📞 Помощь

```bash
# Справка по скриптам
python3 backup_db.py --help
python3 migrate_db.py --help
python3 backup_scheduler.py --help
python3 compare_schemas.py --help

# Справка Alembic
python3 -m alembic --help
python3 -m alembic upgrade --help
```
