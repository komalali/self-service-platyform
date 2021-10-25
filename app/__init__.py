import os
from flask import Flask, render_template

import pulumi.automation as auto


def ensure_plugins():
    ws = auto.LocalWorkspace()
    ws.install_plugin("aws", "v4.0.0")


def create_app():
    ensure_plugins()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="secret",
        PROJECT_NAME="self-service-platyform",
        PULUMI_ORG=os.environ.get("PULUMI_ORG"),
    )

    @app.route("/", methods=["GET"])
    def index():
        """index page"""
        return render_template("index.html")

    from . import sites

    app.register_blueprint(sites.bp)

    from . import databases

    app.register_blueprint(databases.bp)

    from . import virtual_machines

    app.register_blueprint(virtual_machines.bp)

    from . import vpcs

    app.register_blueprint(vpcs.bp)

    return app
