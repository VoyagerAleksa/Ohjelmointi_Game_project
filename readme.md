# Lentopeli - Kadonneen Matkatavaran Metsästys

Hot/cold-tyylinen lentopeli Euroopan lentokentillä! Etsi kadonnutta perintölaukkua vihjeiden avulla.

## Asennus

### 1. Lataa SQL-skriptit GitHubista
- **database/** -kansiossa: `lp.sql` + `Database_creation.sql`

### 2. Tietokanta (MariaDB/MySQL)
```bash
mysql -u käyttäjä -p
CREATE DATABASE projectbase;
USE projectbase;
SOURCE lp.sql
SOURCE Database_creation.sql
