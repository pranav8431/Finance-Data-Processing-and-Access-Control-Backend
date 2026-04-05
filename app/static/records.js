(function () {
  const { q, request } = window.UI;

  function requireId() {
    const id = Number(q("record-id").value);
    if (!id || id < 1) throw new Error("Record ID must be >= 1");
    return id;
  }

  function createPayload() {
    const body = {
      amount: q("record-amount").value.trim(),
      type: q("record-type").value,
      category: q("record-category").value.trim(),
      date: q("record-date").value,
    };
    const notes = q("record-notes").value.trim();
    if (notes) body.notes = notes;
    return body;
  }

  function updatePayload() {
    const body = {};
    const amount = q("record-amount").value.trim();
    const type = q("record-type").value;
    const category = q("record-category").value.trim();
    const date = q("record-date").value;
    const notes = q("record-notes").value.trim();

    if (amount) body.amount = amount;
    if (type) body.type = type;
    if (category) body.category = category;
    if (date) body.date = date;
    if (notes) body.notes = notes;
    return body;
  }

  function queryParams() {
    const params = new URLSearchParams();

    const add = (k, v) => {
      if (v !== "" && v != null) params.set(k, String(v));
    };

    add("type", q("filter-type").value);
    add("category", q("filter-category").value.trim());
    add("created_by", q("filter-created-by").value.trim());
    add("start_date", q("filter-start-date").value);
    add("end_date", q("filter-end-date").value);
    add("limit", q("filter-limit").value.trim());
    add("offset", q("filter-offset").value.trim());

    const asString = params.toString();
    return asString ? `?${asString}` : "";
  }

  async function safeRun(fn) {
    try {
      await fn();
    } catch (err) {
      q("response-console").textContent = String(err.message || err);
    }
  }

  q("btn-records-create")?.addEventListener("click", () =>
    safeRun(() => request("POST", "/api/v1/records", createPayload(), { outputId: "response-console", allowError: true }))
  );

  q("btn-records-list")?.addEventListener("click", () =>
    safeRun(() => request("GET", `/api/v1/records${queryParams()}`, null, { outputId: "response-console", allowError: true }))
  );

  q("btn-records-get")?.addEventListener("click", () =>
    safeRun(() => request("GET", `/api/v1/records/${requireId()}`, null, { outputId: "response-console", allowError: true }))
  );

  q("btn-records-update")?.addEventListener("click", () =>
    safeRun(() => request("PATCH", `/api/v1/records/${requireId()}`, updatePayload(), { outputId: "response-console", allowError: true }))
  );

  q("btn-records-delete")?.addEventListener("click", () =>
    safeRun(() => request("DELETE", `/api/v1/records/${requireId()}`, null, { outputId: "response-console", allowError: true }))
  );
})();
