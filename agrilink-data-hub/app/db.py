import pymysql
from flask import current_app, g


def get_db():
    if "db" not in g:
        g.db = pymysql.connect(
            host=current_app.config["DB_HOST"],
            user=current_app.config["DB_USER"],
            password=current_app.config["DB_PASSWORD"],
            database=current_app.config["DB_NAME"],
            port=current_app.config["DB_PORT"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False,
        )
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_db(sql, args=(), one=False):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        rows = cur.fetchall()
    return (rows[0] if rows else None) if one else rows


def execute_db(sql, args=()):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, args)
        last_id = cur.lastrowid
    db.commit()
    return last_id
