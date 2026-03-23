#!/usr/bin/env python3
"""
Скрипт для сравнения текущей схемы БД с моделями SQLAlchemy
Помогает понять какие изменения будут внесены миграцией
"""
import os
from sqlalchemy import create_engine, inspect, MetaData
from database import Base
from tabulate import tabulate


def compare_schemas(db_url=None):
    """Сравнивает схему БД с моделями"""
    
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", 
                          "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
    
    print("\n" + "="*80)
    print("СРАВНЕНИЕ СХЕМЫ БАЗЫ ДАННЫХ С МОДЕЛЯМИ SQLALCHEMY")
    print("="*80 + "\n")
    
    # Подключаемся к БД
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    # Получаем метаданные из моделей
    model_metadata = Base.metadata
    
    # Получаем таблицы из БД
    db_tables = set(inspector.get_table_names())
    model_tables = set(model_metadata.tables.keys())
    
    print("📋 ТАБЛИЦЫ:\n")
    
    # Новые таблицы (есть в моделях, нет в БД)
    new_tables = model_tables - db_tables
    if new_tables:
        print("➕ Будут СОЗДАНЫ:")
        for table in sorted(new_tables):
            print(f"   • {table}")
    
    # Удаленные таблицы (есть в БД, нет в моделях)
    removed_tables = db_tables - model_tables
    if removed_tables:
        print("\n➖ Будут УДАЛЕНЫ:")
        for table in sorted(removed_tables):
            print(f"   • {table}")
    
    # Общие таблицы
    common_tables = model_tables & db_tables
    
    if not new_tables and not removed_tables:
        print("✓ Все таблицы совпадают\n")
    
    # Сравниваем колонки в общих таблицах
    print("\n" + "="*80)
    print("📊 КОЛОНКИ В ТАБЛИЦАХ:\n")
    
    has_changes = False
    
    for table_name in sorted(common_tables):
        # Колонки из БД
        db_columns = {col['name']: col for col in inspector.get_columns(table_name)}
        
        # Колонки из моделей
        model_table = model_metadata.tables[table_name]
        model_columns = {col.name: col for col in model_table.columns}
        
        # Новые колонки
        new_columns = set(model_columns.keys()) - set(db_columns.keys())
        
        # Удаленные колонки
        removed_columns = set(db_columns.keys()) - set(model_columns.keys())
        
        # Измененные колонки
        changed_columns = []
        for col_name in set(model_columns.keys()) & set(db_columns.keys()):
            db_col = db_columns[col_name]
            model_col = model_columns[col_name]
            
            # Сравниваем типы (упрощенно)
            db_type = str(db_col['type'])
            model_type = str(model_col.type)
            
            if db_type != model_type or db_col['nullable'] != model_col.nullable:
                changed_columns.append({
                    'name': col_name,
                    'db_type': db_type,
                    'model_type': model_type,
                    'db_nullable': db_col['nullable'],
                    'model_nullable': model_col.nullable
                })
        
        # Выводим изменения для таблицы
        if new_columns or removed_columns or changed_columns:
            has_changes = True
            print(f"\n📦 Таблица: {table_name}")
            print("-" * 80)
            
            if new_columns:
                print("\n  ➕ Новые колонки:")
                for col_name in sorted(new_columns):
                    col = model_columns[col_name]
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    print(f"     • {col_name:30} {str(col.type):20} {nullable}")
            
            if removed_columns:
                print("\n  ➖ Удаленные колонки:")
                for col_name in sorted(removed_columns):
                    col = db_columns[col_name]
                    print(f"     • {col_name:30} {str(col['type']):20}")
            
            if changed_columns:
                print("\n  🔄 Измененные колонки:")
                for change in changed_columns:
                    print(f"\n     • {change['name']}")
                    print(f"       БД:     {change['db_type']:20} {'NULL' if change['db_nullable'] else 'NOT NULL'}")
                    print(f"       Модель: {change['model_type']:20} {'NULL' if change['model_nullable'] else 'NOT NULL'}")
    
    if not has_changes:
        print("✓ Все колонки совпадают\n")
    
    # Проверка индексов
    print("\n" + "="*80)
    print("🔍 ИНДЕКСЫ:\n")
    
    for table_name in sorted(common_tables):
        db_indexes = inspector.get_indexes(table_name)
        model_table = model_metadata.tables[table_name]
        model_indexes = [idx for idx in model_table.indexes]
        
        if db_indexes or model_indexes:
            print(f"\n📦 Таблица: {table_name}")
            
            if db_indexes:
                print("  БД:")
                for idx in db_indexes:
                    cols = ', '.join(idx['column_names'])
                    unique = "UNIQUE" if idx.get('unique') else ""
                    print(f"    • {idx['name']:30} ({cols}) {unique}")
            
            if model_indexes:
                print("  Модель:")
                for idx in model_indexes:
                    cols = ', '.join([col.name for col in idx.columns])
                    unique = "UNIQUE" if idx.unique else ""
                    print(f"    • {idx.name:30} ({cols}) {unique}")
    
    # Проверка внешних ключей
    print("\n" + "="*80)
    print("🔗 ВНЕШНИЕ КЛЮЧИ:\n")
    
    for table_name in sorted(common_tables):
        db_fks = inspector.get_foreign_keys(table_name)
        
        if db_fks:
            print(f"\n📦 Таблица: {table_name}")
            for fk in db_fks:
                constrained = ', '.join(fk['constrained_columns'])
                referred = f"{fk['referred_table']}.{', '.join(fk['referred_columns'])}"
                print(f"  • {constrained:30} → {referred}")
    
    print("\n" + "="*80)
    print("\n💡 Для применения этих изменений выполните:")
    print("   python3 migrate_db.py --full -m 'Описание изменений'\n")


def check_migration_needed(db_url=None):
    """Быстрая проверка - нужна ли миграция"""
    
    if db_url is None:
        db_url = os.getenv("DATABASE_URL")
    
    engine = create_engine(db_url)
    inspector = inspect(engine)
    
    db_tables = set(inspector.get_table_names())
    model_tables = set(Base.metadata.tables.keys())
    
    # Проверяем таблицы
    if db_tables != model_tables:
        return True
    
    # Проверяем колонки
    for table_name in model_tables:
        db_columns = {col['name'] for col in inspector.get_columns(table_name)}
        model_table = Base.metadata.tables[table_name]
        model_columns = {col.name for col in model_table.columns}
        
        if db_columns != model_columns:
            return True
    
    return False


if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='Сравнение схемы БД с моделями')
    parser.add_argument('--db-url', help='URL подключения к БД')
    parser.add_argument('--quick', action='store_true', 
                       help='Быстрая проверка (нужна ли миграция)')
    
    args = parser.parse_args()
    
    try:
        if args.quick:
            needed = check_migration_needed(args.db_url)
            if needed:
                print("⚠ Обнаружены изменения - требуется миграция")
                sys.exit(1)
            else:
                print("✓ Схема БД совпадает с моделями")
                sys.exit(0)
        else:
            # Устанавливаем tabulate если нужно
            try:
                import tabulate
            except ImportError:
                import subprocess
                print("Установка tabulate...")
                subprocess.run([sys.executable, "-m", "pip", "install", "tabulate", 
                              "--break-system-packages"], check=True)
            
            compare_schemas(args.db_url)
            
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        sys.exit(1)
