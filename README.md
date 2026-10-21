# SecurePortal, Säker inloggningsportal

Ett webbprojekt byggt med Python, Flask och SQLite med fokus på grundläggande webbsäkerhet.

## Om projektet

SecurePortal är ett portfolio-projekt som demonstrerar grundläggande säkerhetsprinciper vid utveckling av webbapplikationer. Applikationen innehåller användarregistrering, inloggning, sessionshantering och åtkomstkontroll till en skyddad kontrollpanel.

## Funktioner

- Registrering av användarkonton och inloggning
- Säker hashning av lösenord med Werkzeug
- SQLite-databas med parametriserade SQL-frågor
- CSRF-skydd med Flask-WTF
- Skyddad kontrollpanel för inloggade användare
- Utloggning via POST-förfrågan
- Automatiserade tester med pytest

## Säkerhetsåtgärder

- **Lösenordsskydd:** Lösenord lagras som hashvärden, inte i klartext.
- **CSRF-skydd:** Formulär skyddas mot Cross-Site Request Forgery.
- **Åtkomstkontroll:** Oinloggade användare nekas åtkomst till kontrollpanelen.
- **Skydd mot SQL-injektion:** Databasfrågor använder parametriserade värden.
- **Sessionssäkerhet:** HTTP-only-cookies och inställningen `SameSite=Lax` används.
- **Indatavalidering:** Krav på användarnamn och lösenord kontrolleras vid registrering.

## Tekniker

- Python
- Flask
- Flask-WTF
- SQLite
- Werkzeug
- pytest
- HTML

## Kom igång

### 1. Klona projektet

```bash
git clone https://github.com/PaulinaStenqvist/SecurePortal
cd secure-portal
```

### 2. Skapa en virtuell miljö

```bash
python -m venv .venv
```

Aktivera miljön i Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Installera beroenden

```powershell
python -m pip install -r requirements.txt
```

### 4. Skapa en utvecklingsnyckel

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Starta applikationen

```powershell
python app.py
```

Öppna sedan http://127.0.0.1:5000 i webbläsaren.

## Tester

Kör testerna med:

```powershell
python -m pytest -v
```

Projektets nuvarande testsvit innehåller sju godkända tester.

## Planerade förbättringar

- Behörighetsstyrning baserad på användarroller
- Begränsning av upp
