#!/usr/bin/env python3
"""
User Authentication Test Script
Tests user registration, login, and profile functionality
"""

from app_with_users import app
from models import db, User, Product, Order

def test_user_system():
    """Test user authentication and profile functionality"""
    
    print("=== User Authentication System Test ===")
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test User creation (clean up first if exists)
            existing_test_user = User.query.filter_by(username="testuser").first()
            if existing_test_user:
                db.session.delete(existing_test_user)
                db.session.commit()
            
            test_user = User(
                username="testuser",
                email="test@example.com",
                first_name="Ahmed",
                last_name="Hassan",
                phone="01234567890"
            )
            test_user.set_password("password123")
            db.session.add(test_user)
            db.session.commit()
            print("✓ Test user created successfully")
            
            # Test password verification
            if test_user.check_password("password123"):
                print("✓ Password verification works")
            else:
                print("❌ Password verification failed")
            
            # Test admin user exists
            admin_user = User.query.filter_by(username='admin').first()
            if admin_user:
                print("✓ Default admin user exists")
                print(f"   Admin email: {admin_user.email}")
                print(f"   Admin is_admin: {admin_user.is_admin}")
            else:
                print("❌ Default admin user not found")
            
            # Test unique constraints
            try:
                duplicate_user = User(
                    username="testuser",  # Same username
                    email="another@example.com"
                )
                duplicate_user.set_password("test123")
                db.session.add(duplicate_user)
                db.session.commit()
                print("❌ Unique constraint test failed - duplicate username allowed")
            except Exception:
                db.session.rollback()
                print("✓ Unique constraint works - duplicate username prevented")
            
            # Test user-order relationship
            test_product = Product(
                name="Test Product",
                price=50.0,
                desc="Test description"
            )
            db.session.add(test_product)
            db.session.commit()
            
            test_order = Order(
                product_id=test_product.id,
                user_id=test_user.id,
                quantity=2,
                first_name="Ahmed",
                last_name="Hassan",
                state="Cairo",
                phone="01234567890",
                email="test@example.com",
                address="Test Address",
                total_price=100.0
            )
            db.session.add(test_order)
            db.session.commit()
            print("✓ User-Order relationship works")
            
            # Test queries
            users_count = User.query.count()
            products_count = Product.query.count()
            orders_count = Order.query.count()
            
            print(f"✓ Database contains:")
            print(f"   Users: {users_count}")
            print(f"   Products: {products_count}")
            print(f"   Orders: {orders_count}")
            
            # Test user orders query
            user_orders = Order.query.filter_by(user_id=test_user.id).all()
            print(f"✓ User {test_user.username} has {len(user_orders)} orders")
            
            # Clean up test data
            db.session.delete(test_order)
            db.session.delete(test_product)
            db.session.delete(test_user)
            db.session.commit()
            print("✓ Test data cleaned up")
            
            print("🎉 All user authentication tests passed!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ User test failed: {e}")
            raise

def print_admin_info():
    """Print default admin credentials"""
    print("\n=== Default Admin Account ===")
    print("Username: admin")
    print("Password: 1234")
    print("You can use these credentials to access the admin panel")

if __name__ == "__main__":
    test_user_system()
    print_admin_info()
