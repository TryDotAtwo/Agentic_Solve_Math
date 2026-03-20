const REFRESH_MS = 4000;
const SVG_NS = "http://www.w3.org/2000/svg";

let activeRunId = null;
let activeAgentId = "root.orchestrator";

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

function svgEl(tag, attrs = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      node.setAttribute(key, String(value));
    }
  });
  return node;
}

function formatTimestamp(value) {
  if (!value) return "No timestamp";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function truncate(value, limit = 180) {
  if (!value) return "No data yet.";
  return value.length > limit ? `${value.slice(0, limit - 3)}...` : value;
}

function departmentColorMap(payload) {
  const palette = [
    "#f4ad56",
    "#7ec6c4",
    "#f27c61",
    "#9cbf6a",
    "#b998ef",
    "#78a6ef",
    "#d9b36b",
    "#8fd0a7",
  ];
  const mapping = { root_command: "#f4ad56" };
  payload.root_team.departments.forEach((department, index) => {
    mapping[department.key] = palette[index % palette.length];
  });
  return mapping;
}

function agentMaps(payload) {
  const dossiersById = new Map(payload.agents.map((agent) => [agent.agent_id, agent]));
  const nodesById = new Map(payload.graph.nodes.map((node) => [node.id, node]));
  return { dossiersById, nodesById };
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
      label: "Runtime",
      value: runtimeStatus,
      meta: payload.runtime_status?.model ?? "No live launch recorded yet",
    },
    {
      label: "Agents",
      value: String(payload.stats.root_agents),
      meta: `${payload.root_team.department_count} departments in the root team`,
    },
    {
      label: "Runs",
      value: String(payload.stats.runs_total),
      meta: `Active ${payload.stats.runs_active} | completed ${payload.stats.runs_completed}`,
    },
    {
      label: "Subprojects",
      value: String(payload.stats.subprojects_total),
      meta: `Sessions ${payload.stats.sessions_total}`,
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

function polar(centerX, centerY, radius, angle) {
  return {
    x: centerX + Math.cos(angle) * radius,
    y: centerY + Math.sin(angle) * radius,
  };
}

function computeGraphLayout(payload, width, height) {
  const centerX = width / 2;
  const centerY = height / 2;
  const positions = {
    "root.orchestrator": { x: centerX, y: centerY, angle: -Math.PI / 2 },
  };
  const departments = payload.root_team.departments;
  const headRadius = Math.min(width, height) * 0.24;
  const staffRadius = Math.min(width, height) * 0.42;
  const startAngle = -Math.PI / 2;

  departments.forEach((department, index) => {
    const angle = startAngle + (index * Math.PI * 2) / departments.length;
    positions[department.head_agent_id] = { ...polar(centerX, centerY, headRadius, angle), angle };
    const members = department.staff_agent_ids;
    const spread = Math.max(0.34, Math.min(0.7, members.length * 0.18));
    members.forEach((agentId, memberIndex) => {
      const offset =
        members.length === 1 ? 0 : ((memberIndex / (members.length - 1)) - 0.5) * spread;
      positions[agentId] = {
        ...polar(centerX, centerY, staffRadius, angle + offset),
        angle: angle + offset,
      };
    });
  });

  return positions;
}

function shortNodeLabel(node) {
  if (node.rank === "executive") return "ROOT";
  const words = node.label.split(/\s+/).filter(Boolean);
  const initials = words.slice(0, 2).map((word) => word[0]).join("");
  return (initials || node.label.slice(0, 2)).toUpperCase();
}

function drawGraph(payload) {
  const container = document.getElementById("graph-surface");
  const meta = document.getElementById("graph-meta");
  container.innerHTML = "";
  meta.innerHTML = "";

  if (!payload.graph.nodes.length) {
    container.append(el("div", "empty-state", "No graph data available yet."));
    return;
  }

  const { dossiersById } = agentMaps(payload);
  if (!dossiersById.has(activeAgentId)) {
    activeAgentId = "root.orchestrator";
  }

  const width = 1180;
  const height = 760;
  const positions = computeGraphLayout(payload, width, height);
  const colors = departmentColorMap(payload);
  const selectedAgent = dossiersById.get(activeAgentId);

  meta.append(el("span", "pill", `${payload.graph.nodes.length} nodes`));
  meta.append(el("span", "pill", `${payload.graph.edges.length} hierarchy edges`));
  meta.append(el("span", "pill", `${payload.graph.call_edges.length} callable links`));
  meta.append(el("span", "pill pill--muted", `Selected: ${selectedAgent.display_name}`));

  const svg = svgEl("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": "Root multi-agent graph",
  });

  payload.graph.edges.forEach((edge) => {
    const source = positions[edge.source];
    const target = positions[edge.target];
    if (!source || !target) return;
    svg.append(
      svgEl("line", {
        class: "graph-edge",
        x1: source.x,
        y1: source.y,
        x2: target.x,
        y2: target.y,
      })
    );
  });

  payload.graph.call_edges
    .filter((edge) => edge.source === activeAgentId || edge.target === activeAgentId)
    .forEach((edge) => {
      const source = positions[edge.source];
      const target = positions[edge.target];
      if (!source || !target) return;
      const curve = 0.18;
      const controlX = (source.x + target.x) / 2 + (source.y - target.y) * curve;
      const controlY = (source.y + target.y) / 2 + (target.x - source.x) * curve;
      svg.append(
        svgEl("path", {
          class: `graph-edge graph-edge--call ${edge.target === activeAgentId ? "graph-edge--incoming" : ""}`.trim(),
          d: `M ${source.x} ${source.y} Q ${controlX} ${controlY} ${target.x} ${target.y}`,
        })
      );
    });

  payload.graph.nodes.forEach((node) => {
    const position = positions[node.id];
    if (!position) return;
    const radius = node.rank === "executive" ? 34 : node.rank === "head" ? 26 : 19;
    const group = svgEl("g", {
      class: `graph-node ${node.id === activeAgentId ? "is-active" : ""}`.trim(),
      transform: `translate(${position.x}, ${position.y})`,
      tabindex: "0",
    });

    group.addEventListener("click", () => {
      activeAgentId = node.id;
      renderDashboard(payload);
      if (activeRunId) loadRunDetail(activeRunId);
    });

    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activeAgentId = node.id;
        renderDashboard(payload);
        if (activeRunId) loadRunDetail(activeRunId);
      }
    });

    group.append(svgEl("circle", { class: "graph-node__halo", r: radius + 11 }));
    group.append(
      svgEl("circle", {
        class: "graph-node__shell",
        r: radius,
        fill: colors[node.department_key] || "#7ec6c4",
      })
    );

    if (node.shared_service) {
      group.append(
        svgEl("circle", {
          r: radius + 6,
          fill: "none",
          stroke: "rgba(255, 255, 255, 0.35)",
          "stroke-dasharray": "5 5",
        })
      );
    }

    const title = svgEl("title");
    title.textContent = `${node.label} | ${node.id}`;
    group.append(title);

    const label = svgEl("text", { class: "graph-node__label", x: 0, y: 0 });
    label.textContent = shortNodeLabel(node);
    group.append(label);

    const caption = svgEl("text", { class: "graph-node__caption", x: 0, y: radius + 20 });
    caption.textContent = truncate(node.label, 18);
    group.append(caption);

    const subCaption = svgEl("text", {
      class: "graph-node__caption graph-node__caption--muted",
      x: 0,
      y: radius + 35,
    });
    subCaption.textContent = node.rank === "executive" ? node.model : node.rank;
    group.append(subCaption);

    svg.append(group);
  });

  container.append(svg);
}

function renderInspector(payload) {
  const container = document.getElementById("agent-inspector");
  container.innerHTML = "";
  const { dossiersById } = agentMaps(payload);
  const departmentNames = Object.fromEntries(
    payload.root_team.departments.map((department) => [department.key, department.name])
  );
  departmentNames.root_command = "Root Command";

  const agent = dossiersById.get(activeAgentId) ?? payload.agents[0];
  if (!agent) {
    container.append(el("div", "empty-state", "No agent dossier available."));
    return;
  }

  const hero = el("section", "inspector__hero");
  hero.append(el("div", "subtle-eyebrow", agent.agent_id));
  hero.append(el("h3", "", agent.display_name));
  hero.append(
    el("div", "soft-copy", `${departmentNames[agent.department_key] || agent.department_key} | ${agent.rank}`)
  );
  const tags = el("div", "tag-row");
  tags.append(el("span", "tag", agent.preferred_model));
  tags.append(el("span", "tag", `${agent.allowed_tools.length} tool classes`));
  tags.append(el("span", "tag", `${agent.callable_agents.length} callable links`));
  if (agent.shared_service) tags.append(el("span", "tag tag--muted", "Shared service"));
  hero.append(tags);
  container.append(hero);

  [
    ["Base instructions", agent.instructions_excerpt],
    ["Working rules", agent.rules_excerpt],
    ["Private memory", agent.memory_excerpt],
    ["Reports", agent.reports_excerpt],
  ].forEach(([label, value]) => {
    const section = el("section", "inspector__section");
    section.append(el("h4", "", label));
    section.append(el("p", "soft-copy", value || "No content recorded yet."));
    container.append(section);
  });

  const paths = el("section", "inspector__section");
  paths.append(el("h4", "", "Private files"));
  const pathList = el("ul", "path-list");
  [
    ["Memory", agent.memory_path],
    ["Instructions", agent.instructions_path],
    ["Rules", agent.rules_path],
    ["Reports", agent.reports_path],
  ].forEach(([label, value]) => {
    const item = el("li", "");
    item.append(el("div", "metric-label", label));
    item.append(el("div", "mono soft-copy", value));
    pathList.append(item);
  });
  paths.append(pathList);
  container.append(paths);

  const links = el("section", "inspector__section");
  links.append(el("h4", "", "Reachable agents"));
  const linkRow = el("div", "tag-row");
  agent.callable_agents.forEach((agentId) => {
    const chip = el("button", "link-chip", agentId);
    chip.type = "button";
    chip.addEventListener("click", () => {
      activeAgentId = agentId;
      renderDashboard(payload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
    linkRow.append(chip);
  });
  if (!linkRow.children.length) {
    linkRow.append(el("span", "tag tag--muted", "No callable agents"));
  }
  links.append(linkRow);
  container.append(links);

  const writes = el("section", "inspector__section");
  writes.append(el("h4", "", "Writable surfaces"));
  const writeList = el("ul", "path-list");
  agent.write_roots.slice(0, 6).forEach((value) => {
    const item = el("li", "");
    item.append(el("div", "mono soft-copy", value));
    writeList.append(item);
  });
  writes.append(writeList);
  container.append(writes);
}

function renderMilestones(payload) {
  const container = document.getElementById("milestone-list");
  container.innerHTML = "";

  if (!payload.milestones.length) {
    container.append(el("div", "empty-state", "No department-head milestones have been recorded yet."));
    return;
  }

  payload.milestones.forEach((milestone) => {
    const card = el("article", "milestone-card");
    card.append(
      el("div", "subtle-eyebrow", `${milestone.department_key || "-"} | ${formatTimestamp(milestone.created_at)}`)
    );
    card.append(el("h3", "", milestone.title));
    card.append(el("div", "soft-copy", milestone.agent_id || "Unknown author"));
    card.append(el("p", "soft-copy", milestone.summary || "No summary provided."));

    const actions = el("ul", "timeline__actions");
    (milestone.next_actions || []).forEach((item) => actions.append(el("li", "", item)));
    if (!actions.children.length) {
      actions.append(el("li", "", "No next actions recorded."));
    }
    card.append(actions);
    container.append(card);
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
    row.append(el("div", "soft-copy", `Updated ${formatTimestamp(run.updated_at)}`));
    row.append(el("div", "soft-copy", `${run.artifact_count} artifacts | ${run.event_count} events`));
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
  const tags = el("div", "detail-tags");
  tags.append(el("span", `badge badge--${statusTone(payload.current_status)}`, payload.current_status));
  tags.append(el("span", "badge", handoff.requester_agent_id));
  tags.append(el("span", "badge", handoff.target_agent_id));
  overview.append(tags);

  const grid = el("div", "detail-grid");
  [
    ["Created", formatTimestamp(handoff.created_at)],
    ["Updated", formatTimestamp(payload.updated_at)],
    ["Handoff", handoff.handoff_id],
    ["Artifacts", String((payload.trace.artifacts || []).length)],
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
  const eventList = el("ul", "detail-list");
  (payload.trace.events || []).forEach((item) => eventList.append(el("li", "", item)));
  if (!eventList.children.length) {
    eventList.append(el("li", "", "No events recorded yet."));
  }
  tracePanel.append(eventList);
  const artifactList = el("ul", "detail-list");
  (payload.trace.artifacts || []).forEach((item) => artifactList.append(el("li", "mono", item)));
  if (!artifactList.children.length) {
    artifactList.append(el("li", "", "No canonical artifacts yet."));
  }
  tracePanel.append(artifactList);
  container.append(tracePanel);

  if (execution) {
    const executionPanel = el("section", "run-detail__panel");
    executionPanel.append(el("h3", "", "Execution"));
    executionPanel.append(el("div", "run-detail__body", `${execution.mode} | ${execution.status}`));
    executionPanel.append(el("div", "run-detail__value mono", execution.command.join(" ")));
    container.append(executionPanel);
  }

  if (result) {
    const resultPanel = el("section", "run-detail__panel");
    resultPanel.append(el("h3", "", "Result"));
    resultPanel.append(el("div", "run-detail__body", result.summary));
    const resultList = el("ul", "detail-list");
    (result.canonical_paths || []).forEach((item) => resultList.append(el("li", "mono", item)));
    if (!resultList.children.length) {
      resultList.append(el("li", "", "No canonical paths recorded."));
    }
    resultPanel.append(resultList);
    container.append(resultPanel);
  }
}

function renderWorkspace(payload) {
  const container = document.getElementById("workspace-grid");
  container.innerHTML = "";

  const latestIntake = payload.latest_intake;
  const cards = [
    {
      title: "Root workspace",
      body: payload.workspace.root,
      meta: `${payload.subprojects.length} isolated subprojects discovered`,
    },
    {
      title: "Canonical rules",
      body: payload.workspace.rules_dir,
      meta: "Root-managed documentation tree",
    },
    {
      title: "Latest intake",
      body: latestIntake?.source_file || payload.workspace.intake_dir,
      meta: latestIntake
        ? `${latestIntake.competition_links.length} competition links detected`
        : "No parsed intake available",
    },
    {
      title: "Session storage",
      body: payload.sessions.length ? payload.sessions.map((item) => item.name).join(", ") : "No session DB yet",
      meta: payload.sessions.length ? "SQLite sessions available" : "No SQLite sessions found",
    },
  ];

  cards.forEach((item) => {
    const card = el("article", "workspace-card");
    card.append(el("div", "card__label", item.title));
    card.append(el("p", "mono", item.body));
    card.append(el("p", "card__meta", item.meta));
    container.append(card);
  });

  if (payload.subprojects.length) {
    const projects = el("article", "workspace-card");
    projects.append(el("h3", "", "Visible subprojects"));
    payload.subprojects.forEach((project) => {
      projects.append(el("p", "soft-copy", `${project.name} | ${project.role}`));
    });
    container.append(projects);
  }
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
  document.getElementById("generated-at").textContent = `Snapshot ${formatTimestamp(payload.generated_at)}`;
  renderMissionControl(payload);
  drawGraph(payload);
  renderInspector(payload);
  renderMilestones(payload);
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
