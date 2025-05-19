document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const loginPage = document.getElementById('login-page');
    const dashboard = document.getElementById('dashboard');
    const loginForm = document.getElementById('login-form');
    const notificationBell = document.getElementById('notification-bell');
    const notificationCount = document.getElementById('notification-count');
    const profileToggle = document.getElementById('profile-toggle');
    const profileDropdown = document.getElementById('profile-dropdown');
    const logoutButton = document.getElementById('logout');
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const navLinks = document.querySelectorAll('.nav-link');
    const pages = document.querySelectorAll('.page');

    // Authentication
    const defaultCredentials = { username: 'admin', password: 'admin' };
    let isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';

    const showLoginPage = () => {
        loginPage.classList.remove('hidden');
        dashboard.classList.add('hidden');
    };

    const showDashboard = () => {
        loginPage.classList.add('hidden');
        dashboard.classList.remove('hidden');
    };

    if (!isLoggedIn) {
        showLoginPage();
    } else {
        showDashboard();
    }

    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        if (username === defaultCredentials.username && password === defaultCredentials.password) {
            localStorage.setItem('isLoggedIn', 'true');
            isLoggedIn = true;
            showDashboard();
        } else {
            alert('Invalid credentials');
        }
    });

    logoutButton.addEventListener('click', () => {
        localStorage.removeItem('isLoggedIn');
        isLoggedIn = false;
        showLoginPage();
    });

    // Sidebar Toggle
    sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });

    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }

    // Navigation
    const showPage = (pageId) => {
        pages.forEach(page => {
            page.classList.add('hidden');
            if (page.id === pageId) {
                page.classList.remove('hidden');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${pageId}`) {
                link.classList.add('active');
            }
        });
    };

    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const pageId = link.getAttribute('href').substring(1);
            showPage(pageId);
            if (window.innerWidth < 768) {
                sidebar.classList.add('collapsed');
            }
        });
    });

    // Show home page by default
    showPage('home');

    // Notification Simulation
    let alertCount = 0;
    const updateNotifications = () => {
        alertCount += Math.floor(Math.random() * 3);
        notificationCount.textContent = alertCount;
    };
    setInterval(updateNotifications, 10000);
    updateNotifications();

    // Profile Dropdown
    profileToggle.addEventListener('click', () => {
        profileDropdown.classList.toggle('hidden');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!profileToggle.contains(e.target) && !profileDropdown.contains(e.target)) {
            profileDropdown.classList.add('hidden');
        }
    });

    // Dark Mode Toggle
    const isDarkMode = localStorage.getItem('darkMode') === 'true';
    if (isDarkMode) {
        document.documentElement.classList.add('dark');
    }

    darkModeToggle.addEventListener('click', () => {
        document.documentElement.classList.toggle('dark');
        localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
    });
});