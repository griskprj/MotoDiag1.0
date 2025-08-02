document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Получаем форму и её элементы
    const form = e.target;
    const registerBtn = document.querySelector('.register-btn');
    
    // Получаем значения полей
    const formData = new FormData(form);
    const username = formData.get('username');
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');
    const privacyChecked = formData.get('privacy') === 'on';
    
    // Сбрасываем все сообщения об ошибках
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
    });

    // Валидация
    let isValid = true;
    
    if (password !== confirmPassword) {
        document.getElementById('confirm-password-error').textContent = 'Пароли не совпадают';
        document.getElementById('confirm-password-error').style.display = 'block';
        isValid = false;
    }
    
    if (!privacyChecked) {
        isValid = false;
    }

    if (isValid) {
        // Анимация кнопки
        registerBtn.textContent = 'Регистрация...';
        registerBtn.style.opacity = '0.7';
        
        // Отправка данных на сервер
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                registerBtn.textContent = 'Успешно!';
                registerBtn.style.background = 'linear-gradient(to right, #2d7d2d, #1e4e1e)';
                setTimeout(() => window.location.href = 'login', 1500);
            } else {
                registerBtn.textContent = 'Зарегистрироваться';
                registerBtn.style.opacity = '1';
                // Показ ошибок с сервера
                Object.keys(data.errors).forEach(field => {
                    const errorElement = document.getElementById(`${field}-error`);
                    if (errorElement) {
                        errorElement.textContent = data.errors[field];
                        errorElement.style.display = 'block';
                    }
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            registerBtn.textContent = 'Ошибка!';
        });
    }
});