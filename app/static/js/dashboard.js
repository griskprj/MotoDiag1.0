// dashboard.js

document.addEventListener('DOMContentLoaded', function() {
    // ==================== БУРГЕР-МЕНЮ ====================
    const burgerMenu = document.querySelector('.burger-menu');
    const headerNav = document.querySelector('.header-nav');
    const navLinks = document.querySelectorAll('.header-link');
    
    // Функция переключения меню
    function toggleMenu() {
        burgerMenu.classList.toggle('active');
        headerNav.classList.toggle('active');
        
        // Блокировка скролла при открытом меню
        if (burgerMenu.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
            document.addEventListener('click', closeMenuOnClickOutside);
        } else {
            document.body.style.overflow = '';
            document.removeEventListener('click', closeMenuOnClickOutside);
        }
    }
    
    // Закрытие меню при клике вне области
    function closeMenuOnClickOutside(e) {
        if (!headerNav.contains(e.target) && !burgerMenu.contains(e.target)) {
            toggleMenu();
        }
    }
    
    // Закрытие меню при клике на ссылку
    function closeMenu() {
        if (burgerMenu.classList.contains('active')) {
            toggleMenu();
        }
    }
    
    // Навешиваем обработчики событий
    burgerMenu.addEventListener('click', toggleMenu);
    navLinks.forEach(link => link.addEventListener('click', closeMenu));

    // ==================== УВЕДОМЛЕНИЯ ====================
    const notifications = document.querySelector('.notifications');
    const notificationBadge = document.querySelector('.notification-badge');
    
    // Функция обновления количества уведомлений
    function updateNotifications() {
        // В реальном приложении здесь был бы запрос к серверу
        const count = Math.floor(Math.random() * 5); // Для демонстрации
        notificationBadge.textContent = count || '';
        notificationBadge.style.display = count ? 'flex' : 'none';
    }
    
    notifications.addEventListener('click', function(e) {
        e.preventDefault();
        alert(`У вас ${notificationBadge.textContent || 'нет'} новых уведомлений`);
        // После просмотра обнуляем счетчик
        notificationBadge.textContent = '';
        notificationBadge.style.display = 'none';
    });

    // ==================== ПОГОДА ====================
    const weatherIcon = document.querySelector('.weather-icon svg');
    const weatherTemp = document.querySelector('.weather-info p:first-child');
    const weatherAdvice = document.querySelector('.weather-info p:last-child');
    
    // Конфигурация погоды
    const weatherConditions = [
        { 
            temp: "+18°C", 
            desc: "солнечно", 
            advice: "Идеальная погода для поездки",
            icon: `
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 2v2"/>
                <path d="M12 20v2"/>
                <path d="m4.93 4.93 1.41 1.41"/>
                <path d="m17.66 17.66 1.41 1.41"/>
                <path d="M2 12h2"/>
                <path d="M20 12h2"/>
                <path d="m6.34 17.66-1.41 1.41"/>
                <path d="m19.07 4.93-1.41 1.41"/>
            `,
            class: 'sunny'
        },
        { 
            temp: "+12°C", 
            desc: "облачно", 
            advice: "Возьмите ветровку",
            icon: `
                <path d="M18 10h-1a4 4 0 0 0-4 4v1"/>
                <path d="M6 10H5a4 4 0 0 0-4 4v1"/>
                <path d="M8 15a5 5 0 0 1 8 0"/>
                <path d="M16 15a5 5 0 0 1 5 5H3a5 5 0 0 1 5-5"/>
            `,
            class: 'cloudy'
        },
        { 
            temp: "+22°C", 
            desc: "ясно", 
            advice: "Отличный день для длинной поездки",
            icon: `
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 2v2"/>
                <path d="M12 20v2"/>
                <path d="m4.93 4.93 1.41 1.41"/>
                <path d="m17.66 17.66 1.41 1.41"/>
                <path d="M2 12h2"/>
                <path d="M20 12h2"/>
                <path d="m6.34 17.66-1.41 1.41"/>
                <path d="m19.07 4.93-1.41 1.41"/>
            `,
            class: 'clear'
        },
        { 
            temp: "+8°C", 
            desc: "дождь", 
            advice: "Будьте осторожны на дороге",
            icon: `
                <path d="M16 13v8"/>
                <path d="M8 13v8"/>
                <path d="M12 15v8"/>
                <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/>
            `,
            class: 'rainy'
        }
    ];
    
    // Обновление погоды
    async function updateWeather() {
        try {
            const response = await fetch('/api/weather');
            if (!response.ok) throw new Error('Weather fetch failed');
            
            const weatherData = await response.json();
            
            // Анимация изменения
            weatherIcon.style.opacity = '0';
            setTimeout(() => {
                // Установите соответствующую иконку в зависимости от погоды
                setWeatherIcon(weatherData.condition);
                
                weatherTemp.textContent = `${weatherData.temp}, ${weatherData.condition}`;
                weatherAdvice.textContent = weatherData.advice;
                weatherIcon.style.opacity = '1';
            }, 300);
        } catch (error) {
            console.error('Error fetching weather:', error);
            // Можно оставить fallback на случай ошибки
            const randomWeather = weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
            weatherIcon.innerHTML = randomWeather.icon;
            weatherTemp.textContent = `${randomWeather.temp}, ${randomWeather.desc}`;
            weatherAdvice.textContent = randomWeather.advice;
        }
    }
    function setWeatherIcon(condition) {
        // Упрощенная логика - можно расширить
        if (condition.toLowerCase().includes('дождь')) {
            weatherIcon.innerHTML = `
                <path d="M16 13v8"/>
                <path d="M8 13v8"/>
                <path d="M12 15v8"/>
                <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"/>
            `;
            weatherIcon.className = 'rainy';
        } else if (condition.toLowerCase().includes('облачно')) {
            weatherIcon.innerHTML = `
                <path d="M18 10h-1a4 4 0 0 0-4 4v1"/>
                <path d="M6 10H5a4 4 0 0 0-4 4v1"/>
                <path d="M8 15a5 5 0 0 1 8 0"/>
                <path d="M16 15a5 5 0 0 1 5 5H3a5 5 0 0 1 5-5"/>
            `;
            weatherIcon.className = 'cloudy';
        } else {
            // По умолчанию солнечно
            weatherIcon.innerHTML = `
                <circle cx="12" cy="12" r="4"/>
                <path d="M12 2v2"/>
                <path d="M12 20v2"/>
                <path d="m4.93 4.93 1.41 1.41"/>
                <path d="m17.66 17.66 1.41 1.41"/>
                <path d="M2 12h2"/>
                <path d="M20 12h2"/>
                <path d="m6.34 17.66-1.41 1.41"/>
                <path d="m19.07 4.93-1.41 1.41"/>
            `;
            weatherIcon.className = 'sunny';
        }
    }

    // ==================== КАРТОЧКИ ДАШБОРДА ====================
    const dashboardCards = document.querySelectorAll('.dashboard-card');
    
    // Анимация при наведении на карточки
    dashboardCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 12px 40px var(--shadow-color)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '0 8px 32px var(--shadow-color)';
        });
    });

    // ==================== СОБЫТИЯ ====================
    const eventItems = document.querySelectorAll('.event-item');
    const eventButtons = document.querySelectorAll('.event-btn');
    
    // Обработка кликов по событиям
    eventItems.forEach(item => {
        item.addEventListener('click', function(e) {
            if (!e.target.classList.contains('event-btn')) {
                this.classList.toggle('expanded');
            }
        });
    });
    
    // Обработка кнопок событий
    eventButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const eventTitle = this.closest('.event-item').querySelector('.event-title').textContent;
            alert(`Вы выбрали: ${eventTitle}\nДействие: ${this.textContent}`);
        });
    });

    // ==================== СООБЩЕСТВО ====================
    const communityCards = document.querySelectorAll('.community-card');
    const communityButtons = document.querySelectorAll('.community-btn');
    
    // Обработка карточек сообщества
    communityCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.classList.contains('community-btn')) {
                const userName = this.querySelector('.community-name').textContent;
                const userBike = this.querySelector('.community-bike').textContent;
                alert(`Профиль: ${userName}\nМотоцикл: ${userBike}`);
            }
        });
    });
    
    // Обработка кнопок "Добавить"
    communityButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const userName = this.closest('.community-card').querySelector('.community-name').textContent;
            this.textContent = 'Запрос отправлен';
            this.style.background = 'var(--highlight-color)';
            
            setTimeout(() => {
                this.textContent = 'Добавить';
                this.style.background = '';
            }, 2000);
        });
    });

    // ==================== ИНИЦИАЛИЗАЦИЯ ====================
    function init() {
        // Первоначальная загрузка данных
        updateNotifications();
        updateWeather();
        
        // Установка интервалов обновления
        setInterval(updateWeather, 300000); // Каждые 5 минут
        setInterval(updateNotifications, 600000); // Каждые 10 минут
        
        // Имитация активности сообщества
        setInterval(() => {
            const activeCount = Math.floor(Math.random() * 5) + 1;
            document.querySelector('.dashboard-card:nth-child(3) p').textContent = 
                `В вашем кругу 12 райдеров. ${activeCount} из них активны прямо сейчас.`;
        }, 10000);
    }
    
    // Запуск инициализации
    init();
});