from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import execute_db, query_db

bp = Blueprint("farmers", __name__, url_prefix="/farmers")


@bp.route("/")
def list_farmers():
    farmers = query_db("""
        SELECT f.*,
               COUNT(pr.record_id) AS production_count
        FROM farmers f
        LEFT JOIN production_records pr ON f.farmer_id = pr.farmer_id
        GROUP BY f.farmer_id
        ORDER BY f.created_at DESC
    """)
    return render_template("farmers/list.html", farmers=farmers)


@bp.route("/add", methods=["GET", "POST"])
def add_farmer():
    if request.method == "POST":
        execute_db("""
            INSERT INTO farmers (first_name, last_name, email, phone, farm_name, location)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["first_name"],
            request.form["last_name"],
            request.form.get("email") or None,
            request.form.get("phone") or None,
            request.form["farm_name"],
            request.form["location"],
        ))
        flash("Farmer added successfully.", "success")
        return redirect(url_for("farmers.list_farmers"))
    return render_template("farmers/form.html", farmer=None, action="Add")


@bp.route("/edit/<int:farmer_id>", methods=["GET", "POST"])
def edit_farmer(farmer_id):
    farmer = query_db("SELECT * FROM farmers WHERE farmer_id = %s", (farmer_id,), one=True)
    if not farmer:
        flash("Farmer not found.", "danger")
        return redirect(url_for("farmers.list_farmers"))

    if request.method == "POST":
        execute_db("""
            UPDATE farmers
            SET first_name=%s, last_name=%s, email=%s, phone=%s, farm_name=%s, location=%s
            WHERE farmer_id=%s
        """, (
            request.form["first_name"],
            request.form["last_name"],
            request.form.get("email") or None,
            request.form.get("phone") or None,
            request.form["farm_name"],
            request.form["location"],
            farmer_id,
        ))
        flash("Farmer updated.", "success")
        return redirect(url_for("farmers.list_farmers"))

    return render_template("farmers/form.html", farmer=farmer, action="Edit")


@bp.route("/delete/<int:farmer_id>", methods=["POST"])
def delete_farmer(farmer_id):
    execute_db("DELETE FROM farmers WHERE farmer_id = %s", (farmer_id,))
    flash("Farmer deleted.", "info")
    return redirect(url_for("farmers.list_farmers"))
