const REFRESH_MS = 4000;
const SVG_NS = "http://www.w3.org/2000/svg";

let activeRunId = null;
let activeAgentId = "root.orchestrator";
let activeDialogueThreadKey = null;
let activeDialogueFilter = "all";
let latestPayload = null;

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
  if (!value) return "";
  return value.length > limit ? `${value.slice(0, limit - 3)}...` : value;
}

function statusTone(status) {
  if (["completed", "succeeded", "dry_run"].includes(status)) return "success";
  if (["failed", "execution_failed", "timed_out", "escalated"].includes(status)) return "failed";
  return "running";
}

function combinedAgents(payload) {
  const rootAgents = payload.agents || [];
  const subprojectAgents = payload.subproject_focus?.agents || [];
  return [...rootAgents, ...subprojectAgents];
}

function agentMap(payload) {
  return new Map(combinedAgents(payload).map((agent) => [agent.agent_id, agent]));
}

function colorMapFromGraph(graph) {
  const palette = [
    "#f4ad56",
    "#7ec6c4",
    "#f27c61",
    "#9cbf6a",
    "#b998ef",
    "#78a6ef",
    "#d9b36b",
    "#8fd0a7",
    "#c98f7a",
    "#76c8dd",
  ];
  const keys = [...new Set((graph?.nodes || []).map((node) => node.department_key))];
  const mapping = {};
  keys.forEach((key, index) => {
    mapping[key] = palette[index % palette.length];
  });
  return mapping;
}

function ensureActiveAgent(payload) {
  const agents = agentMap(payload);
  if (!agents.has(activeAgentId)) {
    activeAgentId = payload.current_focus?.active_agent_id || "root.orchestrator";
  }
  if (!agents.has(activeAgentId) && combinedAgents(payload).length) {
    activeAgentId = combinedAgents(payload)[0].agent_id;
  }
}

function findAgentLabel(payload, agentId) {
  if (!agentId) return "Unknown agent";
  return agentMap(payload).get(agentId)?.display_name || agentId;
}

function agentScope(agentId) {
  if (!agentId) return null;
  return agentId.startsWith("subproject.") ? "subproject" : "root";
}

function shortNodeLabel(node) {
  if (node.rank === "executive") return "ROOT";
  if (node.rank === "head") {
    const words = node.label.split(/\s+/).filter(Boolean);
    return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase();
  }
  const words = node.label.split(/\s+/).filter(Boolean);
  return (words[0]?.slice(0, 2) || node.label.slice(0, 2)).toUpperCase();
}

function graphHierarchy(graph) {
  const executive = graph.nodes.find((node) => node.rank === "executive") || graph.nodes[0];
  const headNodes = graph.nodes
    .filter((node) => node.rank === "head")
    .sort((left, right) => left.label.localeCompare(right.label));
  const staffNodes = graph.nodes
    .filter((node) => node.rank === "staff")
    .sort((left, right) => left.label.localeCompare(right.label));
  const staffByHead = new Map(headNodes.map((head) => [head.id, []]));

  graph.edges.forEach((edge) => {
    if (!staffByHead.has(edge.source)) return;
    const list = staffByHead.get(edge.source);
    if (list) list.push(edge.target);
  });

  const unassignedStaff = staffNodes
    .map((node) => node.id)
    .filter((agentId) => ![...staffByHead.values()].some((items) => items.includes(agentId)));
  if (unassignedStaff.length && headNodes.length) {
    staffByHead.get(headNodes[0].id).push(...unassignedStaff);
  }

  return { executive, headNodes, staffByHead };
}

function polar(centerX, centerY, radius, angle) {
  return {
    x: centerX + Math.cos(angle) * radius,
    y: centerY + Math.sin(angle) * radius,
  };
}

function computeRadialGraphLayout(graph, width, height, centerX = width / 2, centerY = height / 2) {
  const positions = {};
  const { executive, headNodes, staffByHead } = graphHierarchy(graph);
  positions[executive.id] = { x: centerX, y: centerY, angle: -Math.PI / 2 };

  if (!headNodes.length) {
    graph.nodes
      .filter((node) => node.id !== executive.id)
      .forEach((node, index, list) => {
        const angle = -Math.PI / 2 + (index * Math.PI * 2) / Math.max(1, list.length);
        positions[node.id] = {
          ...polar(centerX, centerY, Math.min(width, height) * 0.34, angle),
          angle,
        };
      });
    return positions;
  }

  const headRadius = Math.min(width, height) * 0.24;
  const staffRadius = Math.min(width, height) * 0.42;
  const outerRadius = Math.min(width, height) * 0.48;
  const startAngle = -Math.PI / 2;

  headNodes.forEach((head, index) => {
    const angle = startAngle + (index * Math.PI * 2) / headNodes.length;
    positions[head.id] = { ...polar(centerX, centerY, headRadius, angle), angle };

    const staff = (staffByHead.get(head.id) || []).slice().sort();
    const spread = Math.max(0.34, Math.min(0.82, staff.length * 0.18));
    staff.forEach((agentId, memberIndex) => {
      const offset =
        staff.length <= 1 ? 0 : ((memberIndex / (staff.length - 1)) - 0.5) * spread;
      positions[agentId] = {
        ...polar(centerX, centerY, staffRadius, angle + offset),
        angle: angle + offset,
      };
    });
  });

  graph.nodes.forEach((node, index) => {
    if (!positions[node.id]) {
      const angle = startAngle + (index * Math.PI * 2) / Math.max(1, graph.nodes.length - 1);
      positions[node.id] = {
        ...polar(centerX, centerY, outerRadius, angle),
        angle,
      };
    }
  });
  return positions;
}

function drawGraphElements(svg, graph, positions, colors, focusState, graphScope) {
  graph.edges.forEach((edge) => {
    const source = positions[edge.source];
    const target = positions[edge.target];
    if (!source || !target) return;
    svg.append(svgEl("line", { class: "graph-edge", x1: source.x, y1: source.y, x2: target.x, y2: target.y }));
  });

  if (
    focusState?.sourceScope === graphScope &&
    focusState?.targetScope === graphScope &&
    focusState?.sourceAgentId &&
    focusState?.targetAgentId
  ) {
    const source = positions[focusState.sourceAgentId];
    const target = positions[focusState.targetAgentId];
    if (source && target) {
      svg.append(
        svgEl("line", {
          class: "graph-edge graph-edge--focus-route",
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
        })
      );
    }
  }

  graph.call_edges
    .filter((edge) => edge.source === activeAgentId || edge.target === activeAgentId)
    .forEach((edge) => {
      const source = positions[edge.source];
      const target = positions[edge.target];
      if (!source || !target) return;
      const controlX = (source.x + target.x) / 2 + (source.y - target.y) * 0.18;
      const controlY = (source.y + target.y) / 2 + (target.x - source.x) * 0.18;
      svg.append(
        svgEl("path", {
          class: `graph-edge graph-edge--call ${edge.target === activeAgentId ? "graph-edge--incoming" : ""}`.trim(),
          d: `M ${source.x} ${source.y} Q ${controlX} ${controlY} ${target.x} ${target.y}`,
        })
      );
    });

  graph.nodes.forEach((node) => {
    const position = positions[node.id];
    if (!position) return;
    const radius = node.rank === "executive" ? 30 : node.rank === "head" ? 24 : 18;
    const classes = ["graph-node"];
    if (node.id === activeAgentId) classes.push("is-active");
    if (node.id === focusState?.sourceAgentId) classes.push("graph-node--focus-source");
    if (node.id === focusState?.targetAgentId) classes.push("graph-node--focus-target");
    if (node.id === focusState?.sourceAgentId || node.id === focusState?.targetAgentId) {
      classes.push("graph-node--focus-route");
    }
    const group = svgEl("g", {
      class: classes.join(" "),
      transform: `translate(${position.x}, ${position.y})`,
      tabindex: "0",
    });

    group.addEventListener("click", () => {
      activeAgentId = node.id;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
    group.addEventListener("keydown", (event) => {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        activeAgentId = node.id;
        renderDashboard(latestPayload);
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
          r: radius + 5,
          fill: "none",
          stroke: "rgba(255, 255, 255, 0.38)",
          "stroke-dasharray": "5 4",
        })
      );
    }

    const title = svgEl("title");
    title.textContent = `${node.label} | ${node.id}`;
    group.append(title);

    const label = svgEl("text", { class: "graph-node__label", x: 0, y: 0 });
    label.textContent = shortNodeLabel(node);
    group.append(label);

    const caption = svgEl("text", { class: "graph-node__caption", x: 0, y: radius + 18 });
    caption.textContent = truncate(node.label, 18);
    group.append(caption);

    const subCaption = svgEl("text", {
      class: "graph-node__caption graph-node__caption--muted",
      x: 0,
      y: radius + 32,
    });
    subCaption.textContent = node.rank === "executive" ? node.model : node.rank;
    group.append(subCaption);

    svg.append(group);
  });
}

function dialogueConsoleState(payload) {
  const entries = filteredDialogueEntries(payload.dialogue_feed);
  const threads = buildDialogueThreads(entries);
  const selectedThread = ensureActiveDialogueThread(threads);
  return { entries, threads, selectedThread };
}

function buildDialogueFocusState(payload) {
  const { selectedThread } = dialogueConsoleState(payload);
  const entry = selectedThread?.lastEntry;
  if (!entry?.agent_id) return null;
  const sourceAgentId = entry.agent_id;
  const targetAgentId = entry.target_agent_id || null;
  const sourceScope = agentScope(sourceAgentId);
  const targetScope = agentScope(targetAgentId);
  const crossTeam = Boolean(sourceScope && targetScope && sourceScope !== targetScope);
  const sameTeam = Boolean(sourceScope && targetScope && sourceScope === targetScope);
  return {
    sourceAgentId,
    targetAgentId,
    sourceScope,
    targetScope,
    crossTeam,
    sameTeam,
    threadKey: selectedThread.key,
    routeLabel: targetAgentId
      ? `${findAgentLabel(payload, sourceAgentId)} -> ${findAgentLabel(payload, targetAgentId)}`
      : findAgentLabel(payload, sourceAgentId),
    summary: entry.summary || entry.transcript || "No summary recorded.",
    eventType: dialogueType(entry),
    phase: entry.phase || null,
    eventCount: selectedThread.entries.length,
    projectName: selectedThread.project_name || entry.project_name || null,
  };
}

function renderTopologyStage(payload) {
  const container = document.getElementById("topology-surface");
  const rootMeta = document.getElementById("root-graph-meta");
  const bridgeMeta = document.getElementById("topology-bridge-meta");
  const subMeta = document.getElementById("subproject-graph-meta");
  const focusContainer = document.getElementById("topology-focus");
  container.innerHTML = "";
  rootMeta.innerHTML = "";
  bridgeMeta.innerHTML = "";
  subMeta.innerHTML = "";
  focusContainer.innerHTML = "";

  const rootGraph = payload.graph;
  const subGraph = payload.subproject_focus?.graph || null;
  const focusState = buildDialogueFocusState(payload);
  if (!rootGraph || !rootGraph.nodes?.length) {
    container.append(el("div", "empty-state", "Topology graph is not available yet."));
    return;
  }

  const width = 1720;
  const height = 780;
  const rootCenterX = subGraph ? 430 : width / 2;
  const subCenterX = 1290;
  const centerY = 430;
  const layoutSize = 610;
  const rootPositions = computeRadialGraphLayout(rootGraph, layoutSize, layoutSize, rootCenterX, centerY);
  const subPositions = subGraph
    ? computeRadialGraphLayout(subGraph, layoutSize, layoutSize, subCenterX, centerY)
    : {};
  const rootSelected = rootGraph.nodes.find((node) => node.id === activeAgentId) || rootGraph.nodes[0];
  const subSelected = subGraph?.nodes.find((node) => node.id === activeAgentId) || subGraph?.nodes?.[0] || null;

  rootMeta.append(el("span", "pill", `${rootGraph.nodes.length} nodes`));
  rootMeta.append(el("span", "pill", `${rootGraph.edges.length} hierarchy edges`));
  rootMeta.append(el("span", "pill", `${rootGraph.call_edges.length} callable links`));
  rootMeta.append(el("span", "pill pill--muted", `Selected: ${rootSelected.label}`));

  if (subGraph) {
    subMeta.append(el("span", "pill", `${subGraph.nodes.length} nodes`));
    subMeta.append(el("span", "pill", `${subGraph.edges.length} hierarchy edges`));
    subMeta.append(el("span", "pill", `${subGraph.call_edges.length} callable links`));
    subMeta.append(el("span", "pill pill--muted", `Selected: ${subSelected?.label || "Subproject Commander"}`));
  } else {
    subMeta.append(el("span", "pill pill--muted", "No active subproject graph"));
  }

  const bridge = payload.team_bridge;
  if (bridge) {
    bridgeMeta.append(el("span", `badge badge--${statusTone(bridge.current_status)}`, bridge.current_status || "idle"));
    if (bridge.run_id) bridgeMeta.append(el("span", "badge", bridge.run_id));
    if (bridge.handoff_id) bridgeMeta.append(el("span", "badge", bridge.handoff_id));
  } else {
    bridgeMeta.append(el("span", "pill pill--muted", "No active bridge"));
  }

  const focusCard = el("section", "topology-focus__card");
  focusCard.append(el("div", "subtle-eyebrow", "Route focus"));
  if (focusState) {
    focusCard.append(el("div", "topology-focus__title", focusState.routeLabel));
    focusCard.append(el("p", "soft-copy", truncate(focusState.summary, 180)));
    const focusPills = el("div", "toolbar-pills");
    focusPills.append(el("span", "pill", `${focusState.eventCount} events`));
    focusPills.append(el("span", "pill", focusState.eventType));
    if (focusState.phase) focusPills.append(el("span", "pill pill--muted", focusState.phase));
    focusPills.append(
      el(
        "span",
        `pill ${focusState.crossTeam ? "" : "pill--muted"}`.trim(),
        focusState.crossTeam ? "Cross-team route" : "In-team route"
      )
    );
    focusCard.append(focusPills);
  } else {
    focusCard.append(el("div", "topology-focus__title", "Topology synced to active agent"));
    focusCard.append(
      el("p", "soft-copy", "Select a dialogue thread to highlight the exact route between agents on the graphs.")
    );
  }
  focusContainer.append(focusCard);

  const svg = svgEl("svg", {
    viewBox: `0 0 ${width} ${height}`,
    role: "img",
    "aria-label": "Root and active subproject topology stage",
  });

  const defs = svgEl("defs");
  const gradient = svgEl("linearGradient", { id: "bridge-gradient", x1: "0%", y1: "0%", x2: "100%", y2: "0%" });
  gradient.append(svgEl("stop", { offset: "0%", "stop-color": "rgba(244, 173, 86, 0.18)" }));
  gradient.append(svgEl("stop", { offset: "50%", "stop-color": "rgba(255, 255, 255, 0.18)" }));
  gradient.append(svgEl("stop", { offset: "100%", "stop-color": "rgba(126, 198, 196, 0.18)" }));
  defs.append(gradient);
  svg.append(defs);

  svg.append(svgEl("circle", { class: "topology-orbit", cx: rootCenterX, cy: centerY, r: 246 }));
  if (subGraph) {
    svg.append(svgEl("circle", { class: "topology-orbit topology-orbit--sub", cx: subCenterX, cy: centerY, r: 246 }));
  }

  const rootLabel = svgEl("text", { class: "topology-stage__label", x: rootCenterX, y: 74 });
  rootLabel.textContent = "Root Team";
  svg.append(rootLabel);

  const rootCaption = svgEl("text", { class: "topology-stage__caption", x: rootCenterX, y: 100 });
  rootCaption.textContent = "Command hierarchy and internal callable links";
  svg.append(rootCaption);

  if (subGraph) {
    const subLabel = svgEl("text", { class: "topology-stage__label", x: subCenterX, y: 74 });
    subLabel.textContent = payload.subproject_focus?.project_name || "Active Subproject";
    svg.append(subLabel);

    const subCaption = svgEl("text", { class: "topology-stage__caption", x: subCenterX, y: 100 });
    subCaption.textContent = "Focused local team and its internal routing";
    svg.append(subCaption);
  }

  if ((bridge && subGraph) || (focusState?.crossTeam && subGraph)) {
    const bridgeSourceId = focusState?.crossTeam && focusState.sourceScope === "root"
      ? focusState.sourceAgentId
      : bridge?.source_agent_id;
    const bridgeTargetId = focusState?.crossTeam && focusState.targetScope === "subproject"
      ? focusState.targetAgentId
      : bridge?.target_agent_id;
    const source = rootPositions[bridgeSourceId] || rootPositions[rootGraph.nodes[0].id];
    const target = subPositions[bridgeTargetId] || subPositions[subGraph.nodes[0].id];
    if (source && target) {
      const bridgeLine = svgEl("line", {
        class: `graph-edge graph-edge--bridge ${focusState?.crossTeam ? "graph-edge--bridge-focus" : ""}`.trim(),
        x1: source.x,
        y1: source.y,
        x2: target.x,
        y2: target.y,
      });
      svg.append(bridgeLine);
    }
  }

  drawGraphElements(svg, rootGraph, rootPositions, colorMapFromGraph(rootGraph), focusState, "root");
  if (subGraph) {
    drawGraphElements(svg, subGraph, subPositions, colorMapFromGraph(subGraph), focusState, "subproject");
  }

  container.append(svg);
}

function renderSignal(payload) {
  const container = document.getElementById("signal-grid");
  container.innerHTML = "";

  const focus = payload.current_focus || {};
  const cards = [
    ["Runtime", focus.status || "idle", payload.runtime_status?.model || "No active model"],
    ["Scope", focus.active_scope || "root", focus.active_team_id || "No active team"],
    ["Active agent", focus.active_agent_name || focus.active_agent_id || "No active agent", focus.active_department_key || "No department"],
    ["Project focus", focus.active_project_name || payload.subproject_focus?.project_name || "No active subproject", focus.active_run_id || "No active run"],
    ["Phase", focus.current_phase || "idle", focus.last_event_type || "No recent event type"],
    ["Last change", focus.last_event_summary || "No runtime events recorded yet", formatTimestamp(focus.last_event_at)],
  ];

  cards.forEach(([label, value, meta]) => {
    const card = el("article", "signal-card");
    card.append(el("div", "card__label", label));
    card.append(el("div", "card__value signal-card__value", value));
    card.append(el("div", "card__meta", meta));
    container.append(card);
  });
}

function renderMissionControl(payload) {
  const container = document.getElementById("mission-control");
  container.innerHTML = "";
  const cards = [
    ["Bootstrap", payload.bootstrap.configured ? "Ready" : "Missing", `Route: ${payload.bootstrap.provider_route}`],
    ["SDK", payload.sdk.available ? "Available" : "Unavailable", payload.sdk.version ? `agents ${payload.sdk.version}` : payload.sdk.reason],
    ["Events", String(payload.current_focus?.event_count || 0), `${payload.live_events.length} recent events in feed`],
    ["Runs", String(payload.stats.runs_total), `Active ${payload.stats.runs_active} | completed ${payload.stats.runs_completed}`],
    ["Root team", String(payload.root_team.agent_count), `${payload.root_team.department_count} departments`],
    ["Subproject focus", payload.subproject_focus?.project_name || "None", payload.subproject_focus ? `${payload.subproject_focus.agent_count} agents` : "No focused subproject"],
  ];

  cards.forEach(([label, value, meta]) => {
    const card = el("article", "card");
    card.append(el("div", "card__label", label));
    card.append(el("div", "card__value", value));
    card.append(el("div", "card__meta", meta));
    container.append(card);
  });
}

function renderInspector(payload) {
  const container = document.getElementById("agent-inspector");
  container.innerHTML = "";
  const agents = agentMap(payload);
  const agent = agents.get(activeAgentId);

  if (!agent) {
    container.append(el("div", "empty-state", "No agent dossier available yet."));
    return;
  }

  const hero = el("section", "inspector__hero");
  hero.append(el("div", "subtle-eyebrow", agent.agent_id));
  hero.append(el("h3", "", agent.display_name));
  hero.append(el("div", "soft-copy", `${agent.department_key} | ${agent.rank} | ${agent.scope}`));
  const tags = el("div", "tag-row");
  tags.append(el("span", "tag", agent.preferred_model));
  tags.append(el("span", "tag", `${agent.callable_agents.length} callable agents`));
  tags.append(el("span", "tag", `${agent.allowed_tools.length} tool classes`));
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

  const linkSection = el("section", "inspector__section");
  linkSection.append(el("h4", "", "Reachable agents"));
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
  linkSection.append(linkRow);
  container.append(linkSection);

  const fileSection = el("section", "inspector__section");
  fileSection.append(el("h4", "", "Private surfaces"));
  const paths = el("ul", "path-list");
  [
    ["Memory", agent.memory_path],
    ["Instructions", agent.instructions_path],
    ["Rules", agent.rules_path],
    ["Reports", agent.reports_path],
  ].forEach(([label, value]) => {
    const item = el("li", "");
    item.append(el("div", "metric-label", label));
    item.append(el("div", "mono soft-copy", value));
    paths.append(item);
  });
  fileSection.append(paths);
  container.append(fileSection);
}

function feedCard(entry, variant) {
  const card = el("article", `feed-card ${variant ? `feed-card--${variant}` : ""}`.trim());
  const eyebrow = entry.project_name
    ? `${entry.scope || "-"} | ${entry.project_name} | ${formatTimestamp(entry.created_at)}`
    : `${entry.scope || "-"} | ${formatTimestamp(entry.created_at)}`;
  card.append(el("div", "subtle-eyebrow", eyebrow));
  card.append(el("h3", "", entry.title || entry.event_type || "Event"));

  const meta = [];
  if (entry.agent_name || entry.agent_id) meta.push(entry.agent_name || entry.agent_id);
  if (entry.target_agent_name || entry.target_agent_id) meta.push(`to ${entry.target_agent_name || entry.target_agent_id}`);
  if (entry.tool_name) meta.push(entry.tool_name);
  if (entry.phase) meta.push(entry.phase);
  if (meta.length) card.append(el("div", "soft-copy", meta.join(" | ")));

  card.append(el("p", "soft-copy", entry.summary || "No summary recorded."));
  if (entry.transcript) {
    card.append(el("div", "feed-card__transcript", entry.transcript));
  }

  if (entry.agent_id) {
    card.addEventListener("click", () => {
      activeAgentId = entry.agent_id;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
  }
  return card;
}

function dialogueType(entry) {
  if (!entry) return "all";
  if (entry.event_type === "handoff") return "handoff";
  if (entry.event_type === "tool_called" || entry.event_type === "tool_output") return "tool";
  return "message";
}

function filteredDialogueEntries(entries) {
  if (activeDialogueFilter === "all") return entries || [];
  return (entries || []).filter((entry) => dialogueType(entry) === activeDialogueFilter);
}

function dialogueThreadKey(entry) {
  const project = entry.project_name || entry.scope || "root";
  const participants = [entry.agent_id, entry.target_agent_id].filter(Boolean);
  const stableParticipants = [...new Set(participants)].sort();
  const identity = stableParticipants.length ? stableParticipants.join("::") : entry.event_type || "event";
  return `${project}::${identity}`;
}

function buildDialogueThreads(entries) {
  const grouped = new Map();
  [...(entries || [])]
    .reverse()
    .forEach((entry) => {
      const key = dialogueThreadKey(entry);
      if (!grouped.has(key)) {
        grouped.set(key, {
          key,
          project_name: entry.project_name || null,
          scope: entry.scope || null,
          entries: [],
        });
      }
      grouped.get(key).entries.push(entry);
    });

  return [...grouped.values()]
    .map((thread) => ({
      ...thread,
      lastEntry: thread.entries[thread.entries.length - 1],
    }))
    .sort((left, right) => {
      const leftTime = Date.parse(left.lastEntry?.created_at || "") || 0;
      const rightTime = Date.parse(right.lastEntry?.created_at || "") || 0;
      return rightTime - leftTime;
    });
}

function ensureActiveDialogueThread(threads) {
  if (!threads.length) {
    activeDialogueThreadKey = null;
    return null;
  }
  if (!threads.some((thread) => thread.key === activeDialogueThreadKey)) {
    activeDialogueThreadKey = threads[0].key;
  }
  return threads.find((thread) => thread.key === activeDialogueThreadKey) || threads[0];
}

function dialogueThreadTitle(payload, thread) {
  const lastEntry = thread.lastEntry;
  if (!lastEntry) return "Dialogue thread";
  if (lastEntry.agent_id && lastEntry.target_agent_id) {
    return `${findAgentLabel(payload, lastEntry.agent_id)} <-> ${findAgentLabel(payload, lastEntry.target_agent_id)}`;
  }
  if (lastEntry.agent_id) {
    return findAgentLabel(payload, lastEntry.agent_id);
  }
  return thread.project_name || "Dialogue thread";
}

function renderDialogueConsole(payload) {
  const filterContainer = document.getElementById("dialogue-filters");
  const listContainer = document.getElementById("dialogue-list");
  const detailContainer = document.getElementById("dialogue-detail");
  const { threads, selectedThread } = dialogueConsoleState(payload);

  filterContainer.innerHTML = "";
  listContainer.innerHTML = "";
  detailContainer.innerHTML = "";

  [
    ["all", "All"],
    ["message", "Messages"],
    ["handoff", "Handoffs"],
    ["tool", "Tools"],
  ].forEach(([value, label]) => {
    const chip = el("button", `filter-chip ${activeDialogueFilter === value ? "is-active" : ""}`.trim(), label);
    chip.type = "button";
    chip.addEventListener("click", () => {
      activeDialogueFilter = value;
      activeDialogueThreadKey = null;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
    filterContainer.append(chip);
  });

  if (!threads.length) {
    listContainer.append(el("div", "empty-state", "No dialogue events match the current filter."));
    detailContainer.append(el("div", "empty-state", "Choose a dialogue event to inspect its transcript and metadata."));
    return;
  }

  threads.forEach((thread) => {
    const entry = thread.lastEntry;
    const crossTeam =
      agentScope(entry.agent_id) && agentScope(entry.target_agent_id) && agentScope(entry.agent_id) !== agentScope(entry.target_agent_id);
    const item = el(
      "article",
      `dialogue-item ${thread.key === activeDialogueThreadKey ? "is-active" : ""} ${crossTeam ? "dialogue-item--cross-team" : ""}`.trim()
    );
    item.addEventListener("click", () => {
      activeDialogueThreadKey = thread.key;
      if (entry.agent_id) activeAgentId = entry.agent_id;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });

    const header = el("div", "dialogue-item__header");
    header.append(el("span", "dialogue-item__type", dialogueType(entry)));
    header.append(el("span", "dialogue-item__time", formatTimestamp(entry.created_at)));
    item.append(header);
    item.append(el("h3", "", dialogueThreadTitle(payload, thread)));
    item.append(el("div", "soft-copy", truncate(entry.summary || "No summary recorded.", 112)));

    const meta = [];
    meta.push(`${thread.entries.length} events`);
    if (entry.project_name) meta.push(entry.project_name);
    if (entry.tool_name) meta.push(entry.tool_name);
    if (crossTeam) meta.push("cross-team");
    if (meta.length) item.append(el("div", "dialogue-item__meta", meta.join(" | ")));
    listContainer.append(item);
  });

  const detailCard = el("section", "dialogue-detail__card");
  detailCard.append(
    el(
      "div",
      "subtle-eyebrow",
      `${selectedThread.project_name || selectedThread.scope || "root"} | ${selectedThread.entries.length} events`
    )
  );
  detailCard.append(el("h3", "", dialogueThreadTitle(payload, selectedThread)));

  const tagRow = el("div", "tag-row");
  const firstEntry = selectedThread.entries[0];
  const lastEntry = selectedThread.lastEntry;
  if (firstEntry?.agent_id) {
    const agentButton = el("button", "link-chip", findAgentLabel(payload, firstEntry.agent_id));
    agentButton.type = "button";
    agentButton.addEventListener("click", () => {
      activeAgentId = firstEntry.agent_id;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
    tagRow.append(agentButton);
  }
  if (firstEntry?.target_agent_id) {
    const targetButton = el("button", "link-chip", findAgentLabel(payload, firstEntry.target_agent_id));
    targetButton.type = "button";
    targetButton.addEventListener("click", () => {
      activeAgentId = firstEntry.target_agent_id;
      renderDashboard(latestPayload);
      if (activeRunId) loadRunDetail(activeRunId);
    });
    tagRow.append(targetButton);
  }
  if (lastEntry?.tool_name) tagRow.append(el("span", "tag", lastEntry.tool_name));
  if (lastEntry?.phase) tagRow.append(el("span", "tag tag--muted", lastEntry.phase));
  detailCard.append(tagRow);

  if (lastEntry?.summary) {
    detailCard.append(el("p", "soft-copy", lastEntry.summary));
  }

  const transcript = el("div", "dialogue-detail__transcript");
  selectedThread.entries.forEach((entry) => {
    const bubble = el("article", `chat-bubble chat-bubble--${dialogueType(entry)}`.trim());
    const bubbleHeader = el("div", "chat-bubble__header");
    bubbleHeader.append(el("span", "chat-bubble__author", findAgentLabel(payload, entry.agent_id)));
    bubbleHeader.append(el("span", "chat-bubble__time", formatTimestamp(entry.created_at)));
    bubble.append(bubbleHeader);
    bubble.append(el("div", "chat-bubble__kind", dialogueType(entry)));
    if (entry.target_agent_id) {
      bubble.append(el("div", "chat-bubble__target", `to ${findAgentLabel(payload, entry.target_agent_id)}`));
    }
    bubble.append(el("div", "chat-bubble__body", entry.transcript || entry.summary || "No transcript recorded."));
    transcript.append(bubble);
  });
  detailCard.append(transcript);

  const metaList = el("ul", "path-list");
  [
    ["Scope", lastEntry?.scope || "-"],
    ["Team", lastEntry?.team_id || "-"],
    ["Session", lastEntry?.session_id || "-"],
    ["Run", lastEntry?.run_id || "-"],
  ].forEach(([label, value]) => {
    const item = el("li", "");
    item.append(el("div", "metric-label", label));
    item.append(el("div", "mono soft-copy", value));
    metaList.append(item);
  });
  detailCard.append(metaList);
  detailContainer.append(detailCard);
}

function renderFeed(containerId, entries, emptyText, variant) {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  if (!entries?.length) {
    container.append(el("div", "empty-state", emptyText));
    return;
  }
  entries.forEach((entry) => container.append(feedCard(entry, variant)));
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
    card.append(el("div", "subtle-eyebrow", `${milestone.department_key || "-"} | ${formatTimestamp(milestone.created_at)}`));
    card.append(el("h3", "", milestone.title));
    card.append(el("div", "soft-copy", milestone.agent_id || "Unknown author"));
    card.append(el("p", "soft-copy", milestone.summary || "No summary provided."));
    const actions = el("ul", "timeline__actions");
    (milestone.next_actions || []).forEach((item) => actions.append(el("li", "", item)));
    if (!actions.children.length) actions.append(el("li", "", "No next actions recorded."));
    card.append(actions);
    if (milestone.agent_id) {
      card.addEventListener("click", () => {
        activeAgentId = milestone.agent_id;
        renderDashboard(payload);
      });
    }
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

  container.innerHTML = "";
  const handoff = payload.handoff;
  const taskRequest = handoff.task_request;

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
  if (!eventList.children.length) eventList.append(el("li", "", "No events recorded yet."));
  tracePanel.append(eventList);
  const artifactList = el("ul", "detail-list");
  (payload.trace.artifacts || []).forEach((item) => artifactList.append(el("li", "mono", item)));
  if (!artifactList.children.length) artifactList.append(el("li", "", "No canonical artifacts yet."));
  tracePanel.append(artifactList);
  container.append(tracePanel);

  if (payload.execution) {
    const executionPanel = el("section", "run-detail__panel");
    executionPanel.append(el("h3", "", "Execution"));
    executionPanel.append(el("div", "run-detail__body", `${payload.execution.mode} | ${payload.execution.status}`));
    executionPanel.append(el("div", "run-detail__value mono", payload.execution.command.join(" ")));
    container.append(executionPanel);
  }

  if (payload.result) {
    const resultPanel = el("section", "run-detail__panel");
    resultPanel.append(el("h3", "", "Result"));
    resultPanel.append(el("div", "run-detail__body", payload.result.summary));
    const resultList = el("ul", "detail-list");
    (payload.result.canonical_paths || []).forEach((item) => resultList.append(el("li", "mono", item)));
    if (!resultList.children.length) resultList.append(el("li", "", "No canonical paths recorded."));
    resultPanel.append(resultList);
    container.append(resultPanel);
  }
}

function renderWorkspace(payload) {
  const container = document.getElementById("workspace-grid");
  container.innerHTML = "";
  const cards = [
    ["Root workspace", payload.workspace.root, `${payload.subprojects.length} isolated subprojects discovered`],
    ["Canonical rules", payload.workspace.rules_dir, "Root-managed documentation tree"],
    [
      "Latest intake",
      payload.latest_intake?.source_file || payload.workspace.intake_dir,
      payload.latest_intake ? `${payload.latest_intake.competition_links.length} competition links detected` : "No parsed intake available",
    ],
    [
      "Subproject focus",
      payload.subproject_focus?.project_name || "No active subproject focus",
      payload.subproject_focus ? `${payload.subproject_focus.agent_count} agents in focused team` : "Graph will appear when a focused project is available",
    ],
    [
      "Session storage",
      payload.sessions.length ? payload.sessions.map((item) => item.name).join(", ") : "No session DB yet",
      payload.sessions.length ? "SQLite sessions available" : "No SQLite sessions found",
    ],
  ];

  cards.forEach(([title, body, meta]) => {
    const card = el("article", "workspace-card");
    card.append(el("div", "card__label", title));
    card.append(el("p", "mono", body));
    card.append(el("p", "card__meta", meta));
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
  latestPayload = payload;
  ensureActiveAgent(payload);
  document.getElementById("generated-at").textContent = `Snapshot ${formatTimestamp(payload.generated_at)}`;
  renderSignal(payload);
  renderMissionControl(payload);
  renderTopologyStage(payload);
  renderInspector(payload);
  renderDialogueConsole(payload);
  renderFeed("activity-feed", payload.live_events, "No live runtime events recorded yet.", "activity");
  renderMilestones(payload);
  renderWorkspace(payload);
  renderRunList(payload);
  renderLogs(payload);
}

async function refreshDashboard() {
  const response = await fetch("/api/dashboard");
  const payload = await response.json();
  renderDashboard(payload);
  if (activeRunId) {
    loadRunDetail(activeRunId);
  } else if (payload.runs?.length) {
    activeRunId = payload.runs[0].run_id;
    loadRunDetail(activeRunId);
  }
}

refreshDashboard();
setInterval(refreshDashboard, REFRESH_MS);
