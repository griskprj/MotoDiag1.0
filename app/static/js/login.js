document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const form = e.target;
    const loginBtn = document.querySelector('.login-btn');
    
    // Сбрасываем ошибки
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
        el.style.display = 'none';
    });

    // Анимация кнопки
    loginBtn.textContent = 'Вход...';
    loginBtn.disabled = true;
    loginBtn.style.opacity = '0.7';

    // Получаем CSRF-токен
    const csrfToken = document.querySelector('[name="csrf_token"]').value;

    // Формируем данные для отправки
    const formData = new URLSearchParams();
    formData.append('username', form.username.value);
    formData.append('password', form.password.value);
    formData.append('remember', document.getElementById('remember').checked);
    formData.append('csrf_token', csrfToken);

    // Отправляем запрос
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Network error');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Успешный вход
            loginBtn.textContent = 'Успешно!';
            loginBtn.style.background = 'linear-gradient(to right, #2d7d2d, #1e4e1e)';
            setTimeout(() => {
                window.location.href = data.redirect || '/';
            }, 1000);
        } else {
            // Показываем ошибки
            showFormErrors(data);
            resetLoginButton(loginBtn);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Ошибка соединения с сервером');
        resetLoginButton(loginBtn);
    });

    // Функции помощники
    function showFormErrors(data) {
        if (data.errors) {
            Object.entries(data.errors).forEach(([field, error]) => {
                const errorElement = document.getElementById(`${field}-error`);
                if (errorElement) {
                    errorElement.textContent = error;
                    errorElement.style.display = 'block';
                }
            });
        }
        if (data.message) showAlert(data.message);
    }

    function showAlert(message) {
        let alertDiv = document.querySelector('.alert');
        if (!alertDiv) {
            alertDiv = document.createElement('div');
            alertDiv.className = 'alert';
            form.prepend(alertDiv);
        }
        alertDiv.textContent = message;
        alertDiv.style.display = 'block';
    }

    function resetLoginButton(btn) {
        btn.textContent = 'Войти';
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.style.background = '';
    }
});