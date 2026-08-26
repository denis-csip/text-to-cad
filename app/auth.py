"""Authentification text-to-cad — fédérée sur IDEAS (comme ARIZ-Copilot).

Reprend fidèlement le relais IDEAS d'ARIZ-Copilot (supabase/functions/ideas-login) :
on valide les identifiants auprès de l'API GraphQL IDEAS, puis on gère une session
LOCALE (cookie signé) + un compte local (SQLite). IDEAS fait foi pour l'identité ;
SQLite gère statut (pending/active/blocked), rôle admin, et rattachement des études.

Aucune dépendance externe : urllib + sqlite3 + hmac (stdlib).
"""
import os, json, time, hmac, hashlib, base64, sqlite3, threading
import urllib.request, urllib.error
from pathlib import Path

# --- Config (via variables d'environnement) ---------------------------------
IDEAS_ENDPOINT = os.environ.get("IDEAS_ENDPOINT", "https://ideas.aiard.eu/api")
IDEAS_APP = os.environ.get("IDEAS_APP_NAME", "text-to-cad")   # header x-application
DB_PATH = Path(os.environ.get("TCAD_DB", "/data/text-to-cad.db"))
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-insecure-secret-change-me")
ADMIN_EMAILS = {e.strip().lower() for e in
                os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()}
SESSION_TTL = 60 * 60 * 24 * 14        # 14 jours
COOKIE_NAME = "tcad_session"

_db_lock = threading.Lock()


# --- Base de comptes (SQLite) -----------------------------------------------
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(str(DB_PATH), timeout=10)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA busy_timeout=5000")
    return c


def init_db():
    with _db_lock, _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users(
          id         INTEGER PRIMARY KEY AUTOINCREMENT,
          email      TEXT UNIQUE NOT NULL,
          name       TEXT,
          ideas_id   TEXT,
          status     TEXT NOT NULL DEFAULT 'pending',   -- pending | active | blocked
          is_admin   INTEGER NOT NULL DEFAULT 0,
          created_at INTEGER,
          last_login INTEGER
        );
        """)


def get_user(email):
    if not email:
        return None
    with _db_lock, _conn() as c:
        r = c.execute("SELECT * FROM users WHERE email=?", (email.lower(),)).fetchone()
        return dict(r) if r else None


def upsert_user(email, name, ideas_id):
    """Crée ou met à jour le compte local. Renvoie (user, is_new).
    Allowlist ADMIN_EMAILS = promu admin ET activé d'office (comme ARIZ)."""
    email = (email or "").lower()
    now = int(time.time())
    admin = email in ADMIN_EMAILS
    with _db_lock, _conn() as c:
        ex = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if ex:
            status = "active" if admin else ex["status"]
            is_admin = 1 if (admin or ex["is_admin"]) else 0
            c.execute("UPDATE users SET name=?, ideas_id=?, is_admin=?, status=?, "
                      "last_login=? WHERE email=?",
                      (name, ideas_id, is_admin, status, now, email))
            is_new = False
        else:
            status = "active" if admin else "pending"
            c.execute("INSERT INTO users(email,name,ideas_id,status,is_admin,"
                      "created_at,last_login) VALUES(?,?,?,?,?,?,?)",
                      (email, name, ideas_id, status, 1 if admin else 0, now, now))
            is_new = True
        r = c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return dict(r), is_new


def list_users():
    with _db_lock, _conn() as c:
        return [dict(r) for r in c.execute(
            "SELECT id,email,name,status,is_admin,created_at,last_login "
            "FROM users ORDER BY created_at DESC").fetchall()]


def set_status(email, status):
    if status not in ("pending", "active", "blocked"):
        raise ValueError("statut invalide")
    with _db_lock, _conn() as c:
        c.execute("UPDATE users SET status=? WHERE email=?", (status, email.lower()))


# --- Session : cookie signé (stateless, HMAC-SHA256) ------------------------
def make_session(user):
    payload = {"email": user["email"], "uid": user["id"], "t": int(time.time())}
    raw = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    sig = hmac.new(SESSION_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    return f"{raw}.{sig}"


def read_session(cookie):
    if not cookie or "." not in cookie:
        return None
    raw, _, sig = cookie.rpartition(".")
    exp = hmac.new(SESSION_SECRET.encode(), raw.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, exp):
        return None
    try:
        pad = "=" * (-len(raw) % 4)
        data = json.loads(base64.urlsafe_b64decode((raw + pad).encode()))
    except Exception:
        return None
    if int(time.time()) - int(data.get("t", 0)) > SESSION_TTL:
        return None
    return data


def current_user(cookie):
    """Utilisateur ACTIF derrière un cookie de session, sinon None."""
    sess = read_session(cookie)
    if not sess:
        return None
    u = get_user(sess.get("email"))
    if u and u["status"] == "active":
        return u
    return None


# --- Relais IDEAS (porté de ARIZ-Copilot/supabase/functions/ideas-login) ----
def signin_ideas(email, password):
    """Valide les identifiants auprès de l'API GraphQL IDEAS.
    On ne demande QUE id/name/email (les champs décoratifs cassaient sur des
    profils incomplets). Réponse partielle tolérée : si signin.email est là,
    l'auth a réussi même si `errors` est présent."""
    query = ("mutation Signin($email:String!,$password:String!){"
             "signin(email:$email,password:$password){id name email}}")
    body = json.dumps({"query": query,
                       "variables": {"email": (email or "").strip(),
                                     "password": password or ""}}).encode()
    req = urllib.request.Request(
        IDEAS_ENDPOINT, data=body, method="POST",
        headers={"Content-Type": "application/json", "x-application": IDEAS_APP})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            payload = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        # 5xx = plateforme en panne (pas un refus d'identifiants)
        return {"error": f"IDEAS HTTP {e.code}", "unreachable": e.code >= 500}
    except Exception as e:
        return {"error": f"network: {e}", "unreachable": True}

    signin = (payload.get("data") or {}).get("signin")
    if signin and signin.get("email"):
        return {"user": signin}          # succès (même si `errors` non vide)
    errs = payload.get("errors")
    if errs:
        return {"error": errs[0].get("message", "Authentication failed")}
    return {"error": "Invalid response from IDEAS API"}
