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
        python -c 'from models import db; from app import server; 
        with server.app_context(): db.create_all()' &&
        gunicorn --bind 0.0.0.0:5000 --reload main:server
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
python -c "from models import db; from app import server; with server.app_context(): db.create_all()"

# Uruchomienie serwera
gunicorn --bind 0.0.0.0:5000 main:server
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
python main.py

# Test połączenia z bazą
python -c "from models import User; print(User.query.count())"
```

## 📝 Licencja

MIT License - Zobacz plik LICENSE dla szczegółów.

## 🤝 Kontakt

Dla pytań dotyczących developmentu lub architektury, skontaktuj się z zespołem deweloperskim.