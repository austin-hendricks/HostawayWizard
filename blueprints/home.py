from flask import Blueprint

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET"])
def home():
    # Return a simple paragraph for now
    return "<p>HostawayWizard is the Future!</p>"
