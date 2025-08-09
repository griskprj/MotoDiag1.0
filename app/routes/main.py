from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from app.models import Motorcycle, ElementsFluid
from app.utils.calculates import calculate_moto_condition, calculate_upcoming_maintenance
from app.extension import db

main_bp = Blueprint('main', __name__, url_prefix='/')

@main_bp.route("/")
def main():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('auth_bp.login'))  # Перенаправляем на страницу входа

@main_bp.route("/index")
@login_required
def index():
    user = current_user
    user_moto = Motorcycle.query.filter_by(owner_id=user.id).all()

    if not user_moto:
        return redirect(url_for('moto.add_moto_pg'))  # Убедитесь, что имя blueprint правильное

    moto_data = []
    total_mileage = 0
    total_score = 0
    upcoming_maintenance = []

    for moto in user_moto:
        elements = ElementsFluid.query.filter_by(moto_id=moto.id).first()

        # предстоящее обслуживание
        maintenance_items = calculate_upcoming_maintenance(moto, elements)
        upcoming_maintenance.extend(maintenance_items)
    
        condition, score = calculate_moto_condition(moto, elements)
        total_score += score
        total_mileage += moto.mileage

        moto_data.append({
                "id": moto.id,
                "model": moto.model,
                "year": moto.years_create,
                "mileage": moto.mileage,
                "engine": moto.engine_volume,
                "type": moto.moto_type,
                "image": moto.image,
                "condition": condition,
                "score": round(score),
                "elements": {
                    "brake_fluid": elements.brake_fluid if elements else False,
                    "oil_filter": elements.oil_filter if elements else False,
                    "air_filter": elements.air_filter if elements else False,
                    "spark_plug": elements.spark_plug if elements else False,
                    "chain_lubricate": elements.drive_maintenance if elements else False,
                    "chain_change": elements.drive_change if elements else False,
                    "brake_fluid_date": elements.brake_fluid_date if elements else None,
                    "oil_filter_date": elements.oil_filter_date if elements else None,
                    "air_filter_date": elements.air_filter_date if elements else None,
                    "spark_plug_date": elements.spark_plug_date if elements else None,
                    "chain_lubricate_date": elements.drive_maintenance_date if elements else None,
                    "chain_change_date": elements.drive_change_date if elements else None
                }
        })
    
    avg_score = total_score / len(user_moto) if user_moto else 0
    avg_condition = "Нет данных"

    if avg_score >= 80:
        avg_condition = "Отличное"
    elif avg_score >= 60:
        avg_condition = "Хорошее"
    elif avg_score >= 40:
        avg_condition = "Среднее"
    elif avg_score >= 20:
        avg_condition = "Плохое"
    else:
        avg_condition = "Критическое"

    upcoming_maintenance.sort(key=lambda x: x['remaining_km'])

    return render_template('index.html',
                         user=user,
                         moto_data=moto_data,
                         total_mileage=total_mileage,
                         avg_condition=avg_condition,
                         upcoming_maintenance=upcoming_maintenance[:3])