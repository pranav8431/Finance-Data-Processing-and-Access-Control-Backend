(function () {
  const { q, request } = window.UI;

  function requireId() {
    const id = Number(q("user-id").value);
    if (!id || id < 1) throw new Error("User ID must be >= 1");
    return id;
  }

  function payloadCreate() {
    return {
      name: q("user-name").value.trim(),
      email: q("user-email").value.trim(),
      password: q("user-password").value,
      role: q("user-role").value,
      status: q("user-status").value,
    };
  }

  function payloadUpdate() {
    const body = {};
    const name = q("user-name").value.trim();
    const email = q("user-email").value.trim();
    const role = q("user-role").value;
    const status = q("user-status").value;
    if (name) body.name = name;
    if (email) body.email = email;
    if (role) body.role = role;
    if (status) body.status = status;
    return body;
  }

  async function safeRun(fn) {
    try {
      await fn();
    } catch (err) {
      q("response-console").textContent = String(err.message || err);
    }
  }

  q("btn-users-create")?.addEventListener("click", () =>
    safeRun(() => request("POST", "/api/v1/users", payloadCreate(), { outputId: "response-console", allowError: true }))
  );

  q("btn-users-list")?.addEventListener("click", () =>
    safeRun(() => request("GET", "/api/v1/users", null, { outputId: "response-console", allowError: true }))
  );

  q("btn-users-get")?.addEventListener("click", () =>
    safeRun(() => request("GET", `/api/v1/users/${requireId()}`, null, { outputId: "response-console", allowError: true }))
  );

  q("btn-users-update")?.addEventListener("click", () =>
    safeRun(() => request("PATCH", `/api/v1/users/${requireId()}`, payloadUpdate(), { outputId: "response-console", allowError: true }))
  );
})();
