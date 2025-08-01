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
