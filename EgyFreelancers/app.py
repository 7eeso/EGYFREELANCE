from pathlib import Path
import sqlite3
from flask import Flask, render_template, request, jsonify

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "egyfreelancers.db"
app = Flask(__name__)

CATEGORIES = {
    "design": "Graphic design",
    "development": "Web development",
    "writing": "Writing & translation",
    "marketing": "Marketing",
    "video": "Video editing",
    "business": "Business",
}
PAYMENTS = {
    "vodafone_cash": "Vodafone Cash",
    "orange_cash": "Orange Cash",
    "etisalat_cash": "e& money",
    "instapay": "InstaPay",
    "fawry": "Fawry",
    "telda": "Telda",
    "bank_transfer": "Bank transfer",
}

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize():
    with connect() as conn:
        conn.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
        count = conn.execute("SELECT COUNT(*) FROM gigs").fetchone()[0]
        if count == 0:
            demos = [
                ("I will design a clean brand identity", "A thoughtful logo, color palette, and starter brand guide for your business.", "design", 850, "instapay", "Mariam"),
                ("I will build a responsive landing page", "A responsive page built around your product, service, or portfolio.", "development", 2400, "vodafone_cash", "Omar"),
                ("I will edit your short promotional video", "Clean cuts, captions, pacing, and a polished export for social media.", "video", 700, "fawry", "Youssef"),
                ("I will write clear Arabic or English website copy", "Helpful, natural copy for your homepage, services, or product.", "writing", 500, "telda", "Nour"),
                ("I will create social media designs", "A consistent set of posts that gives your business a recognizable look.", "marketing", 950, "orange_cash", "Salma"),
                ("I will create a simple business website", "A small business website with clear sections and mobile-friendly layout.", "development", 3200, "bank_transfer", "Ahmed"),
            ]
            conn.executemany("""INSERT INTO gigs(title,description,category,price,payment_method,seller_name,status)
                               VALUES(?,?,?,?,?,?,'approved')""", demos)

@app.context_processor
def shared():
    return {"categories": CATEGORIES, "payments": PAYMENTS}

@app.route("/")
def home():
    return render_template("client/home.html")

@app.route("/explore")
def explore():
    return render_template("client/explore.html")

@app.route("/gig/<int:gig_id>")
def gig_detail(gig_id):
    with connect() as conn:
        gig = conn.execute("SELECT * FROM gigs WHERE id=? AND status='approved'", (gig_id,)).fetchone()
    return render_template("client/gig_detail.html", gig=gig), (200 if gig else 404)

@app.route("/freelancer/post-gig")
def post_gig():
    return render_template("freelancer/post_gig.html")

@app.route("/freelancer/dashboard")
def freelancer_dashboard():
    return render_template("freelancer/dashboard.html")

@app.route("/freelancer/profile")
def freelancer_profile():
    return render_template("freelancer/profile.html")

@app.route("/post-project")
def post_project():
    return render_template("client/post_project.html")

@app.route("/login")
def login():
    return render_template("auth/login.html")

@app.route("/register")
def register():
    return render_template("auth/register.html")

@app.route("/api/gigs", methods=["GET", "POST"])
def gigs_api():
    if request.method == "GET":
        search = request.args.get("search", "").strip()
        category = request.args.get("category", "").strip()
        sql = "SELECT * FROM gigs WHERE status='approved'"
        args = []
        if category:
            if category not in CATEGORIES:
                return jsonify(error="Unknown category"), 400
            sql += " AND category=?"
            args.append(category)
        if search:
            sql += " AND (title LIKE ? OR description LIKE ? OR seller_name LIKE ?)"
            term = f"%{search}%"
            args += [term, term, term]
        sql += " ORDER BY id DESC LIMIT 80"
        with connect() as conn:
            rows = conn.execute(sql, args).fetchall()
        return jsonify(gigs=[dict(row) for row in rows])

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    seller = str(data.get("seller_name", "")).strip()
    category = data.get("category")
    payment = data.get("payment_method")
    try:
        price = int(data.get("price"))
    except (TypeError, ValueError):
        return jsonify(error="Enter a valid price in EGP."), 400
    if not title or len(title) > 120: return jsonify(error="Title is required (max 120 characters)."), 400
    if not description or len(description) > 2000: return jsonify(error="Description is required (max 2000 characters)."), 400
    if not seller or len(seller) > 80: return jsonify(error="Display name is required (max 80 characters)."), 400
    if category not in CATEGORIES: return jsonify(error="Choose a valid category."), 400
    if payment not in PAYMENTS: return jsonify(error="Choose a payment preference."), 400
    if not 1 <= price <= 1_000_000: return jsonify(error="Price must be between 1 and 1,000,000 EGP."), 400
    with connect() as conn:
        cur = conn.execute("""INSERT INTO gigs(title,description,category,price,payment_method,seller_name,status)
                            VALUES(?,?,?,?,?,?, 'pending')""",
                           (title, description, category, price, payment, seller))
        gig_id = cur.lastrowid
    return jsonify(message="Your gig was submitted for review.", gig_id=gig_id), 201

if __name__ == "__main__":
    initialize()
    app.run(debug=True)
