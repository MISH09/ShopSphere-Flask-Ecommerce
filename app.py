from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "shopsphere.db"

app = Flask(__name__)
app.secret_key = "change-this-secret-key-before-deployment"

PRODUCTS = [
    {"id": 1, "name": "Everyday Sneakers", "category": "Fashion", "price": 2499, "old_price": 3299, "emoji": "👟", "color": "peach", "description": "Lightweight everyday sneakers designed for comfort, walks, and weekend plans."},
    {"id": 2, "name": "Studio Headphones", "category": "Electronics", "price": 3999, "old_price": 4999, "emoji": "🎧", "color": "lavender", "description": "Immersive sound, soft ear cushions, and a clean minimal design for work or travel."},
    {"id": 3, "name": "Ceramic Coffee Set", "category": "Home", "price": 1299, "old_price": 1599, "emoji": "☕", "color": "sage", "description": "A thoughtfully designed ceramic cup set that makes your morning ritual feel special."},
    {"id": 4, "name": "Classic Backpack", "category": "Fashion", "price": 1899, "old_price": 2299, "emoji": "🎒", "color": "blue", "description": "A roomy, versatile backpack with everyday organisation and a timeless silhouette."},
    {"id": 5, "name": "Smart Watch", "category": "Electronics", "price": 5499, "old_price": 6999, "emoji": "⌚", "color": "pink", "description": "Keep your day on track with activity insights, notifications, and a bright display."},
    {"id": 6, "name": "Soft Throw Blanket", "category": "Home", "price": 1599, "old_price": 1999, "emoji": "🧶", "color": "cream", "description": "A soft textured throw for cosy evenings, slow mornings, and relaxed spaces."},
    {"id": 7, "name": "Daily Skincare Kit", "category": "Beauty", "price": 999, "old_price": 1299, "emoji": "🧴", "color": "sage", "description": "A simple daily-care set designed to make your routine easy and refreshing."},
    {"id": 8, "name": "Minimal Desk Lamp", "category": "Home", "price": 2199, "old_price": 2799, "emoji": "💡", "color": "lavender", "description": "A modern desk lamp that brings a warm glow to your workspace or bedside table."},
]

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )""")
        conn.execute("""CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            address TEXT NOT NULL,
            total REAL NOT NULL,
            items TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

def get_product(product_id):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)

def cart_details():
    cart = session.get("cart", {})
    rows, total, count = [], 0, 0
    for product_id, quantity in cart.items():
        product = get_product(int(product_id))
        if product and int(quantity) > 0:
            subtotal = product["price"] * int(quantity)
            rows.append({"product": product, "quantity": int(quantity), "subtotal": subtotal})
            total += subtotal
            count += int(quantity)
    return rows, total, count

@app.context_processor
def inject_cart_count():
    return {"cart_count": cart_details()[2], "current_user": session.get("user")}

@app.route("/")
def home():
    return render_template("index.html", products=PRODUCTS[:4], categories=sorted({p["category"] for p in PRODUCTS}))

@app.route("/products")
def products():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip()
    sort = request.args.get("sort", "featured")
    results = [p for p in PRODUCTS if query in p["name"].lower() or query in p["description"].lower()]
    if category:
        results = [p for p in results if p["category"] == category]
    if sort == "price-low":
        results.sort(key=lambda p: p["price"])
    elif sort == "price-high":
        results.sort(key=lambda p: p["price"], reverse=True)
    elif sort == "name":
        results.sort(key=lambda p: p["name"].lower())
    return render_template("products.html", products=results, categories=sorted({p["category"] for p in PRODUCTS}), query=query, selected_category=category, sort=sort)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    product = get_product(product_id)
    if not product:
        flash("That product could not be found.", "error")
        return redirect(url_for("products"))
    return render_template("product_detail.html", product=product)

@app.post("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    product = get_product(product_id)
    if not product:
        flash("That product could not be found.", "error")
        return redirect(url_for("products"))
    try:
        quantity = max(1, min(10, int(request.form.get("quantity", 1))))
    except ValueError:
        quantity = 1
    cart = session.get("cart", {})
    key = str(product_id)
    cart[key] = min(10, int(cart.get(key, 0)) + quantity)
    session["cart"] = cart
    flash(f'{product["name"]} added to your cart.', "success")
    return redirect(request.referrer or url_for("products"))

@app.route("/cart")
def cart():
    rows, total, _ = cart_details()
    return render_template("cart.html", rows=rows, total=total)

@app.post("/cart/update")
def update_cart():
    cart = session.get("cart", {})
    for key in list(cart.keys()):
        try:
            quantity = int(request.form.get(f"quantity_{key}", cart[key]))
            if quantity <= 0:
                cart.pop(key, None)
            else:
                cart[key] = min(10, quantity)
        except ValueError:
            pass
    session["cart"] = cart
    flash("Your cart has been updated.", "success")
    return redirect(url_for("cart"))

@app.post("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    flash("Item removed from your cart.", "success")
    return redirect(url_for("cart"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password of at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with connect_db() as conn:
                cur = conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                                   (name, email, generate_password_hash(password)))
                user_id = cur.lastrowid
            session["user"] = {"id": user_id, "name": name, "email": email}
            flash("Account created successfully.", "success")
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            flash("An account with that email already exists. Please log in.", "error")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with connect_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user"] = {"id": user["id"], "name": user["name"], "email": user["email"]}
            flash(f'Welcome back, {user["name"]}!', "success")
            return redirect(url_for("home"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")

@app.post("/logout")
def logout():
    session.pop("user", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    rows, total, _ = cart_details()
    if not rows:
        flash("Your cart is empty. Add a product before checkout.", "error")
        return redirect(url_for("products"))
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        if not name or not email or not address:
            flash("Please complete all shipping details.", "error")
            return render_template("checkout.html", rows=rows, total=total)
        items = "; ".join(f'{r["product"]["name"]} x {r["quantity"]}' for r in rows)
        user_id = current_user["id"] if (current_user := session.get("user")) else None
        with connect_db() as conn:
            cur = conn.execute("INSERT INTO orders (user_id, customer_name, email, address, total, items) VALUES (?, ?, ?, ?, ?, ?)",
                               (user_id, name, email, address, total, items))
            order_id = cur.lastrowid
        session["cart"] = {}
        return render_template("order_success.html", order_id=order_id, name=name, total=total)
    user = session.get("user", {})
    return render_template("checkout.html", rows=rows, total=total, user=user)

@app.route("/orders")
def orders():
    user = session.get("user")
    if not user:
        flash("Please log in to view your order history.", "error")
        return redirect(url_for("login"))
    with connect_db() as conn:
        orders_list = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)).fetchall()
    return render_template("orders.html", orders=orders_list)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thanks for reaching out! This demo contact form is ready for backend integration.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")

init_db()

if __name__ == "__main__":
    app.run(debug=True)
