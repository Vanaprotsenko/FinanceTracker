const CURRENCY_MAP = {
    980: { code: 'UAH', symbol: '₴', flag: '🇺🇦', name: 'Ukrainian Hryvnia' },
    840: { code: 'USD', symbol: '$', flag: '🇺🇸', name: 'US Dollar' },
    978: { code: 'EUR', symbol: '€', flag: '🇪🇺', name: 'Euro' },
};


const MonoMixin = {

    monoCards: [],
    monoCardsLoading: false,
    monoSyncing: false,

    getCurrencyInfo(code) {
        return CURRENCY_MAP[code] || { code: `${code}`, symbol: '', flag: '💳', name: 'Unknown' };
    },

    formatCardBalance(balance, currencyCode) {
        const info = this.getCurrencyInfo(currencyCode);
        const amount = (balance / 100).toFixed(2);
        return `${info.symbol} ${parseFloat(amount).toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    },

    truncateCardId(cardId) {
        if (!cardId) return '—';
        if (cardId.length <= 12) return cardId;
        return cardId.slice(0, 6) + '…' + cardId.slice(-4);
    },

    async loadMonoCards() {
        this.monoCardsLoading = true;
        try {
            const data = await this.apiFetch('/mono/cards-info');
            this.monoCards = [];
            this.$nextTick(() => {
                this.monoCards = (data && data.response) ? data.response : [];
            });
        } catch (e) {
            console.error('Failed to load mono cards:', e);
        } finally {
            this.monoCardsLoading = false;
        }
    },

    async syncMonoCards() {
        this.monoSyncing = true;
        try {
            await this.apiFetch('/mono/save-mono-cards', { method: 'POST' });
            this.showToast('Cards synced from Monobank', 'success');
            await this.loadMonoCards();
        } catch (e) {
        } finally {
            this.monoSyncing = false;
        }
    },

    async deleteMonoCard(cardId) {
        if (!confirm('Delete this Mono card?')) return;
        try {
            await this.apiFetch(`/mono/delete-mono-card?card_id=${encodeURIComponent(cardId)}`, {
                method: 'DELETE'
            });
            this.showToast('Card deleted', 'success');
            await this.loadMonoCards();
        } catch (e) { }
    },

    async addTransactions(cardId) {
        this.showToast('Syncing transactions…', 'info');
        try {
            await this.apiFetch(`/mono/save-transaction?card_id=${encodeURIComponent(cardId)}`, {
                method: 'POST'
            });
            this.showToast('Transactions added', 'success');
            await this.loadMonoCards();
        } catch (e) {
        }
    },

    syncingToRecords: false,

    async syncTransactionsToRecords(cardId) {
        if (this.syncingToRecords) return;
        this.syncingToRecords = true;
        this.showToast('Syncing transactions to records…', 'info');
        try {
            const data = await this.apiFetch(`/mono/sync-transactions?card_id=${encodeURIComponent(cardId)}`, {
                method: 'POST'
            });
            this.showToast(data?.response || 'Transactions synced to records', 'success');
        } catch (e) {
        } finally {
            this.syncingToRecords = false;
        }
    },

    selectedCard: null,

    openCardDetail(card) {
        this.selectedCard = card;
    },

    closeCardDetail() {
        this.selectedCard = null;
    },

    formatTxnAmount(amount, currencyCode) {
        const info = this.getCurrencyInfo(currencyCode);
        const val = (Math.abs(amount) / 100);
        const formatted = val.toLocaleString('uk-UA', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
        const sign = amount >= 0 ? '+' : '−';
        return `${sign} ${info.symbol}${formatted}`;
    },

    formatTxnDate(isoString) {
        const d = new Date(isoString);
        const day = d.getDate().toString().padStart(2, '0');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        const month = months[d.getMonth()];
        const hours = d.getHours().toString().padStart(2, '0');
        const mins = d.getMinutes().toString().padStart(2, '0');
        return `${day} ${month}, ${hours}:${mins}`;
    },

    txnOperationInfo(txn) {
        // Show operation amount if different currency than card
        if (this.selectedCard && txn.currency !== this.selectedCard.currency_code) {
            const info = this.getCurrencyInfo(txn.currency);
            const val = (Math.abs(txn.operationAmount) / 100);
            return `${info.symbol}${val.toLocaleString('uk-UA', { minimumFractionDigits: 2 })}`;
        }
        return null;
    },
};
