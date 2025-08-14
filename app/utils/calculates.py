''' CALCULATE UPCOMING MAINTENANCE '''
def calculate_upcoming_maintenance(moto, elements):
    maintenance_items = []
    current_mileage = moto.mileage

    MAINTENANCE_INTERVALS = {
        'oil_filter': 5000,
        'air_filter': 8000,
        'spark_plug': 10000,
        'brake_fluid': 11000,
    }

    MAINTENANCE_NAMES = {
        'oil_filter': 'Замена масляного фильтра',
        'air_filter': 'Замена воздушного фильтра',
        'spark_plug': 'Замена свечей зажигания',
        'brake_fluid': 'Замена тормозной жидкости',
    }

    DRIVE_MAINTENANCE = {
        'chain': {'maintenance': 2000, 'change': 10000},
        'belt': {'change': 15000},
        'shaft': {'maintenance': 5000}
    }

    # Проверяем, что elements существует
    if not elements:
        return maintenance_items

    drive_type = moto.drive_type
    drive_intervals = DRIVE_MAINTENANCE.get(drive_type, {})

    # Обработка обслуживания привода
    if 'maintenance' in drive_intervals:
        km_since_last = current_mileage - (elements.drive_maintenance_mileage or 0)
        remaining_km = drive_intervals['maintenance'] - km_since_last

        if not elements.drive_maintenance or km_since_last >= drive_intervals['maintenance']:
            action_name = "Смазка цепи" if drive_type == "chain" else "Замена масла в кардане"
            
            maintenance_items.append({
                'name': action_name,
                'moto_model': moto.model,
                'moto_id': moto.id,
                'interval': f"Каждые {drive_intervals['maintenance']:,} км".replace(',', ''),
                'remaining_km': remaining_km,
                'remaining_days': estimate_days(remaining_km),
                'is_overdue': remaining_km < 0
            })

    if 'change' in drive_intervals:
        km_since_last = current_mileage - (elements.drive_change_mileage or 0)
        remaining_km = drive_intervals['change'] - km_since_last

        if not elements.drive_change or km_since_last >= drive_intervals['change']:
            action_name = "Замена цепи" if drive_type == "chain" else "Замена ремня" if drive_type == "belt" else "Обслуживание кардана"
            
            maintenance_items.append({
                'name': action_name,
                'moto_model': moto.model,
                'moto_id': moto.id,
                'interval': f"Каждые {drive_intervals['change']:,} км".replace(',', ''),
                'remaining_km': remaining_km,
                'remaining_days': estimate_days(remaining_km),
                'is_overdue': remaining_km < 0
            })

    # Обработка остального обслуживания
    for element in MAINTENANCE_INTERVALS.keys():
        last_change_mileage = getattr(elements, f"{element}_mileage", 0) or 0
        interval = MAINTENANCE_INTERVALS[element]
        km_since_last = max(0, current_mileage - last_change_mileage)
        remaining_km = interval - km_since_last

        # Показываем элемент, если он требует обслуживания (флаг False или пробег превысил интервал)
        if not getattr(elements, element, True) or km_since_last >= interval:
            if remaining_km <= 5000:
                maintenance_items.append({
                    'name': MAINTENANCE_NAMES[element],
                    'moto_model': moto.model,
                    'moto_id': moto.id,
                    'interval': f"Каждые {interval:,} км".replace(',', ''),
                    'remaining_km': remaining_km,
                    'remaining_days': estimate_days(remaining_km),
                    'is_overdue': remaining_km < 0
                })

    return maintenance_items


''' ESTIMATE DAYS '''
def estimate_days(remaining_km):
    km_per_day = 50
    days = remaining_km / km_per_day
    return round(days)


''' CALCULATE MOTORCYCLE CONDITION '''
def calculate_moto_condition(moto, elements):
    if not elements:
        return "Нет данных", 0
    
    WEIGHTS = {
        'oil_filter': 1.5,
        'air_filter': 1.2,
        'spark_plug': 1.3,
        'brake_fluid': 1.7,
        'drive_maintenance': 1.0,
        'drive_change': 1.4
    }

    MAINTENANCE_INTERVALS = {
        'oil_filter': 5000,
        'air_filter': 8000,
        'spark_plug': 10000,
        'brake_fluid': 11000,
        'drive_maintenance': 2000 if moto.drive_type == 'chain' else 5000 if moto.drive_type == 'shaft' else 0,
        'drive_change': 10000 if moto.drive_type == 'chain' else 15000 if moto.drive_type == 'belt' else 0
    }

    current_mileage = moto.mileage
    total_score = 0
    max_score = 0

    for element in MAINTENANCE_INTERVALS.keys():
        # Пропускаем элементы, которые не применимы для данного типа привода
        if MAINTENANCE_INTERVALS[element] == 0:
            continue
            
        last_change_mileage = getattr(elements, f"{element}_mileage", 0) or 0
        interval = MAINTENANCE_INTERVALS[element]
        km_since_last = max(0, current_mileage - last_change_mileage)

        if km_since_last == 0:
            element_score = 1.0
        else:
            # Насколько превышен интервал (%)
            overdue_percent = max(0, (km_since_last - interval) / interval * 100)
        
            # Оценка элемента: 1.0 если в пределах интервала, уменьшается при превышении
            element_score = max(0, 1 - min(1, overdue_percent / 100))

        weight = WEIGHTS.get(element, 1.0)
        total_score += element_score * weight
        max_score += weight

    if max_score == 0:
        return "Нет данных", 0

    normalized_score = (total_score / max_score) * 100

    if normalized_score >= 80:
        return "Отличное", normalized_score
    elif normalized_score >= 60:
        return "Хорошее", normalized_score
    elif normalized_score >= 40:
        return "Среднее", normalized_score
    elif normalized_score >= 20:
        return "Плохое", normalized_score
    else:
        return "Критическое", normalized_score