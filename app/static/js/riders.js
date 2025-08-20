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

function subscribe(userId) {
    fetch(`/community/subscribe/${userId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token() }}',
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    });
}

function unsubscribe(userId) {
    fetch(`/community/unsubscribe/${userId}`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token() }}',
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message);
        }
    });
}