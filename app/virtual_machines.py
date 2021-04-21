from flask import Blueprint, render_template

bp = Blueprint("virtual_machines", __name__, url_prefix="/vms")


@bp.route("/", methods=["GET"])
def list_vms():
    """index page"""
    return render_template("virtual_machines/index.html")


# TODO: Implement CRUD endpoints
# https://github.com/komalali/self-service-platyform/issues/4
