from flask import Blueprint, render_template

bp = Blueprint("vpcs", __name__, url_prefix="/vpcs")


@bp.route("/", methods=["GET"])
def list_vpcs():
    """index page"""
    return render_template("vpcs/index.html")

