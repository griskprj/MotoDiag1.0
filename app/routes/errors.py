from flask import Blueprint, render_template, redirect, url_for

errors_bp = Blueprint('errors', __name__, url_prefix='/errors')

@errors_bp.route("/404")
def error_404():
    return render_template("/errors/404.html")

@errors_bp.route("/502")
def error_502():
    return render_template("/errors/502.html")

@errors_bp.route("/429")
def error_429():
    return render_template("/errors/429.html")