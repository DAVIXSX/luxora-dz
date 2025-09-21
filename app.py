import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, Response
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = "mysecretkey"  # غيّره عندك

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER), exist_ok=True)

ADMIN_USERNAME = "luxoradz"
ADMIN_PASSWORD = "kadari"
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL DEFAULT 0,
                desc TEXT,
                image TEXT,
                category_id INTEGER,
                FOREIGN KEY(category_id) REFERENCES categories(id)
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER,
                first_name TEXT,
                last_name TEXT,
                state TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT,
                total_price REAL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)
        # Product requests table for inquiries
        conn.execute("""
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
        """)
        # Admins table for authentication
        conn.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        # Add categories table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            )
        """)
        # Add product_images table for multiple images per product
        conn.execute("""
            CREATE TABLE IF NOT EXISTS product_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                image_path TEXT NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE,
                FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)
        # Seed default admin if not exists
        conn.execute(
            "INSERT OR IGNORE INTO admins (username, password_hash) VALUES (?, ?)",
            (ADMIN_USERNAME, generate_password_hash(ADMIN_PASSWORD))
        )
        # Seed default categories if not exist
        try:
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", ("إلكترونيات",))
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", ("أجهزة منزلية",))
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", ("إكسسوارات",))
        except:
            pass
init_db()

# الصفحة الرئيسية - عرض المنتجات
@app.route("/")
def index():
    with get_db_connection() as conn:
        products = conn.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("index.html", products=products)

# صفحة المنتج - تعرض تفاصيل المنتج + زر اضافة للكمية
@app.route("/product/<int:pid>")
def product(pid):
    with get_db_connection() as conn:
        product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if not product:
            flash("المنتج غير موجود.", "error")
            return redirect(url_for("index"))
        
        # Fetch all images for this product
        images = conn.execute("SELECT * FROM product_images WHERE product_id=? ORDER BY is_primary DESC, id ASC", (pid,)).fetchall()
    
    return render_template("product.html", product=product, images=images)

# استقبال الطلب مباشرة من صفحة المنتج - عرض نموذج المعلومات
@app.route("/order/<int:pid>", methods=["GET", "POST"])
def order(pid):
    print(f"[DEBUG] Order route called - PID: {pid}, Method: {request.method}")
    print(f"[DEBUG] Form data: {dict(request.form)}")
    print(f"[DEBUG] Args data: {dict(request.args)}")
    
    with get_db_connection() as conn:
        product = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not product:
        print(f"[DEBUG] Product not found for PID: {pid}")
        flash("المنتج غير موجود", "error")
        return redirect(url_for("index"))
    
    print(f"[DEBUG] Product found: {product['name']}")
    
    if request.method == "GET":
        print(f"[DEBUG] GET request - showing customer info form")
        # عرض نموذج المعلومات
        quantity = request.args.get("quantity", 1, type=int)
        print(f"[DEBUG] Quantity from args: {quantity}")
        return render_template("customer_info.html", product=product, quantity=quantity)
    
    # Check if this is just a POST from product page with quantity
    if "first_name" not in request.form:
        print(f"[DEBUG] POST from product page (no first_name) - redirecting to GET with quantity")
        # This is from the product page, just get quantity and redirect to GET to show customer info form
        quantity = request.form.get("quantity", 1, type=int)
        print(f"[DEBUG] Quantity from form: {quantity}")
        return redirect(url_for("order", pid=pid, quantity=quantity))
    
    # POST - معالجة النموذج
    print(f"[DEBUG] Processing customer info form")
    quantity = request.form.get("quantity", 1, type=int)
    first_name = request.form.get("first_name", "").strip()
    last_name = request.form.get("last_name", "").strip()
    phone = request.form.get("phone", "").strip()
    state = request.form.get("state", "").strip()
    address = request.form.get("address", "").strip()
    notes = request.form.get("notes", "").strip()
    
    print(f"[DEBUG] Customer info: name='{first_name}', phone='{phone}', state='{state}', quantity={quantity}")

    # التحقق من الحقول المطلوبة (العنوان اختياري)
    if not all([first_name, phone, state]):
        print(f"[DEBUG] Validation failed - missing required fields")
        flash("الرجاء تعبئة الحقول المطلوبة: الاسم، رقم الهاتف، والولاية", "error")
        return render_template("customer_info.html", product=product, quantity=quantity)

    # حساب السعر الإجمالي
    total_price = float(product["price"]) * quantity

    # حفظ الطلب والطلبات في قاعدة البيانات
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # حفظ في جدول الطلبات (orders)
            cursor.execute(
                """
                INSERT INTO orders 
                (product_id, quantity, first_name, last_name, phone, state, address, notes, total_price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (pid, quantity, first_name, last_name, phone, state, address, notes, total_price)
            )
            order_id = cursor.lastrowid
            
            # حفظ في جدول طلبات المنتجات (product_requests) أيضاً
            full_name = f"{first_name} {last_name}".strip()
            email = request.form.get("email", "").strip() or None  # Optional email
            cursor.execute(
                """
                INSERT INTO product_requests 
                (product_id, user_name, email, phone, state, address, quantity, message, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'ordered')
                """,
                (pid, full_name, email, phone, state, address, quantity, notes, total_price)
            )
            request_id = cursor.lastrowid
            
            conn.commit()

        # توجيه المستخدم إلى صفحة تأكيد الطلب
        print(f"[DEBUG] Order saved successfully with ID: {order_id}, Request ID: {request_id}")
        print(f"[DEBUG] Redirecting to order_confirmation with ID: {order_id}")
        return redirect(url_for("order_confirmation", order_id=order_id))
    except Exception as e:
        print("Error saving order:", e)
        flash("حدث خطأ أثناء حفظ الطلب. حاول مرة أخرى.", "error")
        return render_template("customer_info.html", product=product, quantity=quantity)

# تأكيد الطلب - صفحة تعرض تفاصيل الطلب
@app.route("/order/confirmation/<int:order_id>")
def order_confirmation(order_id):
    print(f"[DEBUG] Order confirmation route called with ID: {order_id}")
    with get_db_connection() as conn:
        order = conn.execute("""
            SELECT o.*, p.name as product_name, p.price as unit_price
            FROM orders o JOIN products p ON o.product_id = p.id
            WHERE o.id = ?
        """, (order_id,)).fetchone()
    if not order:
        print(f"[DEBUG] Order not found for ID: {order_id}")
        flash("الطلب غير موجود.", "error")
        return redirect(url_for("index"))
    print(f"[DEBUG] Order found: {order['product_name']} x {order['quantity']}")
    return render_template("order_confirmation.html", order=order)

# تسجيل الدخول للأدمن
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        # Debug logging
        print(f"[DEBUG] Login attempt - Username: '{username}', Password length: {len(password)}")
        print(f"[DEBUG] Form data: {dict(request.form)}")
        
        # Look up admin in DB and verify password hash
        with get_db_connection() as conn:
            admin_row = conn.execute(
                "SELECT * FROM admins WHERE username = ?",
                (username,)
            ).fetchone()
        
        if admin_row:
            print(f"[DEBUG] Found user: {admin_row['username']}")
            password_valid = check_password_hash(admin_row["password_hash"], password)
            print(f"[DEBUG] Password valid: {password_valid}")
            
            if password_valid:
                session["admin"] = True
                print(f"[DEBUG] Login successful, redirecting to admin")
                return redirect(url_for("admin"))
        else:
            print(f"[DEBUG] No user found with username: '{username}'")
        
        print(f"[DEBUG] Login failed, showing error message")
        flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    flash("تم تسجيل الخروج.", "success")
    return redirect(url_for("index"))

# لوحة الإدارة - إضافة منتجات وعرض الطلبات
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        # Handle multiple product submissions
        products_added = 0
        products_with_errors = []
        
        try:
            # Get all form data
            form_data = request.form
            files_data = request.files
            
            # Find all product entries (look for name_0, name_1, etc.)
            product_indices = set()
            for key in form_data.keys():
                if key.startswith('name_'):
                    index = key.split('_')[1]
                    product_indices.add(index)
            
            # If no products found, show error
            if not product_indices:
                flash("لم يتم العثور على أي منتجات لإضافتها.", "error")
                return redirect(url_for("admin"))
            
            # Process each product
            for index in product_indices:
                name = request.form.get(f"name_{index}", "").strip()
                price = request.form.get(f"price_{index}", type=float)
                desc = request.form.get(f"desc_{index}", "").strip()
                category_id = request.form.get(f"category_{index}", type=int)
                # Handle multiple image uploads
                image_files = request.files.getlist(f"images_{index}")
                
                # Validate required fields
                if not name:
                    products_with_errors.append(f"المنتج #{int(index)+1}: اسم المنتج مطلوب")
                    continue
                    
                if price is None:
                    products_with_errors.append(f"المنتج #{int(index)+1}: السعر مطلوب")
                    continue
                    
                if price < 0:
                    products_with_errors.append(f"المنتج #{int(index)+1}: السعر يجب أن يكون قيمة موجبة")
                    continue
                
                # Handle image uploads (multiple images)
                image_filenames = []
                for image_file in image_files:
                    if image_file and image_file.filename != "":
                        # Validate file type
                        if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                            products_with_errors.append(f"المنتج #{int(index)+1}: نوع الصورة غير مدعوم")
                            continue
                            
                        filename = secure_filename(image_file.filename)
                        target = os.path.join(BASE_DIR, app.config["UPLOAD_FOLDER"], filename)
                        image_file.save(target)
                        image_filenames.append(f"uploads/{filename}")
                
                # Add product to database
                try:
                    with get_db_connection() as conn:
                        cursor = conn.cursor()
                        # Insert product and get its ID
                        cursor.execute("INSERT INTO products (name, price, desc, image, category_id) VALUES (?, ?, ?, ?, ?)",
                                     (name, price, desc, image_filenames[0] if image_filenames else None, category_id))
                        product_id = cursor.lastrowid
                        
                        # Insert all images into product_images table
                        for i, image_path in enumerate(image_filenames):
                            is_primary = (i == 0)  # First image is primary
                            cursor.execute("INSERT INTO product_images (product_id, image_path, is_primary) VALUES (?, ?, ?)",
                                         (product_id, image_path, is_primary))
                        
                        conn.commit()
                        products_added += 1
                except Exception as e:
                    products_with_errors.append(f"المنتج #{int(index)+1}: خطأ في حفظ المنتج - {str(e)}")
            
            # Provide feedback to user
            if products_added > 0:
                if products_added == 1:
                    flash("تم إضافة المنتج بنجاح.", "success")
                else:
                    flash(f"تم إضافة {products_added} منتجات بنجاح.", "success")
            
            if products_with_errors:
                error_message = "حدثت أخطاء في بعض المنتجات: " + "; ".join(products_with_errors)
                flash(error_message, "error")
                
        except Exception as e:
            flash(f"حدث خطأ غير متوقع: {str(e)}", "error")
            return redirect(url_for("admin"))

        return redirect(url_for("admin"))

    # Handle GET request with search/filter parameters
    search_query = request.args.get('search', '').strip()
    category_filter = request.args.get('category', type=int)
    sort_by = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'DESC')
    
    # Build query based on filters
    base_query = """
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id
    """
    
    count_query = "SELECT COUNT(*) as count FROM products p"
    
    where_clauses = []
    params = []
    
    if search_query:
        where_clauses.append("(p.name LIKE ? OR p.desc LIKE ?)")
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        count_query += " WHERE p.name LIKE ? OR p.desc LIKE ?"
    
    if category_filter:
        category_clause = "p.category_id = ?"
        if where_clauses:
            where_clauses.append(category_clause)
        else:
            where_clauses.append(category_clause)
        params.append(category_filter)
        if search_query:
            count_query += " AND p.category_id = ?"
        else:
            count_query += " WHERE p.category_id = ?"
    
    if where_clauses:
        base_query += " WHERE " + " AND ".join(where_clauses)
    
    # Add sorting
    valid_sort_columns = ['id', 'name', 'price']
    valid_sort_orders = ['ASC', 'DESC']
    
    if sort_by in valid_sort_columns and sort_order in valid_sort_orders:
        base_query += f" ORDER BY p.{sort_by} {sort_order}"
    else:
        base_query += " ORDER BY p.id DESC"
    
    with get_db_connection() as conn:
        products = conn.execute(base_query, params).fetchall()
        orders = conn.execute("SELECT o.id, p.name as product_name, o.quantity, o.first_name, o.last_name, o.state, o.phone, (o.quantity * p.price) as total_price FROM orders o JOIN products p ON o.product_id = p.id ORDER BY o.id DESC").fetchall()
        categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        
        # Get total product count for statistics
        if search_query or category_filter:
            count_params = []
            if search_query:
                count_params.extend([f"%{search_query}%", f"%{search_query}%"])
            if category_filter:
                count_params.append(category_filter)
            total_products = conn.execute(count_query, count_params).fetchone()['count']
        else:
            total_products = conn.execute("SELECT COUNT(*) as count FROM products").fetchone()['count']
    
    return render_template("admin.html", 
                         products=products, 
                         orders=orders, 
                         categories=categories,
                         search_query=search_query,
                         category_filter=category_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         total_products=total_products)

# Add category route
@app.route("/admin/add_category", methods=["POST"])
def add_category():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    name = request.form.get("category_name", "").strip()
    description = request.form.get("category_description", "").strip()
    
    if not name:
        flash("اسم الفئة مطلوب", "error")
        return redirect(url_for("admin"))
    
    try:
        with get_db_connection() as conn:
            conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
            conn.commit()
        flash("تمت إضافة الفئة بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء إضافة الفئة: {str(e)}", "error")
    
    return redirect(url_for("admin"))

# Delete category route
@app.route("/admin/delete_category/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    try:
        with get_db_connection() as conn:
            # Check if category has products
            product_count = conn.execute("SELECT COUNT(*) as count FROM products WHERE category_id = ?", (category_id,)).fetchone()
            if product_count['count'] > 0:
                flash("لا يمكن حذف الفئة لأنها تحتوي على منتجات", "error")
                return redirect(url_for("admin"))
            
            conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
            conn.commit()
        flash("تم حذف الفئة بنجاح", "success")
    except Exception as e:
        flash(f"حدث خطأ أثناء حذف الفئة: {str(e)}", "error")
    
    return redirect(url_for("admin"))

# Edit product route
@app.route("/admin/edit/<int:pid>", methods=["GET", "POST"])
def edit_product(pid):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    with get_db_connection() as conn:
        product = conn.execute("SELECT * FROM products WHERE id = ?", (pid,)).fetchone()
        categories = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        
        if not product:
            flash("المنتج غير موجود", "error")
            return redirect(url_for("admin"))
        
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            price = request.form.get("price", type=float)
            desc = request.form.get("desc", "").strip()
            category_id = request.form.get("category", type=int)
            # Handle multiple image uploads
            image_files = request.files.getlist("images")
            
            # Validate required fields
            if not name:
                flash("اسم المنتج مطلوب", "error")
                return render_template("edit_product.html", product=product, categories=categories)
                
            if price is None:
                flash("السعر مطلوب", "error")
                return render_template("edit_product.html", product=product, categories=categories)
                
            if price < 0:
                flash("السعر يجب أن يكون قيمة موجبة", "error")
                return render_template("edit_product.html", product=product, categories=categories)
            
            # Handle image uploads (multiple images)
            image_filenames = []
            for image_file in image_files:
                if image_file and image_file.filename != "":
                    # Validate file type
                    if not image_file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                        flash("نوع الصورة غير مدعوم", "error")
                        return render_template("edit_product.html", product=product, categories=categories)
                        
                    filename = secure_filename(image_file.filename)
                    target = os.path.join(BASE_DIR, app.config["UPLOAD_FOLDER"], filename)
                    image_file.save(target)
                    image_filenames.append(f"uploads/{filename}")
            
            # Use first new image as main image, or keep existing if no new images
            main_image = image_filenames[0] if image_filenames else product['image']
            
            # Update product in database
            try:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    # Update product
                    cursor.execute("""
                        UPDATE products 
                        SET name = ?, price = ?, desc = ?, image = ?, category_id = ? 
                        WHERE id = ?
                    """, (name, price, desc, main_image, category_id, pid))
                    
                    # If new images were uploaded, add them to product_images table
                    if image_filenames:
                        for i, image_path in enumerate(image_filenames):
                            is_primary = (i == 0)  # First image is primary
                            cursor.execute("INSERT INTO product_images (product_id, image_path, is_primary) VALUES (?, ?, ?)",
                                         (pid, image_path, is_primary))
                    
                    conn.commit()
                flash("تم تحديث المنتج بنجاح", "success")
                return redirect(url_for("admin"))
            except Exception as e:
                flash(f"حدث خطأ أثناء تحديث المنتج: {str(e)}", "error")
        
        return render_template("edit_product.html", product=product, categories=categories)

# Export products to CSV
@app.route("/admin/export/products")
def export_products():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    try:
        with get_db_connection() as conn:
            products = conn.execute("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id 
                ORDER BY p.id DESC
            """).fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'اسم المنتج', 'السعر', 'الوصف', 'الفئة', 'الصورة'])
        
        # Write data
        for product in products:
            writer.writerow([
                product['id'],
                product['name'],
                product['price'],
                product['desc'] or '',
                product['category_name'] or '',
                product['image'] or ''
            ])
        
        # Create response
        csv_data = output.getvalue()
        output.close()
        
        # Return as CSV file
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=products.csv"}
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير المنتجات: {str(e)}", "error")
        return redirect(url_for("admin"))

# Export orders to CSV
@app.route("/admin/export/orders")
def export_orders():
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    try:
        with get_db_connection() as conn:
            orders = conn.execute("""
                SELECT o.*, p.name as product_name, (o.quantity * p.price) as total_price 
                FROM orders o 
                JOIN products p ON o.product_id = p.id 
                ORDER BY o.id DESC
            """).fetchall()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['رقم الطلب', 'اسم المنتج', 'الكمية', 'الاسم الأول', 'الاسم الأخير', 'الولاية', 'رقم الهاتف', 'البريد الإلكتروني', 'العنوان', 'الملاحظات', 'السعر الإجمالي', 'التاريخ'])
        
        # Write data
        for order in orders:
            writer.writerow([
                order['id'],
                order['product_name'],
                order['quantity'],
                order['first_name'],
                order['last_name'],
                order['state'],
                order['phone'],
                order['email'] or '',
                order['address'] or '',
                order['notes'] or '',
                order['total_price'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # You might want to add a created_at field to orders
            ])
        
        # Create response
        csv_data = output.getvalue()
        output.close()
        
        # Return as CSV file
        return Response(
            csv_data,
            mimetype='text/csv',
            headers={"Content-Disposition": "attachment; filename=orders.csv"}
        )
    except Exception as e:
        flash(f"حدث خطأ أثناء تصدير الطلبات: {str(e)}", "error")
        return redirect(url_for("admin"))

# ========== API ENDPOINTS FOR PRODUCT REQUESTS ==========

# API: Submit a product request (JSON)
@app.route("/api/product-requests", methods=["POST"])
def api_product_request():
    """API endpoint to submit product requests via JSON"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
        
        # Required fields validation
        required_fields = ['product_id', 'user_name', 'phone', 'state']
        for field in required_fields:
            if not data.get(field):
                return jsonify({"error": f"Field '{field}' is required"}), 400
        
        # Get product details
        with get_db_connection() as conn:
            product = conn.execute("SELECT * FROM products WHERE id=?", (data['product_id'],)).fetchone()
            if not product:
                return jsonify({"error": "Product not found"}), 404
        
        # Calculate total price
        quantity = data.get('quantity', 1)
        total_price = float(product['price']) * quantity
        
        # Insert into product_requests table
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO product_requests 
                (product_id, user_name, email, phone, state, address, quantity, message, total_price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data['product_id'],
                    data['user_name'],
                    data.get('email'),
                    data['phone'],
                    data['state'],
                    data.get('address'),
                    quantity,
                    data.get('message'),
                    total_price,
                    'pending'
                )
            )
            request_id = cursor.lastrowid
            conn.commit()
        
        # Return success response
        response_data = {
            "success": True,
            "request_id": request_id,
            "product_name": product['name'],
            "user_name": data['user_name'],
            "quantity": quantity,
            "total_price": total_price,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        print(f"[DEBUG] API Product request created: ID {request_id}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"[ERROR] API product request failed: {e}")
        return jsonify({"error": "Failed to create product request"}), 500

# API: Get all product requests (admin only)
@app.route("/api/product-requests", methods=["GET"])
def api_get_product_requests():
    """API endpoint to get all product requests (admin only)"""
    # Simple admin check - in production, use proper token authentication
    if not session.get("admin"):
        return jsonify({"error": "Admin access required"}), 401
    
    try:
        with get_db_connection() as conn:
            requests = conn.execute(
                """
                SELECT pr.*, p.name as product_name, p.price as unit_price
                FROM product_requests pr 
                JOIN products p ON pr.product_id = p.id
                ORDER BY pr.created_at DESC
                """
            ).fetchall()
        
        # Convert to list of dictionaries
        requests_list = [dict(row) for row in requests]
        
        return jsonify({
            "success": True,
            "count": len(requests_list),
            "requests": requests_list
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to fetch product requests: {e}")
        return jsonify({"error": "Failed to fetch requests"}), 500

# API: Update product request status
@app.route("/api/product-requests/<int:request_id>", methods=["PUT"])
def api_update_request_status(request_id):
    """API endpoint to update product request status (admin only)"""
    if not session.get("admin"):
        return jsonify({"error": "Admin access required"}), 401
    
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"error": "Status field required"}), 400
        
        valid_statuses = ['pending', 'approved', 'rejected', 'completed', 'ordered']
        if data['status'] not in valid_statuses:
            return jsonify({"error": f"Invalid status. Valid options: {valid_statuses}"}), 400
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE product_requests SET status = ? WHERE id = ?",
                (data['status'], request_id)
            )
            
            if cursor.rowcount == 0:
                return jsonify({"error": "Request not found"}), 404
            
            conn.commit()
        
        return jsonify({
            "success": True,
            "message": f"Request {request_id} status updated to {data['status']}"
        }), 200
        
    except Exception as e:
        print(f"[ERROR] Failed to update request status: {e}")
        return jsonify({"error": "Failed to update status"}), 500

# ========== WEB INTERFACE ENHANCEMENTS ==========

# Product requests management page for admins
@app.route("/admin/requests")
def admin_requests():
    """Admin page to view and manage product requests"""
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    with get_db_connection() as conn:
        requests = conn.execute(
            """
            SELECT pr.*, p.name as product_name, p.price as unit_price,
                   p.image as product_image
            FROM product_requests pr 
            JOIN products p ON pr.product_id = p.id
            ORDER BY pr.created_at DESC
            """
        ).fetchall()
    
    return render_template("admin_requests.html", requests=requests)

# حذف منتج
@app.route("/delete/<int:pid>", methods=["POST"])
def delete(pid):
    if not session.get("admin"):
        return redirect(url_for("login"))
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM products WHERE id=?", (pid,))
            conn.commit()
        flash("تم حذف المنتج.", "success")
    except Exception as e:
        print("Error deleting product:", e)
        flash("حدث خطأ أثناء الحذف.", "error")
    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)
