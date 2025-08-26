// Открытие модального окна
document.querySelectorAll('.quick-add-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const serviceType = this.textContent.trim();
        document.getElementById('serviceType').value = serviceType;
        document.getElementById('serviceModal').style.display = 'flex';
    });
});

// Закрытие модального окна
document.querySelector('.close-modal').addEventListener('click', function() {
    document.getElementById('serviceModal').style.display = 'none';
});

// Закрытие при клике вне окна
document.querySelector('.modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
    }
});

// Отправка формы
document.getElementById('serviceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/maintenance/add_maintenance', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}' // Добавляем CSRF токен
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            document.getElementById('serviceModal').style.display = 'none';
            this.reset();
            // Обновляем страницу или добавляем запись динамически
            location.reload();
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Ошибка при отправке данных');
        console.error(error);
    }
});


// Обработка формы обновления пробега
document.getElementById('mileageForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/moto/update_mileage', {  // Изменили URL
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}' // Добавляем CSRF токен
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.message || 'Ошибка сервера');
        }
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            location.reload(); // Обновляем страницу
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Ошибка при обновлении пробега: ' + error.message);
        console.error(error);
    }
});


//Обработчики для фильтра
document.querySelectorAll('.filter-select').forEach(select => {
    select.addEventListener('change', function() {
        filterMainenanceItems();
    });
});

//Фильтрация элементов обслуживания
function filterMainenanceItems() {
    const typeFilter = document.querySelector('.filter-select:nth-of-type(1)').value;

    const maintenanceItems = document.querySelectorAll('.maintenance-item:not(.no-maintenance)');

    maintenanceItems.forEach(item => {
        const motoId = item.dataset.motoId;
        const serviceType = item.dataset.serviceType;

        const typeMatch = typeFilter === 'all' || serviceTypeMatches(serviceType, typeFilter);

        if (typeMatch) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// Функция для проверки соответствия типа обслуживания фильтру
function serviceTypeMatches(serviceType, filterValue) {
    const typeMapping = {
        'oil': ['Замена масляного фильтра'],
        'filter': ['Замена воздушного фильтра'],
        'brakes': ['Замена тормозной жидкости'],
        'chain': ['Смазка цепи', 'Замена цепи', 'Замена ремня', 'Замена масла в кардане'],
    };
    
    if (filterValue in typeMapping) {
        return typeMapping[filterValue].includes(serviceType);
    }
    return false;
}



// Функция для открытия модального окна редактирования
function openRedModal() {
    const modal = document.getElementById('editModal');
    modal.style.display = 'flex';
}

// Закрытие модального окна редактирования
document.querySelector('#editModal .close-modal').addEventListener('click', function() {
    document.getElementById('editModal').style.display = 'none';
});

// Закрытие при клике вне окна
document.querySelector('#editModal.modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
    }
});

// Обработка загрузки фото в модальном окне редактирования
const editPhotoUpload = document.getElementById('edit-photo-upload');
const editPhotoInput = document.getElementById('edit-photo-input');
const editPreviewPhoto = document.getElementById('edit-preview-photo');

editPhotoUpload.addEventListener('click', () => editPhotoInput.click());

editPhotoInput.addEventListener('change', function(e) {
    if (e.target.files[0]){
        const reader = new FileReader();
        reader.onload = function(event) {
            editPreviewPhoto.src = event.target.result;
        };
        reader.readAsDataURL(e.target.files[0]);
    }
});

// Отправка формы редактирования
document.getElementById('editForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/moto/update_motorcycle', {
            method: 'POST',
            body: formData
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(result.message);
            document.getElementById('editModal').style.display = 'none';
            location.reload(); // Обновляем страницу для отображения изменений
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert('Ошибка при сохранении изменений');
        console.error(error);
    }
});


// Показываем только соответствующие типу привода кнопки
function updateQuickAddButtons() {
    const driveType = "{{ moto.drive_type }}"; // Получаем тип привода из шаблона
    
    document.querySelectorAll('.quick-add-btn').forEach(btn => {
        btn.classList.remove('show');
        
        if (btn.dataset.serviceType === "Смазка цепи" && driveType === "chain") {
            btn.classList.add('show');
        } else if (btn.dataset.serviceType === "Замена цепи" && driveType === "chain") {
            btn.classList.add('show');
        } else if (btn.dataset.serviceType === "Замена ремня" && driveType === "belt") {
            btn.classList.add('show');
        } else if (btn.dataset.serviceType === "Замена масла в кардане" && driveType === "shaft") {
            btn.classList.add('show');
        } else if (!btn.classList.contains('drive-chain') && 
                !btn.classList.contains('drive-belt') && 
                !btn.classList.contains('drive-shaft')) {
            // Показываем общие кнопки (не связанные с приводом)
            btn.classList.add('show');
        }
    });
}

// Вызываем при загрузке страницы
document.addEventListener('DOMContentLoaded', updateQuickAddButtons);


//Удаление мотоцикла
const deleteBtn = document.querySelector('.delete-btn');
if (deleteBtn) {
    deleteBtn.addEventListener('click', function(e) {
        e.preventDefault();
        
        if (confirm('Вы уверены, что хотите удалить мотоцикл? Вся его история обслуживания будет также удалена.')) {
            console.log('{{ moto.id }}')
            fetch('/moto/delete_moto/' + '{{ moto.id }}', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token() }}' // Добавляем CSRF токен
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert(data.message || 'Мотоцикл успешно удален');
                    window.location.href = "/moto/my_moto";
                } else {
                    alert('Ошибка: ' + (data.message || 'Неизвестная ошибка'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ошибка при удалении мотоцикла');
            });
        }
    });
}





// Функция для открытия модального окна последнего обслуживания
function openMaintenanceModal() {
    const modal = document.getElementById('maintenanceModal');
    modal.style.display = 'flex';
    
    // Установим текущую дату по умолчанию
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('mileageDate').value = today;
}

// Закрытие модального окна последнего обслуживания
document.querySelector('#maintenanceModal .close-modal').addEventListener('click', function() {
    document.getElementById('maintenanceModal').style.display = 'none';
});

// Закрытие при клике вне окна
document.querySelector('#maintenanceModal.modal-overlay').addEventListener('click', function(e) {
    if (e.target === this) {
        this.style.display = 'none';
    }
});

// Обработка отправки формы последнего обслуживания
document.getElementById('maintenanceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/maintenance/update_last_maintenance', {
            method: "POST",
            body: formData
        });
        
        const result = await response.json();
        
        if(result.success) {
            alert(result.message);
            document.getElementById('maintenanceForm').style.display = 'none';
            location.reload();
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Произошла ошибка при отправке данных');
    }
})