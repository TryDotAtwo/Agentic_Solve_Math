const REFRESH_MS = 4000;

let activeRunId = null;

function statusTone(status) {
  if (["completed", "succeeded", "dry_run"].includes(status)) return "success";
  if (["failed", "execution_failed", "timed_out", "escalated"].includes(status)) return "failed";
  return "running";
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined && text !== null) node.textContent = text;
  return node;
}

function renderMissionControl(payload) {
  const container = document.getElementById("mission-control");
  container.innerHTML = "";

  const runtimeStatus = payload.runtime_status?.status ?? "idle";
  const cards = [
    {
      label: "Bootstrap",
      value: payload.bootstrap.configured ? "Ready" : "Missing",
      meta: `Route: ${payload.bootstrap.provider_route}`,
    },
    {
      label: "SDK",
      value: payload.sdk.available ? "Available" : "Unavailable",
      meta: payload.sdk.version ? `agents ${payload.sdk.version}` : payload.sdk.reason,
    },
    {
      label: "Root Runtime",
      value: runtimeStatus,
      meta: payload.runtime_status?.model ?? "No live launch recorded yet",
    },
    {
      label: "Runs",
      value: String(payload.stats.runs_total),
      meta: `active ${payload.stats.runs_active} • completed ${payload.stats.runs_completed}`,
    },
    {
      label: "Subprojects",
      value: String(payload.stats.subprojects_total),
      meta: `sessions ${payload.stats.sessions_total}`,
    },
    {
      label: "Latest Intake",
      value: payload.latest_intake ? String(payload.latest_intake.competition_links.length) : "0",
      meta: payload.latest_intake ? payload.latest_intake.source_file : "No intake file found",
    },
  ];

  cards.forEach((item) => {
    const card = el("article", "card");
    card.append(el("div", "card__label", item.label));
    card.append(el("div", "card__value", item.value));
    card.append(el("div", "card__meta", item.meta));
    container.append(card);
  });
}

function renderRootTeam(payload) {
  const summary = document.getElementById("root-team-summary");
  const departments = document.getElementById("department-grid");
  summary.innerHTML = "";
  departments.innerHTML = "";

  const manager = payload.root_team.manager;
  const summaryCards = [
    {
      label: "Manager",
      value: manager.display_name,
      meta: `${manager.agent_id} • ${manager.preferred_model}`,
    },
    {
      label: "Departments",
      value: String(payload.root_team.department_count),
      meta: `Agents total: ${payload.root_team.agent_count}`,
    },
    {
      label: "Shared Services",
      value: String(payload.root_team.shared_services.length),
      meta: payload.root_team.shared_services.map((item) => item.display_name).join(", ") || "None",
    },
  ];

  summaryCards.forEach((item) => {
    const card = el("article", "card");
    card.append(el("div", "card__label", item.label));
    card.append(el("div", "card__value", item.value));
    card.append(el("div", "card__meta", item.meta));
    summary.append(card);
  });

  payload.root_team.departments.forEach((department) => {
    const card = el("article", "department-card");
    card.append(el("div", "department-card__eyebrow", department.key.replaceAll("_", " ")));
    card.append(el("h3", "", department.name));
    card.append(el("div", "card__meta", `${department.head_display_name} • ${department.head_model}`));

    const list = el("ul", "mini-list");
    list.append(el("li", "", `Head: ${department.head_agent_id}`));
    list.append(el("li", "", `Staff: ${department.staff_count}`));
    list.append(el("li", "", `Shared services: ${department.shared_service_count}`));
    card.append(list);
    departments.append(card);
  });
}

function renderRunList(payload) {
  const container = document.getElementById("run-list");
  container.innerHTML = "";

  if (!payload.runs.length) {
    container.append(el("div", "empty-state", "No root-owned runs have been materialized yet."));
    document.getElementById("run-detail").innerHTML =
      '<div class="empty-state">A run detail panel will appear here after the first handoff is created.</div>';
    activeRunId = null;
    return;
  }

  if (!activeRunId || !payload.runs.some((item) => item.run_id === activeRunId)) {
    activeRunId = payload.runs[0].run_id;
  }

  payload.runs.forEach((run) => {
    const card = el("article", `run-card ${run.run_id === activeRunId ? "is-active" : ""}`.trim());
    card.addEventListener("click", () => {
      activeRunId = run.run_id;
      renderDashboard(payload);
      loadRunDetail(run.run_id);
    });

    card.append(el("div", "run-card__eyebrow", run.project_name));
    card.append(el("h3", "", run.run_id));
    card.append(el("div", "run-card__summary", run.objective));

    const row = el("div", "run-card__row");
    row.append(el("div", "card__meta", `Updated: ${run.updated_at}`));
    row.append(el("div", "card__meta", `Artifacts: ${run.artifact_count}`));
    card.append(row);

    const badges = el("div", "run-card__badges");
    badges.append(el("span", `badge badge--${statusTone(run.current_status)}`, run.current_status));
    badges.append(el("span", "badge", `trace ${run.trace_status}`));
    if (run.execution_status) badges.append(el("span", "badge", `exec ${run.execution_status}`));
    if (run.result_status) badges.append(el("span", "badge", `result ${run.result_status}`));
    card.append(badges);

    const progress = el("div", "progress");
    const bar = el("span");
    bar.style.width = `${run.progress_percent}%`;
    progress.append(bar);
    card.append(progress);

    container.append(card);
  });
}

async function loadRunDetail(runId) {
  const container = document.getElementById("run-detail");
  container.innerHTML = '<div class="empty-state">Loading canonical run payload...</div>';

  const response = await fetch(`/api/run/${encodeURIComponent(runId)}`);
  const payload = await response.json();

  if (!response.ok) {
    container.innerHTML = `<div class="empty-state">Failed to load run detail for ${runId}.</div>`;
    return;
  }

  const handoff = payload.handoff;
  const taskRequest = handoff.task_request;
  const result = payload.result;
  const execution = payload.execution;

  container.innerHTML = "";

  const overview = el("section", "run-detail__panel");
  overview.append(el("div", "run-card__eyebrow", handoff.routing_decision.target_name));
  overview.append(el("h3", "", payload.run_id));
  overview.append(el("div", "run-detail__body", taskRequest.objective));

  const grid = el("div", "detail-grid");
  [
    ["Current status", payload.current_status],
    ["Requester", handoff.requester_agent_id],
    ["Target", handoff.target_agent_id],
    ["Created", handoff.created_at],
    ["Updated", payload.updated_at],
    ["Handoff", handoff.handoff_id],
  ].forEach(([label, value]) => {
    const box = el("div", "card");
    box.append(el("div", "card__label", label));
    box.append(el("div", "run-detail__value mono", value));
    grid.append(box);
  });
  overview.append(grid);
  container.append(overview);

  const tracePanel = el("section", "run-detail__panel");
  tracePanel.append(el("h3", "", "Trace"));
  tracePanel.append(el("div", "run-detail__body", (payload.trace.events || []).join(" • ") || "No events yet"));
  tracePanel.append(
    el("div", "run-detail__value mono", (payload.trace.artifacts || []).join("\n") || "No artifacts")
  );
  container.append(tracePanel);

  if (execution) {
    const executionPanel = el("section", "run-detail__panel");
    executionPanel.append(el("h3", "", "Execution"));
    executionPanel.append(el("div", "run-detail__body", `${execution.mode} • ${execution.status}`));
    executionPanel.append(el("div", "run-detail__value mono", execution.command.join(" ")));
    container.append(executionPanel);
  }

  if (result) {
    const resultPanel = el("section", "run-detail__panel");
    resultPanel.append(el("h3", "", "Result"));
    resultPanel.append(el("div", "run-detail__body", result.summary));
    resultPanel.append(
      el("div", "run-detail__value mono", (result.canonical_paths || []).join("\n") || "No canonical paths")
    );
    container.append(resultPanel);
  }
}

function renderWorkspace(payload) {
  const container = document.getElementById("workspace-grid");
  container.innerHTML = "";

  const cards = [
    {
      label: "Root Path",
      value: payload.workspace.root,
      meta: `${payload.workspace.subprojects.length} isolated subprojects discovered`,
    },
    {
      label: "Rules Tree",
      value: payload.workspace.rules_dir,
      meta: "Canonical root documentation",
    },
    {
      label: "Intake",
      value: payload.workspace.intake_dir,
      meta: payload.latest_intake ? payload.latest_intake.source_file : "No parsed intake available",
    },
    {
      label: "Session Storage",
      value: payload.sessions.length ? payload.sessions[0].name : "No session DB yet",
      meta: payload.sessions.map((item) => item.name).join(", ") || "No SQLite sessions found",
    },
  ];

  cards.forEach((item) => {
    const card = el("article", "card");
    card.append(el("div", "card__label", item.label));
    card.append(el("div", "run-detail__value mono", item.value));
    card.append(el("div", "card__meta", item.meta));
    container.append(card);
  });
}

function renderLogs(payload) {
  const container = document.getElementById("log-columns");
  container.innerHTML = "";

  const columns = [
    ["Research Journal", payload.logs.research_journal],
    ["Agent Interactions", payload.logs.agent_interactions],
    ["User Prompts", payload.logs.user_prompts],
  ];

  columns.forEach(([label, entries]) => {
    const stack = el("section", "log-stack");
    stack.append(el("h3", "", label));
    if (!entries.length) {
      stack.append(el("div", "empty-state", `No entries in ${label} yet.`));
      container.append(stack);
      return;
    }
    entries.forEach((entry) => {
      const card = el("article", "log-card");
      card.append(el("div", "log-card__source", entry.source));
      card.append(el("h3", "", entry.title));
      card.append(el("div", "log-card__excerpt", entry.excerpt || "No excerpt available."));
      stack.append(card);
    });
    container.append(stack);
  });
}

function renderDashboard(payload) {
  document.getElementById("generated-at").textContent = `Snapshot: ${payload.generated_at}`;
  renderMissionControl(payload);
  renderRootTeam(payload);
  renderRunList(payload);
  renderWorkspace(payload);
  renderLogs(payload);
}

async function refreshDashboard() {
  const response = await fetch("/api/dashboard");
  const payload = await response.json();
  renderDashboard(payload);
  if (activeRunId) {
    loadRunDetail(activeRunId);
  }
}

refreshDashboard();
setInterval(refreshDashboard, REFRESH_MS);
