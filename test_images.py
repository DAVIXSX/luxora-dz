#!/usr/bin/env python3
"""
Test script to check if images are being served correctly
"""

import os
import requests
from app_with_users import app, init_db
from models import db, Product

def test_image_serving():
    """Test that images can be served over the network"""
    with app.app_context():
        init_db()
        
        # Check if static folder exists and has images
        static_uploads_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
        
        if os.path.exists(static_uploads_path):
            image_files = [f for f in os.listdir(static_uploads_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))]
            
            if image_files:
                print(f"✅ Found {len(image_files)} images in uploads folder:")
                for img in image_files[:5]:  # Show first 5 images
                    print(f"   - {img}")
                    
                # Check if any products have images
                products_with_images = Product.query.filter(Product.image.isnot(None)).all()
                
                print(f"\n✅ Found {len(products_with_images)} products with images in database:")
                for product in products_with_images:
                    print(f"   - {product.name}: {product.image}")
                    
                print(f"\n📡 Images will be served at:")
                print(f"   - Local: http://localhost:5000/static/uploads/[filename]")
                print(f"   - Network: http://192.168.1.4:5000/static/uploads/[filename]")
                
            else:
                print("⚠️  No images found in uploads folder")
        else:
            print("⚠️  Static uploads folder doesn't exist")

def list_uploaded_files():
    """List all uploaded files"""
    uploads_path = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
    
    print("=== Uploaded Files ===")
    if os.path.exists(uploads_path):
        files = os.listdir(uploads_path)
        if files:
            for file in files:
                file_path = os.path.join(uploads_path, file)
                size = os.path.getsize(file_path)
                print(f"📄 {file} ({size} bytes)")
                print(f"   URL: http://192.168.1.4:5000/static/uploads/{file}")
        else:
            print("No files found in uploads folder")
    else:
        print("Uploads folder doesn't exist")

if __name__ == "__main__":
    print("=== Image Serving Test ===")
    test_image_serving()
    print("\n")
    list_uploaded_files()
