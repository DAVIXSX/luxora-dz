import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from models import db, Product, Order

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mysecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join("static", "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(os.path.join(BASE_DIR, UPLOAD_FOLDER), exist_ok=True)

# Admin credentials from environment variables
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '1234')

# Initialize database
db.init_app(app)

def init_db():
    """Initialize database tables"""
    with app.app_context():
        db.create_all()

# الصفحة الرئيسية - عرض المنتجات
@app.route("/")
def index():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("index.html", products=products)

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
    order = db.session.query(Order).join(Product).filter(Order.id == order_id).first_or_404()
    return render_template("order_confirmation.html", order=order)

# تسجيل الدخول للأدمن
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
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
    orders = db.session.query(Order, Product).join(Product).order_by(Order.id.desc()).all()
    
    return render_template("admin.html", products=products, orders=orders)

# حذف منتج
@app.route("/delete/<int:pid>", methods=["POST"])
def delete(pid):
    if not session.get("admin"):
        return redirect(url_for("login"))
        
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

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
