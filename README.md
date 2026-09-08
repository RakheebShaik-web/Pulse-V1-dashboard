# Pulse V1 Dashboard

Trading dashboard for the Pulse V1 automated trading system.

## Setup

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

## Deploy to Vercel

This is a static HTML dashboard — no build step needed.

1. Go to [vercel.com](https://vercel.com) → New Project
2. Import `RakheebShaik-web/Pulse-V1-dashboard`
3. Framework: **Other**
4. Deploy

## Configuration

The dashboard connects to the backend API. Set the backend URL in `index.html`:

```javascript
const API_URL = 'https://your-backend.onrender.com';
```

Or set via environment variable `API_URL`.

## Features

- Real-time portfolio metrics
- Active positions with live P&L
- Trade history
- Daily statistics
- Pre-market scan results
- Market clock
- Start/stop/close controls
- Auto-refresh every 30 seconds

## Backend

See [Alpaca-Pulse-V1](https://github.com/RakheebShaik-web/Alpaca-Pulse-V1) for the trading system backend.
