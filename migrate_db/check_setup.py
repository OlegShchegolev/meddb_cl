#!/usr/bin/env python3
"""
Скрипт для проверки корректности установки системы миграций
"""
import sys
import subprocess
import os


def check_command(cmd, description):
    """Проверяет доступность команды"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ {description}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description}")
        print(f"  Ошибка: {e.stderr[:200]}")
        return False
    except FileNotFoundError:
        print(f"✗ {description} - команда не найдена")
        return False


def main():
    print("="*70)
    print("ПРОВЕРКА СИСТЕМЫ МИГРАЦИЙ")
    print("="*70)
    print()
    
    all_ok = True
    
    # 1. Проверка Python
    print("1. Python:")
    print(f"   Версия: {sys.version.split()[0]}")
    if sys.version_info < (3, 8):
        print("   ✗ Требуется Python 3.8+")
        all_ok = False
    else:
        print("   ✓ Версия подходит")
    print()
    
    # 2. Проверка PostgreSQL tools
    print("2. PostgreSQL client tools:")
    all_ok &= check_command(["pg_dump", "--version"], "   pg_dump")
    all_ok &= check_command(["pg_restore", "--version"], "   pg_restore")
    all_ok &= check_command(["psql", "--version"], "   psql")
    print()
    
    # 3. Проверка Python модулей
    print("3. Python модули:")
    modules = [
        ("sqlalchemy", "SQLAlchemy"),
        ("alembic", "Alembic"),
        ("psycopg2", "psycopg2"),
    ]
    
    for module, name in modules:
        try:
            __import__(module)
            print(f"   ✓ {name}")
        except ImportError:
            print(f"   ✗ {name} не установлен")
            all_ok = False
    print()
    
    # 4. Проверка Alembic команды
    print("4. Alembic:")
    all_ok &= check_command([sys.executable, "-m", "alembic", "--version"], 
                           "   python3 -m alembic")
    print()
    
    # 5. Проверка переменной окружения
    print("5. Переменные окружения:")
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # Скрываем пароль
        from urllib.parse import urlparse
        parsed = urlparse(db_url)
        safe_url = f"{parsed.scheme}://{parsed.username}:***@{parsed.hostname}:{parsed.port}{parsed.path}"
        print(f"   ✓ DATABASE_URL: {safe_url}")
    else:
        print("   ⚠ DATABASE_URL не установлена (будет использоваться значение по умолчанию)")
    print()
    
    # 6. Проверка структуры проекта
    print("6. Структура проекта:")
    files = [
        "database.py",
        "migrate_db.py",
        "backup_db.py",
        "setup_migrations.py",
    ]
    
    for file in files:
        if os.path.exists(file):
            print(f"   ✓ {file}")
        else:
            print(f"   ⚠ {file} не найден")
    print()
    
    # 7. Проверка Alembic
    print("7. Состояние Alembic:")
    if os.path.exists("alembic") and os.path.exists("alembic.ini"):
        print("   ✓ Alembic настроен")
        
        # Проверяем миграции
        if os.path.exists("alembic/versions"):
            migrations = [f for f in os.listdir("alembic/versions") if f.endswith('.py')]
            print(f"   ℹ Найдено миграций: {len(migrations)}")
    elif os.path.exists("alembic"):
        print("   ⚠ Директория alembic есть, но alembic.ini отсутствует")
        print("   → Запустите: python3 fix_alembic.py")
        all_ok = False
    else:
        print("   ⚠ Alembic не инициализирован")
        print("   → Запустите: python3 setup_migrations.py")
    print()
    
    # Итог
    print("="*70)
    if all_ok:
        print("✓ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print()
        print("Система готова к работе. Следующие шаги:")
        print("  1. python3 migrate_db.py --generate -m 'Initial migration'")
        print("  2. python3 migrate_db.py --apply")
    else:
        print("⚠ ОБНАРУЖЕНЫ ПРОБЛЕМЫ")
        print()
        print("Рекомендации:")
        print("  1. Установите недостающие компоненты")
        print("  2. Запустите: bash quick_start.sh")
    print("="*70)
    
    return 0 if all_ok else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        sys.exit(1)
