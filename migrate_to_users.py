#!/usr/bin/env python3
"""
Database Migration Script for User System
Migrates existing database to support user accounts
"""

import sqlite3
import os
from dotenv import load_dotenv
from app_with_users import app
from models import db, User, Product, Order

def backup_database():
    """Create a backup of the current database"""
    db_path = "database.db"
    if os.path.exists(db_path):
        backup_path = f"database_backup_{int(os.path.getctime(db_path))}.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✓ Database backed up to {backup_path}")
        return True
    return False

def migrate_database():
    """Migrate database to new schema with users"""
    print("=== Database Migration to User System ===")
    
    with app.app_context():
        try:
            # Check if users table exists
            with db.engine.connect() as connection:
                result = connection.execute(db.text("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")).fetchone()
                
                if not result:
                    print("Creating users table...")
                    # Create all new tables
                    db.create_all()
                    
                    # Create default admin user
                    admin_user = User.query.filter_by(username='admin').first()
                    if not admin_user:
                        admin_user = User(
                            username='admin',
                            email='admin@example.com',
                            first_name='Admin',
                            is_admin=True
                        )
                        admin_user.set_password('1234')
                        db.session.add(admin_user)
                        db.session.commit()
                        print("✓ Default admin user created")
                    
                    print("✓ Users table created successfully")
                else:
                    print("✓ Users table already exists")
                
                # Check if orders table has user_id column
                cursor = connection.execute(db.text("PRAGMA table_info(orders);"))
                columns = [row[1] for row in cursor.fetchall()]
                
                if 'user_id' not in columns:
                    print("Adding user_id column to orders table...")
                    connection.execute(db.text("ALTER TABLE orders ADD COLUMN user_id INTEGER;"))
                    connection.commit()
                    print("✓ user_id column added to orders table")
                
                if 'status' not in columns:
                    print("Adding status column to orders table...")
                    connection.execute(db.text("ALTER TABLE orders ADD COLUMN status VARCHAR(50) DEFAULT 'pending';"))
                    connection.commit()
                    print("✓ status column added to orders table")
            
            print("✅ Database migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

def test_migration():
    """Test the migrated database"""
    print("\n=== Testing Migrated Database ===")
    
    with app.app_context():
        try:
            # Test admin user
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print("✓ Admin user exists and can be queried")
                print(f"   Username: {admin_user.username}")
                print(f"   Email: {admin_user.email}")
                print(f"   Is Admin: {admin_user.is_admin}")
            
            # Test creating a test user
            test_user = User(
                username="testmigration",
                email="test@migration.com",
                first_name="Test"
            )
            test_user.set_password("testpass")
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user created successfully")
            
            # Test creating an order with user_id
            products = Product.query.all()
            if products:
                test_order = Order(
                    product_id=products[0].id,
                    user_id=test_user.id,
                    quantity=1,
                    first_name="Test",
                    state="Test State",
                    phone="123456789",
                    address="Test Address",
                    total_price=10.0
                )
                db.session.add(test_order)
                db.session.commit()
                print("✓ Order with user_id created successfully")
                
                # Clean up test data
                db.session.delete(test_order)
                db.session.commit()
            
            # Clean up test user
            db.session.delete(test_user)
            db.session.commit()
            print("✓ Test data cleaned up")
            
            print("🎉 Migration test completed successfully!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration test failed: {e}")
            raise

if __name__ == "__main__":
    load_dotenv()
    
    print("This script will migrate your database to support user accounts.")
    print("A backup will be created before migration.")
    
    response = input("Do you want to proceed? (y/N): ")
    if response.lower() in ['y', 'yes']:
        backup_database()
        
        if migrate_database():
            test_migration()
            print("\n✅ Database successfully migrated to support user accounts!")
            print("\nDefault admin credentials:")
            print("Username: admin")
            print("Password: 1234")
        else:
            print("\n❌ Migration failed. Check the errors above.")
    else:
        print("Migration cancelled.")
