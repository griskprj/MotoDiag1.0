from flask import Blueprint, render_template, jsonify, render_template, request
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import MaintenanceHistory, ElementsFluid, Motorcycle, User, Subscription
from app.extension import db
from app.utils.files import allowed_file

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')


''' РЕНДЕР СТРАНИЦЫ ПРОФИЛЯ'''
@profile_bp.route("/profile")
@login_required
def profile():
    user = current_user
    motos = Motorcycle.query.filter_by(owner_id=user.id).all()
    maintenance_notes = MaintenanceHistory.query.filter_by(owner_id=user.id).all()

    moto_count = 0
    total_mileage = 0
    for moto in motos:
        moto_count += 1
        total_mileage += moto.mileage
    
    maintenance_count = 0
    for maintenance in maintenance_notes:
        maintenance_count += 1


    return render_template('profile.html',
                           user=user,
                           moto_count=moto_count,
                           maintenance_count=maintenance_count,
                           total_mileage=total_mileage)

''' ИЗМЕНЕНИЕ ИНФОРАМЦИИ О ПОЛЬЗОВАТЕЛЕ '''
@profile_bp.route("/profile", methods=['POST'])
@login_required
def update_user():
    user = current_user

    if not user:
        return jsonify({"success": False, "message": "Пользователь не найден"}), 404
    
    username = request.form.get('username')
    email = request.form.get('email')

    if not username or not email:
        return jsonify({"success": False, "message": "Имя пользователя и email обязательны"}), 400

    try:
        # Проверка на уникальность только если значения изменились
        if email != user.email:
            if User.query.filter(User.id != user.id, User.email == email).first():
                return jsonify({"success": False, "message": "Email уже используется другим пользователем"}), 400
        
        if username != user.username:
            if User.query.filter(User.id != user.id, User.username == username).first():
                return jsonify({"success": False, "message": "Имя пользователя уже занято"}), 400

        # Обновляем данные
        user.username = username
        user.email = email
        
        # Обработка загрузки изображения
        if 'avatar' in request.files:
            image_file = request.files['avatar']
            if image_file and allowed_file(image_file.filename):
                user.image = image_file.read()
            elif image_file and not allowed_file(image_file.filename):
                return jsonify({"success": False, "message": "Недопустимый формат изображения"}), 400

        db.session.commit()
        return jsonify({"success": True, "message": "Данные успешно обновлены"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "Ошибка целостности данных: возможно, такое имя пользователя или email уже существуют"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка сервера: {str(e)}"}), 500
    
''' ОБНОВЛЕНИЕ ПАРОЛЯ '''
@profile_bp.route("/change_password", methods=['POST'])
@login_required
def change_password():
    user = current_user

    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    try:
        if not check_password_hash(user.password_hash, current_password):
            print("НЕВЕРНЫЙ ПАРОЛЬ")
            return jsonify({"success": False, "message": "Неверный прошлый пароль"}), 400

        if new_password != confirm_password:
            print("ПАРОЛИ НЕ СОВПАДАЮТ")
            return jsonify({"success": False, "message": "Пароли не совпадают"}), 400
        
        user.password_hash = generate_password_hash(new_password)
        print("ПАРОЛЬ УСТАНОВЛЕН")

        db.session.commit()
        print("КОММИТ ПРОЙДЕН")

        return jsonify({"success": True, "message": "Пароль обновлен"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Ошибка: {str(e)}"}), 500
    
''' УДАЛЕНИЕ АККАУНТА '''
@profile_bp.route("/profile", methods=['DELETE'])
@login_required
def delete_account():
    user = current_user
    motos = Motorcycle.query.filter_by(owner_id=user.id).all()
    
    # Delete subscriptions where useer was subscriber
    Subscription.query.filter_by(subscriber_id=user.id).delete()

    # Delete subscriptions where user subdscribers
    Subscription.query.filter_by(subscribed_to_id=user.id).delete

    for moto in motos:
        el_fluid = ElementsFluid.query.filter_by(moto_id=moto.id).first()
        
        db.session.delete(el_fluid)

        maintenance_histoty = MaintenanceHistory.query.filter_by(moto_id=moto.id).all()
        for maintenance in maintenance_histoty:
            db.session.delete(maintenance)

        db.session.delete(moto)

    db.session.delete(user)
    db.session.commit()

    return jsonify({"success": True, "message": "Вы были успешно удалены. Возвращайтесь :'("})