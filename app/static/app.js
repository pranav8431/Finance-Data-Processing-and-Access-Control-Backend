const q = (id) => document.getElementById(id);

const consoleEl = q("console");

function baseUrl() {
  const value = q("base-url").value.trim();
  return value || window.location.origin;
}

function getToken() {
  return q("token").value.trim();
}

function pretty(value) {
  return JSON.stringify(value, null, 2);
}

function log(title, payload) {
  const ts = new Date().toLocaleTimeString();
  const output = [`[${ts}] ${title}`, typeof payload === "string" ? payload : pretty(payload), ""].join("\n");
  consoleEl.textContent = output + consoleEl.textContent;
}

async function apiRequest(method, path, body = null, opts = {}) {
  const headers = { "Content-Type": "application/json" };
  const token = getToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${baseUrl()}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  });

  const text = await response.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = text;
  }

  if (!response.ok && !opts.allowError) {
    log(`${method} ${path} -> ${response.status}`, data || "Request failed");
    return { ok: false, status: response.status, data };
  }

  log(`${method} ${path} -> ${response.status}`, data || "(no content)");
  return { ok: response.ok, status: response.status, data };
}

function requireId(inputId, label) {
  const value = Number(q(inputId).value);
  if (!value || value < 1) {
    throw new Error(`${label} is required and must be >= 1`);
  }
  return value;
}

function userCreatePayload() {
  return {
    name: q("user-name").value.trim(),
    email: q("user-email").value.trim(),
    password: q("user-password").value,
    role: q("user-role").value,
    status: q("user-status").value,
  };
}

function userUpdatePayload() {
  const payload = {};
  const name = q("user-name").value.trim();
  const email = q("user-email").value.trim();
  const role = q("user-role").value;
  const status = q("user-status").value;

  if (name) payload.name = name;
  if (email) payload.email = email;
  if (role) payload.role = role;
  if (status) payload.status = status;

  return payload;
}

function recordPayload() {
  const payload = {
    amount: q("record-amount").value.trim(),
    type: q("record-type").value,
    category: q("record-category").value.trim(),
    date: q("record-date").value,
  };
  const notes = q("record-notes").value.trim();
  if (notes) payload.notes = notes;
  return payload;
}

function recordUpdatePayload() {
  const payload = {};
  const amount = q("record-amount").value.trim();
  const type = q("record-type").value;
  const category = q("record-category").value.trim();
  const date = q("record-date").value;
  const notes = q("record-notes").value.trim();

  if (amount) payload.amount = amount;
  if (type) payload.type = type;
  if (category) payload.category = category;
  if (date) payload.date = date;
  if (notes) payload.notes = notes;

  return payload;
}

function recordsQuery() {
  const params = new URLSearchParams();

  const add = (k, v) => {
    if (v !== "" && v != null) params.set(k, String(v));
  };

  add("type", q("filter-type").value);
  add("category", q("filter-category").value.trim());
  add("start_date", q("filter-start").value);
  add("end_date", q("filter-end").value);
  add("created_by", q("record-created-by").value.trim());
  add("limit", q("filter-limit").value.trim());
  add("offset", q("filter-offset").value.trim());

  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
}

function wireEvents() {
  q("btn-clear").addEventListener("click", () => {
    consoleEl.textContent = "Console cleared.";
  });

  q("btn-health").addEventListener("click", async () => {
    await apiRequest("GET", "/health");
  });

  document.querySelectorAll(".preset").forEach((el) => {
    el.addEventListener("click", () => {
      q("login-email").value = el.dataset.email;
      q("login-password").value = el.dataset.password;
      log("Preset loaded", { email: el.dataset.email });
    });
  });

  q("btn-login").addEventListener("click", async () => {
    const body = {
      email: q("login-email").value.trim(),
      password: q("login-password").value,
    };
    const result = await apiRequest("POST", "/api/v1/auth/login", body, { allowError: true });
    if (result.ok && result.data?.access_token) {
      q("token").value = result.data.access_token;
      log("Token stored", { token_prefix: result.data.access_token.slice(0, 24) + "..." });
    }
  });

  q("btn-users-create").addEventListener("click", async () => {
    await apiRequest("POST", "/api/v1/users", userCreatePayload(), { allowError: true });
  });

  q("btn-users-list").addEventListener("click", async () => {
    await apiRequest("GET", "/api/v1/users", null, { allowError: true });
  });

  q("btn-users-get").addEventListener("click", async () => {
    try {
      const userId = requireId("user-id", "User ID");
      await apiRequest("GET", `/api/v1/users/${userId}`, null, { allowError: true });
    } catch (err) {
      log("Validation error", String(err.message || err));
    }
  });

  q("btn-users-update").addEventListener("click", async () => {
    try {
      const userId = requireId("user-id", "User ID");
      await apiRequest("PATCH", `/api/v1/users/${userId}`, userUpdatePayload(), { allowError: true });
    } catch (err) {
      log("Validation error", String(err.message || err));
    }
  });

  q("btn-records-create").addEventListener("click", async () => {
    await apiRequest("POST", "/api/v1/records", recordPayload(), { allowError: true });
  });

  q("btn-records-list").addEventListener("click", async () => {
    await apiRequest("GET", `/api/v1/records${recordsQuery()}`, null, { allowError: true });
  });

  q("btn-records-get").addEventListener("click", async () => {
    try {
      const recordId = requireId("record-id", "Record ID");
      await apiRequest("GET", `/api/v1/records/${recordId}`, null, { allowError: true });
    } catch (err) {
      log("Validation error", String(err.message || err));
    }
  });

  q("btn-records-update").addEventListener("click", async () => {
    try {
      const recordId = requireId("record-id", "Record ID");
      await apiRequest("PATCH", `/api/v1/records/${recordId}`, recordUpdatePayload(), { allowError: true });
    } catch (err) {
      log("Validation error", String(err.message || err));
    }
  });

  q("btn-records-delete").addEventListener("click", async () => {
    try {
      const recordId = requireId("record-id", "Record ID");
      await apiRequest("DELETE", `/api/v1/records/${recordId}`, null, { allowError: true });
    } catch (err) {
      log("Validation error", String(err.message || err));
    }
  });

  q("btn-dashboard-summary").addEventListener("click", async () => {
    await apiRequest("GET", "/api/v1/dashboard/summary", null, { allowError: true });
  });
}

wireEvents();
log("Ready", {
  message: "Use login presets, authenticate, then test all endpoints.",
  current_origin: window.location.origin,
});
