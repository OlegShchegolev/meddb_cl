#!/usr/bin/env python3
"""
Скрипт для автоматического резервного копирования базы данных по расписанию
"""
import os
import time
import schedule
from datetime import datetime
from backup_db import create_backup
import logging


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backup_scheduler.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BackupScheduler:
    """Планировщик автоматических резервных копий"""
    
    def __init__(self, backup_dir="./backups", retention_days=30):
        self.backup_dir = backup_dir
        self.retention_days = retention_days
        self.db_url = os.getenv("DATABASE_URL", 
                                "postgresql://medical_user:medical_pass@localhost:5432/medical_db")
    
    def run_backup(self):
        """Выполняет резервное копирование"""
        try:
            logger.info("Запуск автоматического резервного копирования...")
            backup_file = create_backup(self.backup_dir, self.db_url)
            logger.info(f"✓ Резервная копия создана: {backup_file}")
            
            # Очистка старых бэкапов
            self.cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"✗ Ошибка при создании резервной копии: {e}")
    
    def cleanup_old_backups(self):
        """Удаляет резервные копии старше заданного количества дней"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            current_time = time.time()
            retention_seconds = self.retention_days * 24 * 60 * 60
            
            deleted_count = 0
            for filename in os.listdir(self.backup_dir):
                filepath = os.path.join(self.backup_dir, filename)
                
                # Проверяем только файлы резервных копий
                if not filename.endswith('.sql'):
                    continue
                
                file_age = current_time - os.path.getmtime(filepath)
                
                if file_age > retention_seconds:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Удален старый бэкап: {filename}")
            
            if deleted_count > 0:
                logger.info(f"Удалено {deleted_count} старых резервных копий")
                
        except Exception as e:
            logger.error(f"Ошибка при очистке старых бэкапов: {e}")
    
    def start_scheduler(self, schedule_type="daily", time_str="03:00"):
        """
        Запускает планировщик резервного копирования
        
        Args:
            schedule_type: Тип расписания ('hourly', 'daily', 'weekly')
            time_str: Время для daily/weekly в формате "HH:MM"
        """
        logger.info("="*70)
        logger.info("ПЛАНИРОВЩИК АВТОМАТИЧЕСКИХ РЕЗЕРВНЫХ КОПИЙ")
        logger.info("="*70)
        logger.info(f"Директория бэкапов: {self.backup_dir}")
        logger.info(f"Хранение бэкапов: {self.retention_days} дней")
        logger.info(f"База данных: {self.db_url.split('@')[-1]}")
        
        if schedule_type == "hourly":
            schedule.every().hour.do(self.run_backup)
            logger.info("Расписание: Каждый час")
            
        elif schedule_type == "daily":
            schedule.every().day.at(time_str).do(self.run_backup)
            logger.info(f"Расписание: Каждый день в {time_str}")
            
        elif schedule_type == "weekly":
            schedule.every().sunday.at(time_str).do(self.run_backup)
            logger.info(f"Расписание: Каждое воскресенье в {time_str}")
        
        logger.info("="*70)
        logger.info("Планировщик запущен. Нажмите Ctrl+C для остановки")
        logger.info("="*70)
        
        # Создаем первую резервную копию сразу
        logger.info("\nСоздание первой резервной копии...")
        self.run_backup()
        
        # Основной цикл планировщика
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Проверяем каждую минуту
                
        except KeyboardInterrupt:
            logger.info("\nПланировщик остановлен пользователем")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Автоматическое резервное копирование БД')
    parser.add_argument('--schedule', choices=['hourly', 'daily', 'weekly'], 
                       default='daily',
                       help='Частота резервного копирования (по умолчанию: daily)')
    parser.add_argument('--time', default='03:00',
                       help='Время для daily/weekly в формате HH:MM (по умолчанию: 03:00)')
    parser.add_argument('--retention-days', type=int, default=30,
                       help='Количество дней хранения бэкапов (по умолчанию: 30)')
    parser.add_argument('--backup-dir', default='./backups',
                       help='Директория для бэкапов (по умолчанию: ./backups)')
    parser.add_argument('--db-url',
                       help='URL подключения к БД (по умолчанию: из DATABASE_URL)')
    
    args = parser.parse_args()
    
    # Создаем планировщик
    scheduler = BackupScheduler(
        backup_dir=args.backup_dir,
        retention_days=args.retention_days
    )
    
    if args.db_url:
        scheduler.db_url = args.db_url
    
    # Запускаем планировщик
    scheduler.start_scheduler(
        schedule_type=args.schedule,
        time_str=args.time
    )


if __name__ == "__main__":
    # Установка зависимости
    import subprocess
    import sys
    
    try:
        import schedule
    except ImportError:
        print("Установка модуля schedule...")
        subprocess.run([sys.executable, "-m", "pip", "install", "schedule", 
                       "--break-system-packages"], check=True)
        import schedule
    
    main()
