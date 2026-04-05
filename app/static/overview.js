(function () {
  const { q, request, getToken } = window.UI;

  function refreshKpis() {
    const baseInput = q("base-url");
    const kpiBase = q("kpi-base");
    const kpiToken = q("kpi-token");
    if (kpiBase && baseInput) {
      kpiBase.textContent = baseInput.value || window.location.origin;
    }
    if (kpiToken) {
      kpiToken.textContent = getToken() ? "Yes" : "No";
    }
  }

  q("btn-save-config")?.addEventListener("click", refreshKpis);
  q("btn-clear-token")?.addEventListener("click", refreshKpis);

  q("btn-health")?.addEventListener("click", async () => {
    const res = await request("GET", "/health", null, { outputId: "response-console", allowError: true });
    const healthEl = q("kpi-health");
    if (healthEl) {
      healthEl.textContent = res.ok ? "Healthy" : "Unreachable";
    }
  });

  refreshKpis();
})();
