(function () {
  "use strict";

  const $ = (selector, scope) => (scope || document).querySelector(selector);
  const body = document.body;
  const token = $('meta[name="csrf-token"]')?.content || "";
  const API = "/api/";
  const resourceName = body.dataset.resource || "";
  const statusChip = $("#api-status");
  const toastNode = $("#toast");
  let toastTimer;

  const f = (name, label, type = "text", more = {}) => ({ name, label, type, ...more });
  const required = { required: true };
  const fk = (name, label, target, isRequired = false) => f(name, label, "relation", { target, required: isRequired });
  const active = () => f("habilitado", "Habilitado", "boolean");

  const resources = {
    regiones: { title: "Regiones", fields: [f("nombre", "Nombre", "text", required), f("codigo", "Código", "text", { required:true, maxlength:5 }), active()], columns: ["nombre", "codigo", "habilitado"] },
    comunas: { title: "Comunas", fields: [f("nombre", "Nombre", "text", required), fk("region", "Región", "regiones", true), active()], columns: ["nombre", "region", "habilitado"] },
    perfiles: { title: "Perfiles", fields: [f("nombre", "Nombre", "text", required), f("descripcion", "Descripción", "textarea"), active()], columns: ["nombre", "descripcion", "habilitado"] },
    organizaciones: { title: "Organizaciones", fields: [f("nombre", "Nombre", "text", required), f("descripcion", "Descripción", "textarea"), f("correo", "Correo", "email"), f("telefono", "Teléfono", "tel"), fk("comuna", "Comuna", "comunas", true), active()], columns: ["nombre", "correo", "comuna", "habilitado"] },
    categorias: { title: "Categorías", fields: [f("nombre", "Nombre", "text", required), f("descripcion", "Descripción", "textarea"), active()], columns: ["nombre", "descripcion", "habilitado"] },
    estados: { title: "Estados", fields: [f("nombre", "Nombre", "text", required), f("descripcion", "Descripción", "textarea"), active()], columns: ["nombre", "descripcion", "habilitado"] },
    voluntarios: { title: "Voluntarios", fields: [f("nombre", "Nombre completo", "text", required), f("rut", "RUT", "text", { required:true, maxlength:12 }), f("correo", "Correo", "email"), f("telefono", "Teléfono", "tel"), f("fecha_nacimiento", "Fecha de nacimiento", "date"), fk("comuna", "Comuna", "comunas"), fk("perfil", "Perfil", "perfiles"), active()], columns: ["nombre", "rut", "correo", "comuna", "habilitado"] },
    coordinadores: { title: "Coordinadores", fields: [f("nombre", "Nombre completo", "text", required), f("rut", "RUT", "text", { required:true, maxlength:12 }), f("correo", "Correo", "email"), f("telefono", "Teléfono", "tel"), fk("organizacion", "Organización", "organizaciones", true), active()], columns: ["nombre", "rut", "organizacion", "habilitado"] },
    actividades: { title: "Actividades", fields: [f("nombre", "Nombre de la actividad", "text", required), f("descripcion", "Descripción", "textarea"), f("fecha_inicio", "Fecha y hora de inicio", "datetime-local", required), f("fecha_fin", "Fecha y hora de término", "datetime-local"), f("cupo_maximo", "Cupos disponibles", "number", { min:0 }), fk("organizacion", "Organización", "organizaciones", true), fk("categoria", "Categoría", "categorias"), fk("coordinador", "Coordinador", "coordinadores"), fk("estado", "Estado", "estados"), fk("comuna", "Comuna", "comunas"), active()], columns: ["nombre", "fecha_inicio", "organizacion", "cupo_maximo", "habilitado"] },
    inscripciones: { title: "Inscripciones", fields: [fk("voluntario", "Voluntario", "voluntarios", true), fk("actividad", "Actividad", "actividades", true), f("asistio", "Asistió", "boolean"), f("observaciones", "Observaciones", "textarea"), active()], columns: ["voluntario", "actividad", "asistio", "habilitado"] },
    recursos: { title: "Recursos", fields: [f("nombre", "Nombre", "text", required), f("descripcion", "Descripción", "textarea"), f("cantidad_disponible", "Cantidad disponible", "number", { min:0 }), fk("organizacion", "Organización", "organizaciones", true), active()], columns: ["nombre", "cantidad_disponible", "organizacion", "habilitado"] },
    asignaciones: { title: "Asignaciones de recursos", fields: [fk("actividad", "Actividad", "actividades", true), fk("recurso", "Recurso", "recursos", true), f("cantidad", "Cantidad", "number", { min:1 }), f("observaciones", "Observaciones", "textarea"), active()], columns: ["actividad", "recurso", "cantidad", "habilitado"] },
    historial: { title: "Historial de estados", fields: [fk("actividad", "Actividad", "actividades", true), fk("estado", "Estado", "estados", true), f("observacion", "Observación", "textarea")], columns: ["actividad", "estado", "fecha_cambio"] }
  };

  function svg(id) {
    const element = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    element.setAttribute("class", "ico");
    element.setAttribute("aria-hidden", "true");
    const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
    use.setAttribute("href", "#ic-" + id);
    element.append(use);
    return element;
  }
  function elt(tag, className, textValue) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    if (textValue !== undefined) e.textContent = String(textValue);
    return e;
  }
  function setStatus(online) {
    if (!statusChip) return;
    statusChip.classList.remove("online", "offline");
    statusChip.classList.add(online ? "online" : "offline");
    $("span", statusChip).textContent = online ? "API conectada" : "API no disponible";
  }
  function toast(message, error = false) {
    if (!toastNode) return;
    window.clearTimeout(toastTimer);
    toastNode.textContent = message;
    toastNode.hidden = false;
    toastNode.classList.toggle("error", error);
    toastTimer = window.setTimeout(() => { toastNode.hidden = true; }, 4500);
  }
  function friendlyError(data, fallback) {
    if (typeof data === "string") return data;
    if (Array.isArray(data)) return data.map(v => friendlyError(v, fallback)).join("; ");
    if (data && typeof data === "object") {
      return Object.entries(data).map(([name, value]) => name + ": " + friendlyError(value, fallback)).join(" · ");
    }
    return fallback;
  }
  async function request(path, options = {}) {
    const headers = { Accept: "application/json", ...(options.headers || {}) };
    if (options.body !== undefined) headers["Content-Type"] = "application/json";
    if (options.method && options.method !== "GET") headers["X-CSRFToken"] = token;
    const response = await fetch(path, { credentials: "same-origin", ...options, headers });
    const data = response.status === 204 ? null : await response.json().catch(() => null);
    if (!response.ok) throw new Error(friendlyError(data, "Error HTTP " + response.status));
    return data;
  }
  async function getCollection(slug) {
    const records = [];
    let url = API + slug + "/";
    let pages = 0;
    while (url && pages < 40) {
      const parsed = new URL(url, window.location.origin);
      if (parsed.origin !== window.location.origin || !parsed.pathname.startsWith(API + slug + "/")) {
        throw new Error("Ruta de paginación inesperada");
      }
      const data = await request(parsed.pathname + parsed.search);
      if (Array.isArray(data)) return data;
      if (!data || !Array.isArray(data.results)) throw new Error("Respuesta inesperada de " + slug);
      records.push(...data.results);
      url = data.next;
      pages++;
    }
    if (url) throw new Error("La lista supera el límite de 40 páginas; refine la consulta.");
    return records;
  }
  function readableDate(value, withTime = false) {
    if (!value) return "—";
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return String(value);
    return new Intl.DateTimeFormat("es-CL", {
      day: "2-digit", month: "short", year: "numeric",
      ...(withTime ? { hour:"2-digit", minute:"2-digit" } : {})
    }).format(d);
  }
  function initials(name) {
    return String(name || "?").trim().split(/\s+/).slice(0, 2).map(s => s.charAt(0).toUpperCase()).join("") || "?";
  }
  function emptyState(message, hint) {
    const box = elt("div", "empty-state");
    box.append(elt("strong", "", message), elt("span", "", hint));
    return box;
  }

  // Menú móvil accesible.
  const navToggle = $("#nav-toggle"), sidebar = $("#sidebar"), shade = $("#sidebar-shade");
  function closeSidebar() {
    sidebar?.classList.remove("is-open");
    if (shade) shade.hidden = true;
    navToggle?.setAttribute("aria-expanded", "false");
  }
  navToggle?.addEventListener("click", () => {
    const opened = sidebar.classList.toggle("is-open");
    if (shade) shade.hidden = !opened;
    navToggle.setAttribute("aria-expanded", String(opened));
  });
  shade?.addEventListener("click", closeSidebar);
  document.addEventListener("keydown", e => { if (e.key === "Escape") closeSidebar(); });

  async function dashboard() {
    const metricKeys = ["voluntarios", "actividades", "organizaciones", "inscripciones"];
    const activitiesBox = $("#dashboard-activities"), volunteersBox = $("#dashboard-volunteers");
    async function load() {
      const refresh = $("#refresh-dashboard");
      refresh.disabled = true;
      const entries = await Promise.allSettled(metricKeys.map(getCollection));
      const records = {};
      entries.forEach((result, index) => {
        const key = metricKeys[index];
        records[key] = result.status === "fulfilled" ? result.value : null;
        const metric = $("#stat-" + key);
        if (metric) metric.textContent = records[key] ? new Intl.NumberFormat("es-CL").format(records[key].length) : "—";
      });
      const allOk = entries.every(result => result.status === "fulfilled");
      setStatus(allOk);
      if (!allOk) toast("No se pudieron consultar todos los módulos. Comprueba el servidor y la base de datos.", true);

      activitiesBox.replaceChildren();
      const activities = records.actividades;
      if (!activities) activitiesBox.append(emptyState("No se pudieron cargar las actividades", "Revisa la conexión de Django con la base de datos."));
      else if (!activities.length) activitiesBox.append(emptyState("Todavía no hay actividades", "Registra tu primera actividad desde el menú de gestión."));
      else {
        const ordered = [...activities].sort((a, b) => new Date(a.fecha_inicio || 0) - new Date(b.fecha_inicio || 0));
        const now = Date.now();
        const upcoming = ordered.filter(a => !a.fecha_fin || new Date(a.fecha_fin).getTime() >= now);
        const chosen = (upcoming.length ? upcoming : ordered).slice(0, 5);
        chosen.forEach(item => {
          const row = elt("div", "activity-item");
          const date = new Date(item.fecha_inicio);
          const dateBox = elt("div", "activity-date");
          dateBox.append(elt("strong", "", Number.isNaN(date.getTime()) ? "—" : date.getDate()), elt("small", "", Number.isNaN(date.getTime()) ? "S/F" : new Intl.DateTimeFormat("es-CL",{month:"short"}).format(date)));
          const info = elt("div", "activity-meta");
          info.append(elt("strong", "", item.nombre || "Actividad sin nombre"), elt("span", "", readableDate(item.fecha_inicio, true) + " · " + (item.cupo_maximo ?? 0) + " cupos"));
          row.append(dateBox, info, elt("span", "activity-badge", "Registrada"));
          activitiesBox.append(row);
        });
      }

      volunteersBox.replaceChildren();
      const volunteers = records.voluntarios;
      if (!volunteers) volunteersBox.append(emptyState("No se pudieron cargar los voluntarios", "Revisa la API de voluntarios."));
      else if (!volunteers.length) volunteersBox.append(emptyState("Todavía no hay voluntarios", "Los nuevos registros aparecerán aquí."));
      else {
        [...volunteers].sort((a, b) => (b.id || 0) - (a.id || 0)).slice(0, 5).forEach((item, index) => {
          const row = elt("div", "volunteer-item");
          const info = elt("div", "volunteer-meta");
          info.append(elt("strong", "", item.nombre || "Sin nombre"), elt("span", "", item.correo || "Voluntario registrado"));
          row.append(elt("span", "volunteer-avatar", initials(item.nombre)), info, elt("span", "volunteer-index", String(index + 1).padStart(2, "0")));
          volunteersBox.append(row);
        });
      }
      refresh.disabled = false;
    }
    $("#refresh-dashboard")?.addEventListener("click", load);
    await load();
  }

  async function panel() {
    const config = resources[resourceName];
    if (!config) return;
    const tableHead = $("#record-head"), tableBody = $("#record-body");
    const search = $("#record-search"), filter = $("#record-filter");
    const dialog = $("#record-dialog"), form = $("#record-form"), fieldsArea = $("#dialog-fields");
    const formError = $("#form-error"), saveButton = $("#form-save");
    let records = [], lookups = {}, editingId = null, page = 1, busy = false;
    const PAGE_SIZE = 9;
    if (!config.fields.some(field => field.name === "habilitado")) filter.hidden = true;

    function labelFor(key) {
      const field = config.fields.find(field => field.name === key);
      return field ? field.label : ({ fecha_cambio:"Fecha de cambio" })[key] || key;
    }
    async function loadLookups() {
      const targetSet = [...new Set(config.fields.filter(field => field.type === "relation").map(field => field.target))];
      await Promise.all(targetSet.map(async target => {
        lookups[target] = await getCollection(target);
      }));
    }
    function relatedName(target, id) {
      if (id === null || id === undefined || id === "") return "—";
      const match = (lookups[target] || []).find(item => String(item.id) === String(id));
      return match ? (match.nombre || match.rut || "N° " + id) : "N° " + id;
    }
    function cellValue(item, key) {
      const field = config.fields.find(field => field.name === key);
      if (field?.type === "relation") return relatedName(field.target, item[key]);
      if (field?.type === "boolean") return item[key] ? "Sí" : "No";
      if (field?.type === "datetime-local") return readableDate(item[key], true);
      if (field?.type === "date" || key.startsWith("fecha_")) return readableDate(item[key], key !== "fecha_nacimiento");
      if (item[key] === null || item[key] === undefined || item[key] === "") return "—";
      return String(item[key]);
    }
    function filtered() {
      const query = search.value.trim().toLocaleLowerCase("es-CL").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
      return records.filter(item => {
        if (filter.value === "active" && !item.habilitado) return false;
        if (filter.value === "inactive" && item.habilitado) return false;
        if (!query) return true;
        return config.columns.some(key => cellValue(item, key).toLocaleLowerCase("es-CL").normalize("NFD").replace(/[\u0300-\u036f]/g, "").includes(query));
      });
    }
    function renderTable() {
      const items = filtered();
      const totalPages = Math.max(1, Math.ceil(items.length / PAGE_SIZE));
      page = Math.min(page, totalPages);
      tableHead.replaceChildren();
      const headerRow = elt("tr");
      config.columns.forEach(key => headerRow.append(elt("th", "", labelFor(key))));
      headerRow.append(elt("th", "", "Acciones"));
      tableHead.append(headerRow);
      tableBody.replaceChildren();
      const shown = items.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
      if (!shown.length) {
        const row = elt("tr"), cell = elt("td", "table-message", records.length ? "No hay resultados para los filtros seleccionados." : "Todavía no hay registros. Selecciona «Nuevo registro» para comenzar.");
        cell.colSpan = config.columns.length + 1;
        row.append(cell);
        tableBody.append(row);
      } else {
        shown.forEach(item => {
          const row = elt("tr");
          config.columns.forEach(key => {
            const cell = elt("td");
            if (key === "habilitado" || key === "asistio") {
              const badge = elt("span", "status-badge" + (!item[key] ? " no" : ""), item[key] ? "Sí" : "No");
              cell.append(badge);
            } else {
              const text = elt("div", "cell-truncate", cellValue(item, key));
              text.title = cellValue(item, key);
              cell.append(text);
            }
            row.append(cell);
          });
          const buttons = elt("div", "table-actions");
          const edit = elt("button"), del = elt("button", "danger");
          edit.type = "button"; del.type = "button";
          edit.title = "Editar registro"; del.title = "Eliminar registro";
          edit.setAttribute("aria-label", "Editar registro " + item.id);
          del.setAttribute("aria-label", "Eliminar registro " + item.id);
          edit.append(svg("edit")); del.append(svg("trash"));
          edit.addEventListener("click", () => openDialog(item));
          del.addEventListener("click", () => remove(item));
          buttons.append(edit, del);
          const actionCell = elt("td"); actionCell.append(buttons); row.append(actionCell);
          tableBody.append(row);
        });
      }
      $("#table-results").textContent = items.length + " registro(s) · mostrando " + shown.length;
      $("#page-label").textContent = page + " / " + totalPages;
      $("#page-prev").disabled = page <= 1;
      $("#page-next").disabled = page >= totalPages;
      $("#panel-count").textContent = new Intl.NumberFormat("es-CL").format(records.length);
      const withStatus = config.fields.some(field => field.name === "habilitado");
      $("#panel-active").textContent = withStatus ? String(records.filter(item => item.habilitado).length) : "N/A";
    }
    function inputFor(field, record) {
      const wrapper = elt("div", "form-group");
      if (field.type === "textarea") wrapper.classList.add("full");
      if (field.type === "boolean") wrapper.classList.add("check");
      const label = elt("label", "", field.label);
      label.htmlFor = "field-" + field.name;
      if (field.required) label.append(elt("em", "", " *"));
      let control;
      if (field.type === "relation") {
        control = elt("select");
        const placeholder = elt("option", "", field.required ? "Seleccionar..." : "Sin asignar");
        placeholder.value = ""; control.append(placeholder);
        (lookups[field.target] || []).forEach(entity => {
          const option = elt("option", "", entity.nombre || entity.rut || "N° " + entity.id);
          option.value = String(entity.id);
          control.append(option);
        });
        control.value = record?.[field.name] == null ? "" : String(record[field.name]);
        if (field.required && control.options.length === 1) {
          wrapper.append(elt("small", "form-hint", "Primero crea un registro en " + resources[field.target].title + "."));
        }
      } else if (field.type === "textarea") {
        control = elt("textarea");
        control.rows = 3;
        control.value = record?.[field.name] ?? "";
      } else {
        control = elt("input");
        control.type = field.type === "boolean" ? "checkbox" : field.type;
        if (field.type === "boolean") {
          control.checked = record ? Boolean(record[field.name]) : field.name === "habilitado";
        } else if (field.type === "datetime-local") {
          if (record?.[field.name]) {
            const date = new Date(record[field.name]);
            if (!Number.isNaN(date.getTime())) {
              const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
              control.value = local.toISOString().slice(0,16);
            }
          }
        } else control.value = record?.[field.name] ?? (field.type === "number" ? String(field.name === "cantidad" ? 1 : 0) : "");
      }
      control.id = "field-" + field.name;
      control.name = field.name;
      control.required = !!field.required;
      if (field.maxlength) control.maxLength = field.maxlength;
      if (field.min !== undefined) control.min = String(field.min);
      if (field.type === "number") control.step = "1";
      wrapper.prepend(label);
      wrapper.append(control);
      return wrapper;
    }
    async function openDialog(record = null) {
      if (busy) return;
      try {
        $("#create-record").disabled = true;
        await loadLookups();
        fieldsArea.replaceChildren();
        config.fields.forEach(field => fieldsArea.append(inputFor(field, record)));
        editingId = record ? record.id : null;
        $("#dialog-title").textContent = record ? "Editar " + config.title.toLowerCase() : "Nuevo registro";
        saveButton.textContent = record ? "Guardar cambios" : "Crear registro";
        formError.hidden = true;
        dialog.showModal();
      } catch (error) {
        toast("No se pudo preparar el formulario: " + error.message, true);
      } finally {
        $("#create-record").disabled = false;
      }
    }
    function closeDialog() {
      if (!busy) dialog.close();
    }
    function payloadFromForm() {
      const payload = {};
      config.fields.forEach(field => {
        const control = $("#field-" + field.name, form);
        if (field.type === "boolean") payload[field.name] = control.checked;
        else if (field.type === "relation") payload[field.name] = control.value ? Number(control.value) : null;
        else if (field.type === "number") payload[field.name] = control.value === "" ? null : Number(control.value);
        else if (field.type === "datetime-local") payload[field.name] = control.value ? new Date(control.value).toISOString() : null;
        else payload[field.name] = control.value.trim() || (field.required ? "" : null);
      });
      return payload;
    }
    async function refresh() {
      $("#refresh-records").disabled = true;
      try {
        const [items] = await Promise.all([getCollection(resourceName), loadLookups()]);
        records = [...items].sort((a,b) => (b.id || 0) - (a.id || 0));
        setStatus(true);
        $("#panel-updated").textContent = new Intl.DateTimeFormat("es-CL",{hour:"2-digit",minute:"2-digit"}).format(new Date());
        renderTable();
      } catch (error) {
        setStatus(false);
        records = [];
        renderTable();
        const row = elt("tr"), cell = elt("td", "table-message", "No se pudo cargar la información: " + error.message);
        cell.colSpan = config.columns.length + 1; row.append(cell); tableBody.replaceChildren(row);
        toast("La API no respondió. Revisa la base de datos y las migraciones.", true);
      } finally {
        $("#refresh-records").disabled = false;
      }
    }
    async function remove(record) {
      const title = record.nombre || "registro N° " + record.id;
      if (!window.confirm("¿Eliminar «" + title + "»? Esta acción no se puede deshacer y puede afectar registros relacionados.")) return;
      try {
        await request(API + resourceName + "/" + record.id + "/", { method: "DELETE" });
        toast("Registro eliminado correctamente.");
        await refresh();
      } catch (error) { toast("No se pudo eliminar: " + error.message, true); }
    }

    $("#create-record").addEventListener("click", () => openDialog());
    $("#dialog-close").addEventListener("click", closeDialog);
    $("#dialog-cancel").addEventListener("click", closeDialog);
    dialog.addEventListener("cancel", event => { if (busy) event.preventDefault(); });
    dialog.addEventListener("click", event => { if (event.target === dialog) closeDialog(); });
    search.addEventListener("input", () => { page = 1; renderTable(); });
    filter.addEventListener("change", () => { page = 1; renderTable(); });
    $("#page-prev").addEventListener("click", () => { page--; renderTable(); });
    $("#page-next").addEventListener("click", () => { page++; renderTable(); });
    $("#refresh-records").addEventListener("click", refresh);
    form.addEventListener("submit", async event => {
      event.preventDefault();
      if (busy || !form.reportValidity()) return;
      busy = true;
      saveButton.disabled = true;
      formError.hidden = true;
      try {
        const url = API + resourceName + "/" + (editingId === null ? "" : editingId + "/");
        await request(url, { method: editingId === null ? "POST" : "PATCH", body: JSON.stringify(payloadFromForm()) });
        dialog.close();
        toast(editingId === null ? "Registro creado correctamente." : "Cambios guardados correctamente.");
        editingId = null;
        await refresh();
      } catch (error) {
        formError.textContent = error.message;
        formError.hidden = false;
      } finally {
        busy = false;
        saveButton.disabled = false;
      }
    });
    await refresh();
  }

  if (body.dataset.page === "dashboard") dashboard();
  if (body.dataset.page === "panel") panel();
})();
