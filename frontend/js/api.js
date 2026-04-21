const API_BASE = window.location.origin;

function parseApiErrorDetail(detail, fallbackMessage) {
    if (!detail) return fallbackMessage;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        const messages = detail
            .map((item) => {
                if (typeof item === 'string') return item;
                if (item && typeof item === 'object') {
                    const path = Array.isArray(item.loc) ? item.loc.join('.') : '';
                    const msg = item.msg || JSON.stringify(item);
                    return path ? `${path}: ${msg}` : msg;
                }
                return String(item);
            })
            .filter(Boolean);
        return messages.length ? messages.join('; ') : fallbackMessage;
    }
    if (typeof detail === 'object') {
        if (typeof detail.msg === 'string') return detail.msg;
        try {
            return JSON.stringify(detail);
        } catch (_) {
            return fallbackMessage;
        }
    }
    return String(detail);
}

// ─── Token Management ───────────────────────────────────────────────
function saveToken(token) {
    localStorage.setItem('ft_token', token);
}

function getToken() {
    return localStorage.getItem('ft_token');
}

function clearToken() {
    localStorage.removeItem('ft_token');
}

function isLoggedIn() {
    return !!getToken();
}

function requireAuth() {
    if (!isLoggedIn()) {
        window.location.href = '/login.html';
    }
}

function logout() {
    clearToken();
    window.location.href = '/login.html';
}

// ─── Fetch Wrapper ──────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        clearToken();
        window.location.href = '/login.html';
        throw new Error('Unauthorized');
    }

    return response;
}

// ─── Auth Endpoints ─────────────────────────────────────────────────
async function apiSignup(email, name, password) {
    const resp = await apiFetch('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, name, password }),
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(parseApiErrorDetail(err.detail, 'Signup failed'));
    }
    return resp.json();
}

async function apiLogin(email, password) {
    const resp = await apiFetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(parseApiErrorDetail(err.detail, 'Login failed'));
    }
    return resp.json();
}

async function apiTelegramSignup(email, name, password, telegramId, telegramUsername) {
    const query = new URLSearchParams({
        telegram_id: String(telegramId),
        telegram_username: telegramUsername || '',
    });
    const resp = await apiFetch(`/auth/tg-signup?${query.toString()}`, {
        method: 'POST',
        body: JSON.stringify({ email, name, password }),
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(parseApiErrorDetail(err.detail, 'Telegram signup failed'));
    }
    return resp.json();
}

// ─── Records Endpoints ─────────────────────────────────────────────
async function apiGetRecords() {
    const resp = await apiFetch('/records/');
    if (!resp.ok) throw new Error('Failed to fetch records');
    return resp.json();
}

async function apiCreateRecord(data) {
    const resp = await apiFetch('/records/', {
        method: 'POST',
        body: JSON.stringify(data),
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to create record');
    }
    return resp.json();
}

async function apiDeleteRecord(recordId) {
    const resp = await apiFetch(`/records/${recordId}`, {
        method: 'DELETE',
    });
    if (!resp.ok) throw new Error('Failed to delete record');
    return true;
}

async function apiUpdateRecord(recordId, amount, description, currency, createdAt) {
    let path = `/records/${recordId}?amount=${amount}&description=${encodeURIComponent(description)}&currency=${encodeURIComponent(currency)}`;
    if (createdAt) path += `&created_at=${encodeURIComponent(createdAt)}`;
    const resp = await apiFetch(path, { method: 'PATCH' });
    if (!resp.ok) throw new Error('Failed to update record');
    return resp.json();
}

// ─── Categories Endpoints ──────────────────────────────────────────
async function apiGetCategories() {
    const resp = await apiFetch('/categories/');
    if (!resp.ok) throw new Error('Failed to fetch categories');
    return resp.json();
}

// ─── Mono Endpoints ─────────────────────────────────────────────────
async function apiMonoVerifyToken() {
    const resp = await apiFetch('/mono/verifytoken');
    return resp.ok;
}

async function apiMonoSaveToken(monoToken) {
    const resp = await apiFetch('/mono/savetoken', {
        method: 'POST',
        body: JSON.stringify({ mono_token: monoToken }),
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to save token');
    }
    return resp.json();
}

async function apiMonoSaveCards() {
    const resp = await apiFetch('/mono/save-mono-cards', {
        method: 'POST',
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to save cards');
    }
    return resp.json();
}

async function apiMonoGetCards() {
    const resp = await apiFetch('/mono/cards-info');
    if (!resp.ok) throw new Error('Failed to fetch cards');
    return resp.json();
}

async function apiMonoDeleteCard(cardId) {
    const resp = await apiFetch(`/mono/delete-mono-card?card_id=${encodeURIComponent(cardId)}`, {
        method: 'DELETE',
    });
    if (!resp.ok) throw new Error('Failed to delete card');
    return resp.json();
}

async function apiMonoSyncTransactions(cardId) {
    const resp = await apiFetch(`/mono/sync-transactions?card_id=${encodeURIComponent(cardId)}`, {
        method: 'POST',
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to sync transactions');
    }
    return resp.json();
}

async function apiMonoSaveTransaction(cardId) {
    const resp = await apiFetch(`/mono/save-transaction?card_id=${encodeURIComponent(cardId)}`, {
        method: 'POST',
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to save transaction');
    }
    return resp.json();
}

async function apiMonoGetTransactions(cardId) {
    const resp = await apiFetch(`/mono/get-transaction?card_id=${encodeURIComponent(cardId)}`);
    if (!resp.ok) throw new Error('Failed to fetch transactions');
    return resp.json();
}

async function apiMonoUpdateCardName(cardId, cardName) {
    const resp = await apiFetch(`/mono/update-card-name?card_id=${encodeURIComponent(cardId)}&card_name=${encodeURIComponent(cardName)}`, {
        method: 'POST',
    });
    if (!resp.ok) throw new Error('Failed to update card name');
    return resp.json();
}

async function apiMonoSync(cardId) {
    const resp = await apiFetch(`/mono/sync?card_id=${encodeURIComponent(cardId)}`, {
        method: 'POST',
    });
    if (!resp.ok) {
        const err = await resp.json();
        throw new Error(err.detail || 'Failed to sync card');
    }
    return resp.json();
}

const CURRENCY_MAP = {
    '980': { symbol: '₴', name: 'UAH' },
    '840': { symbol: '$', name: 'USD' },
    '978': { symbol: '€', name: 'EUR' },
    '826': { symbol: '£', name: 'GBP' },
    'UAH': { symbol: '₴', name: 'UAH' },
    'USD': { symbol: '$', name: 'USD' },
    'EUR': { symbol: '€', name: 'EUR' },
    'GBP': { symbol: '£', name: 'GBP' },
};

function getCurrencySymbol(code) {
    if (!code) return '₴';
    const c = CURRENCY_MAP[String(code).toUpperCase()];
    return c ? c.symbol : code;
}

function getCurrencyName(code) {
    if (!code) return 'UAH';
    const c = CURRENCY_MAP[String(code).toUpperCase()];
    return c ? c.name : String(code);
}

function formatAmount(amount, currencyCode) {
    const sym = getCurrencySymbol(currencyCode);
    const abs = Math.abs(amount).toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    return amount < 0 ? `-${sym}${abs}` : `+${sym}${abs}`;
}

// ─── Exchange Rates (frontend-only, free API) ───────────────────────
let _ratesCache = {};

async function fetchExchangeRates(baseCurrency) {
    const base = (baseCurrency || 'UAH').toUpperCase();
    if (_ratesCache[base]) return _ratesCache[base];
    try {
        const resp = await fetch(`https://open.er-api.com/v6/latest/${base}`);
        if (!resp.ok) throw new Error('Rates API error');
        const data = await resp.json();
        _ratesCache[base] = data.rates;
        return data.rates;
    } catch (err) {
        console.error('Failed to fetch exchange rates:', err);
        return null;
    }
}

function convertAmount(amount, fromCurrency, toCurrency, ratesFromTarget) {
    // ratesFromTarget: rates object where base = toCurrency
    // To convert FROM -> TO: amount / ratesFromTarget[FROM]
    const from = (fromCurrency || 'UAH').toUpperCase();
    const to = (toCurrency || 'UAH').toUpperCase();
    if (from === to) return amount;
    if (!ratesFromTarget || !ratesFromTarget[from]) return amount;
    return amount / ratesFromTarget[from];
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function formatTime(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
}

function timeAgo(dateStr) {
    const now = new Date();
    const d = new Date(dateStr);
    const diff = Math.floor((now - d) / 1000);
    if (diff < 60) return 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)} mins ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)} hours ago`;
    return formatDate(dateStr);
}

// Toast notification
function showToast(message, type = 'success') {
    const existing = document.getElementById('toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.id = 'toast-notification';
    toast.className = `fixed bottom-6 right-6 z-[100] px-6 py-4 rounded-2xl shadow-2xl text-sm font-bold flex items-center gap-3 transition-all duration-500 transform translate-y-4 opacity-0`;

    if (type === 'success') {
        toast.style.background = '#00322a';
        toast.style.color = '#68fadd';
    } else if (type === 'error') {
        toast.style.background = '#93000a';
        toast.style.color = '#ffdad6';
    } else {
        toast.style.background = '#002b5b';
        toast.style.color = '#d6e3ff';
    }

    const icon = type === 'success' ? 'check_circle' : type === 'error' ? 'error' : 'info';
    toast.innerHTML = `<span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">${icon}</span>${message}`;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateY(0)';
        toast.style.opacity = '1';
    });

    setTimeout(() => {
        toast.style.transform = 'translateY(4px)';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3500);
}

// Category icon mapping based on category name
const CATEGORY_ICONS = {
    'groceries': 'shopping_cart',
    'dining': 'restaurant',
    'transport': 'commute',
    'salary': 'payments',
    'utilities': 'electric_bolt',
    'entertainment': 'sports_esports',
    'health': 'local_hospital',
    'transfer': 'swap_horiz',
    'shopping': 'shopping_bag',
    'education': 'school',
    'travel': 'flight',
    'subscriptions': 'subscriptions',
    'rent': 'home',
    'gifts': 'card_giftcard',
    'investments': 'trending_up',
    'other': 'receipt_long',
};

function getCategoryIcon(descriptionOrCategoryName, categoryName) {
    // If categoryName is provided from server, use it for icon lookup
    const name = (categoryName || '').toLowerCase();
    if (name && CATEGORY_ICONS[name]) return CATEGORY_ICONS[name];

    // Fallback: guess from description
    const desc = (descriptionOrCategoryName || '').toLowerCase();
    if (desc.includes('grocer') || desc.includes('supermarket') || desc.includes('silpo') || desc.includes('atb')) return 'shopping_cart';
    if (desc.includes('restaurant') || desc.includes('cafe') || desc.includes('dining') || desc.includes('food')) return 'restaurant';
    if (desc.includes('transport') || desc.includes('uber') || desc.includes('bolt') || desc.includes('taxi')) return 'commute';
    if (desc.includes('salary') || desc.includes('income') || desc.includes('зарплата')) return 'payments';
    if (desc.includes('utility') || desc.includes('electric') || desc.includes('water') || desc.includes('gas')) return 'electric_bolt';
    if (desc.includes('entertainment') || desc.includes('cinema') || desc.includes('game')) return 'sports_esports';
    if (desc.includes('health') || desc.includes('pharmacy') || desc.includes('doctor')) return 'local_hospital';
    if (desc.includes('transfer') || desc.includes('переказ')) return 'swap_horiz';
    return 'receipt_long';
}

function getCategoryName(descriptionOrCategoryName, categoryName) {
    // If server provides category_name, use it directly
    if (categoryName) return categoryName;

    // Fallback: guess from description
    const desc = (descriptionOrCategoryName || '').toLowerCase();
    if (desc.includes('grocer') || desc.includes('supermarket') || desc.includes('silpo') || desc.includes('atb')) return 'Groceries';
    if (desc.includes('restaurant') || desc.includes('cafe') || desc.includes('dining') || desc.includes('food')) return 'Dining';
    if (desc.includes('transport') || desc.includes('uber') || desc.includes('bolt') || desc.includes('taxi')) return 'Transport';
    if (desc.includes('salary') || desc.includes('income') || desc.includes('зарплата')) return 'Salary';
    if (desc.includes('utility') || desc.includes('electric') || desc.includes('water') || desc.includes('gas')) return 'Utilities';
    if (desc.includes('entertainment') || desc.includes('cinema') || desc.includes('game')) return 'Entertainment';
    if (desc.includes('health') || desc.includes('pharmacy') || desc.includes('doctor')) return 'Health';
    if (desc.includes('transfer') || desc.includes('переказ')) return 'Transfer';
    return 'Other';
}
