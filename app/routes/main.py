from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import current_user
from app.utils.weather import get_current_weather

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/weather')
def api_weather():
    weather_data = get_current_weather()
    return jsonify(weather_data)

@main_bp.route('/')
def main():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('auth_bp.login'))

@main_bp.route("/dashboard")
def dashboard():
    weather_data = get_current_weather()
    return render_template('dashboard.html', weather=weather_data)
