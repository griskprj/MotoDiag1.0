from flask import Blueprint, render_template
from flask_login import current_user
from datetime import datetime
from app.models import User, Motorcycle

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
