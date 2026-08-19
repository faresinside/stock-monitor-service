# ❄️ Midea PortaSplit Stock Monitor (Raspberry Pi & Web UI)

Système automatisé de surveillance de la disponibilité du climatiseur mobile **Midea PortaSplit** en France, prêt à être déployé sur **Raspberry Pi**.

---

## 🌟 Fonctionnalités

- 🏬 **Surveillance multi-boutiques (Rafraîchissement toutes les 30 sec)** :
  - **Optimea.fr** (Site officiel du distributeur - Prioritaire)
  - **Boulanger**
  - **Castorama** (Suivi dynamique de la fiche produit)
  - **Amazon.fr**
  - **Darty**
  - **Leroy Merlin**
- 🎮 **Alertes instantanées via Discord Webhook** (Ou Ntfy / Telegram)
- 📍 **Filtrage régional Île-de-France (IDF)** pour le retrait magasin local.
- 📊 **Dashboard Web Glassmorphism** accessible en HTTPS via Traefik (`https://portasplit.faresinside.fr/`).

---

## 📱 Configuration des Notifications Discord (Recommandé)

### 1. Obtenir votre lien Webhook Discord (30 secondes)
1. Ouvrez l'application **Discord** (sur PC, Mac ou Mobile).
2. Rendez-vous sur votre serveur Discord (ou créez un serveur privé).
3. Dans le salon textuel de votre choix (ex: `#alertes-stock`), cliquez sur l'icône de roue crantée ⚙️ (**Paramètres du salon**).
4. Cliquez sur la rubrique **Intégrations**, puis sur **Webhooks**.
5. Cliquez sur **Nouveau Webhook** (ou modifier un webhook existant).
6. Cliquez sur le bouton **Copier l'URL du Webhook**.

### 2. Ajouter l'URL dans le fichier `.env` sur votre Raspberry Pi
Connectez-vous à votre Raspberry Pi via SSH :
```bash
ssh pi-server@raspberrypi "nano ~/portasplit/.env"
```

Remplacez la ligne `DISCORD_WEBHOOK_URL=` par l'URL copiée :
```env
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz...
```
Sauvegardez avec `Ctrl+O` puis appuyez sur `Entrée`, puis quittez avec `Ctrl+X`.

### 3. Appliquer la modification
Redémarrez le container sur le Raspberry Pi :
```bash
ssh pi-server@raspberrypi "cd ~/portasplit && docker compose restart"
```

Vous pouvez maintenant tester l'envoi de la notification depuis le Dashboard Web ([https://portasplit.faresinside.fr/](https://portasplit.faresinside.fr/)) en cliquant sur le bouton **"Test Notification Discord"** !

---

## 🛠️ Déploiement Docker sur Raspberry Pi

```bash
cd ~/portasplit
docker compose up -d --build
```

---

## 🌐 Accès au Dashboard Web

- **URL Traefik HTTPS :** [https://portasplit.faresinside.fr/](https://portasplit.faresinside.fr/)
- **Accès direct IP local :** `http://192.168.1.9:8005`
