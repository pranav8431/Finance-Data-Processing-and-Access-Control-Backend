(function () {
  const { q, request } = window.UI;

  function setMoney(id, value) {
    const el = q(id);
    if (el) el.textContent = value ?? "-";
  }

  q("btn-dashboard-summary")?.addEventListener("click", async () => {
    const res = await request("GET", "/api/v1/dashboard/summary", null, {
      outputId: "response-console",
      allowError: true,
    });

    if (res.ok) {
      setMoney("kpi-income", res.data?.total_income);
      setMoney("kpi-expenses", res.data?.total_expenses);
      setMoney("kpi-net", res.data?.net_balance);
    }
  });
})();
