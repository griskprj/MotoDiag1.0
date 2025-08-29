from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import Motorcycle, MaintenanceHistory, ElementsFluid
from app.extension import db
from app.utils.calculates import calculate_upcoming_maintenance

maintenance_bp = Blueprint('maintenance', __name__, url_prefix='/maintenance')


''' РЕНДЕР СТРАНИЦЫ ОБСЛУЖИВАНИЯ '''
@maintenance_bp.route('/maintenance')
@login_required
def maintenance():
    user = current_user
    user_moto = Motorcycle.query.filter_by(owner_id=user.id).all()
    
    moto_data = []
    upcoming_maintenance = []
    maintenance_history = []
    
    for moto in user_moto:
        elements = ElementsFluid.query.filter_by(moto_id=moto.id).first()
        maintenance_history_db = MaintenanceHistory.query.filter_by(moto_id=moto.id).all()
        
        # Предстоящее обслуживание
        maintenance_items = calculate_upcoming_maintenance(moto, elements)
        upcoming_maintenance.extend(maintenance_items)

        for maintenance in maintenance_history_db:
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
        
        moto_data.append({
            "id": moto.id,
            "model": moto.model,
            "mileage": moto.mileage,
            "drive_type": moto.drive_type
        })
    
    upcoming_maintenance.sort(key=lambda x: x['remaining_km'])
    maintenance_history.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('service.html',
                        user=user,
                        moto_data=moto_data,
                        upcoming_maintenance=upcoming_maintenance[:5],
                        maintenance_history=maintenance_history[:10])

''' ДОБАВЛЕНИЕ ОБСУЛЖИВАНИЯ '''
@maintenance_bp.route('/add_maintenance', methods=['POST'])
@login_required
def add_maintenance():
    if request.method == 'POST':
        try:
            user = current_user
            moto_id = request.form.get('moto_id')
            service_type = request.form.get('service_type')
            mileage = int(request.form.get('mileage'))
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
            cost = int(request.form.get('cost')) if request.form.get('cost') else None
            notes = request.form.get('notes')
            
            moto = Motorcycle.query.get(moto_id)
            if not moto:
                return jsonify({
                    "success": False,
                    "message": "Мотоцикл не найден"
                }), 404
            
            if moto.mileage > mileage:
                return jsonify({
                    "success": False,
                    "message": "Пробег не может быть меньше текущего"
                }), 400
            
            if cost == None or cost == "":
                cost = 0
            
            #get_photo
            image_file = request.files.get('maintenance_image')
            image_data = None
            if image_file:
                image_data = image_file.read()

            moto.mileage = mileage
            moto.last_mileage_update = datetime.utcnow()
            
            # Добавляем запись в историю обслуживания
            new_record = MaintenanceHistory(
                owner_id=user.id,
                moto_id=moto_id,
                service_type=service_type,
                mileage=mileage,
                date=date,
                cost=cost,
                notes=notes,
                image=image_data
            )
            
            db.session.add(new_record)

            elements = ElementsFluid.query.filter_by(moto_id=moto_id).first()
            print(elements)

            if elements:
                service_mapping = {
                    'Замена масляного фильтра': 'oil_filter',
                    'Замена воздушного фильтра': 'air_filter',
                    'Замена свечей зажигания': 'spark_plug',
                    'Замена тормозной жидкости': 'brake_fluid',
                    'Смазка цепи': 'drive_maintenance',
                    'Замена цепи': 'drive_change',
                    'Замена ремня': 'drive_change',
                    'Обслуживание кардана': 'drive_maintenance',
                    'Замена масла в кардане': 'drive_maintenance'
                }

                if service_type in service_mapping:
                    element = service_mapping[service_type]
                    setattr(elements, element, True)
                    setattr(elements, f"{element}_date", date)
                    setattr(elements, f"{element}_mileage", mileage)
                    

            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Обслуживание успешно добавлено'})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 400

''' РЕДАКТИРОВАНИЕ ОБСУЛЖИВАНИЯ '''
@maintenance_bp.route('/edit_maintenance/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance(maintenance_id):
    if request.method == 'GET':
        maintenance = MaintenanceHistory.query.filter_by(
            id=maintenance_id,
            owner_id=current_user.id
        ).first_or_404()

        return jsonify({
            "success": True,
            "data": {
                "id": maintenance.id,
                "moto_id": maintenance.moto_id,
                "service_type": maintenance.service_type,
                "mileage": maintenance.mileage,
                "date": maintenance.date.strftime('%Y-%m-%d'),
                "cost": maintenance.cost,
                "notes": maintenance.notes,
                "has_image": bool(maintenance.image)
            }
        })
    
    elif request.method == 'POST':
        try:
            maintenance = MaintenanceHistory.query.filter_by(
                id=maintenance_id,
                owner_id=current_user.id
            ).first_or_404()

            maintenance.service_type = request.form.get('service_type')
            maintenance.mileage = int(request.form.get('mileage'))
            maintenance.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
            maintenance.cost = int(request.form.get('cost')) if request.form.get('cost') else 0
            maintenance.notes = request.form.get('notes')

            image_file = request.files.get('maintenance_image')
            if image_file and image_file.filename != '':
                if image_file.content_length > 10 * 1024 * 1024:
                    return jsonify({
                        "success": False,
                        "message": "Размер файла не должен превышать 10МБ"
                    }), 400
                maintenance.image = image_file.read()
            
            elements = ElementsFluid.query.filter_by(moto_id=maintenance.moto_id).first()
            if elements:
                service_mapping = {
                    'Замена масляного фильтра': 'oil_filter',
                    'Замена воздушного фильтра': 'air_filter',
                    'Замена свечей зажигания': 'spark_plug',
                    'Замена тормозной жидкости': 'brake_fluid',
                    'Смазка цепи': 'drive_maintenance',
                    'Замена цепи': 'drive_change',
                    'Замена ремня': 'drive_change',
                    'Обслуживание кардана': 'drive_maintenance',
                    'Замена масла в кардане': 'drive_maintenance'
                }

                if maintenance.service_type in service_mapping:
                    element = service_mapping[maintenance.service_type]

                    setattr(elements, element, True)
                    setattr(elements, f"{element}_date", maintenance.date)
                    setattr(elements, f"{element}_mileage", maintenance.mileage)
            
            db.session.commit()

            return jsonify({
                "success": True,
                "message": "Обслуживание успешно добавлено" 
            })

        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Ошибка: {str(e)}'}), 400

''' УДАЛЕНИЕ ОБСЛУЖИВАНИЯ '''
''' УДАЛЕНИЕ ОБСЛУЖИВАНИЯ '''
@maintenance_bp.route('/delete_maintenance/<int:maintenance_id>', methods=['DELETE'])
@login_required
def delete_maintenance(maintenance_id):
    try:
        # ПРАВИЛЬНО: все условия в одном словаре
        maintenance = MaintenanceHistory.query.filter_by(
            id=maintenance_id, 
            owner_id=current_user.id
        ).first()
        
        if not maintenance:
            return jsonify({
                "success": False, 
                "message": "Запись обслуживания не найдена"
            }), 404
        
        # Сохраняем данные для возможного отката элементов
        moto_id = maintenance.moto_id
        service_type = maintenance.service_type
        
        db.session.delete(maintenance)
        
        # Обновляем статус элемента, если это была последняя запись данного типа
        elements = ElementsFluid.query.filter_by(moto_id=moto_id).first()
        if elements:
            service_mapping = {
                'Замена масляного фильтра': 'oil_filter',
                'Замена воздушного фильтра': 'air_filter',
                'Замена свечей зажигания': 'spark_plug',
                'Замена тормозной жидкости': 'brake_fluid',
                'Смазка цепи': 'drive_maintenance',
                'Замена цепи': 'drive_change',
                'Замена ремня': 'drive_change',
                'Обслуживание кардана': 'drive_maintenance',
                'Замена масла в кардане': 'drive_maintenance'
            }
            
            if service_type in service_mapping:
                element = service_mapping[service_type]
                # Проверяем, есть ли другие записи этого типа обслуживания
                # ПРАВИЛЬНО: используем filter() для сложных условий
                other_records = MaintenanceHistory.query.filter(
                    MaintenanceHistory.moto_id == moto_id,
                    MaintenanceHistory.service_type == service_type,
                    MaintenanceHistory.id != maintenance_id
                ).count()
                
                if other_records == 0:
                    # Если это последняя запись, сбрасываем статус
                    setattr(elements, element, False)
                    setattr(elements, f"{element}_date", None)
                    setattr(elements, f"{element}_mileage", 0)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "Обслуживание успешно удалено"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False, 
            "message": f"Ошибка при удалении: {str(e)}"
        }), 500
    
''' ПОЛУЧЕНИЕ ВСЕХ ЗАПИСЕЙ ОБСЛУЖИВАНИЯ '''
@maintenance_bp.route("/get_maintenance_history", methods=['GET'])
@login_required
def get_maintenance_history():
    try:
        moto_id = request.args.get('moto_id')
        page = request.args.get('page', 1, type=int)

        per_page = 10

        query = MaintenanceHistory.query.filter_by(owner_id=current_user.id)
        if moto_id:
            query = query.filter_by(moto_id=moto_id)
        
        maintenance_history = query.order_by(
            MaintenanceHistory.date.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)

        history_data = []
        for maintenance in maintenance_history.items:
            moto = Motorcycle.query.get(maintenance.moto_id)

            history_data.append({
                "id": maintenance.id,
                "service_type": maintenance.service_type,
                "moto_model": moto.model if moto else "Неизвестно",
                "date": maintenance.date.strftime('%d.%m.%Y'),
                "mileage": maintenance.mileage,
                "cost": maintenance.cost,
                "notes": maintenance.notes[:80] + "..." if maintenance.notes and len(maintenance.notes) > 80 else maintenance.notes,
                "has_image": bool(maintenance.image)
            })
        
        return jsonify({
            "success": True,
            "data": history_data,
            "total": maintenance_history.total,
            "pages": maintenance_history.pages,
            "current_page": page
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Ошибка при получении данных: {str(e)}"
        }), 500

            
        
''' ДОБАВЛЕНИЕ ПОСЛЕДНЕГО ОБСЛУЖИВАНИЯ МОТОЦИКЛА (КОМПЛЕКСНО) '''
@maintenance_bp.route("/update_last_maintenance", methods=['POST'])
@login_required
def update_last_mainenance():
    if request.method == "POST":
        try:
            moto_id = request.form.get('moto_id')
            moto = Motorcycle.query.filter_by(id=moto_id, owner_id=current_user.id).first()
            if not moto:
                return jsonify({"success": False, "message": "Мотоцикл не найден"}), 404
            
            elements = ElementsFluid.query.filter_by(moto_id=moto_id).first()
            if not elements:
                return jsonify({"success": False, "message": "Данные обслуживания не найдены"}), 404
            
            maintenance_fields = {
                'brake-liquid': ('brake_fluid', 'brake_fluid_mileage'),
                'oil-filter': ('oil_filter', 'oil_filter_mileage'),
                'air-filter': ('air_filter', 'air_filter_mileage'),
                'spark-plug': ('spark_plug', 'spark_plug_mileage'),
                'chain-lubricate': ('drive_maintenance', 'drive_maintenance_mileage'),
                'chain-change': ('drive_change', 'drive_change_mileage'),
                'belt-change': ('drive_change', 'drive_change_mileage'),
                'change-oil-shift': ('drive_maintenance', 'drive_maintenance_mileage'),
            }

            for field_name, (status_field, mileage_field) in maintenance_fields.items():
                mileage_value = request.form.get(field_name)
                
                # Пропускаем пустые поля
                if not mileage_value or mileage_value.strip() == '':
                    mileage_value = 0
                
                try:
                    mileage = int(mileage_value)
                    
                    # Проверяем, что пробег в допустимых пределах
                    if mileage < 0:
                        return jsonify({
                            "success": False,
                            "message": f"Пробег для {field_name} не может быть отрицательным"
                        }), 400
                    
                    if mileage > moto.mileage:
                        return jsonify({
                            "success": False,
                            "message": f"Пробег обслуживания не может быть больше текущего пробега мотоцикла"
                        }), 400
                    
                    # Обновляем данные
                    setattr(elements, status_field, True)
                    setattr(elements, mileage_field, mileage)
                    setattr(elements, f"{status_field}_date", datetime.utcnow())
                    
                except ValueError:
                    return jsonify({
                        "success": False,
                        "message": f"Некорректное значение пробега для {field_name}"
                    }), 400

            db.session.commit()
            
            return jsonify({"success": True, "message": "Данные успешно обновлены"})
        
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "success": False,
                "message": f"Ошибка сервера: {str(e)}"
            }), 500
    
    return jsonify({"success": False, "message": "Недопустимый метод запроса"}), 405

''' ФОТО ОБСЛУЖИВАНИЯ '''
@maintenance_bp.route("/maintenance_image/<int:maintenance_id>")
@login_required
def maintenance_image(maintenance_id):
    maintenance = MaintenanceHistory.query.get_or_404(maintenance_id)
    
    from io import BytesIO
    from flask import send_file

    if maintenance.image:
        return send_file(
            BytesIO(maintenance.image),
            mimetype='image/jpg',
            as_attachment=False
        )
    