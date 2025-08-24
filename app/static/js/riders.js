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

// Функции подписки/отписки
async function subscribe(userId) {
    try {
        const response = await fetch(`/community/subscribe/${userId}`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            }
        });
        
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
    const metaToken = document.querySelector('meta[name="csrf-token"]');
    return metaToken ? metaToken.getAttribute('content') : '';
}

function updateSubscriptionUI(userId, isSubscribed, subscribersCount) {
    const card = document.querySelector(`.rider-card[data-user-id="${userId}"]`);
    if (!card) return;
    
    const button = card.querySelector(`button[onclick*="${userId}"]`);
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
    
    // Обновляем счетчик подписчиков
    if (subscribersCount !== undefined) {
        const subscriberElement = card.querySelector('.subscribers-count');
        if (subscriberElement) {
            subscriberElement.textContent = subscribersCount;
        }
    }
}

function showError(message) {
    alert(message);
}

// Фильтрация и сортировка
document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('filter-select');
    const sortSelect = document.getElementById('sort-select');
    
    if (filterSelect) filterSelect.addEventListener('change', filterRiders);
    if (sortSelect) sortSelect.addEventListener('change', sortRiders);
});

function filterRiders() {
    const filterValue = document.getElementById('filter-select').value;
    const riderCards = document.querySelectorAll('.rider-card');
    
    riderCards.forEach(card => {
        if (filterValue === 'all') {
            card.style.display = 'block';
        } else if (filterValue === 'subscribed') {
            // Проверяем, есть ли кнопка отписки (значит пользователь подписан)
            const unsubscribeBtn = card.querySelector('button.btn-secondary');
            card.style.display = unsubscribeBtn ? 'block' : 'none';
        }
    });
}

function sortRiders() {
    const sortValue = document.getElementById('sort-select').value;
    const ridersContainer = document.querySelector('.riders-grid');
    const riderCards = Array.from(ridersContainer.querySelectorAll('.rider-card'));
    
    riderCards.sort((a, b) => {
        const aDate = new Date(a.dataset.joinDate);
        const bDate = new Date(b.dataset.joinDate);
        const aMotos = parseInt(a.dataset.motoCount) || 0;
        const bMotos = parseInt(b.dataset.motoCount) || 0;
        const aMileage = parseInt(a.dataset.mileage) || 0;
        const bMileage = parseInt(b.dataset.mileage) || 0;
        
        switch(sortValue) {
            case 'newest':
                return bDate - aDate; // Новые сначала
            case 'oldest':
                return aDate - bDate; // Старые сначала
            case 'most_motos':
                return bMotos - aMotos; // Больше мотоциклов
            case 'most_mileage':
                return bMileage - aMileage; // Больше пробега
            default:
                return 0;
        }
    });
    
    // Очищаем контейнер и добавляем отсортированные карточки
    ridersContainer.innerHTML = '';
    riderCards.forEach(card => ridersContainer.appendChild(card));
}
