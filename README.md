# Dashboard Analizy Ofert Pracy

Kompleksowe narzędzie do analizy rynku pracy w Polsce wykorzystujące framework Dash z uwierzytelnianiem opartym na rolach użytkowników. Aplikacja umożliwia interaktywną analizę ofert pracy, trendów wynagrodzeń, analizę umiejętności i rozmieszczenie geograficzne ofert.

## 🚀 Główne Funkcjonalności

### Uwierzytelnianie i Zarządzanie Użytkownikami
- **System ról**: `viewer`, `analyst`, `admin`
- **Logowanie**: Email + hasło
- **Rejestracja**: Automatyczne generowanie nazwy użytkownika z imienia i emaila
- **Personalizacja**: Wybór preferowanej branży zatrudnienia
- **Panel administracyjny**: Zarządzanie użytkownikami (tylko admin)

### Analiza Danych
- **Upload danych**: Wsparcie dla plików JSON z ofertami pracy
- **Interaktywne wizualizacje**: Wykresy słupkowe, scatter plots, mapy cieplne
- **Filtrowanie danych**: Zaawansowane opcje filtrowania po różnych kryteriach
- **Eksport wyników**: Możliwość eksportu analiz

## 📊 Widoki i Zakładki

### 1. **Analiza Umiejętności** (Skills Analysis)
- Top 20 najpopularniejszych umiejętności
- Kombinacje umiejętności i ich współwystępowanie
- Wagowa analiza umiejętności według poziomu doświadczenia
- Wykresy słupkowe i tabele z danymi

### 2. **Poziomy Doświadczenia** (Experience Levels)
- Rozkład ofert według wymagań doświadczenia
- Korelacja doświadczenia z wynagrodzeniem
- Wykresy kołowe i histogramy

### 3. **Analiza Geograficzna** (Location Analysis)
- Mapa cieplna ofert pracy według lokalizacji
- Ranking miast według liczby ofert
- Analiza zdalnej pracy vs praca w biurze

### 4. **Analiza Firm** (Company Analysis)
- Ranking firm według liczby publikowanych ofert
- Analiza wielkości firm (startup, korporacje, SME)
- Preferencje firm w zakresie umiejętności

### 5. **Trendy Rynkowe** (Market Trends)
- Zmiany w czasie popularności umiejętności
- Sezonowość publikowania ofert
- Emerging skills i technologie

### 6. **Analiza Wynagrodzeń** (Salary Analysis)
- Rozkład wynagrodzeń według pozycji i doświadczenia
- Box plots i histogramy wynagrodzeń
- Korelacja wynagrodzenia z umiejętnościami

### 7. **Szczegółowa Analiza Umiejętności** (Detailed Skills)
- Deep-dive w konkretne umiejętności
- Analiza kombinacji umiejętności
- Matryca korelacji między umiejętnościami

## 🏗️ Architektura Systemu

### Backend
```
Flask Server (server.py)
├── Authentication (auth.py)
│   ├── Login/Register routes
│   ├── Role-based access control
│   └── Session management
├── Database Models (models.py)
│   ├── User model with roles
│   ├── UserSession for tracking
│   └── SQLAlchemy ORM
└── Admin Panel
    ├── User management
    ├── Data upload (admin only)
    └── System monitoring
```

### Frontend - Dash Application
```
Dash App (app.py)
├── Protected Layout (authentication required)
├── Multi-tab Interface
├── Interactive Visualizations (visualizations.py)
├── Data Processing (data_processor.py)
└── Client-side Data Stores
```

### Komponenty

#### 1. **DataProcessor** (`data_processor.py`)
```python
class DataProcessor:
    - load_data_from_json()    # Wczytywanie danych JSON
    - validate_data()          # Walidacja struktury danych
    - process_skills()         # Analiza umiejętności
    - calculate_statistics()   # Obliczenia statystyczne
    - filter_data()           # Filtrowanie danych
```

#### 2. **ChartGenerator** (`visualizations.py`)
```python
class ChartGenerator:
    - create_skills_chart()      # Wykresy umiejętności
    - create_salary_analysis()   # Analiza wynagrodzeń
    - create_location_map()      # Mapy geograficzne
    - create_correlation_matrix() # Matryce korelacji
    - create_trend_analysis()    # Analiza trendów
```

#### 3. **User Model** (`models.py`)
```python
class User:
    - id, username, email, first_name
    - password_hash (bcrypt)
    - role (viewer/analyst/admin)
    - preferred_category
    - created_at, is_active
    
    Methods:
    - can_access_advanced()  # Sprawdza dostęp do zaawansowanych funkcji
    - can_access_admin()     # Sprawdza uprawnienia administratora
```

### Struktura Ról

| Rola | Dostęp | Opis |
|------|---------|------|
| `viewer` | Podstawowe zakładki | Przeglądanie analiz, ograniczony dostęp |
| `analyst` | Wszystkie analiz | Pełny dostęp do wszystkich wizualizacji |
| `admin` | Pełny dostęp + zarządzanie | Upload danych, zarządzanie użytkownikami |

## 🛠️ Technologie

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM dla bazy danych
- **Flask-Login** - Zarządzanie sesjami
- **PostgreSQL** - Baza danych (Replit/Docker)
- **Werkzeug** - Password hashing i proxy

### Frontend/Visualization
- **Dash** - Framework do aplikacji analitycznych
- **Plotly** - Interaktywne wykresy
- **Dash Bootstrap Components** - UI komponenty
- **Bootstrap** - CSS framework (dark theme)
- **Font Awesome** - Ikony

### Data Processing
- **Pandas** - Manipulacja i analiza danych
- **NumPy** - Obliczenia numeryczne
- **Collections** - Counter dla analizy częstości

## 🐧 Instalacja Lokalna (Linux bez Docker)

### 1. Wymagania systemowe
- **System operacyjny**: Ubuntu 20.04+ / Debian 11+ / CentOS 8+ / Fedora 35+
- **Python**: 3.11 lub nowszy
- **PostgreSQL**: 12 lub nowszy
- **Git**: Do klonowania repozytorium

### 2. Instalacja zależności systemowych

#### Ubuntu/Debian:
```bash
# Aktualizacja systemu
sudo apt update && sudo apt upgrade -y

# Instalacja Python 3.11 i narzędzi
# Dla Ubuntu 20.04/22.04 - dodaj deadsnakes PPA dla Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Alternatywnie, użyj systemowego Python 3.10+ (wystarczający):
# sudo apt install -y python3 python3-venv python3-dev python3-pip

# Instalacja PostgreSQL
sudo apt install -y postgresql postgresql-contrib postgresql-server-dev-all

# Instalacja dodatkowych narzędzi
sudo apt install -y git curl build-essential libpq-dev
```

#### CentOS/RHEL/Fedora:
```bash
# CentOS/RHEL
sudo dnf install -y python3.11 python3.11-devel python3-pip postgresql postgresql-server postgresql-devel git gcc gcc-c++

# Fedora
sudo dnf install -y python3.11 python3.11-devel python3-pip postgresql postgresql-server postgresql-devel git gcc gcc-c++

# Inicjalizacja PostgreSQL (CentOS/RHEL)
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

### 3. Generowanie bezpiecznego hasła

```bash
# Generowanie bezpiecznego hasła do bazy danych
DB_PASSWORD=$(python3 -c "import secrets, string; chars=string.ascii_letters+string.digits; print(''.join(secrets.choice(chars) for _ in range(20)))")

echo "✅ Wygenerowane hasło do bazy danych: ${DB_PASSWORD}"
echo "❗ ZAPAMIĘTAJ to hasło - będzie użyte w następnym kroku!"
```

### 4. Konfiguracja PostgreSQL

```bash
# Przełączenie na użytkownika postgres i konfiguracja bazy
sudo -u postgres psql << EOF
CREATE DATABASE jobmarket;
CREATE USER jobmarket WITH PASSWORD '${DB_PASSWORD}';
ALTER USER jobmarket CREATEDB;
GRANT ALL PRIVILEGES ON DATABASE jobmarket TO jobmarket;
\q
EOF

echo "✅ Baza danych PostgreSQL skonfigurowana pomyślnie"
```

**Opcjonalnie - Konfiguracja połączeń lokalnych:**
```bash
# Edycja pliku konfiguracyjnego (lokalizacja może się różnić)
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Dodaj linię dla lokalnych połączeń:
local   jobmarket    jobmarket                     md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 5. Klonowanie i przygotowanie projektu

```bash
# Klonowanie repozytorium
git clone <repository-url>
cd job-market-dashboard

# Utworzenie środowiska wirtualnego
python3.11 -m venv venv

# Aktywacja środowiska wirtualnego
source venv/bin/activate

# Aktualizacja pip
pip install --upgrade pip setuptools wheel
```

### 6. Instalacja zależności Python

```bash
# Instalacja z pyproject.toml (zalecane)
pip install -e .
```

### 7. Konfiguracja zmiennych środowiskowych

```bash
# Utworzenie pliku .env z wcześniej wygenerowanym hasłem
cat > .env << EOF
DATABASE_URL=postgresql://jobmarket:${DB_PASSWORD}@localhost:5432/jobmarket
SESSION_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
FLASK_ENV=development
PYTHONPATH=.
EOF

echo "✅ Plik .env utworzony pomyślnie"

# Wczytanie zmiennych (dla bieżącej sesji) - bezpieczniejsza metoda
set -a
source .env
set +a

# Dla trwałej konfiguracji dodaj do ~/.bashrc (opcjonalnie)
echo "# Job Market Dashboard environment" >> ~/.bashrc
echo "set -a; source $(pwd)/.env; set +a" >> ~/.bashrc
```

### 8. Inicjalizacja bazy danych

```bash
# Sprawdzenie połączenia z bazą danych
python3 -c "
from app import app
from models import db, User
try:
    with app.app_context():
        db.create_all()
    print('✅ Baza danych została zainicjalizowana pomyślnie')
except Exception as e:
    print(f'❌ Błąd inicjalizacji bazy danych: {e}')
"
```

### 9. Uruchomienie aplikacji

#### Rozwój (Development):
```bash
# Uruchomienie z Gunicorn (zalecane)
gunicorn --bind 0.0.0.0:5000 --reload --timeout 120 main:app

# Lub bezpośrednio z Python (tylko do rozwoju)
python -c "from app import app; app.run(debug=True, host='0.0.0.0', port=5000)"
```

#### Produkcja:
```bash
# Utworzenie katalogu na logi
mkdir -p logs

# Uruchomienie z wieloma workerami
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app

# Z logowaniem
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 \
         --access-logfile logs/access.log --error-logfile logs/error.log \
         main:app
```

### 10. Tworzenie usługi systemowej (opcjonalnie)

```bash
# Utworzenie pliku usługi systemd
sudo tee /etc/systemd/system/jobmarket.service > /dev/null << EOF
[Unit]
Description=Job Market Dashboard
After=network.target postgresql.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Uruchomienie usługi
sudo systemctl daemon-reload
sudo systemctl enable jobmarket
sudo systemctl start jobmarket

# Sprawdzenie statusu
sudo systemctl status jobmarket

# Logi usługi
sudo journalctl -u jobmarket -f
```

### 11. Weryfikacja instalacji

```bash
# Sprawdzenie czy aplikacja działa
curl http://localhost:5000

# Sprawdzenie logów
tail -f logs/*.log

# Test połączenia z bazą danych
python3 -c "
from app import app
from models import User
with app.app_context():
    print(f'Liczba użytkowników w bazie: {User.query.count()}')
"
```

### 12. Pierwszy Administrator

Po uruchomieniu aplikacji:
1. Przejdź do `http://localhost:5000` lub `http://server-ip:5000`
2. Kliknij "Zarejestruj się"
3. Pierwszy użytkownik automatycznie otrzyma rolę administratora
4. Zaloguj się używając emaila i hasła

### Rozwiązywanie problemów

#### Problem z połączeniem do PostgreSQL:
```bash
# Sprawdzenie czy PostgreSQL działa
sudo systemctl status postgresql

# Sprawdzenie portów (preferuj ss zamiast netstat)
sudo ss -tlnp | grep 5432
# lub tradycyjnie: sudo netstat -tlnp | grep 5432

# Test połączenia
psql -h localhost -U jobmarket -d jobmarket
```

#### Problem z uprawnieniami Python:
```bash
# Upewnienie się że środowisko wirtualne jest aktywne
which python3
# Powinno pokazać: /path/to/project/venv/bin/python3

# Reinstalacja zależności
pip install --upgrade --force-reinstall -e .
```

#### Problem z importami:
```bash
# Dodanie ścieżki projektu do PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Sprawdzenie czy wszystkie moduły się importują
python3 -c "
try:
    import app, models, auth, forms, data_processor, visualizations
    print('✅ Wszystkie moduły zaimportowane pomyślnie')
except ImportError as e:
    print(f'❌ Błąd importu: {e}')
"
```

## 🐳 Instalacja Lokalna (Docker)

### 1. Wymagania
- Docker
- Docker Compose
- Git

### 2. Klonowanie repozytorium
```bash
git clone <repository-url>
cd job-market-dashboard
```

### 3. Konfiguracja Docker

Utwórz `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
RUN pip install -U pip setuptools wheel
RUN pip install -e .

# Copy application files
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--reuse-port", "--reload", "main:app"]
```

Utwórz `docker-compose.yml`:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: jobmarket
      POSTGRES_USER: jobmarket
      POSTGRES_PASSWORD: jobmarket123
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://jobmarket:jobmarket123@db:5432/jobmarket
      SESSION_SECRET: your-super-secret-key-change-this-in-production
      FLASK_ENV: development
    volumes:
      - .:/app
    depends_on:
      - db
    command: >
      sh -c "
        python -c 'from models import db; from app import app; 
        with app.app_context(): db.create_all()' &&
        gunicorn --bind 0.0.0.0:5000 --reload main:app
      "

volumes:
  postgres_data:
```

### 4. Uruchomienie
```bash
# Budowanie i uruchomienie
docker-compose up --build

# W tle
docker-compose up -d

# Sprawdzenie logów
docker-compose logs -f web

# Zatrzymanie
docker-compose down
```

### 5. Pierwszy Administrator
Po uruchomieniu aplikacji:
1. Przejdź do `http://localhost:5000`
2. Kliknij "Zarejestruj się"
3. Pierwszy użytkownik automatycznie otrzyma rolę administratora
4. Zaloguj się używając emaila i hasła

## 📁 Struktura Plików

```
job-market-dashboard/
├── app.py                 # Główna aplikacja Dash
├── main.py               # Entry point dla Gunicorn
├── models.py             # Modele bazy danych
├── auth.py               # Uwierzytelnianie i autoryzacja
├── forms.py              # Formularze WTForms
├── data_processor.py     # Przetwarzanie danych
├── visualizations.py     # Generowanie wykresów
├── templates/            # Szablony HTML
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   └── admin.html
├── assets/               # Statyczne pliki CSS/JS
├── docker-compose.yml    # Konfiguracja Docker
├── Dockerfile
└── README.md
```

## 🔧 Konfiguracja Środowiska

### Zmienne Środowiskowe
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SESSION_SECRET=your-secret-key
FLASK_ENV=development
```

### Pierwsze Uruchomienie
```bash
# Inicjalizacja bazy danych
python -c "from models import db; from app import app; with app.app_context(): db.create_all()"

# Uruchomienie serwera
gunicorn --bind 0.0.0.0:5000 main:app
```

## 📊 Format Danych

Aplikacja oczekuje danych w formacie JSON:
```json
[
  {
    "title": "Python Developer",
    "company": "Tech Corp",
    "location": "Warszawa",
    "salary_min": 8000,
    "salary_max": 12000,
    "currency": "PLN",
    "experience_level": "Mid",
    "skills": ["Python", "Django", "PostgreSQL"],
    "category": "IT",
    "remote": true,
    "company_size": "Startup",
    "posted_date": "2024-01-15"
  }
]
```

## 🚨 Bezpieczeństwo

- Hasła użytkowników hashowane z Werkzeug
- Ochrona CSRF w formularzach
- Autoryzacja oparta na rolach
- Sesje zarządzane przez Flask-Login
- SSL/TLS dla połączeń z bazą danych

## 🔄 Development

### Dodawanie Nowych Widoków
1. Dodaj nową zakładkę w `app.py` w sekcji `tabs`
2. Stwórz callback do obsługi zawartości zakładki
3. Zaimplementuj logikę w `data_processor.py`
4. Dodaj wizualizacje w `visualizations.py`

### Testowanie
```bash
# Sprawdź czy aplikacja startuje
gunicorn --bind 0.0.0.0:5000 --reload main:app

# Test połączenia z bazą
python -c "from app import app; from models import User; with app.app_context(): print(f'Liczba użytkowników: {User.query.count()}')"
```

## 📝 Licencja

MIT License - Zobacz plik LICENSE dla szczegółów.

## 🤝 Kontakt

Dla pytań dotyczących developmentu lub architektury, skontaktuj się z zespołem deweloperskim.