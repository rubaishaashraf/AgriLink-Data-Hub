from flask import Blueprint, flash, redirect, render_template, request, url_for

from ..db import execute_db, query_db

bp = Blueprint("crops", __name__, url_prefix="/crops")


@bp.route("/")
def list_crops():
    crops = query_db("""
        SELECT c.*, COUNT(pr.record_id) AS times_planted
        FROM crops c
        LEFT JOIN production_records pr ON c.crop_id = pr.crop_id
        GROUP BY c.crop_id
        ORDER BY c.crop_name
    """)
    return render_template("crops/list.html", crops=crops)


@bp.route("/add", methods=["GET", "POST"])
def add_crop():
    if request.method == "POST":
        execute_db(
            "INSERT INTO crops (crop_name, category, description) VALUES (%s, %s, %s)",
            (
                request.form["crop_name"],
                request.form["category"],
                request.form.get("description") or None,
            ),
        )
        flash("Crop added.", "success")
        return redirect(url_for("crops.list_crops"))
    return render_template("crops/form.html", crop=None, action="Add")


@bp.route("/edit/<int:crop_id>", methods=["GET", "POST"])
def edit_crop(crop_id):
    crop = query_db("SELECT * FROM crops WHERE crop_id = %s", (crop_id,), one=True)
    if not crop:
        flash("Crop not found.", "danger")
        return redirect(url_for("crops.list_crops"))

    if request.method == "POST":
        execute_db(
            "UPDATE crops SET crop_name=%s, category=%s, description=%s WHERE crop_id=%s",
            (
                request.form["crop_name"],
                request.form["category"],
                request.form.get("description") or None,
                crop_id,
            ),
        )
        flash("Crop updated.", "success")
        return redirect(url_for("crops.list_crops"))

    return render_template("crops/form.html", crop=crop, action="Edit")


@bp.route("/delete/<int:crop_id>", methods=["POST"])
def delete_crop(crop_id):
    try:
        execute_db("DELETE FROM crops WHERE crop_id = %s", (crop_id,))
        flash("Crop deleted.", "info")
    except Exception:
        flash("Cannot delete crop linked to production records.", "danger")
    return redirect(url_for("crops.list_crops"))
