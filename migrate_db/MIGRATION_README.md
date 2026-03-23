# Система миграции и бэкапирования базы данных

Полное решение для безопасной миграции PostgreSQL базы данных с сохранением всех данных.

## 📋 Содержание

1. [Быстрый старт](#быстрый-старт)
2. [Установка и настройка](#установка-и-настройка)
3. [Использование](#использование)
4. [Сценарии использования](#сценарии-использования)
5. [Восстановление после сбоя](#восстановление-после-сбоя)

---

## 🚀 Быстрый старт

### Первоначальная настройка (один раз)

```bash
# 1. Установите PostgreSQL client tools (если еще не установлены)
# Ubuntu/Debian:
sudo apt-get install postgresql-client

# MacOS:
brew install postgresql

# 2. Настройте систему миграций
python3 setup_migrations.py

# 3. Создайте первую миграцию (снимок текущей схемы)
python3 migrate_db.py --generate -m "Initial migration"
```

### Типичный процесс миграции

```bash
# После изменения моделей в database.py:

# Вариант 1: Полная автоматическая миграция (рекомендуется)
python3 migrate_db.py --full -m "Описание ваших изменений"

# Вариант 2: Пошаговый контроль
python3 migrate_db.py --backup              # Создать бэкап
python3 migrate_db.py --generate -m "..."   # Сгенерировать миграцию
python3 migrate_db.py --apply               # Применить миграцию
```

---

## 🔧 Установка и настройка

### Требования

- Python 3.8+
- PostgreSQL 12+
- PostgreSQL client tools (pg_dump, pg_restore, psql)

### Установка зависимостей

```bash
pip install sqlalchemy alembic psycopg2-binary --break-system-packages
```

### Структура файлов

```
project/
├── database.py              # Ваши модели SQLAlchemy
├── backup_db.py            # Скрипт бэкапирования
├── migrate_db.py           # Основной скрипт миграции
├── setup_migrations.py     # Настройка Alembic
├── alembic.ini            # Конфигурация Alembic (создается автоматически)
├── alembic/               # Директория миграций (создается автоматически)
│   ├── env.py
│   └── versions/          # Файлы миграций
└── backups/               # Резервные копии (создается автоматически)
    ├── medical_db_backup_20260215_143022.sql
    └── medical_db_backup_20260215_143022_readable.sql
```

---

## 📖 Использование

### Скрипт бэкапирования (backup_db.py)

#### Создание резервной копии

```bash
# Базовое использование
python3 backup_db.py backup

# С указанием директории
python3 backup_db.py backup --dir /path/to/backups

# С указанием URL БД
python3 backup_db.py backup --db-url "postgresql://user:pass@host:5432/dbname"
```

#### Список резервных копий

```bash
python3 backup_db.py list
python3 backup_db.py list --dir /path/to/backups
```

#### Восстановление из резервной копии

```bash
# Восстановление в существующую БД
python3 backup_db.py restore --file backups/medical_db_backup_20260215_143022.sql

# Полное восстановление (удаление и пересоздание БД)
python3 backup_db.py restore --file backups/backup.sql --drop
```

### Скрипт миграции (migrate_db.py)

#### Полная миграция (рекомендуется)

```bash
# Выполняет все шаги: бэкап → генерация → просмотр → применение → проверка
python3 migrate_db.py --full -m "Добавлено поле email в patients"

# С автоподтверждением (без интерактивного запроса)
python3 migrate_db.py --full -m "Описание" -y
```

#### Пошаговое использование

```bash
# 1. Создать только бэкап
python3 migrate_db.py --backup

# 2. Сгенерировать миграцию
python3 migrate_db.py --generate -m "Описание изменений"

# 3. Применить миграцию
python3 migrate_db.py --apply

# 4. Откатить последнюю миграцию
python3 migrate_db.py --rollback

# 5. Откатить несколько миграций
python3 migrate_db.py --rollback 3

# 6. Посмотреть историю
python3 migrate_db.py --history
```

### Работа напрямую с Alembic

```bash
# Текущая версия БД
alembic current

# История всех миграций
alembic history

# Применить все миграции
alembic upgrade head

# Откатить одну миграцию назад
alembic downgrade -1

# Откатить к конкретной версии
alembic downgrade <revision_id>

# Создать пустую миграцию (для ручного редактирования)
alembic revision -m "Custom migration"
```

---

## 💡 Сценарии использования

### Сценарий 1: Добавление нового поля в таблицу

```python
# 1. Изменяем модель в database.py
class Patient(Base):
    __tablename__ = "patients"
    # ... существующие поля ...
    email = Column(String(255), nullable=True)  # НОВОЕ ПОЛЕ
```

```bash
# 2. Выполняем миграцию
python3 migrate_db.py --full -m "Добавлено поле email в patients"

# Скрипт автоматически:
# - Создаст бэкап
# - Сгенерирует SQL для добавления колонки
# - Покажет что будет изменено
# - Запросит подтверждение
# - Применит изменения
# - Проверит целостность данных
```

### Сценарий 2: Создание новой таблицы

```python
# 1. Добавляем новую модель в database.py
class MedicalReport(Base):
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), ForeignKey("patients.id"))
    report_date = Column(Date, nullable=False)
    report_text = Column(Text)
```

```bash
# 2. Выполняем миграцию
python3 migrate_db.py --full -m "Добавлена таблица medical_reports"
```

### Сценарий 3: Изменение типа колонки

```python
# 1. Изменяем тип в database.py
class Patient(Base):
    # Было: snils = Column(String(14), ...)
    snils = Column(String(20), ...)  # Увеличили длину
```

```bash
# 2. Выполняем миграцию
python3 migrate_db.py --full -m "Увеличена длина поля SNILS"
```

### Сценарий 4: Переименование колонки

```python
# Для переименования колонки нужна ручная миграция
```

```bash
# 1. Создаем пустую миграцию
alembic revision -m "Rename diagnosis to main_diagnosis"

# 2. Редактируем созданный файл в alembic/versions/
```

```python
# В файле миграции:
def upgrade():
    op.alter_column('patients', 'diagnosis', new_column_name='main_diagnosis')

def downgrade():
    op.alter_column('patients', 'main_diagnosis', new_column_name='diagnosis')
```

```bash
# 3. Применяем миграцию
python3 migrate_db.py --apply
```

### Сценарий 5: Работа с данными в миграции

```bash
# Создаем миграцию с заполнением данных
alembic revision -m "Populate default values"
```

```python
# В файле миграции:
from alembic import op
from sqlalchemy import text

def upgrade():
    # Добавляем колонку
    op.add_column('patients', 
                  sa.Column('status', sa.String(20), nullable=True))
    
    # Заполняем значения по умолчанию
    connection = op.get_bind()
    connection.execute(
        text("UPDATE patients SET status = 'active' WHERE status IS NULL")
    )
    
    # Делаем поле обязательным
    op.alter_column('patients', 'status', nullable=False)

def downgrade():
    op.drop_column('patients', 'status')
```

---

## 🔄 Восстановление после сбоя

### Если миграция прошла неудачно

```bash
# 1. Откатить последнюю миграцию
python3 migrate_db.py --rollback

# 2. Или восстановить из бэкапа
python3 backup_db.py restore --file backups/medical_db_backup_XXXXXXXX.sql --drop
```

### Если данные повреждены

```bash
# Полное восстановление из последнего бэкапа
python3 backup_db.py restore \
    --file backups/medical_db_backup_20260215_143022.sql \
    --drop
```

### Проверка целостности данных

```python
# Создайте скрипт verify_data.py
from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Проверяем количество записей
    result = conn.execute(text("SELECT COUNT(*) FROM patients"))
    print(f"Patients: {result.scalar()}")
    
    # Проверяем внешние ключи
    result = conn.execute(text("""
        SELECT COUNT(*) 
        FROM ultrasounds u 
        LEFT JOIN patients p ON u.patient_id = p.id 
        WHERE p.id IS NULL
    """))
    orphaned = result.scalar()
    if orphaned > 0:
        print(f"⚠ Найдено {orphaned} ultrasounds без пациентов!")
```

---

## 🐳 Использование с Docker

### Создание бэкапа из контейнера

```bash
# Вариант 1: Запуск скрипта внутри контейнера
docker exec -it medical_backend python3 backup_db.py backup

# Вариант 2: Прямое использование pg_dump
docker exec medical_db pg_dump -U medical_user -F c medical_db > backup.sql
```

### Восстановление в контейнер

```bash
# Копируем бэкап в контейнер
docker cp backup.sql medical_db:/tmp/

# Восстанавливаем
docker exec medical_db pg_restore -U medical_user -d medical_db /tmp/backup.sql
```

### Миграция в Docker

```bash
# Запуск миграции в контейнере backend
docker exec -it medical_backend python3 migrate_db.py --full -m "Описание"
```

---

## ⚙️ Настройка переменных окружения

```bash
# .env файл
DATABASE_URL=postgresql://medical_user:medical_pass@localhost:5432/medical_db

# Для продакшн окружения используйте более безопасный способ
# Например, Docker secrets или переменные окружения CI/CD
```

---

## 🎯 Best Practices

1. **Всегда создавайте бэкап перед миграцией**
   ```bash
   python3 backup_db.py backup
   ```

2. **Тестируйте миграции на копии продакшн БД**
   ```bash
   # Создать тестовую БД
   createdb medical_db_test
   # Восстановить данные
   python3 backup_db.py restore --file backup.sql --db-url postgresql://user:pass@localhost/medical_db_test
   # Протестировать миграцию
   DATABASE_URL=postgresql://user:pass@localhost/medical_db_test python3 migrate_db.py --full
   ```

3. **Используйте осмысленные сообщения миграций**
   ```bash
   # Плохо
   python3 migrate_db.py --full -m "Update"
   
   # Хорошо
   python3 migrate_db.py --full -m "Add email field to patients table for notifications"
   ```

4. **Храните бэкапы в безопасном месте**
   - Регулярные автоматические бэкапы
   - Хранение в разных местах (локально + облако)
   - Шифрование бэкапов с чувствительными данными

5. **Версионируйте миграции**
   ```bash
   # Добавьте alembic/versions в git
   git add alembic/versions/*.py
   git commit -m "Add migration: описание"
   ```

6. **Документируйте сложные миграции**
   ```python
   def upgrade():
       """
       Миграция для разделения таблицы findings на отдельные типы.
       
       Шаги:
       1. Создание новых таблиц
       2. Миграция данных
       3. Удаление старой таблицы
       
       Требует: ~5 минут на 100k записей
       """
       pass
   ```

---

## 🔍 Troubleshooting

### Проблема: "pg_dump: command not found"

**Решение:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-client

# MacOS
brew install postgresql
```

### Проблема: "Alembic command not found"

**Решение:**
```bash
python3 -m pip install alembic --break-system-packages
# Или
python3 setup_migrations.py
```

### Проблема: "Permission denied" при создании бэкапа

**Решение:**
```bash
# Создайте директорию с правильными правами
mkdir -p backups
chmod 755 backups
```

### Проблема: Миграция применилась, но данные потеряны

**Решение:**
```bash
# Немедленно откатите миграцию
python3 migrate_db.py --rollback

# Восстановите из последнего бэкапа
python3 backup_db.py list  # Найдите последний бэкап
python3 backup_db.py restore --file backups/backup_XXXX.sql --drop
```

### Проблема: Конфликт миграций в команде

**Решение:**
```bash
# Проверьте текущее состояние
alembic current
alembic history

# Синхронизируйтесь с актуальной версией из git
git pull
alembic upgrade head
```

---

## 📚 Дополнительные ресурсы

- [Документация Alembic](https://alembic.sqlalchemy.org/)
- [Документация PostgreSQL](https://www.postgresql.org/docs/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)

---

## 📝 Changelog

- **v1.0** - Начальная версия системы миграций
- Автоматическое бэкапирование
- Интеграция с Alembic
- Проверка целостности данных
