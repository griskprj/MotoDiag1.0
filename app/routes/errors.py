from flask import Blueprint, render_template, redirect, url_for, request, jsonify

errors_bp = Blueprint('errors', __name__, url_prefix='/errors')

@errors_bp.app_errorhandler(404)
def error_404(e):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'error': 'Not found',
            'message': 'Not found'
        }), 404
    return render_template("/errors/404.html")

@errors_bp.app_errorhandler(502)
def error_502(e):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'error': 'Server fall',
            'message': 'Server fall'
        }), 502
    return render_template("/errors/502.html")

@errors_bp.app_errorhandler(429)
def error_429(e):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'error': 'Too many requests',
            'message': 'Slow down'
        }), 429
    return render_template("/errors/429.html")

@errors_bp.app_errorhandler(401)
def handle_401(e):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401
        
    return render_template("errors/401.html"), 401