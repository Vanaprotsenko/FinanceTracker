const API_URL = ''; // Same origin as the static files when served from FastAPI

// State management
const state = {
    token: localStorage.getItem('token'),
    view: 'dashboard',
    records: [],
    tg: window.Telegram ? window.Telegram.WebApp : null
};

if (state.tg) {
    state.tg.expand();
}

// DOM Elements
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const statsSection = document.getElementById('stats-section');
const mainNav = document.getElementById('main-nav');
const loginFormContainer = document.getElementById('login-form-container');
const signupFormContainer = document.getElementById('signup-form-container');
const recordsBody = document.getElementById('records-body');
const recordModal = document.getElementById('record-modal');
const recordForm = document.getElementById('record-form');
const toastContainer = document.getElementById('toast-container');

// View management
function showView(viewName) {
    state.view = viewName;
    document.querySelectorAll('.view').forEach(v => v.classList.add('hidden'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    if (viewName === 'dashboard') {
        dashboardSection.classList.remove('hidden');
        document.querySelector('[data-view="dashboard"]').classList.add('active');
        loadRecords();
    } else if (viewName === 'stats') {
        statsSection.classList.remove('hidden');
        document.querySelector('[data-view="stats"]').classList.add('active');
        updateStats();
    }
}

function updateAuthState() {
    if (state.token) {
        authSection.classList.add('hidden');
        mainNav.classList.remove('hidden');
        showView('dashboard');
    } else {
        authSection.classList.remove('hidden');
        mainNav.classList.add('hidden');
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// API Calls
async function apiFetch(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...(state.token ? { 'Authorization': `Bearer ${state.token}` } : {})
    };

    try {
        const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
        if (response.status === 401) {
            logout();
            throw new Error('Unauthorized');
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }
        return response.status !== 204 ? await response.json() : null;
    } catch (error) {
        showToast(error.message, 'danger');
        throw error;
    }
}

// Auth Handlers
document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const body = { email, password };
        if (state.tg && state.tg.initData) {
            body.init_data = state.tg.initData;
        }

        const data = await apiFetch('/auth/login', {
            method: 'POST',
            body: JSON.stringify(body)
        });
        state.token = data.access_token;
        localStorage.setItem('token', state.token);
        showToast('Logged in successfully', 'success');

        if (state.tg && state.tg.initData) {
            // Close after a short delay so they see the toast
            setTimeout(() => state.tg.close(), 1500);
        } else {
            updateAuthState();
        }
    } catch (error) { }
});

document.getElementById('signup-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;

    try {
        const body = { name, email };
        if (state.tg && state.tg.initData) {
            body.init_data = state.tg.initData;
        }

        await apiFetch(`/auth/signup?password=${encodeURIComponent(password)}`, {
            method: 'POST',
            body: JSON.stringify(body)
        });
        showToast('Account created! Linking Telegram...', 'success');

        if (state.tg && state.tg.initData) {
            // Close after a short delay so they see the toast
            setTimeout(() => state.tg.close(), 1500);
        } else {
            toggleAuthMode();
        }
    } catch (error) { }
});

function logout() {
    state.token = null;
    localStorage.removeItem('token');
    updateAuthState();
}

document.getElementById('logout-btn').addEventListener('click', logout);

// View Switchers
document.getElementById('switch-to-signup').addEventListener('click', toggleAuthMode);
document.getElementById('switch-to-login').addEventListener('click', toggleAuthMode);

function toggleAuthMode() {
    loginFormContainer.classList.toggle('hidden');
    signupFormContainer.classList.toggle('hidden');
    const title = document.getElementById('auth-title');
    const sub = document.getElementById('auth-subtitle');
    if (loginFormContainer.classList.contains('hidden')) {
        title.textContent = 'Join Us';
        sub.textContent = 'Create an account to start tracking';
    } else {
        title.textContent = 'Welcome Back';
        sub.textContent = 'Login to track your finances';
    }
}

document.querySelectorAll('.nav-btn[data-view]').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
});

// Record Handlers
async function loadRecords() {
    try {
        const records = await apiFetch('/records/');
        state.records = records;
        renderRecords();
    } catch (error) { }
}

function renderRecords() {
    recordsBody.innerHTML = '';
    if (state.records.length === 0) {
        document.getElementById('no-records').classList.remove('hidden');
        return;
    }
    document.getElementById('no-records').classList.add('hidden');

    state.records.forEach(record => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${new Date().toLocaleDateString()}</td>
            <td>${record.description}</td>
            <td><span class="record-type-badge type-${record.type}">${record.type}</span></td>
            <td>${record.amount.toFixed(2)}</td>
            <td>${record.currency}</td>
            <td class="actions-btns">
                <button class="icon-btn edit-btn" onclick="editRecord('${record.id}')">✎</button>
                <button class="icon-btn delete-btn" onclick="deleteRecord('${record.id}')">🗑</button>
            </td>
        `;
        recordsBody.appendChild(tr);
    });
}

// Modal Handlers
document.getElementById('add-record-btn').addEventListener('click', () => {
    document.getElementById('modal-title').textContent = 'Add New Record';
    recordForm.reset();
    document.getElementById('record-id').value = '';
    recordModal.classList.remove('hidden');
});

document.querySelector('.close-modal').addEventListener('click', () => {
    recordModal.classList.add('hidden');
});

recordForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('record-id').value;
    const data = {
        description: document.getElementById('record-description').value,
        amount: parseFloat(document.getElementById('record-amount').value),
        currency: document.getElementById('record-currency').value,
        type: document.getElementById('record-type').value
    };

    try {
        if (id) {
            // Update - Backend expects amount, type, description, currency as params? 
            // Router: async def update_record(record_id: uuid.UUID, amount: float, type: str, description: str, currency: str, ...)
            // These are query params.
            const params = new URLSearchParams(data).toString();
            await apiFetch(`/records/${id}?${params}`, { method: 'PATCH' });
            showToast('Record updated', 'success');
        } else {
            // Create
            await apiFetch('/records/', {
                method: 'POST',
                body: JSON.stringify(data)
            });
            showToast('Record added', 'success');
        }
        recordModal.classList.add('hidden');
        loadRecords();
    } catch (error) { }
});

async function deleteRecord(id) {
    if (confirm('Are you sure you want to delete this record?')) {
        try {
            await apiFetch(`/records/${id}`, { method: 'DELETE' });
            showToast('Record deleted', 'success');
            loadRecords();
        } catch (error) { }
    }
}

window.editRecord = (id) => {
    const record = state.records.find(r => r.id === id);
    if (!record) return;

    document.getElementById('modal-title').textContent = 'Edit Record';
    document.getElementById('record-id').value = record.id;
    document.getElementById('record-description').value = record.description;
    document.getElementById('record-amount').value = record.amount;
    document.getElementById('record-currency').value = record.currency;
    document.getElementById('record-type').value = record.type;

    recordModal.classList.remove('hidden');
};

// Statistics
let statsChart = null;

function updateStats() {
    const income = state.records
        .filter(r => r.type === 'income')
        .reduce((sum, r) => sum + r.amount, 0);
    const expense = state.records
        .filter(r => r.type === 'expense')
        .reduce((sum, r) => sum + r.amount, 0);

    document.getElementById('total-income').textContent = `$${income.toFixed(2)}`;
    document.getElementById('total-expense').textContent = `$${expense.toFixed(2)}`;
    document.getElementById('net-balance').textContent = `$${(income - expense).toFixed(2)}`;

    const ctx = document.getElementById('incomeExpenseChart').getContext('2d');

    if (statsChart) {
        statsChart.destroy();
    }

    statsChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Income', 'Expenses'],
            datasets: [{
                data: [income, expense],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94a3b8' }
                }
            },
            cutout: '70%'
        }
    });
}

// Init
async function initApp() {
    if (state.tg && state.tg.initData && !state.token) {
        try {
            const data = await apiFetch('/auth/telegram/login', {
                method: 'POST',
                // Endpoint expects init_data as query param or body? 
                // Router says: def telegram_login(init_data: str, ...) -> This is a query param by default in FastAPI if not typed as Pydantic model
                // Wait, it should be query param. Let's check router again.
                body: JSON.stringify({ init_data: state.tg.initData })
            });
            if (data && data.access_token) {
                state.token = data.access_token;
                localStorage.setItem('token', state.token);
                state.tg.close();
                return;
            }
        } catch (error) {
            console.log("Auto-login failed:", error);
        }
    }

    updateAuthState();
    if (state.token) {
        loadRecords();
    }
}

initApp();
