from flask import Blueprint, render_template

bp = Blueprint("databases", __name__, url_prefix="/dbs")


@bp.route("/", methods=["GET"])
def list_dbs():
    """index page"""
    return render_template("databases/index.html")


# TODO: Implement CRUD endpoints
# https://github.com/komalali/self-service-platyform/issues/3
