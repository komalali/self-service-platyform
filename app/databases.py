from flask import Blueprint, render_template

bp = Blueprint("databases", __name__, url_prefix="/databases")


@bp.route("/", methods=["GET"])
def list_databases():
    """index page"""
    return render_template("databases/index.html")

