cd ~/ctf-challenges/bhargav-webtask-cheesevault

cat > README.md << 'EOF'
# Jerry's Cheese Vault - CTF Web Challenge

**Challenge Type:** Web Security - SQL Injection  
**Difficulty:** Easy to Medium  
**Author:** Bhargav Raj Dutta  
**Date Created:** October 21, 2025  
**Flag:** `Exploit3rs{cheese_vault_sql_inject_2025}`

---

## 📖 Story & Context

### Scenario
Tom has finally caught Jerry and locked all his precious cheese collection in a digital vault. You're playing as **Nibbles** (Jerry's nephew), and you need to break into the vault management system to free the cheese! The vault system was hastily built by Tom's human owner and has a critical security flaw in the authentication system.

### Objective
Your mission is to:
1. Bypass the authentication system
2. Access the admin panel
3. Find Tom's secret notes containing the location of the master key to Jerry's cage
4. Retrieve the flag

### Professional Context
This challenge demonstrates **SQL injection vulnerabilities** in authentication systems, a critical security issue that consistently appears in the OWASP Top 10. In real-world scenarios, improper input sanitization in login forms can lead to:
- Complete authentication bypass
- Unauthorized access to sensitive data
- Database compromise
- Privilege escalation

Organizations must use parameterized queries and input validation to prevent SQL injection attacks.

---

## 🚀 Quick Start (Mac)

### Prerequisites
- Docker Desktop for Mac installed
- Terminal access
- Python 3.8+ (for golden solution)

### Deployment Steps
```bash
# 1. Navigate to challenge directory
cd bhargav-webtask-cheesevault

# 2. Build and start the challenge
docker-compose up --build -d

# 3. Wait for database initialization (10 seconds)
sleep 10

# 4. Access the challenge
open http://localhost:8080
```

### Stop the Challenge
```bash
docker-compose down
# Or to remove volumes too:
docker-compose down -v
```

---

## 🏗️ Architecture

### Services
- **web**: Flask application (Python 3.11)
- **db**: PostgreSQL 15 database

### Ports
- Web application: `8080` (configurable via `WEB_PORT` env variable)
- Database: Internal only (not exposed)

### Resource Limits
- Web container: 512MB RAM, 1 CPU
- DB container: 256MB RAM

---

## 🎯 Learning Objectives

1. **Understand SQL Injection**: Learn how improper string concatenation in SQL queries creates vulnerabilities
2. **Authentication Bypass**: Demonstrate how SQL injection can bypass login mechanisms
3. **Privilege Escalation**: Show how attackers can gain unauthorized admin access
4. **Impact Assessment**: Understand the real-world consequences of SQL injection

---

## 🔧 Testing & Validation

### Automated Tests

Run the smoke tests:
```bash
cd tests
bash smoke_test.sh
```

### Manual Testing Checklist

- [ ] Container builds successfully
- [ ] Web application is accessible at http://localhost:8080
- [ ] Login page loads correctly
- [ ] Normal user login works (jerry/cheeselover)
- [ ] SQL injection payload bypasses authentication
- [ ] Admin notes are visible after exploitation
- [ ] Flag is present in admin notes
- [ ] Golden solution script retrieves the flag
- [ ] Reset procedure works (docker-compose down && up)

### Expected Behavior

**Normal Login (jerry/cheeselover):**
- Access granted to vault
- Can see cheese inventory
- Cannot see admin notes

**SQL Injection (admin' OR '1'='1' --):**
- Authentication bypassed
- Logged in as admin
- Can see admin notes section
- Flag visible in "Master Key Location" note

---

## 🎓 Hints

Three-level hint system available in `hints.json`:

**Level 1 (Low):** Look at how the login form processes your input  
**Level 2 (Medium):** Try using SQL comments and logical operators in the username field  
**Level 3 (High):** Payload format: `admin' OR '1'='1' --`

---

## 🏆 Solution Overview

The vulnerability exists in `/login` endpoint where user input is directly concatenated into SQL query:
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

By injecting `admin' OR '1'='1' --` as username, the query becomes:
```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --' AND password = '...'
```

This always evaluates to true, bypassing authentication.

**Full solution in:** `golden_solution/solve.py`  
**Detailed writeup in:** `writeup.md`

---

## 🔒 Security Notes

- No external network calls
- No real personal data used
- All credentials are fictional
- Database is isolated within Docker network
- No privileged containers required

---

## 🐛 Troubleshooting

**Container won't start:**
```bash
docker-compose logs web
docker-compose logs db
```

**Port already in use:**
```bash
# Change port in docker-compose.yml or use env variable
WEB_PORT=9090 docker-compose up -d
```

**Reset to clean state:**
```bash
docker-compose down -v
docker-compose up --build -d
```

---

## 📝 Files Included