from flask import Blueprint, render_template, jsonify
from flask_login import current_user
from datetime import datetime
from app.models import User, Motorcycle, MaintenanceHistory

community_bp = Blueprint("community_bp", __name__, url_prefix="/community")

@community_bp.route("/riders")
def riders():
    current_user_data = current_user if current_user.is_authenticated  else None

    users = User.query.all()
    users_data = []

    for user in users:
        user_motos = Motorcycle.query.filter_by(owner_id=user.id).all()
        moto_count = len(user_motos)
        total_mileage = sum(moto.mileage for moto in user_motos) if user_motos else 0

        users_data.append({
            "id": user.id,
            "image": user.image,
            "username": user.username,
            "moto_count": moto_count,
            "total_mileage": total_mileage,
            "join_date": user.join_date or datetime.utcnow()
        })

    return render_template("riders.html", 
        users_data=users_data,
        user=current_user_data
    )

@community_bp.route("rider/<int:user_id>")
def rider(user_id):
    print("COMMUNITY PROFILE")
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}),404
    
    user_motos = Motorcycle.query.filter_by(owner_id=user.id).all()
    moto_count = len(user_motos)
    total_mileage = sum(moto.mileage for moto in user_motos) if user_motos else 0
    maintenance_count = len(MaintenanceHistory.query.filter_by(owner_id=user.id).all())

    users_data = ({
        "id": user.id,
        "image": user.image,
        "username": user.username,
        "moto_count": moto_count,
        "total_mileage": total_mileage,
        "maintenance_count": maintenance_count,
        "join_date": user.join_date or datetime.utcnow()
    })

    moto_data = []
    for moto in user_motos:
        moto_data.append({
            "id": moto.id,
            "model": moto.model,
            "year": moto.years_create,
            "mileage": moto.mileage,
            "engine": moto.engine_volume,
            "drive_type": moto.drive_type,
            "condition": moto.condition
        })

    return render_template("community_profile.html", 
                            user=users_data,
                            moto_data=moto_data
    )
