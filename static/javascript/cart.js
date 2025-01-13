document.addEventListener('DOMContentLoaded', () => {
    const totalItemsEl = document.querySelector('#total-items');
    const totalPriceEl = document.querySelector('#total-price');

    // Event listener for "Remove" buttons
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function (e) {
            e.preventDefault();

            const bookId = this.closest('.cart-item').querySelector('input[name="book_id"]').value;
            console.log("bookId: ", bookId);

            fetch('/remove_from_cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ 'book_id': bookId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    this.closest('.cart-item').remove();
                    updateCartSummary(data);
                } else {
                    alert('Error removing item');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
        });
    });

    // Event listener for quantity changes
    document.querySelectorAll('.item-quantity').forEach(input => {
        input.addEventListener('change', function () {
            const cartId = this.closest('.cart-item').dataset.cartId;
            let quantity = this.value;

            if (quantity <= 0) {
                alert('Quantity must be at least 1');
                this.value = 1;
                return;
            }

            fetch('/update_cart', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: new URLSearchParams({ 'cart_id': cartId, 'quantity': quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    updateCartSummary(data);
                    this.closest('.cart-item').querySelector('.item-details p').textContent = `Price: R${data.item_total_price}`;
                } else {
                    alert('Error updating item quantity');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Something went wrong. Please try again.');
            });
        });
    });

    // Update cart summary
    function updateCartSummary(data) {
    console.log('Cart summary data:', data);
    const totalItemsEl = document.querySelector('#total-items');
    const totalPriceEl = document.querySelector('#total-price');

    if (data.total_items !== undefined && data.total_price !== undefined) {
        totalItemsEl.textContent = data.total_items ; // Default to 0
        totalPriceEl.textContent = `${data.total_price}`; // Default to R0
    } else {
        console.error('Missing total_items or total_price in response:', data);
    }
}


    // Checkout functionality
    document.querySelector('.checkout-button').addEventListener('click', () => {
        const customerId = document.querySelector('meta[name="customer-id"]').getAttribute('content');
        fetch('/place_order', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ 'customer_id': customerId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`Order placed successfully! Order ID: ${data.order_id}`);
                window.location.href = `/orders/${customerId}`;
            } else {
                alert('Error placing order');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Something went wrong. Please try again.');
        });
    });
});
