# Website Enrichment System

A Python-based asynchronous scraper that enriches website data by extracting emails, social media links, and WhatsApp contacts from company websites. Built with `aiohttp`, `BeautifulSoup`, and `Playwright` for robust scraping.

---

# Features

- Asynchronous scraping for speed and scalability
- Fallback to Playwright for dynamic content
- Regex + `mailto:` detection for hidden emails
- Configurable timeouts, retries, and backoff in `config/settings.py`
- Automatic input/output handling:
  - Drop Excel files into `input/`
  - Enriched results saved into `outputs/Enriched_<filename>.xlsx`
- Progress bar with live enriched count

---

# Project Structure

```text
website_enrichment_system/
│
├── config/
│   └── settings.py        # Configuration (folders, scraper settings)
├── processors/
│   └── enrich.py          # Scraper logic
├── input/                 # Place Excel files here
├── outputs/               # Enriched files saved here
├── logs/                  # Log file for errors
├── utils/                 
│   └── helpers.py         # Helpers for merging
├── exporters/             
│   └── excel_exporter.py  # Export format creator (xlsx)
├── main.py                # Entry point
├── requirements.txt       # Requirements for project
└── README.md              # Project documentation
```

---

# Installation

## 1. Clone the Repository

```bash
git clone https://github.com/WakoDigitalHub/website-enrichment-system.git

cd website-enrichment-system
```

---

## 2. Create a Virtual Environment

### Linux / Mac

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Usage

## 1. Place Your Excel File

Example:

```text
input/companies.xlsx
```

---

## 2. Run the Script

```bash
python main.py
```

---

## 3. Output

The enriched file will appear in:

```text
outputs/Enriched_companies.xlsx
```

---

# Configuration

All scraper settings are centralized in:

```text
config/settings.py
```

Example:

```python
SCRAPER_SETTINGS = {
    "aiohttp_timeout": 30,        # seconds
    "aiohttp_retries": 2,         # number of retries
    "aiohttp_backoff": 1.5,       # exponential backoff factor
    "playwright_timeout": 45000   # milliseconds
    "limit_depth": 5              #depth of internal url scraping"
}
```

Adjust these values to balance speed vs. thoroughness.

---

# Testing

Run unit tests with:

```bash
pytest tests/
```

Tests cover:

- Regex extraction (emails, socials, WhatsApp)
- Utility functions (`normalize_url`, `extract_emails`)
- Basic scraper behavior

---

# Contributing

1. Fork the repository
2. Create a feature branch:

```bash
git checkout -b feature-name
```

3. Commit your changes:

```bash
git commit -m "Add feature"
```

4. Push to your branch:

```bash
git push origin feature-name
```

5. Open a Pull Request

---

# License

This project is licensed under the MIT License. See `LICENSE` for details.
