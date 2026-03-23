#!/usr/bin/env python3
"""
Скрипт для инициализации и настройки Alembic для миграций базы данных
"""
import os
import subprocess
import sys


def setup_alembic():
    """Настраивает Alembic для проекта"""
    
    print("Установка Alembic...")
    subprocess.run([sys.executable, "-m", "pip", "install", "alembic", "--break-system-packages"], 
                   check=True)
    
    print("\nИнициализация Alembic...")
    alembic_exists = os.path.exists("alembic")
    alembic_ini_exists = os.path.exists("alembic.ini")
    
    if not alembic_exists:
        subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
        print("✓ Alembic инициализирован")
    elif not alembic_ini_exists:
        print("⚠ Директория alembic существует, но alembic.ini отсутствует")
        print("Создание alembic.ini...")
        subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
        print("✓ alembic.ini создан")
    else:
        print("⚠ Alembic уже настроен")
    
    # Обновляем alembic.ini
    print("\nНастройка alembic.ini...")
    if not os.path.exists("alembic.ini"):
        print("✗ Ошибка: alembic.ini не создался. Попробуйте:")
        print("  1. Удалите директорию alembic: rm -rf alembic")
        print("  2. Запустите снова: python3 setup_migrations.py")
        return
    
    with open("alembic.ini", "r") as f:
        config = f.read()
    
    # Заменяем sqlalchemy.url на переменную окружения
    config = config.replace(
        "sqlalchemy.url = driver://user:pass@localhost/dbname",
        "# sqlalchemy.url = driver://user:pass@localhost/dbname\n"
        "# URL берется из env.py"
    )
    
    with open("alembic.ini", "w") as f:
        f.write(config)
    
    print("✓ alembic.ini обновлен")
    
    # Обновляем alembic/env.py
    print("\nНастройка alembic/env.py...")
    env_content = '''from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Импортируем модели
from database import Base
import database

# this is the Alembic Config object
config = context.config

# Получаем DATABASE_URL из переменных окружения
database_url = os.getenv("DATABASE_URL", "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
config.set_main_option("sqlalchemy.url", database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные моделей для автогенерации миграций
target_metadata = Base.metadata

def run_migrations_offline() -> None:
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


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  # Отслеживать изменения типов
            compare_server_default=True,  # Отслеживать изменения значений по умолчанию
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''
    
    with open("alembic/env.py", "w") as f:
        f.write(env_content)
    
    print("✓ alembic/env.py обновлен")
    print("\n" + "="*70)
    print("Alembic настроен успешно!")
    print("="*70)


if __name__ == "__main__":
    setup_alembic()
