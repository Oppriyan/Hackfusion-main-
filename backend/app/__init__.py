import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

# ==================================================
# FORCE LOAD ROOT .env (Bulletproof)
# ==================================================

ROOT_PATH = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_PATH / ".env"

load_dotenv(dotenv_path=ENV_PATH)

print("AZURE KEY LOADED:", bool(os.getenv("AZURE_OPENAI_API_KEY")))
print("AZURE KEY:", os.getenv("AZURE_OPENAI_API_KEY"))

# ==================================================
# IMPORT AFTER ENV LOAD
# ==================================================

from app.models.database import init_db, get_db
from app.utils.excel_loader import load_all_data

from app.routes.inventory import inventory_bp
from app.routes.order import order_bp
from app.routes.chat import chat_bp
from app.routes.prescription import prescription_bp
from app.routes.webhook import webhook_bp
from app.routes.analytics import analytics_bp
from app.routes.auth import auth_bp

from werkzeug.security import generate_password_hash


# ==================================================
# APP FACTORY
# ==================================================

def create_app():

    # Configure static files and template folder for frontend
    app = Flask(__name__, 
                static_folder=os.path.join(ROOT_PATH, "Frontend"),
                static_url_path="/static",
                template_folder=os.path.join(ROOT_PATH, "Frontend", "html"))
    
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize database
    init_db()

    # -------------------------------------------------
    # SEED DEFAULT USERS
    # -------------------------------------------------
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email = ?", ("admin@pharmacy.com",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Admin",
            "admin@pharmacy.com",
            generate_password_hash("admin123"),
            "admin"
        ))

    cursor.execute("SELECT * FROM users WHERE email = ?", ("clerk@pharmacy.com",))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (
            "Clerk",
            "clerk@pharmacy.com",
            generate_password_hash("clerk123"),
            "user"
        ))

    conn.commit()
    conn.close()

    # Load Excel data
    load_all_data()

    # Register blueprints
    app.register_blueprint(inventory_bp, url_prefix="/inventory")
    app.register_blueprint(order_bp)
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(prescription_bp)
    app.register_blueprint(webhook_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(auth_bp)

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    # Serve frontend
    from flask import render_template
    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")
    
    @app.route("/<path:path>", methods=["GET"])
    def serve_static(path):
        from flask import send_from_directory
        # Try to serve from static folder first
        static_path = os.path.join(ROOT_PATH, "Frontend", path)
        if os.path.exists(static_path):
            if os.path.isfile(static_path):
                return send_from_directory(os.path.join(ROOT_PATH, "Frontend"), path)
            else:
                return render_template("index.html")
        return render_template("index.html")

    return app