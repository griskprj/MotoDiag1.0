// Поиск райдеров
document.getElementById('rider-search').addEventListener('input', function() {
    const searchTerm = this.value.toLowerCase();
    const riderCards = document.querySelectorAll('.rider-card');
    
    riderCards.forEach(card => {
        const username = card.querySelector('h3').textContent.toLowerCase();
        if (username.includes(searchTerm)) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
});

// Функции подписки/отписки с улучшенной обработкой ошибок
async function subscribe(userId) {
    try {
        const response = await fetch(`/community/subscribe/${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        });
        
        // Проверяем тип ответа
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Сервер вернул не JSON ответ');
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateSubscriptionUI(userId, true, data.subscribers_count);
        } else {
            showError(data.message || 'Ошибка при подписке');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Произошла ошибка при выполнении запроса');
    }
}

async function unsubscribe(userId) {
    try {
        const response = await fetch(`/community/unsubscribe/${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        });
        
        // Проверяем тип ответа
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            throw new Error('Сервер вернул не JSON ответ');
        }
        
        const data = await response.json();
        
        if (data.success) {
            updateSubscriptionUI(userId, false, data.subscribers_count);
        } else {
            showError(data.message || 'Ошибка при отписке');
        }
    } catch (error) {
        console.error('Error:', error);
        showError('Произошла ошибка при выполнении запроса');
    }
}

// Вспомогательные функции
function getCSRFToken() {
    // Попробуем найти CSRF токен в мета-тегах
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    if (metaToken) {
        return metaToken.getAttribute('content');
    }
    
    // Или в форме
    const formToken = document.querySelector('input[name="csrf_token"]');
    if (formToken) {
        return formToken.value;
    }
    
    console.warn('CSRF token not found');
    return '';
}

function updateSubscriptionUI(userId, isSubscribed, subscribersCount) {
    const button = document.querySelector(`button[onclick*="${userId}"]`);
    if (!button) return;
    
    if (isSubscribed) {
        button.textContent = 'Отписаться';
        button.setAttribute('onclick', `unsubscribe(${userId})`);
        button.classList.remove('btn-primary');
        button.classList.add('btn-secondary');
    } else {
        button.textContent = 'Подписаться';
        button.setAttribute('onclick', `subscribe(${userId})`);
        button.classList.remove('btn-secondary');
        button.classList.add('btn-primary');
    }
    
    // Обновляем счетчик подписчиков если передан
    if (subscribersCount !== undefined) {
        const subscriberElement = document.querySelector(`.rider-card[data-user-id="${userId}"] .subscribers-count`);
        if (subscriberElement) {
            subscriberElement.textContent = subscribersCount;
        }
    }
    window.location.reload()
}

function showError(message) {
    // Простое уведомление об ошибке
    alert(message);
}

// Фильтрация и сортировка (клиентская сторона)
document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('filter-select');
    const sortSelect = document.getElementById('sort-select');
    
    if (filterSelect) {
        filterSelect.addEventListener('change', filterRiders);
    }
    
    if (sortSelect) {
        sortSelect.addEventListener('change', sortRiders);
    }
    
    // Инициализация данных для карточек
    initRiderCards();
});

function filterRiders() {
    const filterValue = document.getElementById('filter-select').value;
    const riderCards = document.querySelectorAll('.rider-card');
    
    riderCards.forEach(card => {
        if (filterValue === 'all') {
            card.style.display = 'block';
        } else if (filterValue === 'subscribed') {
            // Простая клиентская фильтрация по подпискам
            const subscribeBtn = card.querySelector('.btn-secondary');
            card.style.display = subscribeBtn ? 'block' : 'none';
        }
    });
}

function sortRiders() {
    const sortValue = document.getElementById('sort-select').value;
    const ridersContainer = document.querySelector('.riders-grid');
    const riderCards = Array.from(ridersContainer.querySelectorAll('.rider-card'));
    
    riderCards.sort((a, b) => {
        switch(sortValue) {
            case 'newest':
                return new Date(b.dataset.joinDate) - new Date(a.dataset.joinDate);
            case 'oldest':
                return new Date(a.dataset.joinDate) - new Date(b.dataset.joinDate);
            case 'most_motos':
                return parseInt(b.dataset.motoCount) - parseInt(a.dataset.motoCount);
            case 'most_mileage':
                return parseInt(b.dataset.mileage) - parseInt(a.dataset.mileage);
            default:
                return 0;
        }
    });
    
    // Очищаем контейнер и добавляем отсортированные карточки
    ridersContainer.innerHTML = '';
    riderCards.forEach(card => ridersContainer.appendChild(card));
}

function initRiderCards() {
    document.querySelectorAll('.rider-card').forEach(card => {
        // Извлекаем данные из текста для сортировки
        const joinDateText = card.querySelector('.rider-stats strong:last-child')?.textContent;
        const motoCountText = card.querySelector('.rider-info p')?.textContent;
        const mileageText = card.querySelector('.rider-stats strong:first-child')?.textContent;
        
        // Преобразуем в значения для сортировки
        card.dataset.joinDate = parseJoinDate(joinDateText);
        card.dataset.motoCount = parseMotoCount(motoCountText);
        card.dataset.mileage = parseMileage(mileageText);
    });
}

// Вспомогательные функции для парсинга данных
function parseJoinDate(text) {
    if (!text) return new Date();
    
    // Простой парсинг относительных дат
    const now = new Date();
    if (text.includes('день') || text.includes('дня') || text.includes('дней')) {
        const days = parseInt(text) || 0;
        return new Date(now.setDate(now.getDate() - days));
    }
    return new Date();
}

function parseMotoCount(text) {
    return parseInt(text) || 0;
}

function parseMileage(text) {
    if (!text) return 0;
    return parseInt(text.replace(/\sкм/g, '').replace(/\s/g, '')) || 0;
}