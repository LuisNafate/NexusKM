const state = {
  token: sessionStorage.getItem("nexuskm-token"),
  person: null,
  catalog: null,
  view: "impact",
  apiId: "API-002",
  detail: null,
  pendingCommand: null,
};
const viewNames = {
  impact: ["Impacto técnico", "Identifica los proyectos y el conocimiento afectados por una API."],
  documents: ["Documentos", "Contenido versionado y responsables del equipo."],
  requests: ["Solicitudes", "Revisión técnica, del propietario y de seguridad."],
  audit: ["Auditoría", "Acciones registradas y responsables de cada cambio."],
  synchronization: ["Sincronización", "Operaciones pendientes entre las bases y recuperación de fallos."],
};
const roleNames = {
  LIDER: "Líder de proyecto", TECNICO: "Revisión técnica", SEGURIDAD: "Seguridad",
  PROPIETARIO: "Propietaria documental", ADMIN: "Administración",
};
const $ = (selector) => document.querySelector(selector);
function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (character) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[character]));
}
const e = escapeHtml;
function date(value) {
  return value ? new Date(value).toLocaleString("es-MX", { dateStyle: "medium", timeStyle: "short" }) : "—";
}
function tag(value) {
  const appearance = ["PUBLICADA", "VIGENTE", "COMPLETA"].includes(value) ? "positive" : "warning";
  return `<span class="tag ${appearance}">${e(value.replaceAll("_", " "))}</span>`;
}
async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (state.token) headers.Authorization = "Bearer " + state.token;
  const response = await fetch("/api" + path, { ...options, headers });
  const body = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(body.detail) ? body.detail.map((item) => item.msg).join(". ") : body.detail;
    if (response.status === 401 && state.person) logout();
    throw new Error(detail || "La operación no pudo completarse.");
  }
  return body;
}
function notice(message, retry = false) {
  const element = $("#message");
  element.hidden = false;
  element.innerHTML = `<span>${e(message)}</span>${retry ? '<button id="retry-command">Reintentar operación</button>' : ""}`;
}
async function command(path, body, method = "POST") {
  const fingerprint = JSON.stringify({ path, body, method });
  if (!state.pendingCommand || state.pendingCommand.fingerprint !== fingerprint) {
    state.pendingCommand = { path, body, method, key: crypto.randomUUID(), fingerprint };
  }
  const operation = state.pendingCommand;
  const result = await api(operation.path, {
    method: operation.method,
    headers: { "Idempotency-Key": operation.key },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  state.pendingCommand = null;
  notice(
    result.synchronization.pending
      ? "Cambio registrado. La sincronización está pendiente y se reintentará automáticamente."
      : "Cambio guardado y sincronizado.",
  );
  return result;
}
async function guarded(task, errorSelector = "#message") {
  try {
    return await task();
  } catch (error) {
    if (errorSelector === "#message") notice(error.message, Boolean(state.pendingCommand));
    else $(errorSelector).textContent = error.message;
    return null;
  }
}
function logout() {
  sessionStorage.removeItem("nexuskm-token");
  state.token = null;
  state.person = null;
  state.pendingCommand = null;
  $("#workspace").hidden = true;
  $("#login-screen").hidden = false;
  $("#password").value = "";
  $("#editor").close();
}
async function openWorkspace() {
  state.person = await api("/me");
  state.catalog = await api("/catalog");
  $("#identity").innerHTML = `<div class="identity-name">${e(state.person.name)}</div><div class="identity-role">${e(roleNames[state.person.role])}</div>`;
  $("#sync-navigation").hidden = state.person.role !== "ADMIN";
  $("#login-screen").hidden = true;
  $("#workspace").hidden = false;
  await renderView();
}
async function renderView() {
  const [title, description] = viewNames[state.view];
  $("#view-title").textContent = title;
  $("#view-description").textContent = description;
  $("#header-actions").innerHTML = state.view === "documents"
    ? '<button class="primary" id="new-document">Nuevo documento</button>' : "";
  document.querySelectorAll("[data-view]").forEach((button) => {
    button.classList.toggle("selected", button.dataset.view === state.view);
  });
  $("#view").innerHTML = '<div class="empty">Cargando información…</div>';
  $("#view").setAttribute("aria-busy", "true");
  await {
    impact: renderImpact,
    documents: renderDocuments,
    requests: renderRequests,
    audit: renderAudit,
    synchronization: renderSynchronization,
  }[state.view]();
}
async function renderImpact() {
  $("#view").setAttribute("aria-busy", "true");
  const result = await api("/impact/" + encodeURIComponent(state.apiId));
  if (state.view !== "impact") return;
  const paths = result.paths.filter((path) => path.service);
  const uniqueProjects = new Set(paths.map((path) => path.project_id).filter(Boolean));
  const options = state.catalog.apis.map((item) =>
    `<option value="${e(item.api_id)}" ${item.api_id === state.apiId ? "selected" : ""}>${e(item.name)}</option>`,
  ).join("");
  const pathMarkup = paths.map((path) => {
    const nodes = [
      ["API consumida", result.api_name], ["Microservicio consumidor", path.service],
      ["Componente", path.component], ["Repositorio", path.repository], ["Proyecto", path.project],
    ];
    return `<div class="dependency-path">${nodes.map(([kind, name], index) =>
      `<div class="path-node ${index === 0 ? "source" : ""}"><small>${e(kind)}</small><span class="node-name">${e(name || "Sin asociación")}</span></div>`,
    ).join("")}</div><p class="path-caption">Dependencia ${e(path.dependency_id)} · Criticidad ${e(path.criticality)}. El servicio consume la API y pertenece al contexto técnico del proyecto.</p>`;
  }).join("");
  $("#view").innerHTML = `
    <div class="toolbar">
      <div class="field"><label for="api-selection">API que cambiará</label><select id="api-selection">${options}</select></div>
      <button class="primary" id="consult-impact">Consultar impacto</button>
    </div>
    <section class="panel impact-panel">
      <div class="section-header"><h2>Recorrido de dependencias</h2><p>${paths.length} consumidor${paths.length === 1 ? "" : "es"}</p></div>
      <p class="impact-finding"><strong>${e(result.api_name)}</strong> está conectada con ${uniqueProjects.size} proyecto${uniqueProjects.size === 1 ? "" : "s"} a través de sus consumidores.</p>
      ${pathMarkup || '<p class="empty">La API existe y aún no tiene consumidores registrados.</p>'}
    </section>
    <div class="results-grid">
      <section class="panel">
        <div class="section-header"><h2>Responsables del impacto</h2></div>
        <ul class="detail-list">${result.projects.map((project) =>
          `<li>${e(project.name)}<p>${e(project.leader)} · Líder de ${e(project.code)}</p></li>`,
        ).join("") || "<li>Sin proyectos asociados.</li>"}</ul>
      </section>
      <section class="panel">
        <div class="section-header"><h2>Conocimiento vigente</h2></div>
        <ul class="detail-list">${result.documents.map((document) =>
          `<li><button class="text-action" data-open-document="${e(document.document_id)}">${e(document.title)}</button>
          <p>Versión ${e(document.number)} · ${document.content_ready ? e(document.content.summary) : "Contenido pendiente de sincronización"}</p></li>`,
        ).join("") || "<li>Sin documentación vigente autorizada.</li>"}</ul>
      </section>
    </div>
    <p class="source-note">Consulta integrada de ${e(result.sources.join(", "))}. ${result.synchronization_pending ? "Existen actualizaciones pendientes de sincronización." : "Las proyecciones están sincronizadas."}</p>`;
  $("#view").setAttribute("aria-busy", "false");
}
async function renderDocuments() {
  const rows = await api("/documents");
  if (state.view !== "documents") return;
  $("#view").innerHTML = `
    <div class="toolbar"><label for="document-search">Buscar documento</label><input id="document-search" type="search" placeholder="Título o proyecto"><span class="muted" id="document-count">${rows.length} documentos</span></div>
    <div class="table-frame"><table><thead><tr><th>Documento</th><th>Proyecto</th><th>Propietario</th><th class="num">Versiones</th><th></th></tr></thead>
    <tbody id="document-rows">${rows.map((document) =>
      `<tr data-search="${e((document.title + " " + document.project).toLowerCase())}"><td>${e(document.title)}
      <span class="subline">${e(document.kind)} · ${e(document.classification)}${document.sync_pending ? " · Sincronización pendiente" : ""}</span></td>
      <td>${e(document.project)}</td><td>${e(document.owner)}</td><td class="num">${document.version_count}</td>
      <td><button data-open-document="${e(document.document_id)}">Abrir</button></td></tr>`,
    ).join("")}</tbody></table></div>
    ${rows.length ? "" : '<p class="empty">Aún no hay documentos autorizados. Puedes crear el primero.</p>'}`;
  $("#view").setAttribute("aria-busy", "false");
}
async function renderRequests() {
  const rows = await api("/requests");
  if (state.view !== "requests") return;
  $("#view").innerHTML = rows.map((request) => {
    const kinds = [];
    if (state.person.role === "TECNICO" && state.person.person_id !== request.requester_id) kinds.push("TECNICA");
    if (state.person.role === "SEGURIDAD") kinds.push("SEGURIDAD");
    if (state.person.person_id === request.owner_id) kinds.push("PROPIETARIO");
    const closed = ["PUBLICADA", "CANCELADA"].includes(request.state);
    const canPublish = request.state === "APROBADA" && (state.person.person_id === request.owner_id || state.person.role === "ADMIN");
    return `<article class="panel request-card">
      <div class="section-header"><div><h2>${e(request.title)}</h2><p>${e(request.request_id)} · Versión ${e(request.version_number)} · Solicitó ${e(request.requester)}</p></div>${tag(request.state)}</div>
      <div class="approvals">${request.approvals.map((approval) =>
        `<span>${e(approval.reviewer)} · ${e(approval.kind)}</span>`,
      ).join('<span aria-hidden="true"> / </span>') || '<span class="muted">Sin aprobaciones registradas.</span>'}</div>
      <div class="actions">
        <button data-open-document="${e(request.document_id)}">Consultar versión</button>
        ${!closed && kinds.length ? `<select aria-label="Tipo de aprobación para ${e(request.request_id)}" id="kind-${e(request.request_id)}">${kinds.map((kind) => `<option>${kind}</option>`).join("")}</select><button data-approve="${e(request.request_id)}">Registrar aprobación</button>` : ""}
        ${canPublish ? `<button class="primary" data-publish="${e(request.request_id)}">Publicar versión</button>` : ""}
      </div></article>`;
  }).join("") || '<p class="empty">No hay solicitudes de revisión para tus documentos autorizados.</p>';
  $("#view").setAttribute("aria-busy", "false");
}
async function renderAudit() {
  const rows = await api("/audit");
  if (state.view !== "audit") return;
  $("#view").innerHTML = `<div class="table-frame"><table><thead><tr><th>Acción</th><th>Entidad</th><th>Responsable</th><th class="num">Fecha</th></tr></thead><tbody>${rows.map((row) =>
    `<tr><td>${e(row.action.replaceAll("_", " "))}</td><td>${e(row.entity_id)}</td><td>${e(row.actor || "Sistema")}</td><td class="num">${e(date(row.created_at))}</td></tr>`,
  ).join("")}</tbody></table></div>${rows.length ? "" : '<p class="empty">Todavía no tienes acciones registradas.</p>'}`;
  $("#view").setAttribute("aria-busy", "false");
}
async function renderSynchronization() {
  const rows = await api("/synchronization");
  if (state.view !== "synchronization") return;
  $("#header-actions").innerHTML = '<button class="primary" id="retry-sync">Reintentar pendientes</button>';
  $("#view").innerHTML = `<div class="table-frame"><table><thead><tr><th>Documento</th><th>Operación</th><th>Estado</th><th class="num">Intentos</th><th>Último error</th></tr></thead><tbody>${rows.map((row) =>
    `<tr><td>${e(row.document_id)}</td><td>${e(row.action)}</td><td>${tag(row.state)}</td><td class="num">${row.attempts}</td><td>${e(row.last_error || "—")}</td></tr>`,
  ).join("")}</tbody></table></div>`;
  $("#view").setAttribute("aria-busy", "false");
}
function openDialog(title, content) {
  $("#dialog-title").textContent = title;
  $("#dialog-body").innerHTML = content;
  $("#dialog-error").textContent = "";
  if (!$("#editor").open) $("#editor").showModal();
}
const contentSamples = {
  RUNBOOK: {
    summary: "Procedimiento de operación y recuperación del servicio.",
    sections: [{ heading: "Alcance", body: "Describe los servicios y responsables cubiertos." }],
    steps: [{ title: "Comprobar estado", instruction: "Verificar el estado del servicio antes de reintentar." }],
  },
  API: {
    summary: "Contrato de integración y compatibilidad para consumidores.",
    sections: [{ heading: "Contrato", body: "Describe entradas, salidas y condiciones de uso." }],
    endpoints: [{ path: "/resources", method: "GET" }],
  },
  SEGURIDAD: {
    summary: "Análisis de amenazas y medidas de protección del servicio.",
    sections: [{ heading: "Activos", body: "Describe los activos y los riesgos del servicio." }],
    threats: [{ title: "Acceso indebido", mitigation: "Validar identidad y autorización en cada solicitud." }],
  },
};
function showVersionForm(document = null) {
  const kind = document?.kind || "RUNBOOK";
  const ownerOptions = state.catalog.people.filter((person) =>
    state.person.role === "ADMIN" || person.person_id === state.person.person_id,
  ).map((person) => `<option value="${e(person.person_id)}">${e(person.name)}</option>`).join("");
  const projectOptions = state.catalog.projects.map((project) =>
    `<option value="${e(project.project_id)}">${e(project.name)}</option>`,
  ).join("");
  const expiration = new Date(Date.now() + 180 * 86400000).toISOString().slice(0, 10);
  openDialog(document ? "Nueva versión" : "Nuevo documento", `
    <form id="document-form" data-document-id="${e(document?.document_id || "")}" data-kind="${e(kind)}">
      ${document ? "" : `<label for="document-title">Título</label><input id="document-title" name="title" required minlength="3" maxlength="160">
      <div class="form-grid">
        <div><label for="document-kind">Tipo</label><select id="document-kind" name="kind"><option>RUNBOOK</option><option>API</option><option>SEGURIDAD</option></select></div>
        <div><label for="classification">Clasificación</label><select id="classification" name="classification"><option>INTERNO</option><option>RESTRINGIDO</option></select></div>
        <div><label for="owner-id">Propietario</label><select id="owner-id" name="owner_id">${ownerOptions}</select></div>
        <div><label for="project-id">Proyecto</label><select id="project-id" name="project_id">${projectOptions}</select></div>
      </div>`}
      <div class="form-grid">
        <div><label for="version-number">Número de versión</label><input id="version-number" name="number" value="${document ? "1.1" : "1.0"}" pattern="[0-9]+\.[0-9]+(\.[0-9]+)?" required></div>
        <div><label for="expires-at">Vencimiento</label><input id="expires-at" name="expires_at" type="date" value="${expiration}" required></div>
      </div>
      <label for="version-content">Contenido estructurado JSON</label>
      <textarea id="version-content" name="content" spellcheck="false" required></textarea>
      <p class="help">Cada tipo conserva secciones y una estructura propia de pasos, operaciones de API o amenazas.</p>
      <button type="submit" class="primary">Guardar borrador</button>
    </form>`);
  $("#version-content").value = JSON.stringify(contentSamples[kind], null, 2);
}
async function showDocument(documentId) {
  const detail = await api("/documents/" + encodeURIComponent(documentId));
  state.detail = detail;
  const document = detail.document;
  const owner = document.owner_id === state.person.person_id || state.person.role === "ADMIN";
  openDialog(document.title, `
    <p class="muted">${e(document.document_id)} · ${e(document.kind)} · ${e(document.classification)}</p>
    ${detail.sync_pending ? '<p class="notice">Hay una sincronización pendiente. Los cambios de este documento se habilitarán al completarla.</p>' : ""}
    ${owner ? `<form id="rename-form"><label for="rename-title">Título del documento</label>
      <input id="rename-title" name="title" value="${e(document.title)}" required minlength="3" maxlength="160">
      <div class="form-actions"><button type="submit">Guardar título</button><button type="button" id="new-version">Nueva versión</button><button type="button" id="delete-document" class="danger">Dar de baja</button></div></form>` : ""}
    ${detail.versions.map((version) => `<section class="version-block">
      <div class="section-header"><h3>Versión ${e(version.number)}</h3>${tag(version.state)}</div>
      <p class="muted">Vence ${e(date(version.expires_at))}${version.expired ? " · Vencida" : ""}</p>
      ${version.content_ready ? `<p>${e(version.content.summary)}</p>${version.content.sections.map((section) =>
        `<h3>${e(section.heading)}</h3><p class="content-text">${e(section.body)}</p>`,
      ).join("")}` : '<p class="notice">El contenido aún está pendiente de sincronización.</p>'}
      ${owner && version.state === "BORRADOR" ? `<div class="form-actions"><button data-edit-content="${e(version.version_id)}">Editar contenido</button><button data-create-request="${e(version.version_id)}">Enviar a revisión</button></div>` : ""}
    </section>` ).join("")}`);
}
function showContentEditor(versionId) {
  const version = state.detail.versions.find((item) => item.version_id === versionId);
  openDialog("Editar contenido del borrador", `<form id="content-form" data-version-id="${e(versionId)}" data-revision="${version.content_revision}">
    <label for="content-editor">Contenido estructurado JSON</label><textarea id="content-editor" spellcheck="false" required></textarea>
    <div class="form-actions"><button class="primary" type="submit">Guardar contenido</button></div></form>`);
  $("#content-editor").value = JSON.stringify(version.content, null, 2);
}
$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("#login-error").textContent = "";
  const button = event.submitter;
  button.disabled = true;
  await guarded(async () => {
    const values = Object.fromEntries(new FormData(event.target));
    const result = await api("/auth/login", { method: "POST", body: JSON.stringify(values) });
    state.token = result.access_token;
    sessionStorage.setItem("nexuskm-token", state.token);
    $("#password").value = "";
    await openWorkspace();
  }, "#login-error");
  button.disabled = false;
});
document.addEventListener("submit", async (event) => {
  const form = event.target;
  if (!["document-form", "rename-form", "content-form"].includes(form.id)) return;
  event.preventDefault();
  event.submitter.disabled = true;
  const result = await guarded(async () => {
    if (form.id === "document-form") {
      const values = Object.fromEntries(new FormData(form));
      values.content = JSON.parse(values.content);
      values.expires_at += "T23:59:00-06:00";
      await command(form.dataset.documentId ? "/documents/" + form.dataset.documentId + "/versions" : "/documents", values);
    } else if (form.id === "rename-form") {
      await command("/documents/" + state.detail.document.document_id, {
        title: $("#rename-title").value, expected_revision: state.detail.document.revision,
      }, "PATCH");
    } else {
      await command("/versions/" + form.dataset.versionId + "/content", {
        content: JSON.parse($("#content-editor").value), expected_revision: Number(form.dataset.revision),
      }, "PUT");
    }
    $("#editor").close();
    await renderView();
    return true;
  }, "#dialog-error");
  if (!result) event.submitter.disabled = false;
});
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button");
  if (!button) return;
  if (button.form && button.type === "submit") return;
  if (button.dataset.view) {
    state.view = button.dataset.view;
    $(".sidebar").classList.remove("open");
    $("#menu-toggle").setAttribute("aria-expanded", "false");
    $("#message").hidden = true;
    await guarded(renderView);
    return;
  }
  if (button.id === "logout") return logout();
  if (button.id === "close-dialog") return $("#editor").close();
  if (button.id === "menu-toggle") {
    $(".sidebar").classList.toggle("open");
    button.setAttribute("aria-expanded", String($(".sidebar").classList.contains("open")));
    return;
  }
  if (button.id === "new-document") return showVersionForm();
  if (button.id === "new-version") return showVersionForm(state.detail.document);
  if (button.dataset.editContent) return showContentEditor(button.dataset.editContent);
  if (button.id === "delete-document") {
    return openDialog("Dar de baja el documento", `<p>El documento dejará de aparecer en el catálogo. Su contenido y su historial se conservarán.</p><div class="form-actions"><button id="confirm-delete-document" class="danger">Confirmar baja</button></div>`);
  }
  button.disabled = true;
  await guarded(async () => {
    if (button.id === "consult-impact") {
      state.apiId = $("#api-selection").value;
      await renderImpact();
    } else if (button.dataset.openDocument) {
      await showDocument(button.dataset.openDocument);
    } else if (button.dataset.approve) {
      await command("/requests/" + button.dataset.approve + "/approvals", {
        kind: document.getElementById("kind-" + button.dataset.approve).value,
      });
      await renderView();
    } else if (button.dataset.publish) {
      await command("/requests/" + button.dataset.publish + "/publish", undefined);
      await renderView();
    } else if (button.dataset.createRequest) {
      await command("/requests", { version_id: button.dataset.createRequest });
      $("#editor").close();
      state.view = "requests";
      await renderView();
    } else if (button.id === "confirm-delete-document") {
      await command("/documents/" + state.detail.document.document_id + "?expected_revision=" + state.detail.document.revision, undefined, "DELETE");
      $("#editor").close();
      await renderView();
    } else if (button.id === "retry-sync") {
      const result = await api("/synchronization/retry", { method: "POST" });
      notice(`${result.processed} operaciones recuperadas. ${result.pending} pendientes.`);
      await renderSynchronization();
    } else if (button.id === "retry-command" && state.pendingCommand) {
      const operation = state.pendingCommand;
      await command(operation.path, operation.body, operation.method);
      $("#editor").close();
      await renderView();
    }
  });
  button.disabled = false;
});
document.addEventListener("change", (event) => {
  if (event.target.id === "document-kind") {
    $("#version-content").value = JSON.stringify(contentSamples[event.target.value], null, 2);
  }
});
document.addEventListener("input", (event) => {
  if (event.target.id !== "document-search") return;
  const query = event.target.value.toLowerCase();
  const rows = document.querySelectorAll("[data-search]");
  let shown = 0;
  rows.forEach((row) => {
    row.hidden = !row.dataset.search.includes(query);
    if (!row.hidden) shown++;
  });
  $("#document-count").textContent = shown + " documentos";
});
if (state.token) guarded(openWorkspace).then((result) => {
  if (!state.person) logout();
});
