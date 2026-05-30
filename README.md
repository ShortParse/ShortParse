# ShortParse 🛡️🔮

ShortParse is an automated, high-fidelity Warcraft Logs (WCL) performance analysis, benchmark scoring, and coaching engine built for World of Warcraft raid teams and raid leaders. 

By simply pasting a Warcraft Logs report URL, ShortParse dissects combat events, grades players dynamically against strict real-world item level and fight duration cohorts, identifies rotational/defensive gaps, and generates a premium, glassmorphic review dashboard with actionable coaching metrics.

---

## Key Features

### For Raid Leaders & Players
* **Frosted-Glass Scorecard**: High-fidelity overview of the raid roster, average grades, and critical performance highlights.
* **Raid Coach Drawer**: Click any player to open a dedicated coaching canvas. Displays tailored grade targets, rotational casting gaps, active casting uptimes, and core action items.
* **Avoidable Death Recaps**: A chronological, color-coded interactive timeline showcasing the final 8 seconds leading to a player's death (damage hits in red, heals in green, defensive buffs in blue/purple).
* **Cooldown Efficiency & Timeline Tracker**: Visualizes how effectively players used major cooldowns and when avoidable damage hits occurred.
* **Benchmark Comparisons**: Compares player values (DPS/HPS) against the top 1%, 5%, and 10% of matching character rankings worldwide.
* **Discord Integration**: One-click sharing of high-fidelity embeds of raid summaries directly to your guild's Discord channels.
* **Dynamic Public Announcement Banner**: Global homepage notification banners displaying dynamically configured announcements with layout style and lifecycle controls managed by administrators.

### For Administrators (The AI Autopilot Control Console)
* **WCL Zone-Based AI Encounter Compiler**: Type a WCL Zone ID (e.g. `46`) and click **Update Encounters**. The backend automatically queries zone metadata, scrapes top parses, extracts `DamageTaken` events to aggregate spell telemetry, resolves spell names/tooltips/icons through the Battle.net REST API, and guides the **Gemini AI model** with strict format rules to output complete, production-ready boss modules (`boss.py`) and dynamically updates `__init__.py` files in `shortparse/data/encounters/`.
* **Dynamic Player Cooldowns Auditor**: Click **Update Cooldowns** to programmatically trigger our `SpellAudit` discovery engine, scanning elite rankings to isolate unmapped class cast events, estimate exact timings via cast gaps telemetry, and auto-draft class/spec modules saved under `data/cooldowns/<class>/<spec>_discovered.py`.
* **Dynamic Encounters Module Discovery**: Traverses raid directories automatically on lookup and registers encounters at server runtime. Eliminates hardcoded module maps and allows AI-generated zones to register instantly.
* **System Health & Queue Dashboard**: Real-time admin views of registered users, Patreon members adoption statistics, Redis query cache connected benchmarks, SQLite file footprint in MB, and active job queue process state indicators.

### For Developers & Contributors
* **Visual Encounter Config Builder**: Discreetly hosted at `/builder` (e.g. `https://www.shortparse.com/builder`), this tool lets contributors visually map out raid boss mechanics and Warcraft Logs spell IDs. Includes:
  * Dynamic directory crawler to inspect existing raid data packages.
  * Form inputs for all mechanic fields (Applies To, Severity, Avoidable switches).
  * Intelligent auto-suggestions (e.g., auto-populating score penalties based on severity).
  * Live Python syntax generator formatting clean Typed dictionary blocks.
  * One-click clipboard formatter with Discord markdown fenced code blocks.

---

## Architecture under the Hood

ShortParse is split into two modular repositories:
1. **Core Backend (`ShortParse`)**: A high-performance FastAPI server running on Uvicorn, backed by a SQLAlchemy SQLite/PostgreSQL database, and driven by a multi-threaded WCL GraphQL API client.
2. **Modern SPA Frontend (`ShortParse-Web`)**: A sleek, pure single-page application crafted with vanilla HTML5, custom glassmorphic CSS, and responsive reactive JS.

```
ShortParse (FastAPI Server on Port 8000)
├── shortparse/server/app.py       # API router, server configurations, SPA serving
├── shortparse/reports/analysis.py # Core fight review & parsing compiler
├── shortparse/benchmarks/service.py# Concurrent ranking compiler & progressive fallback
└── shortparse/data/encounters/    # Encounters database (Voidspire, Dreamrift, Quel'Danas)
```

### Progressive Benchmark Fallback
To ensure players are compared fairly, our comparison engine evaluates logs using a multi-tiered filtering progression. If a strict match count ($\ge 10$ logs) is not found, the filters progressively relax to guarantee all 3 comparison baselines (`top_1`, `top_5`, and `top_10` baselines) are always generated:
* **Item Level Tolerance**: Matches peers strictly within **$\pm2$** item levels (falls back to $\pm5$ and $\pm8$).
* **Kill Timer Parity**: Checks fight durations within **$\pm10$ seconds** (falls back to $\pm30$s and $\pm60$s) to maintain bloodlust and potion alignment parity.
* **Healer Count Parity**: Imposes a strict **$\pm1$ healer count** constraint across all primary tiers for HPS. A raid running 4 healers will *never* be evaluated against a 1-healer speedrun.

---

## Self-Hosting & Deployment Guide

### Prerequisites
* **Python 3.10+**
* **Warcraft Logs API Client Credentials**: You need a free WCL client ID and secret. You can obtain these in 2 minutes by creating a client on the [Warcraft Logs API Client Dashboard](https://www.warcraftlogs.com/api/clients).
* **Redis Server** (optional but highly recommended for high-speed benchmark query caching).

---

### Environment Variables (`.env`)

Create a `.env` file in the project root based on the variables below:

```ini
# Environment Configuration
SHORTPARSE_ENV=production
SHORTPARSE_DEBUG=false
SHORTPARSE_STORAGE_DIR=/storage/ShortParse/storage

# Warcraft Logs OAuth Integration
WARCRAFTLOGS_CLIENT_ID=your_wcl_client_id_here
WARCRAFTLOGS_CLIENT_SECRET=your_wcl_client_secret_here
# The exact callback URL registered in your WCL API clients dashboard
WARCRAFTLOGS_REDIRECT_URI=https://yourdomain.com/api/auth/warcraftlogs/callback

# Session & Security
# Generate a secure key in your terminal via: openssl rand -hex 32
JWT_SECRET_KEY=your_secure_random_hex_string

# High-Performance Cache (Redis)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_redis_secure_password
```

---

### Local Installation & Start

1. **Clone the Core and Web repositories**:
   ```bash
   git clone https://github.com/ShortParse/ShortParse.git
   git clone https://github.com/ShortParse/ShortParse-Web.git
   ```

2. **Navigate to the core repository and create a virtual environment**:
   ```bash
   cd ShortParse
   python -m venv .venv
   ```

3. **Activate the environment**:
   * **Linux/macOS**: `source .venv/bin/activate`
   * **Windows (PowerShell)**: `.\.venv\Scripts\Activate.ps1`

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Start Redis server** (via docker for easy local development):
   ```bash
   docker-compose up -d
   ```

6. **Start the FastAPI backend server**:
   ```bash
   uvicorn shortparse.server.app:app --host 0.0.0.0 --port 8000 --reload
   ```

You can now open `http://localhost:8000` to access the local ShortParse application. Accessing `http://localhost:8000/builder` will load up the Visual Config Builder!

---

### Production Deployment

In a production environment, it is highly recommended to run Uvicorn behind an **Nginx** reverse proxy to handle SSL termination and serve the static files directly.

#### Sample Nginx Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name shortparse.com www.shortparse.com;

    ssl_certificate /etc/letsencrypt/live/shortparse.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/shortparse.com/privkey.pem;

    root /var/www/ShortParse-Web;
    index index.html;

    # Serve static assets directly from Nginx
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy builder clean URL to backend
    location /builder {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy API and OAuth requests to FastAPI (stripping the /api prefix)
    location /api/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## License
ShortParse is open-source software licensed under the MIT License.
