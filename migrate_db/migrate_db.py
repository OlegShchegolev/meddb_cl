#!/usr/bin/env python3
"""
Основной скрипт для безопасной миграции базы данных с сохранением данных
"""
import os
import sys
import subprocess
from datetime import datetime
import argparse


class DatabaseMigration:
    """Класс для управления миграцией базы данных"""
    
    def __init__(self, db_url=None, backup_dir="./backups"):
        self.db_url = db_url or os.getenv("DATABASE_URL", 
                                          "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
        self.backup_dir = backup_dir
        self.backup_file = None
        
    def step(self, message):
        """Выводит сообщение о текущем шаге"""
        print("\n" + "="*70)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        print("="*70)
    
    def create_backup(self):
        """Шаг 1: Создание резервной копии"""
        self.step("ШАГ 1: Создание резервной копии текущей базы данных")
        
        from backup_db import create_backup
        self.backup_file = create_backup(self.backup_dir, self.db_url)
        
        return self.backup_file
    
    def generate_migration(self, message="Auto-generated migration"):
        """Шаг 2: Генерация миграции на основе изменений в моделях"""
        self.step(f"ШАГ 2: Генерация миграции - '{message}'")
        
        try:
            cmd = [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", message]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)
            
            # Извлекаем имя созданного файла миграции
            for line in result.stdout.split('\n'):
                if 'Generating' in line:
                    print(f"✓ {line.strip()}")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка при генерации миграции:")
            print(e.stderr)
            return False
        except FileNotFoundError:
            print("✗ Alembic не найден. Запустите setup_migrations.py")
            return False
    
    def review_migration(self):
        """Шаг 3: Просмотр и проверка миграции"""
        self.step("ШАГ 3: Просмотр последней миграции")
        
        # Находим последний файл миграции
        versions_dir = "alembic/versions"
        if not os.path.exists(versions_dir):
            print("✗ Директория миграций не найдена")
            return False
        
        migrations = sorted([f for f in os.listdir(versions_dir) if f.endswith('.py')])
        if not migrations:
            print("⚠ Миграции не найдены")
            return False
        
        latest_migration = os.path.join(versions_dir, migrations[-1])
        
        print(f"\nПоследняя миграция: {migrations[-1]}")
        print("-" * 70)
        
        # Показываем содержимое
        with open(latest_migration, 'r') as f:
            lines = f.readlines()
            in_upgrade = False
            for line in lines:
                if 'def upgrade()' in line:
                    in_upgrade = True
                if in_upgrade:
                    print(line.rstrip())
                if 'def downgrade()' in line and in_upgrade:
                    break
        
        print("-" * 70)
        return True
    
    def apply_migration(self):
        """Шаг 4: Применение миграции"""
        self.step("ШАГ 4: Применение миграции к базе данных")
        
        try:
            # Показываем текущую версию
            result = subprocess.run([sys.executable, "-m", "alembic", "current"], capture_output=True, text=True)
            print("Текущая версия БД:")
            print(result.stdout)
            
            # Применяем миграцию
            print("\nПрименение миграции...")
            result = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], 
                                   capture_output=True, text=True, check=True)
            print(result.stdout)
            
            # Показываем новую версию
            result = subprocess.run([sys.executable, "-m", "alembic", "current"], capture_output=True, text=True)
            print("\nНовая версия БД:")
            print(result.stdout)
            
            print("✓ Миграция успешно применена")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка при применении миграции:")
            print(e.stderr)
            return False
    
    def verify_data(self):
        """Шаг 5: Проверка сохранности данных"""
        self.step("ШАГ 5: Проверка сохранности данных")
        
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(self.db_url)
            
            with engine.connect() as conn:
                # Проверяем количество записей в основных таблицах
                tables = [
                    'patients', 
                    'ultrasounds', 
                    'mammographies', 
                    'mrts',
                    'histology_biopsies',
                    'cytology_biopsies'
                ]
                
                print("\nКоличество записей в таблицах:")
                print("-" * 50)
                for table in tables:
                    try:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                        count = result.scalar()
                        print(f"  {table:30} {count:6} записей")
                    except Exception as e:
                        print(f"  {table:30} [ошибка: {e}]")
                print("-" * 50)
                
            print("\n✓ Проверка завершена")
            return True
            
        except Exception as e:
            print(f"✗ Ошибка при проверке данных: {e}")
            return False
    
    def rollback(self, steps=1):
        """Откат миграции"""
        self.step(f"ОТКАТ: Отмена последних {steps} миграций")
        
        try:
            target = f"head-{steps}"
            result = subprocess.run([sys.executable, "-m", "alembic", "downgrade", target], 
                                   capture_output=True, text=True, check=True)
            print(result.stdout)
            print(f"✓ Откат выполнен успешно")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Ошибка при откате:")
            print(e.stderr)
            return False
    
    def full_migration(self, message="Database schema update", auto_confirm=False):
        """Полный цикл миграции с проверками"""
        print("\n" + "="*70)
        print("БЕЗОПАСНАЯ МИГРАЦИЯ БАЗЫ ДАННЫХ")
        print("="*70)
        
        # Шаг 1: Бэкап
        try:
            self.create_backup()
        except Exception as e:
            print(f"\n✗ КРИТИЧЕСКАЯ ОШИБКА при создании бэкапа: {e}")
            print("Миграция прервана для безопасности данных")
            return False
        
        # Шаг 2: Генерация миграции
        if not self.generate_migration(message):
            print("\n✗ Миграция прервана")
            return False
        
        # Шаг 3: Просмотр миграции
        self.review_migration()
        
        # Подтверждение
        if not auto_confirm:
            print("\n" + "⚠"*35)
            response = input("\nПрименить миграцию? (yes/no): ").strip().lower()
            if response != 'yes':
                print("Миграция отменена пользователем")
                return False
        
        # Шаг 4: Применение миграции
        if not self.apply_migration():
            print("\n✗ Ошибка при применении миграции")
            print(f"\nВы можете восстановить БД из бэкапа: {self.backup_file}")
            return False
        
        # Шаг 5: Проверка данных
        if not self.verify_data():
            print("\n⚠ Обнаружены проблемы с данными")
            response = input("\nОткатить миграцию? (yes/no): ").strip().lower()
            if response == 'yes':
                self.rollback(1)
                return False
        
        print("\n" + "="*70)
        print("✓ МИГРАЦИЯ УСПЕШНО ЗАВЕРШЕНА")
        print("="*70)
        print(f"\nРезервная копия сохранена: {self.backup_file}")
        print("В случае проблем вы можете восстановить данные из этого бэкапа")
        
        return True


def main():
    parser = argparse.ArgumentParser(
        description='Безопасная миграция базы данных с сохранением данных',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  # Полная миграция (бэкап + генерация + применение + проверка)
  python migrate_db.py --full -m "Добавлено поле email в таблицу patients"
  
  # Только создать бэкап
  python migrate_db.py --backup
  
  # Только сгенерировать миграцию
  python migrate_db.py --generate -m "Описание изменений"
  
  # Применить существующие миграции
  python migrate_db.py --apply
  
  # Откатить последнюю миграцию
  python migrate_db.py --rollback
  
  # Просмотр истории миграций
  python migrate_db.py --history
        """
    )
    
    parser.add_argument('--full', action='store_true', 
                       help='Полный цикл миграции')
    parser.add_argument('--backup', action='store_true', 
                       help='Создать только бэкап')
    parser.add_argument('--generate', action='store_true', 
                       help='Только сгенерировать миграцию')
    parser.add_argument('--apply', action='store_true', 
                       help='Применить миграции')
    parser.add_argument('--rollback', type=int, nargs='?', const=1, 
                       help='Откатить N последних миграций (по умолчанию 1)')
    parser.add_argument('--history', action='store_true', 
                       help='Показать историю миграций')
    parser.add_argument('-m', '--message', default='Database schema update',
                       help='Описание миграции')
    parser.add_argument('--db-url', help='URL подключения к БД')
    parser.add_argument('--backup-dir', default='./backups', 
                       help='Директория для бэкапов')
    parser.add_argument('-y', '--yes', action='store_true', 
                       help='Автоматически подтверждать действия')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigration(db_url=args.db_url, backup_dir=args.backup_dir)
    
    try:
        if args.full:
            migrator.full_migration(message=args.message, auto_confirm=args.yes)
        elif args.backup:
            migrator.create_backup()
        elif args.generate:
            migrator.generate_migration(message=args.message)
            migrator.review_migration()
        elif args.apply:
            migrator.apply_migration()
            migrator.verify_data()
        elif args.rollback is not None:
            migrator.rollback(args.rollback)
        elif args.history:
            subprocess.run([sys.executable, "-m", "alembic", "history"])
        else:
            parser.print_help()
            
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
