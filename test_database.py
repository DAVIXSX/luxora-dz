#!/usr/bin/env python3
"""
Database Test Script
Tests the database connection and basic CRUD operations
"""

from app_sql import app
from models import db, Product, Order

def test_database():
    """Test database operations"""
    
    print("=== Database Test ===")
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✓ Database tables created successfully")
            
            # Test Product creation
            test_product = Product(
                name="Test Product",
                price=99.99,
                desc="This is a test product",
                image="test.jpg"
            )
            db.session.add(test_product)
            db.session.commit()
            print("✓ Product created successfully")
            
            # Test Product query
            products = Product.query.all()
            print(f"✓ Found {len(products)} products in database")
            
            # Test Order creation
            test_order = Order(
                product_id=test_product.id,
                quantity=2,
                first_name="Ahmed",
                last_name="Hassan",
                state="Cairo",
                phone="01234567890",
                email="ahmed@test.com",
                address="Test Address",
                notes="Test order",
                total_price=199.98
            )
            db.session.add(test_order)
            db.session.commit()
            print("✓ Order created successfully")
            
            # Test Order query with relationship
            orders = Order.query.all()
            print(f"✓ Found {len(orders)} orders in database")
            
            if orders:
                order = orders[0]
                print(f"✓ Order product relationship: {order.product.name}")
            
            # Clean up test data
            db.session.delete(test_order)
            db.session.delete(test_product)
            db.session.commit()
            print("✓ Test data cleaned up")
            
            print("🎉 All database tests passed!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Database test failed: {e}")
            raise

if __name__ == "__main__":
    test_database()
