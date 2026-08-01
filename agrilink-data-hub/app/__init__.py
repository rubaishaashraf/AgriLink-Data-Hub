from flask import Flask, render_template

from .config import Config
from .db import close_db, query_db


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    app.teardown_appcontext(close_db)

    from .routes.farmers import bp as farmers_bp
    from .routes.crops import bp as crops_bp
    from .routes.production import bp as production_bp
    from .routes.fertilizers import bp as fertilizers_bp

    app.register_blueprint(farmers_bp)
    app.register_blueprint(crops_bp)
    app.register_blueprint(production_bp)
    app.register_blueprint(fertilizers_bp)

    @app.route("/")
    def index():
        stats = query_db("""
            SELECT
                (SELECT COUNT(*) FROM farmers) AS farmer_count,
                (SELECT COUNT(*) FROM crops) AS crop_count,
                (SELECT COUNT(*) FROM production_records) AS production_count,
                (SELECT COUNT(*) FROM fertilizer_inventory fi
                 WHERE fi.quantity <= fi.reorder_level) AS low_stock_count
        """, one=True)

        recent = query_db("""
            SELECT pr.record_id, f.farm_name, c.crop_name, s.season_name,
                   pr.planting_date, pr.status, pr.yield_kg
            FROM production_records pr
            JOIN farmers f ON pr.farmer_id = f.farmer_id
            JOIN crops c ON pr.crop_id = c.crop_id
            JOIN seasons s ON pr.season_id = s.season_id
            ORDER BY pr.created_at DESC
            LIMIT 5
        """)

        return render_template("index.html", stats=stats, recent=recent)

    return app
