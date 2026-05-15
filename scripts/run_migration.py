#!/usr/bin/env python3
import os, runpy
# Set defaults (you can edit these before running if needed)
os.environ.setdefault('DATABASE_URI', 'mysql+pymysql://root@127.0.0.1:3306/kids_ecommerce?charset=utf8mb4')
os.environ.setdefault('SQLITE_PATH', r'instance\kids_ecommerce.db')
runpy.run_path('scripts/migrate_sqlite_to_mysql.py', run_name='__main__')
