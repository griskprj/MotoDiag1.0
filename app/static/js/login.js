document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('remember').checked;
    
    // Здесь можно добавить логику аутентификации
    console.log('Логин:', username);
    console.log('Пароль:', password);
    console.log('Запомнить:', rememberMe);
    
    // Анимация кнопки
    const loginBtn = document.querySelector('.login-btn');
    loginBtn.textContent = 'Вход...';
    loginBtn.style.opacity = '0.7';
    
    setTimeout(() => {
        loginBtn.textContent = 'Войти';
        loginBtn.style.opacity = '1';
        // Здесь можно добавить перенаправление после успешного входа
        // window.location.href = 'dashboard.html';
    }, 1500);
});