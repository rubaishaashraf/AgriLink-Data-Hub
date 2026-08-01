from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import execute_db, get_db, query_db

bp = Blueprint("fertilizers", __name__, url_prefix="/fertilizers")


@bp.route("/")
def list_fertilizers():
    items = query_db("""
        SELECT f.*, fi.quantity, fi.reorder_level,
               CASE WHEN fi.quantity <= fi.reorder_level THEN 1 ELSE 0 END AS is_low_stock
        FROM fertilizers f
        LEFT JOIN fertilizer_inventory fi ON f.fertilizer_id = fi.fertilizer_id
        ORDER BY f.fertilizer_name
    """)
    return render_template("fertilizers/list.html", items=items)


@bp.route("/add", methods=["GET", "POST"])
def add_fertilizer():
    if request.method == "POST":
        fertilizer_id = execute_db(
            """
            INSERT INTO fertilizers (fertilizer_name, fertilizer_type, unit, npk_ratio)
            VALUES (%s, %s, %s, %s)
            """,
            (
                request.form["fertilizer_name"],
                request.form["fertilizer_type"],
                request.form["unit"],
                request.form.get("npk_ratio") or None,
            ),
        )
        execute_db(
            """
            INSERT INTO fertilizer_inventory (fertilizer_id, quantity, reorder_level)
            VALUES (%s, %s, %s)
            """,
            (
                fertilizer_id,
                request.form.get("quantity") or 0,
                request.form.get("reorder_level") or 10,
            ),
        )
        flash("Fertilizer added.", "success")
        return redirect(url_for("fertilizers.list_fertilizers"))

    return render_template("fertilizers/form.html", fertilizer=None, action="Add")


@bp.route("/inventory", methods=["GET", "POST"])
def inventory():
    if request.method == "POST":
        execute_db("""
            UPDATE fertilizer_inventory
            SET quantity = %s, reorder_level = %s
            WHERE fertilizer_id = %s
        """, (
            request.form["quantity"],
            request.form["reorder_level"],
            request.form["fertilizer_id"],
        ))
        flash("Inventory updated.", "success")
        return redirect(url_for("fertilizers.inventory"))

    inventory_rows = query_db("""
        SELECT f.fertilizer_id, f.fertilizer_name, f.unit,
               fi.quantity, fi.reorder_level, fi.last_updated
        FROM fertilizers f
        INNER JOIN fertilizer_inventory fi ON f.fertilizer_id = fi.fertilizer_id
        ORDER BY f.fertilizer_name
    """)
    return render_template("fertilizers/inventory.html", inventory_rows=inventory_rows)


@bp.route("/apply", methods=["GET", "POST"])
def apply_fertilizer():
    records = query_db("""
        SELECT pr.record_id, f.farm_name, c.crop_name, s.season_name
        FROM production_records pr
        JOIN farmers f ON pr.farmer_id = f.farmer_id
        JOIN crops c ON pr.crop_id = c.crop_id
        JOIN seasons s ON pr.season_id = s.season_id
        ORDER BY pr.planting_date DESC
    """)
    fertilizers = query_db(
        "SELECT fertilizer_id, fertilizer_name, unit FROM fertilizers ORDER BY fertilizer_name"
    )

    if request.method == "POST":
        record_id = int(request.form["record_id"])
        fertilizer_id = int(request.form["fertilizer_id"])
        qty = float(request.form["quantity_used"])

        stock = query_db(
            "SELECT quantity FROM fertilizer_inventory WHERE fertilizer_id = %s",
            (fertilizer_id,),
            one=True,
        )

        if not stock or stock["quantity"] < qty:
            flash("Insufficient stock.", "danger")
            return redirect(url_for("fertilizers.apply_fertilizer"))

        db = get_db()
        try:
            with db.cursor() as cur:
                cur.execute("""
                    INSERT INTO fertilizer_applications
                    (record_id, fertilizer_id, application_date, quantity_used, notes)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    record_id,
                    fertilizer_id,
                    request.form["application_date"],
                    qty,
                    request.form.get("notes") or None,
                ))
                cur.execute("""
                    UPDATE fertilizer_inventory
                    SET quantity = quantity - %s
                    WHERE fertilizer_id = %s
                """, (qty, fertilizer_id))
            db.commit()
            flash("Fertilizer application recorded.", "success")
        except Exception:
            db.rollback()
            flash("Failed to record application.", "danger")

        return redirect(url_for("fertilizers.apply_fertilizer"))

    applications = query_db("""
        SELECT fa.application_id, fa.application_date, fa.quantity_used,
               f.farm_name, c.crop_name, fert.fertilizer_name, fert.unit
        FROM fertilizer_applications fa
        JOIN production_records pr ON fa.record_id = pr.record_id
        JOIN farmers f ON pr.farmer_id = f.farmer_id
        JOIN crops c ON pr.crop_id = c.crop_id
        JOIN fertilizers fert ON fa.fertilizer_id = fert.fertilizer_id
        ORDER BY fa.application_date DESC
    """)

    return render_template(
        "fertilizers/application_form.html",
        records=records,
        fertilizers=fertilizers,
        applications=applications,
    )
