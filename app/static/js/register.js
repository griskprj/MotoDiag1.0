document.getElementById('registerForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Получаем значения полей
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const privacyChecked = document.getElementById('privacy').checked;
    
    // Сбрасываем все сообщения об ошибках
    document.querySelectorAll('.error-message').forEach(el => {
        el.style.display = 'none';
    });
    
    let isValid = true;
    
    // Валидация логина
    if (username.length < 4 || username.length > 20) {
        document.getElementById('username-error').style.display = 'block';
        isValid = false;
    }
    
    // Простая валидация email
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        document.getElementById('email-error').style.display = 'block';
        isValid = false;
    }
    
    // Валидация пароля
    if (password.length < 8) {
        document.getElementById('password-error').style.display = 'block';
        isValid = false;
    }
    
    // Проверка совпадения паролей
    if (password !== confirmPassword) {
        document.getElementById('confirm-password-error').style.display = 'block';
        isValid = false;
    }
    
    // Проверка согласия с политикой
    if (!privacyChecked) {
        alert('Необходимо согласиться с политикой конфиденциальности');
        isValid = false;
    }
    
    if (isValid) {
        // Анимация кнопки
        const registerBtn = document.querySelector('.register-btn');
        registerBtn.textContent = 'Регистрация...';
        registerBtn.style.opacity = '0.7';
        
        // Здесь можно добавить AJAX-запрос для регистрации
        console.log('Регистрационные данные:', {
            username,
            email,
            password,
            privacyChecked
        });
        
        setTimeout(() => {
            registerBtn.textContent = 'Успешно!';
            registerBtn.style.background = 'linear-gradient(to right, #2d7d2d, #1e4e1e)';
            
            // Перенаправление на страницу входа через 1.5 секунды
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        }, 1500);
    }
});

// Валидация в реальном времени
document.getElementById('username').addEventListener('input', function() {
    if (this.value.length >= 4 && this.value.length <= 20) {
        document.getElementById('username-error').style.display = 'none';
    }
});

document.getElementById('email').addEventListener('input', function() {
    if (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.value)) {
        document.getElementById('email-error').style.display = 'none';
    }
});

document.getElementById('password').addEventListener('input', function() {
    if (this.value.length >= 8) {
        document.getElementById('password-error').style.display = 'none';
    }
});

document.getElementById('confirm-password').addEventListener('input', function() {
    if (this.value === document.getElementById('password').value) {
        document.getElementById('confirm-password-error').style.display = 'none';
    }
});