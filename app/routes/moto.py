from flask import Blueprint, render_template, url_for, jsonify, request, flash, redirect
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Motorcycle, ElementsFluid, MaintenanceHistory
from app.extension import db
from app.utils.calculates import calculate_moto_condition, calculate_upcoming_maintenance

moto_bp = Blueprint('moto', __name__, url_prefix="/moto")


''' РЕНДЕР СТРАНИЦЫ ДОБАВЛЕНИЯ МОТОЦИКЛА '''
@moto_bp.route("/add_moto_info")
@login_required
def add_moto_pg():
    user = current_user
    print(user)

    return render_template('add_moto_info.html', user=user)

''' ДОБАВЛЕНИЕ МОТОЦИКЛА В БАЗУ ДАННЫХ '''
@moto_bp.route("/add_motorcycle", methods=['POST'])
@login_required
def add_motorcycle():
    if request.method == 'POST':
        model = request.form.get('model')
        type_moto = request.form.get('type')
        drive_type = request.form.get('drive_type')

        try:
            year = int(request.form.get('year'))
            mileage = int(request.form.get('mileage'))
            engine = int(request.form.get('engine'))

            if year < 1900 or year > datetime.now().year:
                return jsonify({"success": False, "message": "Некорректный год"})
            
            if mileage < 0 or engine < 50:
                return jsonify({"success": False, "message": "Пробег или объем двигателя не могут быть отрицательными"})
        except ValueError:
            return jsonify({"success": False, "message": "Ошибка в данных: ожидалось число"})

        # Получаем фото
        image_file = request.files.get('moto_image')
        image_data = None
        if image_file:
            image_data = image_file.read()

        try:
            user = current_user

            new_moto = Motorcycle(
                owner_id=user.id,
                model=model,
                years_create=year,
                mileage=mileage,
                last_mileage_update=datetime.utcnow(),
                moto_type=type_moto,
                engine_volume=engine,
                drive_type=drive_type,
                image=image_data
            )
            
            db.session.add(new_moto)
            db.session.flush()  # Это нужно, чтобы получить ID нового мотоцикла
            
            # Создаем запись о состоянии
            new_elm_fld = ElementsFluid(
                owner_id=user.id,
                moto_id=new_moto.id,
                oil_filter_mileage=mileage,
                air_filter_mileage=mileage,
                spark_plug_mileage=mileage,
                brake_fluid_mileage=mileage,
                drive_maintenance_mileage=mileage if drive_type in ['chain', 'shaft'] else 0,
                drive_change_mileage=mileage if drive_type in ['chain', 'belt'] else 0,
                oil_filter=True,
                air_filter=True,
                spark_plug=True,
                brake_fluid=True,
                drive_maintenance=True if drive_type in ['chain', 'shaft'] else False,
                drive_change=True if drive_type in ['chain', 'belt'] else False
            )

            current_user.first_reg = 0
            db.session.add(new_elm_fld)
            db.session.commit()  # Теперь коммитим обе записи

            return jsonify({
                "success": True,
                "message": "Мотоцикл успешно добавлен",
                "redirect": url_for('main.index')
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"Ошибка при добавлении: {str(e)}"
            }), 500
    
    return jsonify({"success": False, "message": "Недопустимый метод запроса"}), 405

''' МОИ МОТОЦИКЛЫ '''
@moto_bp.route('/my_moto')
@login_required
def my_moto():
    user = current_user
    user_moto = Motorcycle.query.filter_by(owner_id=user.id).all()

    moto_data = []
    for moto in user_moto:
        elements = ElementsFluid.query.filter_by(moto_id=moto.id).first()

        condition, score = calculate_moto_condition(moto, elements)

        moto_data.append({
            "id": moto.id,
            "model": moto.model,
            "year": moto.years_create,
            "mileage": moto.mileage,
            "engine": moto.engine_volume,
            "type": moto.moto_type,
            "image": moto.image,
            "condition": condition,
            "score": round(score)
        })

    return render_template('my_moto.html', moto_data=moto_data, user=user)

''' ДЕТАЛИ МОТОЦИКЛА '''
@moto_bp.route("/moto/<int:moto_id>")
@login_required
def moto(moto_id):
    user = current_user
    moto = Motorcycle.query.filter_by(id=moto_id, owner_id=current_user.id).first()
    maintenance_history = []

    print(f"Drive type in DB: {moto.drive_type if moto else 'Moto not found'}")

    if not moto:
        flash('Мотоцикл не найден', 'danger')
        return redirect(url_for('moto.my_moto'))
    
    elements = ElementsFluid.query.filter_by(moto_id=moto.id).first()
    history = MaintenanceHistory.query.filter_by(moto_id=moto.id).all()

    upcoming_maintenance = calculate_upcoming_maintenance(moto, elements)
    condition, score = calculate_moto_condition(moto, elements)
    
    moto_data = ({
        "id": moto.id,
        "model": moto.model,
        "year": moto.years_create,
        "mileage": moto.mileage,
        "engine": moto.engine_volume,
        "type": moto.moto_type,
        "image": moto.image,
        "condition": condition,
        "score": round(score),
        "last_mileage_update": moto.last_mileage_update.strftime('%d.%m.%Y') if moto.last_mileage_update else None,
        "drive_type": moto.drive_type
    })

    for maintenance in history:
        maintenance_history.append({
            "id": maintenance.id,
            "type": maintenance.service_type,
            "moto_model": moto.model,
            "date": maintenance.date,
            "mileage": maintenance.mileage,
            "cost": maintenance.cost,
            "notes": maintenance.notes[:80],
            "image": maintenance.image
        })

    

    return render_template('moto.html',
                           user=user,
                           moto=moto_data,
                           upcoming_maintenance=upcoming_maintenance,
                           maintenance_history=maintenance_history[:10]
                           )

''' РЕДАКТИРОВАНИЕ МОТОЦИКЛА '''
@moto_bp.route("/update_motorcycle", methods=['POST'])
@login_required
def update_motorcycle():
    if request.method == 'POST':
        moto_id = request.form.get('moto_id')
        model = request.form.get('model')
        type_moto = request.form.get('type')
        drive_type = request.form.get('drive_type')

        try:
            year = int(request.form.get('year'))
            mileage = int(request.form.get('mileage'))
            engine = int(request.form.get('engine'))

            if year < 1900 or year > datetime.now().year:
                return jsonify({"success": False, "message": "Некорректный год"})
            
            if mileage < 0 or engine < 50:
                return jsonify({"success": False, "message": "Пробег или объем двигателя не могут быть отрицательными"})

        except ValueError:
            return jsonify({"success":False, "message": "Получена строка, но ожидалось число"})
        
        moto = Motorcycle.query.filter_by(id=moto_id, owner_id=current_user.id).first()
        if not moto:
            return jsonify({"success": False, "message": "Мотоцикл не найден"}), 404
        
        if mileage < moto.mileage:
            maintenance_history = MaintenanceHistory.query.filter(
                MaintenanceHistory.moto_id == moto_id,
                MaintenanceHistory.mileage > mileage
            ).delete()

        moto.model = model
        moto.years_create = year
        moto.mileage = mileage
        moto.engine_volume = engine
        moto.moto_type = type_moto
        moto.drive_type = drive_type

        image_file = request.files.get('moto_image')
        if image_file:
            moto.image = image_file.read()

        try:
            db.session.commit()
            return jsonify({"success":True, "message": "Данные мотоцикла обновлены"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": True, "message": f"Ошибка при обновлении данных: {str(e)}"})
        
    return jsonify({"success": False, "message": "Недопустимый метод запроса"})

''' ОБНОВЛЕНИЕ ПРОБЕГА МОТОЦИКЛА '''
@moto_bp.route("/update_mileage", methods=['POST'])
@login_required
def update_mileage():
    try:
        moto_id = request.form.get('moto_id')
        new_mileage = int(request.form.get('new_mileage'))
        mileage_date_str = request.form.get('mileage_date')
        
        # Проверяем, что дата передана
        if not mileage_date_str:
            return jsonify({
                "success": False,
                "message": "Дата не указана"
            }), 400
            
        mileage_date = datetime.strptime(mileage_date_str, '%Y-%m-%d')
        
        moto = Motorcycle.query.get(moto_id)
        if not moto or moto.owner_id != current_user.id:
            return jsonify({
                "success": False,
                "message": "Мотоцикл не найден"
            }), 404
    
        # Проверка даты
        if mileage_date.date() > datetime.utcnow().date():
            return jsonify({
                "success": False,
                "message": "Дата не может быть в будущем"
            }), 400
        
        if new_mileage < moto.mileage:
            MaintenanceHistory.query.filter(
                MaintenanceHistory.moto_id == moto_id,
                MaintenanceHistory.mileage > new_mileage
            ).delete()

        # Обновляем данные
        moto.mileage = new_mileage
        moto.last_mileage_update = mileage_date
        
        elements = ElementsFluid.query.filter_by(moto_id=moto.id).first()
        if elements:
            # Обновляем флаги обслуживания
            MAINTENANCE_INTERVALS = {
                'oil_filter': 5000,
                'air_filter': 8000,
                'spark_plug': 10000,
                'brake_fluid': 11000,
                'drive_maintenance': 2000 if moto.drive_type == 'chain' else 5000 if moto.drive_type == 'shaft' else 0,
                'drive_change': 10000 if moto.drive_type == 'chain' else 15000 if moto.drive_type == 'belt' else 0
            }

            for element, interval in MAINTENANCE_INTERVALS.items():
                if interval == 0:
                    continue
                    
                last_change_mileage = getattr(elements, f"{element}_mileage", 0)
                if new_mileage - last_change_mileage >= interval:
                    setattr(elements, element, False)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Пробег успешно обновлен"
        })
    except ValueError as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка в данных: {str(e)}"
        }), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Ошибка сервера: {str(e)}"
        }), 500
    
''' УДАЛЕНИЕ МОТОЦИКЛА '''
@moto_bp.route("/delete_moto/<int:moto_id>", methods=['DELETE'])
@login_required
def delete_moto(moto_id):
    # Проверяем, что мотоцикл принадлежит текущему пользователю
    moto = Motorcycle.query.filter_by(id=moto_id, owner_id=current_user.id).first()
    print("RESPONSE WAS GET")

    if not moto:
        return jsonify({"success": False, "message": "Мотоцикл не найден или не принадлежит вам"}), 404
    
    try:
        # Удаляем связанные записи
        MaintenanceHistory.query.filter_by(moto_id=moto_id).delete()
        ElementsFluid.query.filter_by(moto_id=moto_id).delete()
        
        # Удаляем сам мотоцикл
        db.session.delete(moto)
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Мотоцикл и все связанные данные успешно удалены"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": f"При удалении произошла ошибка: {str(e)}"
        }), 500


@moto_bp.route("/moto_image_<int:moto_id>")
@login_required
def moto_image(moto_id):
    moto = Motorcycle.query.get_or_404(moto_id)
    
    from io import BytesIO
    from flask import send_file

    return send_file(
        BytesIO(moto.image),
        mimetype='image/jpg',
        as_attachment=False
    )