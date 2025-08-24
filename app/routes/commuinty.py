from flask import Blueprint, render_template, jsonify, request
from flask_login import current_user, login_required
from datetime import datetime
from app.models import User, Motorcycle, MaintenanceHistory, Subscription
from app.extension import db

community_bp = Blueprint("community_bp", __name__, url_prefix="/community")

@community_bp.route("/contact")
def contact():
    return render_template("contact.html")

@community_bp.route("/riders")
@login_required
def riders():
    current_user_data = current_user if current_user.is_authenticated  else None

    users = User.query.outerjoin(Subscription, User.id == Subscription.subscribed_to_id)\
        .group_by(User.id)\
        .order_by(db.func.count(Subscription.id).desc())\
        .all()
    users_data = []

    for user in users:
        user_motos = Motorcycle.query.filter_by(owner_id=user.id).all()
        moto_count = len(user_motos)
        total_mileage = sum(moto.mileage for moto in user_motos) if user_motos else 0
        
        subscribers_count = user.subscribers.count()
        subscriptions_count = user.subscriptions.count()

        is_subscribed = False
        if user.is_authenticated:
            is_subscribed = Subscription.query.filter_by(
                subscriber_id=current_user.id,
                subscribed_to_id=user.id
            ).first() is not None

        users_data.append({
            "id": user.id,
            "image": user.image,
            "username": user.username,
            "moto_count": moto_count,
            "total_mileage": total_mileage,
            "join_date": user.join_date or datetime.utcnow(),
            "subscribers_count": subscribers_count,
            "subscriptions_count": subscriptions_count,
            "is_subscribed": is_subscribed
        })

    return render_template("riders.html", 
        users_data=users_data,
        user=current_user_data
    )

@community_bp.route("rider/<int:user_id>")
@login_required
def rider(user_id):
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}),404
    
    user_motos = Motorcycle.query.filter_by(owner_id=user.id).all()
    moto_count = len(user_motos)
    total_mileage = sum(moto.mileage for moto in user_motos) if user_motos else 0
    maintenance_count = len(MaintenanceHistory.query.filter_by(owner_id=user.id).all())

    subscribers_count = user.subscribers.count()
    subscriptions_count = user.subscriptions.count()

    is_subscribed = False
    if current_user.is_authenticated:
        is_subscribed = Subscription.query.filter_by(
            subscriber_id=current_user.id,
            subscribed_to_id=user.id
        ).first() is not None

    users_data = ({
        "id": user.id,
        "image": user.image,
        "username": user.username,
        "moto_count": moto_count,
        "total_mileage": total_mileage,
        "maintenance_count": maintenance_count,
        "join_date": user.join_date or datetime.utcnow(),
        "subscribers_count": subscribers_count,
        "subscriptions_count": subscriptions_count,
        "is_subscribed": is_subscribed
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

@community_bp.route("/subscribe/<int:user_id>", methods=["POST"])
@login_required
def subscribe(user_id):
    if current_user.id == user_id:
        return jsonify({"success": False, "message": "Нельзя подписаться на себя"}), 400
    
    exiting_sub = Subscription.query.filter_by(
        subscriber_id=current_user.id,
        subscribed_to_id=user_id
    ).first()

    if exiting_sub:
        return jsonify({"success": False, "message": "Вы уже подписаны на этого пользователя"}), 400
    
    new_sub = Subscription(
        subscriber_id=current_user.id,
        subscribed_to_id=user_id
    )

    db.session.add(new_sub)
    db.session.commit()

    return jsonify({"success": True, "message": "Подписка оформлена"})

@community_bp.route("/unsubscribe/<int:user_id>", methods=["POST"])
@login_required
def unsubscribe(user_id):
    sub =   Subscription.query.filter_by(
        subscriber_id=current_user.id,
        subscribed_to_id=user_id
    ).first()

    if not sub:
        return jsonify({"success": False, "message": "Подписка не найдена"}), 404
    
    db.session.delete(sub)
    db.session.commit()

    return jsonify({"success": True, "message": "Подписка отменена"})

@community_bp.route("/check_subscription/<int:user_id>")
@login_required
def check_subscription(user_id):
    is_subscribed = Subscription.query.filter_by(
        subscriber_id=current_user.id,
        subscribed_to_id=user_id
    ).first() is not None

    return jsonify({"is_subscribed": is_subscribed})
