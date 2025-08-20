
// Обработка кнопки смены пароля
document.getElementById('change-password-btn').addEventListener('click', function() {
    document.getElementById('password-modal').style.display = 'flex';
});

// Закрытие модального окна
document.querySelector('.close-modal').addEventListener('click', function() {
    document.getElementById('password-modal').style.display = 'none';
});

//Удаление аккаунта
const deleteBtn = document.getElementById('delete-account-btn');
if (deleteBtn) {
    deleteBtn.addEventListener('click', async function() {
        if (confirm('Вы уверены, что хотите удалить аккаунт? Все данные будут удалены без возможности восстановления')) {
            try {
                const csrfToken = document.querySelector('input[name="csrf_token"]').value;
                
                const response = await fetch('/profile/profile', {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        csrf_token: csrfToken  // Добавляем токен и в тело запроса
                    })
                });
                
                const result = await response.json();

                if (result.success) {
                    alert('Ваш аккаунт был успешно удален');
                    window.location.href = '/auth/register';
                } else {
                    alert('Ошибка: ' + (result.message || 'Не удалось удалить аккаунт'));
                }
            } catch (error) {
                console.error('Ошибка:', error);
                alert('Произошла ошибка при отправке данных');
            }
        }
    });
}

document.getElementById('password-form').addEventListener('submit', async function(e){
    e.preventDefault();

    const formData = new FormData(this);

    try {
        const response = await fetch('/profile/change_password', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}',
            },
        });

        const result = await response.json();

        if (result.success) {
            alert('Пароль успешно изменен!');
            window.location.reload();
        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (error) {
        console.error('Ошибка', error);
        alert('Произошла ошибка при отправке данных');
    }
});

document.getElementById('profile-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    try {
        const response = await fetch('/profile/profile', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': '{{ csrf_token() }}'
            },
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert('Данные успешно обновлены!');
            window.location.reload();
        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Произошла ошибка при отправке данных');
    }
});

// Обработка загрузки аватарки
document.getElementById('avatar-upload').addEventListener('change', function(e) {
    if (this.files && this.files[0]) {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            document.getElementById('avatar-preview').src = e.target.result;
        }
        
        reader.readAsDataURL(this.files[0]);
    }
});