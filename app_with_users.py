import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from models import db, Product, Order, User

# Load environment variables
load_dotenv()

app = Flask(__name__)

# File upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')
# Use simple relative database path
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/app_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER), exist_ok=True)

# Initialize database and login manager
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        admin_user = User.query.filter_by(username='youcef').first()
        if not admin_user:
            admin_user = User(
                username='youcef',
                email='youcef@example.com',
                first_name='Youcef',
                is_admin=True
            )
            admin_user.set_password('kadari')  # Default password
            db.session.add(admin_user)
            db.session.commit()
            print("Default admin user created: youcef/kadari")

# الصفحة الرئيسية - عرض المنتجات
@app.route("/")
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products)

# User Registration
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        
        # Validation
        errors = []
        
        if not username or len(username) < 3:
            errors.append("اسم المستخدم يجب أن يكون 3 أحرف على الأقل")
            
        if not email:
            errors.append("البريد الإلكتروني مطلوب")
        else:
            try:
                validate_email(email)
            except EmailNotValidError:
                errors.append("البريد الإلكتروني غير صحيح")
                
        if not password or len(password) < 6:
            errors.append("كلمة المرور يجب أن تكون 6 أحرف على الأقل")
            
        if password != confirm_password:
            errors.append("كلمات المرور غير متطابقة")
            
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                errors.append("اسم المستخدم موجود بالفعل")
            if existing_user.email == email:
                errors.append("البريد الإلكتروني موجود بالفعل")
        
        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("register.html")
        
        try:
            # Create new user
            new_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                phone=phone
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول.", "success")
            return redirect(url_for("login"))
            
        except Exception as e:
            db.session.rollback()
            print("Error creating user:", e)
            flash("حدث خطأ أثناء إنشاء الحساب. حاول مرة أخرى.", "error")
    
    return render_template("register.html")

# User Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username_or_email", "").strip()
        password = request.form.get("password", "").strip()
        remember_me = bool(request.form.get("remember_me"))
        
        if not username_or_email or not password:
            flash("الرجاء إدخال اسم المستخدم وكلمة المرور.", "error")
            return render_template("login.html")
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=remember_me)
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            elif user.is_admin:
                return redirect(url_for('admin'))
            else:
                return redirect(url_for('profile'))
        else:
            flash("اسم المستخدم أو كلمة المرور غير صحيحة.", "error")
    
    return render_template("login.html")

# User Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج بنجاح.", "success")
    return redirect(url_for("index"))

# User Profile
@app.route("/profile")
@login_required
def profile():
    user_orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("profile.html", orders=user_orders)

# Update Profile
@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.first_name = request.form.get("first_name", "").strip()
        current_user.last_name = request.form.get("last_name", "").strip()
        current_user.phone = request.form.get("phone", "").strip()
        current_user.address = request.form.get("address", "").strip()
        
        try:
            db.session.commit()
            flash("تم تحديث الملف الشخصي بنجاح.", "success")
            return redirect(url_for("profile"))
        except Exception as e:
            db.session.rollback()
            print("Error updating profile:", e)
            flash("حدث خطأ أثناء تحديث الملف الشخصي.", "error")
    
    return render_template("edit_profile.html")

# صفحة المنتج - تعرض تفاصيل المنتج + زر اضافة للكمية
@app.route("/product/<int:pid>")
def product(pid):
    product = Product.query.get_or_404(pid)
    return render_template("product.html", product=product)

# استقبال الطلب مباشرة من صفحة المنتج
@app.route("/order/<int:pid>", methods=["POST"])
def order(pid):
    # جلب بيانات النموذج
    quantity = request.form.get("quantity", 1, type=int)
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name", "")
    phone = request.form.get("phone")
    state = request.form.get("state")
    email = request.form.get("email", "")
    address = request.form.get("address")
    notes = request.form.get("notes", "")

    # If user is logged in, pre-fill with user data
    if current_user.is_authenticated:
        first_name = first_name or current_user.first_name
        last_name = last_name or current_user.last_name
        phone = phone or current_user.phone
        email = email or current_user.email
        address = address or current_user.address

    # التحقق من الحقول المطلوبة
    if not all([first_name, phone, state, address]):
        flash("الرجاء تعبئة جميع الحقول المطلوبة", "error")
        return redirect(url_for("product", pid=pid))

    # جلب معلومات المنتج
    product = Product.query.get_or_404(pid)
    
    # حساب السعر الإجمالي
    total_price = float(product.price) * quantity

    try:
        # إنشاء طلب جديد
        new_order = Order(
            product_id=pid,
            user_id=current_user.id if current_user.is_authenticated else None,
            quantity=quantity,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            state=state,
            email=email,
            address=address,
            notes=notes,
            total_price=total_price
        )
        
        # حفظ الطلب في قاعدة البيانات
        db.session.add(new_order)
        db.session.commit()

        # توجيه المستخدم إلى صفحة تأكيد الطلب
        return redirect(url_for("order_confirmation", order_id=new_order.id))
        
    except Exception as e:
        db.session.rollback()
        print("Error saving order:", e)
        flash("حدث خطأ أثناء حفظ الطلب. حاول مرة أخرى.", "error")
        return redirect(url_for("product", pid=pid))

# تأكيد الطلب - صفحة تعرض تفاصيل الطلب
@app.route("/order/confirmation/<int:order_id>")
def order_confirmation(order_id):
    order = Order.query.filter_by(id=order_id).first_or_404()
    return render_template("order_confirmation.html", order=order)

# لوحة الإدارة - إضافة منتجات وعرض الطلبات
@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if not current_user.is_admin:
        flash("ليس لديك صلاحية للوصول إلى هذه الصفحة.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        price = request.form.get("price", type=float)
        desc = request.form.get("desc", "").strip()
        image_file = request.files.get("image")

        if not name or price is None:
            flash("الرجاء إدخال اسم المنتج والسعر بشكل صحيح.", "error")
            return redirect(url_for("admin"))

        filename = None
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            target = os.path.join(BASE_DIR, app.config["UPLOAD_FOLDER"], filename)
            image_file.save(target)

        try:
            # إنشاء منتج جديد
            new_product = Product(
                name=name,
                price=price,
                desc=desc,
                image=f"uploads/{filename}" if filename else None
            )
            
            db.session.add(new_product)
            db.session.commit()
            flash("تم إضافة المنتج.", "success")
            
        except Exception as e:
            db.session.rollback()
            print("Error adding product:", e)
            flash("حدث خطأ أثناء إضافة المنتج.", "error")
            
        return redirect(url_for("admin"))

    # جلب المنتجات والطلبات
    products = Product.query.order_by(Product.id.desc()).all()
    orders = Order.query.join(Product).order_by(Order.created_at.desc()).all()
    users = User.query.order_by(User.created_at.desc()).all()
    
    return render_template("admin.html", products=products, orders=orders, users=users)

# حذف منتج
@app.route("/delete/<int:pid>", methods=["POST"])
@login_required
def delete(pid):
    if not current_user.is_admin:
        flash("ليس لديك صلاحية لحذف المنتجات.", "error")
        return redirect(url_for("index"))
        
    try:
        product = Product.query.get_or_404(pid)
        db.session.delete(product)
        db.session.commit()
        flash("تم حذف المنتج.", "success")
        
    except Exception as e:
        db.session.rollback()
        print("Error deleting product:", e)
        flash("حدث خطأ أثناء الحذف.", "error")
        
    return redirect(url_for("admin"))

# Update order status (Admin only)
@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
@login_required
def update_order_status(order_id):
    if not current_user.is_admin:
        flash("ليس لديك صلاحية لتحديث الطلبات.", "error")
        return redirect(url_for("index"))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get("status")
    
    if new_status in ['pending', 'processing', 'shipped', 'delivered', 'cancelled']:
        order.status = new_status
        db.session.commit()
        flash("تم تحديث حالة الطلب.", "success")
    else:
        flash("حالة الطلب غير صحيحة.", "error")
    
    return redirect(url_for("admin"))

# Serve uploaded files (images) for network access
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files from uploads directory"""
    uploads_path = os.path.join(BASE_DIR, 'static', 'uploads')
    return send_from_directory(uploads_path, filename)

# Serve all static files for network access
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files for network access"""
    static_path = os.path.join(BASE_DIR, 'static')
    return send_from_directory(static_path, filename)

if __name__ == "__main__":
    init_db()
    # Run on all available network interfaces so others on WiFi can access
    app.run(host='0.0.0.0', port=5000, debug=True)
