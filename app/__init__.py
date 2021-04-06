from flask import Flask, render_template

from pulumi.x import automation as auto


def ensure_plugins():
    ws = auto.LocalWorkspace()
    ws.install_plugin("aws", "v3.36.0")


def create_app():
    ensure_plugins()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="secret",
        PROJECT_NAME="static-site-platyform"
    )

    @app.route("/", methods=["GET"])
    def index():
        """index page"""
        return render_template("index.html")

    from . import sites
    app.register_blueprint(sites.bp)

    from . import databases
    app.register_blueprint(databases.bp)

    return app
