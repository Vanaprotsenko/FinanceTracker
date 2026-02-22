// ============================================
// FinanceTracker — Alpine.js Application
// ============================================

const API_URL = ''; // Same origin — served from FastAPI

// Exchange rates to EUR (base currency for mixed-currency stats)
const EXCHANGE_RATES = {
    EUR: 1,
    USD: 0.92,      // 1 USD ≈ 0.92 EUR
    UAH: 0.01944    // 1 UAH ≈ 0.01944 EUR (51.45 UAH per EUR)
};

document.addEventListener('alpine:init', () => {
    Alpine.data('app', () => ({

        token: localStorage.getItem('token'),
        authMode: 'login',
        authLoading: false,
        loginEmail: '',
        loginPassword: '',
        signupName: '',
        signupEmail: '',
        signupPassword: '',

        // --- App State ---
        view: 'dashboard',
        records: [],
        loading: false,
        filter: 'all',

        // --- Modal State ---
        showModal: false,
        showMonoModal: false,
        monoToken: '',
        editingId: null,
        saving: false,
        form: {
            description: '',
            amount: '',
            currency: 'UAH',
            type: 'expense'
        },

        tg: window.Telegram ? window.Telegram.WebApp : null,

        doughnutChart: null,
        trendChart: null,

        get filteredRecords() {
            if (this.filter === 'income') return this.records.filter(r => r.amount >= 0);
            if (this.filter === 'expense') return this.records.filter(r => r.amount < 0);
            return this.records;
        },

        // Detect if all records use the same currency
        get statsCurrency() {
            if (this.records.length === 0) return 'USD';
            const currencies = [...new Set(this.records.map(r => r.currency))];
            return currencies.length === 1 ? currencies[0] : 'EUR';
        },

        get isMixedCurrency() {
            const currencies = [...new Set(this.records.map(r => r.currency))];
            return currencies.length > 1;
        },

        // Convert amount to the stats currency
        convertToStatsCurrency(amount, fromCurrency) {
            const target = this.statsCurrency;
            if (fromCurrency === target) return amount;
            // Convert via EUR as intermediary
            const inEur = amount * (EXCHANGE_RATES[fromCurrency] || 1);
            if (target === 'EUR') return inEur;
            return inEur / (EXCHANGE_RATES[target] || 1);
        },

        get totalIncome() {
            return this.records
                .filter(r => r.amount > 0)
                .reduce((s, r) => s + this.convertToStatsCurrency(r.amount, r.currency), 0);
        },

        get totalExpense() {
            return Math.abs(this.records
                .filter(r => r.amount < 0)
                .reduce((s, r) => s + this.convertToStatsCurrency(r.amount, r.currency), 0));
        },

        get netBalance() {
            return this.totalIncome - this.totalExpense;
        },

        async init() {
            if (this.tg) this.tg.expand();

            // Try Telegram auto-login
            if (this.tg && this.tg.initData && !this.token) {
                try {
                    const data = await this.apiFetch('/auth/telegram/login', {
                        method: 'POST',
                        body: JSON.stringify({ init_data: this.tg.initData })
                    });
                    if (data && data.access_token) {
                        this.token = data.access_token;
                        localStorage.setItem('token', this.token);
                        this.tg.close();
                        return;
                    }
                } catch (e) {
                    console.log('Telegram auto-login failed:', e);
                }
            }

            if (this.token) {
                await this.loadRecords();
            }
        },

        // === API ===
        async apiFetch(endpoint, options = {}) {
            const headers = {
                'Content-Type': 'application/json',
                ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
            };

            try {
                const response = await fetch(`${API_URL}${endpoint}`, { ...options, headers });
                if (response.status === 401) {
                    this.logout();
                    throw new Error('Session expired');
                }
                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.detail || 'Something went wrong');
                }
                return response.status !== 204 ? await response.json() : null;
            } catch (error) {
                this.showToast(error.message, 'danger');
                throw error;
            }
        },

        // === AUTH ===
        async handleLogin() {
            this.authLoading = true;
            try {
                const body = { email: this.loginEmail, password: this.loginPassword };
                if (this.tg && this.tg.initData) body.init_data = this.tg.initData;

                const data = await this.apiFetch('/auth/login', {
                    method: 'POST',
                    body: JSON.stringify(body)
                });

                this.token = data.access_token;
                localStorage.setItem('token', this.token);
                this.showToast('Logged in successfully', 'success');

                if (this.tg && this.tg.initData) {
                    setTimeout(() => this.tg.close(), 1500);
                } else {
                    await this.loadRecords();
                }
            } catch (e) { }
            finally { this.authLoading = false; }
        },

        async handleSignup() {
            this.authLoading = true;
            try {
                const body = { name: this.signupName, email: this.signupEmail };
                if (this.tg && this.tg.initData) body.init_data = this.tg.initData;

                await this.apiFetch(`/auth/signup?password=${encodeURIComponent(this.signupPassword)}`, {
                    method: 'POST',
                    body: JSON.stringify(body)
                });

                this.showToast('Account created! Logging you in...', 'success');

                try {
                    const loginBody = { email: this.signupEmail, password: this.signupPassword };
                    if (this.tg && this.tg.initData) loginBody.init_data = this.tg.initData;
                    const loginData = await this.apiFetch('/auth/login', {
                        method: 'POST',
                        body: JSON.stringify(loginBody)
                    });

                    this.token = loginData.access_token;
                    localStorage.setItem('token', this.token);

                    if (this.tg && this.tg.initData) {
                        setTimeout(() => this.tg.close(), 1500);
                    } else {
                        await this.loadRecords();
                    }
                } catch (loginErr) {
                    // If auto-login fails, pre-fill login form so user can retry
                    this.loginEmail = this.signupEmail;
                    this.loginPassword = this.signupPassword;
                    this.authMode = 'login';
                }
            } catch (e) { }
            finally { this.authLoading = false; }
        },

        logout() {
            this.token = null;
            this.records = [];
            localStorage.removeItem('token');
            this.view = 'dashboard';
        },

        // === VIEWS ===
        showView(name) {
            this.view = name;
            if (name === 'dashboard') this.loadRecords();
            if (name === 'stats') this.$nextTick(() => this.renderCharts());
        },

        // === RECORDS ===
        async loadRecords() {
            this.loading = true;
            try {
                const data = await this.apiFetch('/records/');
                // Force Alpine reactivity by replacing the array
                this.records = [];
                this.$nextTick(() => {
                    this.records = data || [];
                });
            } catch (e) { }
            finally { this.loading = false; }
        },

        openAddModal() {
            this.editingId = null;
            this.form = { description: '', amount: '', currency: 'UAH', type: 'expense' };
            this.showModal = true;
        },

        openEditModal(record) {
            this.editingId = record.id;
            this.form = {
                description: record.description,
                amount: Math.abs(record.amount),
                currency: record.currency,
                type: record.amount >= 0 ? 'income' : 'expense'
            };
            this.showModal = true;
        },

        async saveRecord() {
            const rawAmount = parseFloat(this.form.amount);
            if (!rawAmount || rawAmount <= 0) {
                this.showToast('Please enter a valid amount', 'danger');
                return;
            }

            this.saving = true;
            const amount = this.form.type === 'expense'
                ? -Math.abs(rawAmount)
                : Math.abs(rawAmount);
            const type = this.form.type;

            try {
                if (this.editingId) {
                    const params = new URLSearchParams({
                        amount,
                        type,
                        description: this.form.description,
                        currency: this.form.currency
                    }).toString();
                    await this.apiFetch(`/records/${this.editingId}?${params}`, { method: 'PATCH' });
                    this.showToast('Record updated', 'success');
                } else {
                    await this.apiFetch('/records/', {
                        method: 'POST',
                        body: JSON.stringify({
                            description: this.form.description,
                            amount,
                            type,
                            currency: this.form.currency
                        })
                    });
                    this.showToast('Record added', 'success');
                }
                this.showModal = false;
                await this.loadRecords();
            } catch (e) { }
            finally { this.saving = false; }
        },

        async deleteRecord(id) {
            if (!confirm('Delete this record?')) return;
            try {
                await this.apiFetch(`/records/${id}`, { method: 'DELETE' });
                this.showToast('Record deleted', 'success');
                await this.loadRecords();
            } catch (e) { }
        },

        connectMono() {
            this.monoToken = '';
            this.showMonoModal = true;
        },

        proceedToMono() {
            window.open('https://api.monobank.ua/index.html', '_blank');
        },

        async saveMonoToken() {
            if (!this.monoToken || !this.monoToken.trim()) {
                this.showToast('Please enter a valid token', 'danger');
                return;
            }

            try {
                await this.apiFetch('/auth/mono/savetoken', {
                    method: 'POST',
                    body: JSON.stringify({ mono_token: this.monoToken.trim() })
                });

                this.showToast('Monobank token saved successfully', 'success');
                this.showMonoModal = false;
            } catch (error) {
            }
        },

        formatAmount(amount) {
            const sign = amount >= 0 ? '+' : '';
            return sign + amount.toFixed(2);
        },

        getCurrencySymbol(code) {
            const symbols = { USD: '$', EUR: '€', UAH: '₴' };
            return symbols[code] || code;
        },

        formatStatsCurrency(value) {
            const sym = this.getCurrencySymbol(this.statsCurrency);
            return sym + value.toFixed(2);
        },

        formatDate(record) {
            const date = record.created_at ? new Date(record.created_at) : new Date();
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        },

        renderCharts() {
            this.renderDoughnutChart();
            this.renderTrendChart();
        },

        renderDoughnutChart() {
            const ctx = document.getElementById('incomeExpenseChart');
            if (!ctx) return;

            if (this.doughnutChart) this.doughnutChart.destroy();

            const income = this.totalIncome;
            const expense = this.totalExpense;
            const hasData = income > 0 || expense > 0;
            const sym = this.getCurrencySymbol(this.statsCurrency);

            this.doughnutChart = new Chart(ctx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['Income', 'Expenses'],
                    datasets: [{
                        data: hasData ? [income, expense] : [1, 1],
                        backgroundColor: hasData
                            ? ['rgba(52, 211, 153, 0.8)', 'rgba(248, 113, 113, 0.8)']
                            : ['rgba(100,100,100,0.2)', 'rgba(100,100,100,0.2)'],
                        borderWidth: 0,
                        hoverOffset: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '72%',
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#94a3b8',
                                padding: 16,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: { family: 'Outfit', size: 13 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.label}: ${sym}${ctx.raw.toFixed(2)}`
                            }
                        }
                    }
                }
            });
        },

        renderTrendChart() {
            const ctx = document.getElementById('monthlyTrendChart');
            if (!ctx) return;

            if (this.trendChart) this.trendChart.destroy();

            const months = {};
            const now = new Date();
            for (let i = 5; i >= 0; i--) {
                const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
                const key = d.toLocaleDateString('en-US', { month: 'short' });
                months[key] = { income: 0, expense: 0 };
            }

            this.records.forEach(r => {
                const date = r.created_at ? new Date(r.created_at) : new Date();
                const key = date.toLocaleDateString('en-US', { month: 'short' });
                if (months[key]) {
                    const converted = this.convertToStatsCurrency(Math.abs(r.amount), r.currency);
                    if (r.amount >= 0) months[key].income += converted;
                    else months[key].expense += converted;
                }
            });

            const labels = Object.keys(months);
            const incomeData = labels.map(k => months[k].income);
            const expenseData = labels.map(k => months[k].expense);
            const sym = this.getCurrencySymbol(this.statsCurrency);

            this.trendChart = new Chart(ctx.getContext('2d'), {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Income',
                            data: incomeData,
                            backgroundColor: 'rgba(52, 211, 153, 0.6)',
                            borderRadius: 6,
                            borderSkipped: false,
                            barPercentage: 0.6
                        },
                        {
                            label: 'Expenses',
                            data: expenseData,
                            backgroundColor: 'rgba(248, 113, 113, 0.6)',
                            borderRadius: 6,
                            borderSkipped: false,
                            barPercentage: 0.6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: {
                            grid: { display: false },
                            ticks: {
                                color: '#64748b',
                                font: { family: 'Outfit', size: 12 }
                            }
                        },
                        y: {
                            grid: { color: 'rgba(255,255,255,0.04)' },
                            ticks: {
                                color: '#64748b',
                                font: { family: 'Outfit', size: 12 },
                                callback: (val) => sym + val
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                color: '#94a3b8',
                                padding: 16,
                                usePointStyle: true,
                                pointStyle: 'circle',
                                font: { family: 'Outfit', size: 13 }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: (ctx) => ` ${ctx.dataset.label}: ${sym}${ctx.raw.toFixed(2)}`
                            }
                        }
                    }
                }
            });
        },

        showToast(message, type = 'info') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;

            const icons = { success: '✓', danger: '✕', info: 'ℹ' };
            toast.innerHTML = `<span class="toast-icon">${icons[type] || icons.info}</span>${message}`;

            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(-20px)';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }
    }));
});
