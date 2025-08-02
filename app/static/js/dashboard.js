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

    // ==================== ПОГОДА (WeatherAPI) ====================
    const weatherIcon = document.getElementById('weather-icon');
    const weatherTemp = document.getElementById('weather-temp');
    const weatherCondition = document.getElementById('weather-condition');
    const weatherAdvice = document.getElementById('weather-advice');
    const refreshBtn = document.getElementById('weather-refresh');
    const cityInput = document.getElementById('weather-city-input');

    // Советы для разных погодных условий
    const weatherAdvices = {
        'sunny': 'Идеальная погода для поездки!',
        'clear': 'Отличный день для длинного заезда',
        'cloudy': 'Возможно, стоит надеть ветровку',
        'rain': 'Будьте осторожны на мокрой дороге',
        'snow': 'Не рекомендуем выезжать без необходимости',
        'fog': 'Видимость ограничена, будьте внимательны'
    };

    // Получение погоды с WeatherAPI
    async function fetchWeather(city = 'Sochi') {
        try {
            const response = await fetch(`/get_weather?city=${encodeURIComponent(city)}`);
            const data = await response.json();
            
            if (data.error) throw new Error(data.error);
            
            updateWeatherUI(data);
            saveCityToLocalStorage(city);
        } catch (error) {
            console.error('Ошибка получения погоды:', error);
            weatherTemp.textContent = 'Ошибка загрузки';
            weatherCondition.textContent = '';
            weatherAdvice.textContent = '';
        }
    }

    // Обновление интерфейса с данными о погоде
    function updateWeatherUI(data) {
        weatherTemp.textContent = `${data.temp}°C, ${data.condition}`;
        weatherCondition.textContent = `Влажность: ${data.humidity}% | Ветер: ${data.wind} км/ч`;
        weatherIcon.src = data.icon.startsWith('//') ? `https:${data.icon}` : data.icon;
        
        // Определяем совет по погоде
        const conditionKey = data.condition.toLowerCase();
        let advice = 'Подходящая погода для поездки';
        
        if (conditionKey.includes('дождь')) advice = weatherAdvices['rain'];
        else if (conditionKey.includes('снег')) advice = weatherAdvices['snow'];
        else if (conditionKey.includes('туман')) advice = weatherAdvices['fog'];
        else if (conditionKey.includes('облач')) advice = weatherAdvices['cloudy'];
        else if (conditionKey.includes('ясно')) advice = weatherAdvices['clear'];
        else if (conditionKey.includes('солн')) advice = weatherAdvices['sunny'];
        
        weatherAdvice.textContent = advice;
    }

    // Сохранение города в localStorage
    function saveCityToLocalStorage(city) {
        localStorage.setItem('preferredCity', city);
    }

    // Загрузка города из localStorage
    function loadCityFromLocalStorage() {
        return localStorage.getItem('preferredCity') || 'Moscow';
    }

    // Инициализация погоды
    function initWeather() {
        const defaultCity = loadCityFromLocalStorage();
        cityInput.value = defaultCity;
        fetchWeather(defaultCity);
        
        // Обновление по кнопке
        refreshBtn.addEventListener('click', () => {
            const city = cityInput.value.trim() || 'Moscow';
            fetchWeather(city);
        });
        
        // Обновление по Enter
        cityInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const city = cityInput.value.trim() || 'Moscow';
                fetchWeather(city);
            }
        });
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

    // ==================== ОСНОВНОЙ МОТОЦИКЛ ====================
    const bikeStatusSelect = document.getElementById('bike-status');

    if (bikeStatusSelect) {
        // Загрузка сохраненного статуса из localStorage
        const savedStatus = localStorage.getItem('primaryBikeStatus');
        if (savedStatus) {
            bikeStatusSelect.value = savedStatus;
        }
        
        // Сохранение статуса при изменении
        bikeStatusSelect.addEventListener('change', function() {
            localStorage.setItem('primaryBikeStatus', this.value);
            
            // Визуальная обратная связь
            const statusText = this.options[this.selectedIndex].text;
            const originalText = this.nextElementSibling?.textContent;
            
            if (!this.nextElementSibling || !this.nextElementSibling.classList.contains('status-feedback')) {
                const feedback = document.createElement('span');
                feedback.className = 'status-feedback';
                feedback.textContent = `Статус изменен на: ${statusText}`;
                feedback.style.marginLeft = '10px';
                feedback.style.fontSize = '0.8rem';
                feedback.style.opacity = '0.8';
                this.parentNode.insertBefore(feedback, this.nextSibling);
                
                setTimeout(() => {
                    feedback.style.opacity = '0';
                    setTimeout(() => feedback.remove(), 300);
                }, 2000);
            }
        });
    }

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
        initWeather(); // Инициализация погоды
        
        // Установка интервалов обновления
        setInterval(updateNotifications, 600000); // Каждые 10 минут
        setInterval(() => fetchWeather(cityInput.value || loadCityFromLocalStorage()), 3600000); // Каждый час
        
        // Имитация активности сообщества
        setInterval(() => {
            const activeCount = Math.floor(Math.random() * 5) + 1;
            document.querySelector('.dashboard-card:nth-child(2) p').textContent = 
                `В вашем кругу 12 райдеров. ${activeCount} из них активны прямо сейчас.`;
        }, 10000);
    }
    init()
});