#!/usr/bin/env python3
"""
Скрипт для исправления установки Alembic
Используйте, если у вас есть директория alembic, но нет alembic.ini
"""
import os
import subprocess
import sys


def fix_alembic():
    """Исправляет установку Alembic"""
    
    print("="*70)
    print("ИСПРАВЛЕНИЕ УСТАНОВКИ ALEMBIC")
    print("="*70)
    
    # Проверяем что есть и чего нет
    has_alembic_dir = os.path.exists("alembic")
    has_alembic_ini = os.path.exists("alembic.ini")
    
    print(f"\nСтатус:")
    print(f"  Директория alembic: {'✓ существует' if has_alembic_dir else '✗ отсутствует'}")
    print(f"  Файл alembic.ini:   {'✓ существует' if has_alembic_ini else '✗ отсутствует'}")
    
    # Вариант 1: Нет ни того, ни другого - просто инициализируем
    if not has_alembic_dir and not has_alembic_ini:
        print("\n→ Выполняется полная инициализация...")
        subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
        print("✓ Alembic инициализирован")
        return True
    
    # Вариант 2: Есть директория, нет ini - нужно пересоздать
    if has_alembic_dir and not has_alembic_ini:
        print("\n→ Обнаружена проблема: директория есть, но alembic.ini отсутствует")
        
        # Проверяем есть ли миграции
        versions_dir = "alembic/versions"
        migrations = []
        if os.path.exists(versions_dir):
            migrations = [f for f in os.listdir(versions_dir) if f.endswith('.py')]
        
        if migrations:
            print(f"⚠  Найдено {len(migrations)} миграций в alembic/versions/")
            print("\nВарианты:")
            print("  1. Пересоздать alembic с сохранением миграций")
            print("  2. Удалить всё и начать с нуля")
            
            choice = input("\nВаш выбор (1/2): ").strip()
            
            if choice == "1":
                # Сохраняем миграции
                print("\n→ Сохранение миграций...")
                subprocess.run(["mv", "alembic/versions", "versions_backup"], check=True)
                
                # Удаляем alembic
                subprocess.run(["rm", "-rf", "alembic"], check=True)
                
                # Инициализируем заново
                print("→ Реинициализация alembic...")
                subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
                
                # Восстанавливаем миграции
                print("→ Восстановление миграций...")
                subprocess.run(["rm", "-rf", "alembic/versions"], check=True)
                subprocess.run(["mv", "versions_backup", "alembic/versions"], check=True)
                
                print("✓ Alembic восстановлен с сохранением миграций")
            else:
                # Удаляем всё
                print("\n→ Удаление alembic...")
                subprocess.run(["rm", "-rf", "alembic"], check=True)
                
                print("→ Инициализация alembic...")
                subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
                
                print("✓ Alembic создан заново")
        else:
            print("\n→ Миграции не найдены, безопасно пересоздаём...")
            subprocess.run(["rm", "-rf", "alembic"], check=True)
            subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
            print("✓ Alembic создан заново")
        
        return True
    
    # Вариант 3: Всё на месте
    if has_alembic_dir and has_alembic_ini:
        print("\n✓ Alembic уже настроен корректно")
        return True
    
    return False


def configure_alembic():
    """Настраивает alembic.ini и env.py"""
    
    print("\n" + "="*70)
    print("НАСТРОЙКА КОНФИГУРАЦИИ ALEMBIC")
    print("="*70)
    
    # Настройка alembic.ini
    print("\nНастройка alembic.ini...")
    try:
        with open("alembic.ini", "r") as f:
            config = f.read()
        
        # Комментируем статичный URL
        if "sqlalchemy.url = driver://user:pass@localhost/dbname" in config:
            config = config.replace(
                "sqlalchemy.url = driver://user:pass@localhost/dbname",
                "# sqlalchemy.url = driver://user:pass@localhost/dbname\n"
                "# URL берется из переменной окружения DATABASE_URL через env.py"
            )
            
            with open("alembic.ini", "w") as f:
                f.write(config)
            
            print("✓ alembic.ini обновлен")
        else:
            print("⚠ alembic.ini уже настроен или имеет нестандартную конфигурацию")
    except Exception as e:
        print(f"✗ Ошибка при настройке alembic.ini: {e}")
        return False
    
    # Настройка env.py
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
    
    try:
        with open("alembic/env.py", "w") as f:
            f.write(env_content)
        print("✓ alembic/env.py обновлен")
    except Exception as e:
        print(f"✗ Ошибка при настройке env.py: {e}")
        return False
    
    return True


def main():
    print()
    
    # Шаг 1: Исправление структуры
    if not fix_alembic():
        print("\n✗ Не удалось исправить установку Alembic")
        return 1
    
    # Шаг 2: Настройка конфигурации
    if not configure_alembic():
        print("\n✗ Не удалось настроить конфигурацию Alembic")
        return 1
    
    print("\n" + "="*70)
    print("✓ ALEMBIC УСПЕШНО НАСТРОЕН!")
    print("="*70)
    print("\nСледующие шаги:")
    print("  1. Создайте первую миграцию:")
    print("     python3 migrate_db.py --generate -m 'Initial migration'")
    print("\n  2. Или выполните полную миграцию:")
    print("     python3 migrate_db.py --full -m 'Описание изменений'")
    print()
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        sys.exit(1)
