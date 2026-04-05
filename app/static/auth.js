(function () {
  const { q, request, setToken, renderSession } = window.UI;

  document.querySelectorAll(".preset").forEach((btn) => {
    btn.addEventListener("click", () => {
      q("login-email").value = btn.dataset.email || "";
      q("login-password").value = btn.dataset.password || "";
    });
  });

  q("btn-health")?.addEventListener("click", async () => {
    await request("GET", "/health", null, { outputId: "response-console", allowError: true });
  });

  q("btn-login")?.addEventListener("click", async () => {
    const body = {
      email: q("login-email").value.trim(),
      password: q("login-password").value,
    };

    const res = await request("POST", "/api/v1/auth/login", body, {
      outputId: "response-console",
      allowError: true,
    });

    if (res.ok && res.data?.access_token) {
      q("token").value = res.data.access_token;
      setToken(res.data.access_token);
      renderSession();
    }
  });
})();
