#!/usr/bin/env python3
"""
Migration script to create product_requests table
Run this once to add the new table to your existing database
"""
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def migrate_database():
    """Create the product_requests table"""
    print("Creating product_requests table...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Create the product_requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS product_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                user_name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                state TEXT NOT NULL,
                address TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                message TEXT,
                status TEXT DEFAULT 'pending',
                total_price REAL,
                created_at DATETIME NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_product_requests_status 
            ON product_requests(status)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_product_requests_created_at 
            ON product_requests(created_at DESC)
        ''')
        
        conn.commit()
        print("✅ product_requests table created successfully!")
        
        # Show table info
        cursor.execute("PRAGMA table_info(product_requests)")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()
