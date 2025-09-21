#!/usr/bin/env python3
"""
Admin User Update Script
Removes old admin user and creates new admin user with youcef/kadari credentials
"""

from app_with_users import app, init_db
from models import db, User

def update_admin_user():
    """Update admin user credentials"""
    print("=== Admin User Update ===")
    
    with app.app_context():
        try:
            # Initialize database
            db.create_all()
            
            # Remove old admin user if exists
            old_admin = User.query.filter_by(username='admin').first()
            if old_admin:
                db.session.delete(old_admin)
                print("✓ Removed old admin user (admin)")
            
            # Check if new admin already exists
            new_admin = User.query.filter_by(username='youcef').first()
            if new_admin:
                print("✓ Admin user 'youcef' already exists")
                # Update password in case it's different
                new_admin.set_password('kadari')
                new_admin.is_admin = True
                db.session.commit()
                print("✓ Updated admin user password")
            else:
                # Create new admin user
                new_admin = User(
                    username='youcef',
                    email='youcef@example.com',
                    first_name='Youcef',
                    is_admin=True
                )
                new_admin.set_password('kadari')
                db.session.add(new_admin)
                db.session.commit()
                print("✓ Created new admin user (youcef/kadari)")
            
            print("\n🎉 Admin user updated successfully!")
            print("=" * 40)
            print("👤 New Admin Credentials:")
            print("   Username: youcef")
            print("   Password: kadari")
            print("=" * 40)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Failed to update admin user: {e}")
            raise

if __name__ == "__main__":
    update_admin_user()
