#!/usr/bin/env python3
"""
Скрипт для создания резервной копии базы данных PostgreSQL
"""
import os
import subprocess
from datetime import datetime
import argparse


def create_backup(backup_dir="./backups", db_url=None):
    """
    Создает резервную копию базы данных
    
    Args:
        backup_dir: Директория для сохранения бэкапов
        db_url: URL подключения к БД (если не указан, берется из env)
    """
    # Создаем директорию для бэкапов, если её нет
    os.makedirs(backup_dir, exist_ok=True)
    
    # Получаем параметры подключения из DATABASE_URL
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
    
    # Парсим DATABASE_URL
    # Формат: postgresql://user:password@host:port/database
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    db_user = parsed.username
    db_password = parsed.password
    db_host = parsed.hostname
    db_port = parsed.port or 5432
    db_name = parsed.path.lstrip('/')
    
    # Создаем имя файла с текущей датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"medical_db_backup_{timestamp}.sql")
    
    print(f"Создание резервной копии базы данных '{db_name}'...")
    print(f"Файл: {backup_file}")
    
    # Устанавливаем переменную окружения для пароля
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    try:
        # Выполняем pg_dump
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'c',  # Custom format (сжатый)
            '-b',  # Include large objects
            '-v',  # Verbose
            '-f', backup_file,
            db_name
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✓ Резервная копия успешно создана: {backup_file}")
        print(f"  Размер файла: {os.path.getsize(backup_file) / 1024:.2f} KB")
        
        # Также создаем SQL-версию для читабельности
        sql_backup_file = backup_file.replace('.sql', '_readable.sql')
        cmd_sql = [
            'pg_dump',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'p',  # Plain SQL format
            '-f', sql_backup_file,
            db_name
        ]
        
        subprocess.run(cmd_sql, env=env, capture_output=True, check=True)
        print(f"✓ SQL-версия создана: {sql_backup_file}")
        
        return backup_file
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка при создании резервной копии:")
        print(f"  {e.stderr}")
        raise
    except FileNotFoundError:
        print("✗ Ошибка: pg_dump не найден. Установите PostgreSQL client tools.")
        print("  Ubuntu/Debian: sudo apt-get install postgresql-client")
        print("  MacOS: brew install postgresql")
        raise


def restore_backup(backup_file, db_url=None, drop_existing=False):
    """
    Восстанавливает базу данных из резервной копии
    
    Args:
        backup_file: Путь к файлу резервной копии
        db_url: URL подключения к БД
        drop_existing: Удалить существующую БД перед восстановлением
    """
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Файл резервной копии не найден: {backup_file}")
    
    if db_url is None:
        db_url = os.getenv("DATABASE_URL", "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
    
    from urllib.parse import urlparse
    parsed = urlparse(db_url)
    
    db_user = parsed.username
    db_password = parsed.password
    db_host = parsed.hostname
    db_port = parsed.port or 5432
    db_name = parsed.path.lstrip('/')
    
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password
    
    print(f"Восстановление базы данных '{db_name}' из {backup_file}...")
    
    try:
        if drop_existing:
            print("⚠ Удаление существующей базы данных...")
            # Подключаемся к postgres для удаления целевой БД
            drop_cmd = [
                'psql',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', 'postgres',
                '-c', f'DROP DATABASE IF EXISTS {db_name};'
            ]
            subprocess.run(drop_cmd, env=env, check=True, capture_output=True)
            
            # Создаем новую БД
            create_cmd = [
                'psql',
                '-h', db_host,
                '-p', str(db_port),
                '-U', db_user,
                '-d', 'postgres',
                '-c', f'CREATE DATABASE {db_name};'
            ]
            subprocess.run(create_cmd, env=env, check=True, capture_output=True)
            print("✓ База данных пересоздана")
        
        # Восстанавливаем данные
        restore_cmd = [
            'pg_restore',
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-d', db_name,
            '-v',
            '--no-owner',
            '--no-acl',
            backup_file
        ]
        
        result = subprocess.run(
            restore_cmd,
            env=env,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ База данных успешно восстановлена из {backup_file}")
        else:
            # pg_restore может выдавать warnings, но всё равно работать
            print(f"⚠ Восстановление завершено с предупреждениями:")
            if result.stderr:
                print(result.stderr)
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Ошибка при восстановлении:")
        print(f"  {e.stderr}")
        raise


def list_backups(backup_dir="./backups"):
    """Выводит список доступных резервных копий"""
    if not os.path.exists(backup_dir):
        print(f"Директория {backup_dir} не существует")
        return []
    
    backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.sql') and 'readable' not in f])
    
    if not backups:
        print("Резервные копии не найдены")
        return []
    
    print("\nДоступные резервные копии:")
    print("-" * 70)
    for i, backup in enumerate(backups, 1):
        filepath = os.path.join(backup_dir, backup)
        size = os.path.getsize(filepath) / 1024
        mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
        print(f"{i}. {backup}")
        print(f"   Размер: {size:.2f} KB, Дата: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return backups


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Управление резервными копиями базы данных')
    parser.add_argument('action', choices=['backup', 'restore', 'list'], 
                       help='Действие: backup (создать), restore (восстановить), list (список)')
    parser.add_argument('--file', help='Файл резервной копии для восстановления')
    parser.add_argument('--dir', default='./backups', help='Директория для резервных копий')
    parser.add_argument('--drop', action='store_true', 
                       help='Удалить существующую БД перед восстановлением')
    parser.add_argument('--db-url', help='URL подключения к базе данных')
    
    args = parser.parse_args()
    
    try:
        if args.action == 'backup':
            create_backup(backup_dir=args.dir, db_url=args.db_url)
        elif args.action == 'restore':
            if not args.file:
                backups = list_backups(args.dir)
                if backups:
                    print("\nУкажите файл с помощью --file")
            else:
                restore_backup(args.file, db_url=args.db_url, drop_existing=args.drop)
        elif args.action == 'list':
            list_backups(args.dir)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        exit(1)
