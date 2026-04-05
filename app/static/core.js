(function () {
  const KEY_BASE_URL = "fd_base_url";
  const KEY_TOKEN = "fd_token";

  function q(id) {
    return document.getElementById(id);
  }

  function nowTs() {
    return new Date().toLocaleTimeString();
  }

  function pretty(value) {
    return JSON.stringify(value, null, 2);
  }

  function parseJwt(token) {
    try {
      const payload = token.split(".")[1];
      const normalized = payload.replace(/-/g, "+").replace(/_/g, "/");
      const decoded = atob(normalized);
      return JSON.parse(decoded);
    } catch {
      return null;
    }
  }

  function getBaseUrl() {
    return localStorage.getItem(KEY_BASE_URL) || window.location.origin;
  }

  function getToken() {
    return localStorage.getItem(KEY_TOKEN) || "";
  }

  function setBaseUrl(value) {
    localStorage.setItem(KEY_BASE_URL, value || window.location.origin);
  }

  function setToken(value) {
    if (value) {
      localStorage.setItem(KEY_TOKEN, value);
    } else {
      localStorage.removeItem(KEY_TOKEN);
    }
  }

  function setActiveNav() {
    const current = window.location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll(".nav a").forEach((a) => {
      const href = a.getAttribute("href");
      if (href === current || (current === "" && href === "index.html")) {
        a.classList.add("active");
      }
    });
  }

  function renderSession() {
    const token = getToken();
    const payload = parseJwt(token);
    const userEl = q("session-user");
    const roleEl = q("session-role");
    const statusEl = q("session-status");

    if (userEl) userEl.textContent = payload?.sub || "not set";
    if (roleEl) roleEl.textContent = payload?.role || "unknown";
    if (statusEl) statusEl.textContent = payload?.status || "unknown";
  }

  function wireWorkspace() {
    const baseUrlInput = q("base-url");
    const tokenInput = q("token");
    const saveBtn = q("btn-save-config");
    const clearTokenBtn = q("btn-clear-token");

    if (baseUrlInput) {
      baseUrlInput.value = getBaseUrl();
    }
    if (tokenInput) {
      tokenInput.value = getToken();
    }

    if (saveBtn) {
      saveBtn.addEventListener("click", () => {
        setBaseUrl(baseUrlInput ? baseUrlInput.value.trim() : "");
        if (tokenInput) setToken(tokenInput.value.trim());
        renderSession();
      });
    }

    if (clearTokenBtn) {
      clearTokenBtn.addEventListener("click", () => {
        setToken("");
        if (tokenInput) tokenInput.value = "";
        renderSession();
      });
    }
  }

  function writeOutput(outputId, title, payload) {
    const target = q(outputId);
    if (!target) return;
    const text = typeof payload === "string" ? payload : pretty(payload);
    target.textContent = `[${nowTs()}] ${title}\n${text}`;
  }

  async function request(method, path, body, opts) {
    const options = opts || {};
    const outputId = options.outputId || "response-console";
    const allowError = options.allowError !== false;

    const headers = { "Content-Type": "application/json" };
    const token = getToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    const response = await fetch(`${getBaseUrl()}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });

    const text = await response.text();
    let data = text;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      // keep raw text
    }

    writeOutput(outputId, `${method} ${path} -> ${response.status}`, data || "(no content)");

    if (!response.ok && !allowError) {
      throw new Error(`Request failed with ${response.status}`);
    }

    return { ok: response.ok, status: response.status, data };
  }

  window.UI = {
    q,
    request,
    setToken,
    getToken,
    renderSession,
    wireWorkspace,
  };

  setActiveNav();
  wireWorkspace();
  renderSession();
})();
