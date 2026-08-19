document.addEventListener("DOMContentLoaded", () => {
    const storesGrid = document.getElementById("stores-grid");
    const logsList = document.getElementById("logs-list");
    const btnRefresh = document.getElementById("btn-refresh");
    const btnTestNotif = document.getElementById("btn-test-notif");

    const baseUrl = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';

    async function fetchStatus() {
        try {
            const res = await fetch(baseUrl + "api/status");
            const data = await res.json();
            renderStores(data.stores);
            renderLogs(data.logs);
        } catch (err) {
            console.error("Erreur lors de la récupération des données:", err);
        }
    }

    function renderStores(stores) {
        if (!stores || stores.length === 0) {
            storesGrid.innerHTML = '<div class="loading-spinner">Aucune donnée disponible pour le moment.</div>';
            return;
        }

        storesGrid.innerHTML = stores.map(store => {
            let statusClass = "status-outofstock";
            let statusText = "🔴 Rupture";

            if (store.status === "IN_STOCK") {
                if (store.availability_type === "ONLINE_DELIVERY") {
                    statusClass = "status-instock";
                    statusText = "🌐 EN LIGNE";
                } else {
                    statusClass = "status-instock";
                    statusText = "🏬 EN MAGASIN IDF";
                }
            } else if (store.status === "ERROR") {
                statusClass = "status-error";
                statusText = "⚠️ Erreur";
            } else if (store.status === "UNKNOWN") {
                statusClass = "status-error";
                statusText = "❓ Inconnu";
            }

            const isOfficial = store.store_name.includes("Optimea");

            return `
                <div class="glass-card store-card">
                    <div class="store-header">
                        <span class="store-name">
                            ${store.store_name}
                            ${isOfficial ? '<span class="official-badge">Officiel</span>' : ''}
                        </span>
                        <span class="status-badge ${statusClass}">${statusText}</span>
                    </div>
                    <div class="store-body">
                        ${store.price ? `<div class="store-price">${store.price}</div>` : ''}
                        <div class="store-details">${store.details || store.error_message || 'Vérification effectuée'}</div>
                    </div>
                    <div class="store-footer">
                        <span class="last-check">Vérifié à ${formatTime(store.last_check)}</span>
                        <a href="${store.url}" target="_blank" rel="noopener" class="store-link">Voir la fiche ↗</a>
                    </div>
                </div>
            `;
        }).join("");
    }

    function renderLogs(logs) {
        if (!logs || logs.length === 0) {
            logsList.innerHTML = '<div class="log-item">Aucun journal répertorié.</div>';
            return;
        }

        logsList.innerHTML = logs.map(log => `
            <div class="log-item ${log.is_alert ? 'is-alert' : ''}">
                <span class="log-time">${formatTime(log.timestamp)}</span>
                <span class="log-store">[${log.store_name}]</span>
                <span class="log-msg">${log.message}</span>
            </div>
        `).join("");
    }

    function formatTime(isoString) {
        if (!isoString) return "--:--";
        const date = new Date(isoString);
        return date.toLocaleTimeString("fr-FR", { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    }

    btnRefresh.addEventListener("click", async () => {
        btnRefresh.disabled = true;
        btnRefresh.innerHTML = '<span class="btn-icon">⌛</span> Vérification...';
        try {
            await fetch(baseUrl + "api/check", { method: "POST" });
            setTimeout(fetchStatus, 1500);
        } catch (e) {
            console.error(e);
        } finally {
            setTimeout(() => {
                btnRefresh.disabled = false;
                btnRefresh.innerHTML = '<span class="btn-icon">🔄</span> Vérifier maintenant';
            }, 3000);
        }
    });

    btnTestNotif.addEventListener("click", async () => {
        btnTestNotif.disabled = true;
        btnTestNotif.innerHTML = '<span class="btn-icon">⏳</span> Envoi test...';
        try {
            const res = await fetch(baseUrl + "api/test-notification", { method: "POST" });
            const data = await res.json();
            alert("Notification de test envoyée !\nRésultats: " + JSON.stringify(data.results));
            fetchStatus();
        } catch (e) {
            alert("Erreur lors de l'envoi du test.");
        } finally {
            btnTestNotif.disabled = false;
            btnTestNotif.innerHTML = '<span class="btn-icon">🔔</span> Test Notifications';
        }
    });

    fetchStatus();
    setInterval(fetchStatus, 10000);
});
