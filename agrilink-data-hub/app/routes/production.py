from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import execute_db, query_db

bp = Blueprint("production", __name__, url_prefix="/production")


@bp.route("/")
def list_production():
    records = query_db("""
        SELECT pr.*, f.farm_name, f.first_name, f.last_name,
               c.crop_name, s.season_name, s.year
        FROM production_records pr
        INNER JOIN farmers f ON pr.farmer_id = f.farmer_id
        INNER JOIN crops c ON pr.crop_id = c.crop_id
        INNER JOIN seasons s ON pr.season_id = s.season_id
        ORDER BY pr.planting_date DESC
    """)
    return render_template("production/list.html", records=records)


@bp.route("/add", methods=["GET", "POST"])
def add_production():
    farmers = query_db(
        "SELECT farmer_id, farm_name, first_name, last_name FROM farmers ORDER BY farm_name"
    )
    crops = query_db("SELECT crop_id, crop_name FROM crops ORDER BY crop_name")
    seasons = query_db("SELECT season_id, season_name, year FROM seasons ORDER BY year DESC")

    if request.method == "POST":
        execute_db("""
            INSERT INTO production_records
            (farmer_id, crop_id, season_id, planting_date, harvest_date,
             area_hectares, yield_kg, status, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            request.form["farmer_id"],
            request.form["crop_id"],
            request.form["season_id"],
            request.form["planting_date"],
            request.form.get("harvest_date") or None,
            request.form["area_hectares"],
            request.form.get("yield_kg") or 0,
            request.form["status"],
            request.form.get("notes") or None,
        ))
        flash("Production record added.", "success")
        return redirect(url_for("production.list_production"))

    return render_template(
        "production/form.html",
        record=None,
        farmers=farmers,
        crops=crops,
        seasons=seasons,
        action="Add",
    )


@bp.route("/edit/<int:record_id>", methods=["GET", "POST"])
def edit_production(record_id):
    record = query_db(
        "SELECT * FROM production_records WHERE record_id = %s",
        (record_id,),
        one=True,
    )
    if not record:
        flash("Production record not found.", "danger")
        return redirect(url_for("production.list_production"))

    farmers = query_db(
        "SELECT farmer_id, farm_name, first_name, last_name FROM farmers ORDER BY farm_name"
    )
    crops = query_db("SELECT crop_id, crop_name FROM crops ORDER BY crop_name")
    seasons = query_db("SELECT season_id, season_name, year FROM seasons ORDER BY year DESC")

    if request.method == "POST":
        execute_db("""
            UPDATE production_records
            SET farmer_id=%s, crop_id=%s, season_id=%s, planting_date=%s, harvest_date=%s,
                area_hectares=%s, yield_kg=%s, status=%s, notes=%s
            WHERE record_id=%s
        """, (
            request.form["farmer_id"],
            request.form["crop_id"],
            request.form["season_id"],
            request.form["planting_date"],
            request.form.get("harvest_date") or None,
            request.form["area_hectares"],
            request.form.get("yield_kg") or 0,
            request.form["status"],
            request.form.get("notes") or None,
            record_id,
        ))
        flash("Production record updated.", "success")
        return redirect(url_for("production.list_production"))

    return render_template(
        "production/form.html",
        record=record,
        farmers=farmers,
        crops=crops,
        seasons=seasons,
        action="Edit",
    )


@bp.route("/delete/<int:record_id>", methods=["POST"])
def delete_production(record_id):
    execute_db("DELETE FROM production_records WHERE record_id = %s", (record_id,))
    flash("Production record deleted.", "info")
    return redirect(url_for("production.list_production"))
