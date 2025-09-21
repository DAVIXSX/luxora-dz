#!/usr/bin/env python3
"""
Data Migration Script
Migrates data from the old SQLite database to the new SQLAlchemy structure
"""

import sqlite3
import os
from dotenv import load_dotenv
from app_sql import app
from models import db, Product, Order

def migrate_data():
    """Migrate data from old SQLite database to new structure"""
    
    # Path to the old database
    old_db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    
    if not os.path.exists(old_db_path):
        print(f"Old database not found at {old_db_path}")
        print("Starting with fresh database...")
        return
    
    print("Starting data migration...")
    
    # Connect to old SQLite database
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    with app.app_context():
        # Create new tables
        db.create_all()
        
        try:
            # Migrate products
            print("Migrating products...")
            old_cursor.execute("SELECT * FROM products")
            products = old_cursor.fetchall()
            
            for product_row in products:
                # Check if product already exists
                existing_product = Product.query.filter_by(name=product_row['name']).first()
                if not existing_product:
                    new_product = Product(
                        name=product_row['name'],
                        price=product_row['price'],
                        desc=product_row['desc'],
                        image=product_row['image']
                    )
                    db.session.add(new_product)
            
            db.session.commit()
            products_count = Product.query.count()
            print(f"✓ Migrated {products_count} products")
            
            # Migrate orders
            print("Migrating orders...")
            old_cursor.execute("SELECT * FROM orders")
            orders = old_cursor.fetchall()
            
            for order_row in orders:
                # Find the corresponding product in the new database
                product = Product.query.filter_by(name=
                    old_cursor.execute("SELECT name FROM products WHERE id=?", (order_row['product_id'],)).fetchone()['name']
                ).first()
                
                if product:
                    new_order = Order(
                        product_id=product.id,
                        quantity=order_row['quantity'],
                        first_name=order_row['first_name'],
                        last_name=order_row.get('last_name', ''),
                        state=order_row['state'],
                        phone=order_row['phone'],
                        email=order_row.get('email', ''),
                        address=order_row['address'],
                        notes=order_row.get('notes', ''),
                        total_price=order_row['total_price']
                    )
                    db.session.add(new_order)
            
            db.session.commit()
            orders_count = Order.query.count()
            print(f"✓ Migrated {orders_count} orders")
            
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise
        finally:
            old_conn.close()

def backup_old_database():
    """Create a backup of the old database"""
    old_db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    if os.path.exists(old_db_path):
        backup_path = os.path.join(os.path.dirname(__file__), 'database_backup.db')
        import shutil
        shutil.copy2(old_db_path, backup_path)
        print(f"✓ Old database backed up to {backup_path}")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    print("=== Database Migration Tool ===")
    print(f"Current database URL: {os.getenv('DATABASE_URL', 'sqlite:///database.db')}")
    
    # Ask for confirmation
    response = input("Do you want to proceed with migration? (y/N): ")
    if response.lower() in ['y', 'yes']:
        backup_old_database()
        migrate_data()
    else:
        print("Migration cancelled.")
