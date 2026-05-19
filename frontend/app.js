const api = {
  summary: "/api/summary",
  testCases: "/api/test-cases",
  defects: "/api/defects",
};

const statusLabels = {
  not_started: "Not started",
  in_progress: "In progress",
  passed: "Passed",
  failed: "Failed",
  blocked: "Blocked",
  open: "Open",
  triaged: "Triaged",
  fixed: "Fixed",
  closed: "Closed",
};

let testCases = [];
let defects = [];

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return response.json();
}

async function loadDashboard() {
  const [summary, loadedTests, loadedDefects] = await Promise.all([
    request(api.summary),
    request(api.testCases),
    request(api.defects),
  ]);

  testCases = loadedTests;
  defects = loadedDefects;

  renderSummary(summary);
  renderTestCases();
  renderDefects();
  renderLinkedTestOptions();
}

function renderSummary(summary) {
  document.querySelector("#releaseScore").textContent = `${summary.release_readiness_score}%`;
  document.querySelector("#coverage").textContent = `${summary.automation_coverage}%`;
  document.querySelector("#activeDefects").textContent = summary.active_defects;
  document.querySelector("#modules").textContent = summary.modules_under_test.length;
  document.querySelector("#testCount").textContent = `${summary.total_test_cases} total`;
  document.querySelector("#defectCount").textContent = `${summary.total_defects} total`;
}

function renderTestCases() {
  const container = document.querySelector("#testCases");

  if (!testCases.length) {
    container.innerHTML = `<div class="empty">No test cases yet.</div>`;
    return;
  }

  container.innerHTML = testCases
    .map(
      (testCase) => `
        <article class="item">
          <div class="item-header">
            <h3>${escapeHtml(testCase.title)}</h3>
            <span class="pill ${statusColor(testCase.status)}">${statusLabels[testCase.status]}</span>
          </div>
          <div class="meta">
            <span class="pill">${escapeHtml(testCase.module)}</span>
            <span class="pill">${escapeHtml(testCase.priority)} priority</span>
            <span class="pill">${escapeHtml(testCase.owner)}</span>
            <span class="pill ${testCase.automated ? "green" : ""}">
              ${testCase.automated ? "Automated" : "Manual"}
            </span>
          </div>
          <p>${escapeHtml(testCase.expected_result)}</p>
          <div class="status-row">
            <select data-test-status="${testCase.id}">
              ${["not_started", "in_progress", "passed", "failed", "blocked"]
                .map(
                  (status) =>
                    `<option value="${status}" ${status === testCase.status ? "selected" : ""}>
                      ${statusLabels[status]}
                    </option>`
                )
                .join("")}
            </select>
          </div>
        </article>
      `
    )
    .join("");
}

function renderDefects() {
  const container = document.querySelector("#defects");

  if (!defects.length) {
    container.innerHTML = `<div class="empty">No defects logged.</div>`;
    return;
  }

  container.innerHTML = defects
    .map(
      (defect) => `
        <article class="item">
          <div class="item-header">
            <h3>${escapeHtml(defect.title)}</h3>
            <span class="pill ${severityColor(defect.severity)}">${escapeHtml(defect.severity)}</span>
          </div>
          <div class="meta">
            <span class="pill ${statusColor(defect.status)}">${statusLabels[defect.status]}</span>
            <span class="pill">
              ${defect.linked_test_case_title ? escapeHtml(defect.linked_test_case_title) : "No linked test"}
            </span>
          </div>
          <div class="status-row">
            <select data-defect-status="${defect.id}">
              ${["open", "triaged", "fixed", "closed"]
                .map(
                  (status) =>
                    `<option value="${status}" ${status === defect.status ? "selected" : ""}>
                      ${statusLabels[status]}
                    </option>`
                )
                .join("")}
            </select>
          </div>
        </article>
      `
    )
    .join("");
}

function renderLinkedTestOptions() {
  const select = document.querySelector("#linkedTestCase");
  select.innerHTML = `<option value="">No linked test</option>`;

  for (const testCase of testCases) {
    const option = document.createElement("option");
    option.value = testCase.id;
    option.textContent = testCase.title;
    select.appendChild(option);
  }
}

function statusColor(status) {
  if (["passed", "fixed", "closed"].includes(status)) return "green";
  if (["failed", "blocked", "open"].includes(status)) return "red";
  return "amber";
}

function severityColor(severity) {
  if (severity === "critical") return "red";
  if (severity === "major") return "amber";
  return "";
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.querySelector("#testForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  await request(api.testCases, {
    method: "POST",
    body: JSON.stringify({
      title: form.get("title"),
      module: form.get("module"),
      priority: form.get("priority"),
      owner: form.get("owner"),
      automated: form.get("automated") === "on",
      expected_result: form.get("expected_result"),
    }),
  });
  event.currentTarget.reset();
  await loadDashboard();
});

document.querySelector("#defectForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const linkedId = form.get("linked_test_case_id");
  await request(api.defects, {
    method: "POST",
    body: JSON.stringify({
      title: form.get("title"),
      severity: form.get("severity"),
      linked_test_case_id: linkedId ? Number(linkedId) : null,
    }),
  });
  event.currentTarget.reset();
  await loadDashboard();
});

document.addEventListener("change", async (event) => {
  const testId = event.target.dataset.testStatus;
  const defectId = event.target.dataset.defectStatus;

  if (testId) {
    await request(`/api/test-cases/${testId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status: event.target.value }),
    });
    await loadDashboard();
  }

  if (defectId) {
    await request(`/api/defects/${defectId}/status`, {
      method: "PUT",
      body: JSON.stringify({ status: event.target.value }),
    });
    await loadDashboard();
  }
});

loadDashboard().catch((error) => {
  document.body.insertAdjacentHTML(
    "afterbegin",
    `<div class="empty">Unable to load dashboard: ${escapeHtml(error.message)}</div>`
  );
});

