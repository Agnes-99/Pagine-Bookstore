

//---------------------------------------------------------------Search----------------------------------------------------------------
 
 document.getElementById('search-bar').addEventListener('input', function () {
    let query = this.value.trim();
    if (query) {
        search(query);
    } else {
        clearResults();
    }
});

document.getElementById('search-bar').addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        console.log('Enter pressed');
        let query = this.value.trim();
        console.log('Query:', query);
        if (query) {
            search(query);
        }
    }
});

document.querySelector('.fa-search').addEventListener('click', function () {
    let query = document.getElementById('search-bar').value.trim();
    if (query) {
        search(query);
    }
});

function search(query) {
    console.log(`Searching for: ${query}`);
    fetch(`/search?query=${encodeURIComponent(query)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Search results:', data.results);
            displayResults(data.results);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function displayResults(results) {
    let resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = ''; // Clear previous results
    if (results.length > 0) {
        let ul = document.createElement('ul');
        results.forEach(result => {
            let li = document.createElement('li');

            let link = document.createElement('a');
            link.href = `/book/${result[0]}`;
            link.style.textDecoration ='none';
            link.style.color ='inherit';

            let img = document.createElement('img');
            img.src = result.cover_img_url || result[3];
            img.alt = result.title || result[1];
            img.style.width = '100px';

            let title = document.createElement('p');
            title.textContent = `${result.title || result[1]} by ${result.author || result[2]}`;

            link.appendChild(img);
            link.appendChild(title);
            li.appendChild(link);
            ul.appendChild(li);
        });
        resultsDiv.appendChild(ul);
        resultsDiv.classList.add('active');
    } else {
        resultsDiv.classList.remove('active');
    }
}

function clearResults() {
    document.getElementById('search-results').innerHTML = '';
}

//----------------------------------------------------------Book-------------------------------------------

function loadBookDetails(bookId) {
    fetch(`/book/${bookId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Book not found');
            }
            return response.json();
        })
        .then(data => {
            // Populate book details
            document.getElementById('book-cover').src = data.cover_img_url;
            document.getElementById('book-title').textContent = data.title;
            document.getElementById('book-genre span').textContent = data.genre;
            document.getElementById('book-author').textContent = `By ${data.author}`;
            document.getElementById('book-isbn span').textContent = data.isbn;
            document.getElementById('book-price span').textContent = data.price.toFixed(2);
            document.getElementById('book-stock span').textContent = data.stock_quantity;
            document.getElementById('book-description-text').textContent = data.description;
        })
        .catch(error => {
            console.error('Error loading book details:', error);
            alert('Book not found');
        });
}
