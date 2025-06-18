// Mobile Navigation
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('nav ul');

hamburger.addEventListener('click', () => {
    hamburger.classList.toggle('active');
    navLinks.classList.toggle('active');
});

// Close mobile menu when clicking a link
document.querySelectorAll('nav ul li a').forEach(link => {
    link.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navLinks.classList.remove('active');
    });
});

// Horizontal Scrolling for News Cards
const scrollContainer = document.querySelector('.news-cards');
const scrollLeftBtn = document.querySelector('.scroll-button.left');
const scrollRightBtn = document.querySelector('.scroll-button.right');

scrollLeftBtn.addEventListener('click', () => {
    scrollContainer.scrollBy({
        left: -300,
        behavior: 'smooth'
    });
});

scrollRightBtn.addEventListener('click', () => {
    scrollContainer.scrollBy({
        left: 300,
        behavior: 'smooth'
    });
});

// Show/hide scroll buttons based on scroll position
scrollContainer.addEventListener('scroll', () => {
    const maxScrollLeft = scrollContainer.scrollWidth - scrollContainer.clientWidth;
    
    if (scrollContainer.scrollLeft > 0) {
        scrollLeftBtn.style.display = 'flex';
    } else {
        scrollLeftBtn.style.display = 'none';
    }
    
    if (scrollContainer.scrollLeft < maxScrollLeft) {
        scrollRightBtn.style.display = 'flex';
    } else {
        scrollRightBtn.style.display = 'none';
    }
});

// Initialize scroll buttons
scrollLeftBtn.style.display = 'none';
if (scrollContainer.scrollWidth <= scrollContainer.clientWidth) {
    scrollRightBtn.style.display = 'none';
}

// Subscribe Form Submission
const subscribeForm = document.querySelector('.subscribe-form');
subscribeForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const emailInput = subscribeForm.querySelector('input[type="email"]');
    const email = emailInput.value;
    
    if (email) {
        alert(`Thank you for subscribing with ${email}! You'll receive our latest news updates.`);
        emailInput.value = '';
    }
});

// Set active page in navigation
const currentPage = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('nav ul li a').forEach(link => {
    const linkPage = link.getAttribute('href');
    if (currentPage === linkPage) {
        link.classList.add('active');
    } else {
        link.classList.remove('active');
    }
});