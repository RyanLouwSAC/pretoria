document.getElementById('search-bar').addEventListener('input', function() {
    const query = this.value.toLowerCase();
    const categoryGrid = document.getElementById('category-grid');
    const businessGrid = document.getElementById('business-grid');
    
    if (query) {
        categoryGrid.style.display = 'none'; // Hide category cards
        const businesses = document.querySelectorAll('.business-card');
        let found = false;

        businesses.forEach(function(business) {
            const businessName = business.querySelector('h3').innerText.toLowerCase();
            if (businessName.includes(query)) {
                business.style.display = 'block';
                found = true;
            } else {
                business.style.display = 'none';
            }
        });

        if (!found) {
            businessGrid.innerHTML = '<p>No businesses found matching your criteria.</p>';
        }
    } else {
        categoryGrid.style.display = 'block'; // Show category cards
        const businesses = document.querySelectorAll('.business-card');
        businesses.forEach(function(business) {
            business.style.display = 'block'; // Reset business display
        });
    }
});
