console.log('=== RIDERS JS LOADED ===');

// Поиск райдеров
function initSearch() {
    const searchInput = document.getElementById('rider-search');
    if (searchInput) {
        console.log('Search input found');
        searchInput.addEventListener('input', function() {
            console.log('Search input:', this.value);
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
    } else {
        console.log('Search input NOT found');
    }
}

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

// ОСНОВНАЯ ЛОГИКА ФИЛЬТРАЦИИ И СОРТИРОВКИ
function initFilters() {
    console.log('Initializing filters...');
    
    const filterSelect = document.getElementById('filter-select');
    const sortSelect = document.getElementById('sort-select');
    
    if (filterSelect) {
        console.log('✓ Filter select found');
        filterSelect.addEventListener('change', function() {
            console.log('🔹 Filter changed to:', this.value);
            applyFiltersAndSorting();
        });
    } else {
        console.log('✗ Filter select NOT found');
    }
    
    if (sortSelect) {
        console.log('✓ Sort select found');
        sortSelect.addEventListener('change', function() {
            console.log('🔹 Sort changed to:', this.value);
            applyFiltersAndSorting();
        });
    } else {
        console.log('✗ Sort select NOT found');
    }
}

function initRiderCardsData() {
    console.log('Initializing rider cards data...');
    const riderCards = document.querySelectorAll('.rider-card');
    console.log('Found', riderCards.length, 'rider cards');
    
    riderCards.forEach((card, index) => {
        const joinDate = card.dataset.joinDate;
        const motoCount = card.dataset.motoCount;
        const mileage = card.dataset.mileage;
        
        // Проверяем и корректируем данные
        if (!motoCount && motoCount !== '0') {
            const motoText = card.querySelector('.rider-info p')?.textContent;
            if (motoText) {
                const count = parseInt(motoText.replace(/\D/g, '')) || 0;
                card.dataset.motoCount = count;
            }
        }
        
        if (!mileage && mileage !== '0') {
            const mileageText = card.querySelector('.rider-stats strong:first-child')?.textContent;
            if (mileageText) {
                const mileageValue = parseInt(mileageText.replace(/\D/g, '')) || 0;
                card.dataset.mileage = mileageValue;
            }
        }
        
        console.log(`Card ${index}:`, {
            motoCount: card.dataset.motoCount,
            mileage: card.dataset.mileage,
            joinDate: card.dataset.joinDate
        });
    });
}

function applyFiltersAndSorting() {
    console.log('=== APPLYING FILTERS AND SORTING ===');
    filterRiders();
    sortRiders();
}

function filterRiders() {
    const filterValue = document.getElementById('filter-select')?.value;
    if (!filterValue) {
        console.log('No filter value found');
        return;
    }
    
    console.log('Filtering with value:', filterValue);
    const riderCards = document.querySelectorAll('.rider-card');
    
    riderCards.forEach(card => {
        if (filterValue === 'all') {
            card.style.display = 'block';
        } else if (filterValue === 'subscribed') {
            const unsubscribeBtn = card.querySelector('button.btn-secondary');
            card.style.display = unsubscribeBtn ? 'block' : 'none';
        }
    });
}

function sortRiders() {
    const sortValue = document.getElementById('sort-select')?.value;
    if (!sortValue) {
        console.log('No sort value found');
        return;
    }
    
    console.log('Sorting by:', sortValue);
    const ridersContainer = document.querySelector('.riders-grid');
    if (!ridersContainer) {
        console.log('Riders container not found');
        return;
    }
    
    const riderCards = Array.from(ridersContainer.querySelectorAll('.rider-card[style*="display: block"], .rider-card:not([style])'));
    console.log('Visible cards to sort:', riderCards.length);
    
    if (riderCards.length === 0) {
        console.log('No visible cards to sort');
        return;
    }
    
    riderCards.sort((a, b) => {
        const aDate = new Date(a.dataset.joinDate || 0);
        const bDate = new Date(b.dataset.joinDate || 0);
        const aMotos = parseInt(a.dataset.motoCount) || 0;
        const bMotos = parseInt(b.dataset.motoCount) || 0;
        const aMileage = parseInt(a.dataset.mileage) || 0;
        const bMileage = parseInt(b.dataset.mileage) || 0;
        
        switch(sortValue) {
            case 'newest':
                return bDate - aDate;
            case 'oldest':
                return aDate - bDate;
            case 'most_motos':
                return bMotos - aMotos;
            case 'most_mileage':
                return bMileage - aMileage;
            default:
                return 0;
        }
    });
    
    // Сохраняем текущий scroll position
    const scrollTop = ridersContainer.scrollTop;
    
    // Переставляем карточки
    ridersContainer.innerHTML = '';
    riderCards.forEach(card => {
        ridersContainer.appendChild(card);
    });
    
    // Восстанавливаем scroll position
    ridersContainer.scrollTop = scrollTop;
    
    console.log('✓ Sorting completed');
}

// Глобальная функция для ручного вызова
window.testSorting = function() {
    console.log('=== MANUAL SORTING TEST ===');
    applyFiltersAndSorting();
};

// Основная инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== DOM CONTENT LOADED ===');
    
    initSearch();
    initFilters();
    initRiderCardsData();
    
    // Добавляем кнопку для тестирования
    addTestButton();
});

function addTestButton() {
    const filtersSection = document.querySelector('.filters');
    if (filtersSection && !document.getElementById('test-sort-btn')) {
        const testBtn = document.createElement('button');
        testBtn.id = 'test-sort-btn';
        testBtn.textContent = 'Тест сортировки';
        testBtn.style.marginLeft = '10px';
        testBtn.style.padding = '8px 12px';
        testBtn.style.background = '#7D3CFF';
        testBtn.style.color = 'white';
        testBtn.style.border = 'none';
        testBtn.style.borderRadius = '4px';
        testBtn.style.cursor = 'pointer';
        testBtn.onclick = testSorting;
        
        filtersSection.appendChild(testBtn);
        console.log('✓ Test button added');
    }
}

// Fallback для случаев, когда DOM уже загружен
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAll);
} else {
    setTimeout(initAll, 100);
}

function initAll() {
    console.log('=== INIT ALL ===');
    initSearch();
    initFilters();
    initRiderCardsData();
    addTestButton();
}