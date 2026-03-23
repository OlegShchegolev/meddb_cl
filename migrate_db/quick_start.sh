#!/bin/bash
# Быстрый старт системы миграций

set -e

echo "=================================================="
echo "  НАСТРОЙКА СИСТЕМЫ МИГРАЦИЙ БАЗЫ ДАННЫХ"
echo "=================================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден. Установите Python 3.8+"
    exit 1
fi

echo "✓ Python найден: $(python3 --version)"

# Проверка PostgreSQL client tools
if ! command -v pg_dump &> /dev/null; then
    echo ""
    echo "❌ PostgreSQL client tools не найдены"
    echo ""
    echo "Установите их:"
    echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
    echo "  MacOS: brew install postgresql"
    echo ""
    exit 1
fi

echo "✓ PostgreSQL client tools найдены"

# Установка зависимостей
echo ""
echo "Установка зависимостей Python..."
python3 -m pip install -r requirements_migration.txt --break-system-packages --quiet

echo "✓ Зависимости установлены"

# Настройка Alembic
echo ""
echo "Настройка Alembic..."

# Проверяем наличие директории и файла
if [ -d "alembic" ] && [ ! -f "alembic.ini" ]; then
    echo "⚠  Обнаружена проблема: директория alembic есть, но alembic.ini отсутствует"
    echo "   Запускаем скрипт исправления..."
    python3 fix_alembic.py
else
    python3 setup_migrations.py
fi

# Создание директорий
mkdir -p backups
mkdir -p logs

echo ""
echo "=================================================="
echo "  ✓ НАСТРОЙКА ЗАВЕРШЕНА УСПЕШНО!"
echo "=================================================="
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Создайте первую миграцию (снимок текущей схемы):"
echo "   python3 migrate_db.py --generate -m 'Initial migration'"
echo ""
echo "2. Или сделайте полную миграцию после изменения моделей:"
echo "   python3 migrate_db.py --full -m 'Описание изменений'"
echo ""
echo "3. Для автоматических бэкапов:"
echo "   python3 backup_scheduler.py --schedule daily --time 03:00"
echo ""
echo "Подробная документация: MIGRATION_README.md"
echo ""
