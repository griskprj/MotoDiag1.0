// Анимация уведомлений
document.querySelector('.notifications').addEventListener('click', function() {
    alert('У вас 3 новых уведомления');
});

// Имитация данных о погоде
function updateWeather() {
    const weatherConditions = [
        { temp: "+18°C", desc: "солнечно", advice: "Идеальная погода для поездки" },
        { temp: "+12°C", desc: "облачно", advice: "Возьмите ветровку" },
        { temp: "+22°C", desc: "ясно", advice: "Отличный день для длинной поездки" },
        { temp: "+8°C", desc: "дождь", advice: "Будьте осторожны на дороге" }
    ];
    
    const randomWeather = weatherConditions[Math.floor(Math.random() * weatherConditions.length)];
    const weatherIcon = document.querySelector('.weather-icon svg');
    
    // Простая смена иконки в зависимости от погоды
    if (randomWeather.desc.includes("дождь")) {
        weatherIcon.innerHTML = `
            <path d="M16 13v8"></path>
            <path d="M8 13v8"></path>
            <path d="M12 15v8"></path>
            <path d="M20 16.58A5 5 0 0 0 18 7h-1.26A8 8 0 1 0 4 15.25"></path>
        `;
    } else if (randomWeather.desc.includes("облачно")) {
        weatherIcon.innerHTML = `
            <path d="M17.5 15.5a6.5 6.5 0 1 0-13 0"></path>
            <path d="M8 15a6 6 0 0 0-6 6"></path>
            <path d="M20 15a6 6 0 0 0-6 6"></path>
            <path d="M10 12a6 6 0 0 0-6-6h-.5a5 5 0 0 1 5-5"></path>
            <path d="M14 12a6 6 0 0 0 6-6h-.5a5 5 0 0 1 5-5"></path>
        `;
    } else {
        weatherIcon.innerHTML = `
            <circle cx="12" cy="12" r="4"></circle>
            <path d="M12 2v2"></path>
            <path d="M12 20v2"></path>
            <path d="m4.93 4.93 1.41 1.41"></path>
            <path d="m17.66 17.66 1.41 1.41"></path>
            <path d="M2 12h2"></path>
            <path d="M20 12h2"></path>
            <path d="m6.34 17.66-1.41 1.41"></path>
            <path d="m19.07 4.93-1.41 1.41"></path>
        `;
    }
    
    const weatherInfo = document.querySelector('.weather-info');
    weatherInfo.querySelector('p:first-child').textContent = `${randomWeather.temp}, ${randomWeather.desc}`;
    weatherInfo.querySelector('p:last-child').textContent = randomWeather.advice;
}

// Обновляем погоду каждые 10 секунд для демонстрации
setInterval(updateWeather, 10000);

// Имитация активности сообщества
function updateCommunityStatus() {
    const activeCount = Math.floor(Math.random() * 5) + 1;
    document.querySelector('.dashboard-card:nth-child(3) p').textContent = 
        `В вашем кругу 12 райдеров. ${activeCount} из них активны прямо сейчас.`;
}

setInterval(updateCommunityStatus, 5000);

// Обработчики для кнопок
document.querySelectorAll('.event-btn, .community-btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        e.preventDefault();
        alert('Функция в разработке');
    });
});