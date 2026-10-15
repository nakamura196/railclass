// Access to the 3D models. They are not public: the Worker at AUTH_BASE serves them behind Cloudflare Access with
// IIIF Authorization Flow 2.0. Login window -> cookie on the Worker -> hidden iframe gives a short token -> probe
// gives a signed URL for one file. Tokens are kept in memory only (never in localStorage).
export const AUTH_BASE = "https://railclass-models.ldas.jp";
const COLLECTION = "railclass";
export const LOGIN_URL = `${AUTH_BASE}/auth/login/${COLLECTION}`;
export const LOGOUT_URL = `${AUTH_BASE}/auth/logout/${COLLECTION}`;

let token: { value: string; until: number } | null = null;
let pending: Promise<string | null> | null = null;

/** A token if the visitor is logged in (asked silently through an iframe), else null. */
export function getToken(): Promise<string | null> {
  if (token && token.until > Date.now()) return Promise.resolve(token.value);
  pending ??= askToken().finally(() => { pending = null; });
  return pending;
}

function askToken(): Promise<string | null> {
  return new Promise(done => {
    const messageId = Math.random().toString(36).slice(2);
    const frame = document.createElement("iframe");
    frame.hidden = true;
    frame.src = `${AUTH_BASE}/auth/token/${COLLECTION}?messageId=${messageId}&origin=${encodeURIComponent(location.origin)}`;
    const finish = (v: string | null) => {
      clearTimeout(timer); removeEventListener("message", onMessage); frame.remove(); done(v);
    };
    const onMessage = (e: MessageEvent) => {
      if (e.origin !== AUTH_BASE || e.data?.messageId !== messageId) return;
      if (e.data.type === "AuthAccessToken2") {
        // Keep it a little less than its life (expiresIn is in seconds)
        token = { value: e.data.accessToken, until: Date.now() + (e.data.expiresIn ?? 300) * 1000 - 20000 };
        finish(token.value);
      } else finish(null);   // AuthAccessTokenError2: not logged in
    };
    const timer = setTimeout(() => finish(null), 10000);   // e.g. localhost: the Worker does not answer
    addEventListener("message", onMessage);
    document.body.append(frame);
  });
}

/** Open the login window (call it straight from a click) and wait until it closes; then the token, or null. */
export function login(): Promise<string | null> {
  const win = window.open(LOGIN_URL, "railclass-login", "width=520,height=680");
  if (!win) return Promise.resolve(null);   // blocked
  return new Promise(done => {
    const t0 = Date.now();
    const timer = setInterval(() => {
      if (win.closed || Date.now() - t0 > 600000) { clearInterval(timer); getToken().then(done); }
    }, 500);
  });
}

/** Forget the token (the logout link clears the cookie on the Worker's side). */
export function forget() { token = null; }

/** The signed URL of one file (path as on the Worker, e.g. "acela.glb"), or null: not logged in, or not on the allow list. */
export async function resolve(path: string): Promise<string | null> {
  const t = await getToken();
  if (!t) return null;
  const p = path.split("/").map(encodeURIComponent).join("/");
  try {
    const r = await (await fetch(`${AUTH_BASE}/probe/${COLLECTION}/${p}`, { headers: { Authorization: `Bearer ${t}` } })).json();
    return r.status === 302 ? r.location?.id ?? null : null;
  } catch (e) { return null; }
}

/** Links with data-auth-path: a click logs in if needed, then goes to the signed URL (data-denied = message if refused). */
export function wireDownloads() {
  const links = document.querySelectorAll<HTMLAnchorElement>("a[data-auth-path]");
  if (!links.length) return;
  // Ask now, so that a click already knows the answer: a login window opened after a wait is taken for a popup and blocked.
  let signedIn: boolean | null = null;
  getToken().then(t => { signedIn = !!t; });
  for (const a of links) {
    a.addEventListener("click", async e => {
      e.preventDefault();
      if (signedIn === false) signedIn = !!(await login());   // straight from the click
      const url = await resolve(a.dataset.authPath!);
      if (url) location.href = url; else alert(a.dataset.denied);
    });
  }
}
