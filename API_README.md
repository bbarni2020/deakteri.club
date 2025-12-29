# Deáktéri Hack Club API

A Python Flask API a Deáktéri Hack Club weboldalhoz, amely kezeli a szponzorokat, adományozókat és a számlázási kérelmeket.

## Telepítés

1. Python 3.8+ szükséges
2. Telepítsd a függőségeket:
```bash
pip install -r requirements.txt
```

3. Másold le a `.env.template` fájlt `.env` néven és töltsd ki a megfelelő értékekkel:
```bash
cp .env.template .env
```

4. Szerkeszd a `.env` fájlt:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
RECIPIENT_EMAIL=hackclub@deakteri.hu
DEBUG=False
PORT=5000
```

## Futtatás

### Fejlesztői környezet
```bash
python api.py
```

### Produkciós környezet
```bash
# Gunicorn használatával
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 api:app
```

## API Végpontok

### GET /api/sponsors
Visszaadja a szponzorok listáját.

**Válasz:**
```json
{
  "success": true,
  "sponsors": [
    {
      "id": 1,
      "name": "TechCorp Solutions",
      "logo_url": "https://example.com/logo.png",
      "website": "https://techcorp.com",
      "added_date": "2024-01-15T10:30:00"
    }
  ],
  "count": 1
}
```

### GET /api/donators
Visszaadja a személyes adományozók listáját.

**Válasz:**
```json
{
  "success": true,
  "donators": [
    {
      "id": 1,
      "name": "Kovács János",
      "amount": 50,
      "currency": "USD",
      "message": "Szuper kezdeményezés!",
      "anonymous": false,
      "added_date": "2024-01-10T16:45:00"
    }
  ],
  "count": 1
}
```

### POST /api/invoice
Számlázási kérelem küldése.

**Kérés:**
```json
{
  "companyName": "Example Corp",
  "contactEmail": "contact@example.com",
  "streetAddress": "1234 Main St",
  "suite": "Suite 100",
  "city": "Budapest",
  "state": "Pest",
  "zip": "1055",
  "country": "HU",
  "amount": 500
}
```

**Válasz:**
```json
{
  "success": true,
  "message": "Számlázási kérelem sikeresen elküldve!",
  "email_sent": true
}
```

### POST /api/sponsors (Admin)
Új szponzor hozzáadása.

**Kérés:**
```json
{
  "name": "New Sponsor",
  "logo_url": "https://example.com/logo.png",
  "website": "https://newsponsor.com"
}
```

### POST /api/donators (Admin)
Új adományozó hozzáadása.

**Kérés:**
```json
{
  "name": "John Doe",
  "amount": 100,
  "message": "Great work!",
  "anonymous": false
}
```

**Megjegyzés:** A currency mező automatikusan "USD"-re lesz beállítva.

### GET /api/health
Állapot ellenőrzés.

## Fájlok

- `sponsors.json` - Szponzorok adatai
- `donators.json` - Adományozók adatai
- `invoice_submissions.json` - Számlázási kérelmek biztonsági mentése

## Biztonsági jegyzetek

- Az admin végpontok (POST /api/sponsors, POST /api/donators) jelenleg nem védettek. Produkciós használatra add hozzá az autentikációt.
- Email jelszavakat app password-ként használd Gmail esetén.
- HTTPS használata ajánlott produkciós környezetben.

## Frontend integráció

A `script.js` fájlban módosítsd az `API_BASE_URL` változót a produkciós API URL-re:

```javascript
const API_BASE_URL = 'https://your-api-domain.com/api';
```
