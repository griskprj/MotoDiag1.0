from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required, current_user

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def main():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    else:
        return redirect(url_for('auth_bp.login'))

@main_bp.route('/index')
@login_required
def index():
    user = current_user

    return render_template('dashboard.html', user=user)
