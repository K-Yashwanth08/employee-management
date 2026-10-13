const $ = (selector, parent = document) => parent.querySelector(selector);
const $$ = (selector, parent = document) => [...parent.querySelectorAll(selector)];
const state = { employees: [], total: 0, activeTotal: 0, departments: [], roles: [], page: 1, size: 10, query: "", department: "", view: "dashboard" };
const palette = ["", "tone-1", "tone-2", "tone-3", "tone-4"];

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
}
function initials(person) { return `${person.first_name?.[0] || ""}${person.last_name?.[0] || ""}`.toUpperCase() || "?"; }
function fullName(person) { return `${person.first_name || ""} ${person.last_name || ""}`.trim(); }
function niceDate(value) { if (!value) return "—"; return new Date(`${value}T00:00:00`).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" }); }
function toast(message, isError = false) {
  const item = document.createElement("div"); item.className = `toast${isError ? " error" : ""}`; item.textContent = message;
  $("#toast-region").append(item); setTimeout(() => item.remove(), 3600);
}
async function api(path, options = {}) {
  const response = await fetch(path, { ...options, headers: { ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) } });
  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try { const body = await response.json(); message = body?.error?.message || body?.detail || message; } catch { /* keep status fallback */ }
    throw new Error(message);
  }
  if (response.status === 204) return null;
  return response.json();
}
function setConnection(ok) {
  const indicator = $(".connection"); indicator.classList.toggle("online", ok); indicator.classList.toggle("offline", !ok);
  $("#connection-label").textContent = ok ? "Connected" : "API unavailable";
}
function setLoading(target, count, message) { $(target).innerHTML = `<tr><td colspan="${count}" class="loading-cell">${escapeHtml(message)}</td></tr>`; }
function employeeTableRow(employee, detailed = false) {
  const dept = employee.department?.name || "—", role = employee.role?.name || "—";
  return `<tr>
    <td><div class="employee-cell"><span class="employee-avatar ${palette[employee.id % palette.length]}">${escapeHtml(initials(employee))}</span><span class="employee-name"><strong>${escapeHtml(fullName(employee))}</strong><span>${escapeHtml(employee.work_email)}</span></span></div></td>
    ${detailed ? `<td><span class="table-id">${escapeHtml(employee.employee_code)}</span></td>` : ""}
    <td>${escapeHtml(dept)}</td><td>${escapeHtml(role)}</td>
    ${detailed ? `<td>${escapeHtml(niceDate(employee.joining_date))}</td>` : ""}
    <td><span class="status-pill ${employee.is_active ? "" : "inactive"}">${employee.is_active ? "Active" : "Inactive"}</span></td>
    ${detailed ? `<td class="action-cell"><button class="row-menu" data-employee-action="${employee.id}" aria-label="Actions for ${escapeHtml(fullName(employee))}">···</button></td>` : "<td></td>"}
  </tr>`;
}
async function loadSummary() {
  const [employeeSummary, departments, roles, preview] = await Promise.all([
    api("/employees/summary"),
    api("/departments?page=1&size=100"), api("/roles?page=1&size=100"), api("/employees?page=1&size=5")
  ]);
  state.total = employeeSummary.total; state.activeTotal = employeeSummary.active;
  state.departments = departments.items; state.roles = roles.items;
  $("#stat-total").textContent = employeeSummary.total;
  $("#stat-active").textContent = employeeSummary.total;
  $("#stat-total-note").textContent = `${employeeSummary.inactive} inactive ${employeeSummary.inactive === 1 ? "record" : "records"}`;
  $("#stat-departments").textContent = departments.total;
  $("#stat-roles").textContent = roles.total;
  $("#employee-count").textContent = employeeSummary.active;
  $("#dashboard-employees").innerHTML = preview.items.length ? preview.items.map((item) => employeeTableRow(item)).join("") : `<tr><td colspan="5" class="empty-cell">Your people directory is ready when you are.</td></tr>`;
  $("#dashboard-table-note").textContent = preview.total ? `A glimpse of ${preview.total} people` : "No employees yet";
  await Promise.all([renderDepartmentPreview(), renderEntityCards("departments"), renderEntityCards("roles")]);
}
async function renderDepartmentPreview() {
  const list = state.departments.slice(0, 4);
  if (!list.length) { $("#department-preview").innerHTML = `<div class="empty-cell">Add your first department to get started.</div>`; return; }
  const counts = await Promise.all(list.map(async (department) => {
    try { return (await api(`/departments/${department.id}/employees?page=1&size=1`)).total; } catch { return 0; }
  }));
  $("#department-preview").innerHTML = list.map((department, index) => `<div class="department-row"><span class="dept-symbol ${palette[index % palette.length]}">${escapeHtml(department.name.slice(0, 1).toUpperCase())}</span><span class="dept-name">${escapeHtml(department.name)}</span><span class="dept-members">${counts[index]} ${counts[index] === 1 ? "person" : "people"}</span></div>`).join("");
}
async function renderEntityCards(kind) {
  const isDepartment = kind === "departments", items = isDepartment ? state.departments : state.roles, target = isDepartment ? "#department-grid" : "#role-grid";
  if (!items.length) { $(target).innerHTML = `<article class="entity-card"><div class="entity-icon">✳</div><h3>No ${kind} yet</h3><p>Add your first ${isDepartment ? "department" : "role"} to shape the directory.</p></article>`; return; }
  const counts = isDepartment ? await Promise.all(items.map(async (item) => { try { return (await api(`/departments/${item.id}/employees?page=1&size=1`)).total; } catch { return 0; } })) : [];
  $(target).innerHTML = items.map((item, index) => `<article class="entity-card"><div class="entity-card-top"><span class="entity-icon ${palette[index % palette.length]}">${isDepartment ? escapeHtml(item.name.slice(0, 1).toUpperCase()) : "✳"}</span><span class="status-pill ${item.is_active ? "" : "inactive"}">${item.is_active ? "Active" : "Inactive"}</span></div><h3>${escapeHtml(item.name)}</h3><p>${escapeHtml(item.description || (isDepartment ? "A team working together." : "A craft that helps the team move forward."))}</p><div class="entity-meta"><span>${isDepartment ? "Team members" : "Added to directory"}</span><strong>${isDepartment ? counts[index] : niceDate(item.created_at?.slice(0, 10))}</strong></div></article>`).join("");
}
async function loadEmployees() {
  setLoading("#employee-rows", 7, "Finding your people...");
  const params = new URLSearchParams({ page: String(state.page), size: String(state.size) });
  if (state.query.trim()) params.set("q", state.query.trim()); if (state.department) params.set("department", state.department);
  try {
    const result = await api(`/employees?${params}`); state.employees = result.items;
    $("#employee-rows").innerHTML = result.items.length ? result.items.map((item) => employeeTableRow(item, true)).join("") : `<tr><td colspan="7" class="empty-cell">No people match this view. Try a different search or add an employee.</td></tr>`;
    $("#employee-results-count").textContent = `${result.total} ${result.total === 1 ? "person" : "people"}`;
    const pages = Math.max(result.total_pages, 1), start = result.total ? (state.page - 1) * state.size + 1 : 0, end = Math.min(state.page * state.size, result.total);
    $("#pagination-summary").textContent = `Showing ${start}–${end} of ${result.total}`; $("#page-number").textContent = `${state.page} / ${pages}`;
    $("#previous-page").disabled = state.page <= 1; $("#next-page").disabled = state.page >= pages;
  } catch (error) { $("#employee-rows").innerHTML = `<tr><td colspan="7" class="empty-cell">${escapeHtml(error.message)}</td></tr>`; }
}
function go(view) {
  if (!["dashboard", "employees", "departments", "roles"].includes(view)) return;
  state.view = view; $$(".view-panel").forEach((panel) => panel.classList.toggle("visible", panel.id === `view-${view}`));
  $$(".nav-item").forEach((item) => item.classList.toggle("active", item.dataset.view === view));
  const label = { dashboard: "Overview", employees: "Employees", departments: "Departments", roles: "Roles" }[view];
  $("#breadcrumb-current").textContent = label; $("#sidebar").classList.remove("open");
  if (view === "employees") loadEmployees();
}
function field(label, name, type = "text", value = "", extra = {}) {
  const full = extra.full ? " full" : "", required = extra.required ? "required" : "", options = extra.options;
  if (type === "select") return `<div class="field${full}"><label for="field-${name}">${escapeHtml(label)}</label><select id="field-${name}" name="${name}" ${required}>${options}</select></div>`;
  if (type === "textarea") return `<div class="field${full}"><label for="field-${name}">${escapeHtml(label)}</label><textarea id="field-${name}" name="${name}" placeholder="Optional">${escapeHtml(value)}</textarea></div>`;
  return `<div class="field${full}"><label for="field-${name}">${escapeHtml(label)}</label><input id="field-${name}" name="${name}" type="${type}" value="${escapeHtml(value)}" ${required} ${extra.max ? `maxlength="${extra.max}"` : ""} ${extra.placeholder ? `placeholder="${escapeHtml(extra.placeholder)}"` : ""}></div>`;
}
function openModal({ title, description, fields, submit, kicker = "TEAM DIRECTORY" }) {
  const dialog = $("#form-modal"); $("#modal-title").textContent = title; $("#modal-description").textContent = description;
  $("#modal-kicker").textContent = kicker; $("#modal-fields").innerHTML = fields; $("#modal-error").textContent = "";
  $("#modal-form").onsubmit = async (event) => { event.preventDefault(); $("#modal-error").textContent = ""; $("#modal-submit").disabled = true;
    try { await submit(new FormData(event.currentTarget)); dialog.close(); toast("Saved. Your directory is up to date."); await refresh(); }
    catch (error) { $("#modal-error").textContent = error.message; }
    finally { $("#modal-submit").disabled = false; }
  };
  dialog.showModal();
}
async function employeeForm(employee = null) {
  const editing = Boolean(employee), departments = state.departments.filter((item) => item.is_active), roles = state.roles.filter((item) => item.is_active);
  let managers = [];
  try { managers = (await api("/employees?page=1&size=100")).items.filter((person) => person.id !== employee?.id).map((person) => ({ id: person.id, name: fullName(person) })); }
  catch (error) { toast(`Could not load manager choices: ${error.message}`, true); return; }
  if (employee?.manager && !managers.some((person) => person.id === employee.manager.id)) managers.unshift(employee.manager);
  const selectOptions = (items, selected, blank) => `<option value="">${blank}</option>${items.map((item) => `<option value="${item.id}" ${Number(selected) === item.id ? "selected" : ""}>${escapeHtml(item.name)}</option>`).join("")}`;
  const fields = `${field("First name", "first_name", "text", employee?.first_name || "", { required: true })}${field("Last name", "last_name", "text", employee?.last_name || "", { required: true })}${field("Work email", "work_email", "email", employee?.work_email || "", { required: true, full: true })}${field("Employee code", "employee_code", "text", employee?.employee_code || "", { required: true })}${field("Phone", "phone", "tel", employee?.phone || "")}${field("Department", "department_id", "select", "", { required: true, options: selectOptions(departments, employee?.department?.id, "Choose a department") })}${field("Role", "role_id", "select", "", { required: true, options: selectOptions(roles, employee?.role?.id, "Choose a role") })}${field("Joining date", "joining_date", "date", employee?.joining_date || new Date().toISOString().slice(0, 10), { required: true })}${field("Manager", "manager_id", "select", "", { options: selectOptions(managers, employee?.manager?.id, "No manager") })}`;
  openModal({ title: editing ? "Edit employee" : "Add employee", description: editing ? "Update this team member’s details." : "Add someone new to your team.", fields, submit: async (data) => {
    const body = Object.fromEntries(data.entries()); ["department_id", "role_id", "manager_id"].forEach((key) => { body[key] = body[key] ? Number(body[key]) : null; }); body.phone = body.phone || null;
    await api(editing ? `/employees/${employee.id}` : "/employees", { method: editing ? "PATCH" : "POST", body: JSON.stringify(body) });
  } });
}
function entityForm(kind) {
  const isDepartment = kind === "department", label = isDepartment ? "department" : "role", collection = isDepartment ? "departments" : "roles";
  openModal({ title: `Add ${label}`, description: `Create a ${label} in your directory.`, kicker: isDepartment ? "YOUR ORGANIZATION" : "CAREER & CRAFT", fields: `${field(`${isDepartment ? "Department" : "Role"} name`, "name", "text", "", { required: true })}${field("Description", "description", "textarea", "", { full: true })}`, submit: async (data) => {
    await api(`/${collection}`, { method: "POST", body: JSON.stringify({ name: data.get("name"), description: data.get("description") || null }) });
  } });
}
async function handleRowAction(button) {
  $$(".row-action-menu").forEach((menu) => menu.remove());
  const employee = state.employees.find((person) => person.id === Number(button.dataset.employeeAction)); if (!employee) return;
  const menu = document.createElement("div"); menu.className = "row-action-menu";
  menu.innerHTML = `<button data-edit-employee="${employee.id}">Edit details</button><button class="danger-action" data-deactivate-employee="${employee.id}">Deactivate</button>`;
  button.parentElement.append(menu);
}
async function refresh() {
  try { await loadSummary(); setConnection(true); }
  catch (error) { setConnection(false); toast(`Could not load the directory: ${error.message}`, true); }
  if (state.view === "employees") await loadEmployees();
}

$("#today-label").textContent = new Date().toLocaleDateString(undefined, { weekday: "long", month: "long", day: "numeric" });
$(".nav-list").addEventListener("click", (event) => { const button = event.target.closest("[data-view]"); if (button) go(button.dataset.view); });
document.addEventListener("click", (event) => {
  if (!event.target.closest(".action-cell")) $$(".row-action-menu").forEach((menu) => menu.remove());
  const nav = event.target.closest("[data-go]"); if (nav) go(nav.dataset.go);
  if (event.target.closest("#add-employee")) employeeForm(); if (event.target.closest("#add-department")) entityForm("department"); if (event.target.closest("#add-role")) entityForm("role");
  const action = event.target.closest("[data-employee-action]"); if (action) handleRowAction(action);
  const edit = event.target.closest("[data-edit-employee]"); if (edit) { const person = state.employees.find((employee) => employee.id === Number(edit.dataset.editEmployee)); if (person) employeeForm(person); }
  const deactivate = event.target.closest("[data-deactivate-employee]"); if (deactivate) {
    const person = state.employees.find((employee) => employee.id === Number(deactivate.dataset.deactivateEmployee));
    if (person && confirm(`Deactivate ${fullName(person)}? They will be removed from the active directory.`)) api(`/employees/${person.id}`, { method: "DELETE" }).then(() => { toast("Employee deactivated."); refresh(); }).catch((error) => toast(error.message, true));
  }
});
$("#refresh-button").addEventListener("click", refresh); $("#mobile-menu").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
$("#modal-close").addEventListener("click", () => $("#form-modal").close()); $("#modal-cancel").addEventListener("click", () => $("#form-modal").close());
$("#previous-page").addEventListener("click", () => { if (state.page > 1) { state.page--; loadEmployees(); } });
$("#next-page").addEventListener("click", () => { state.page++; loadEmployees(); });
let searchTimer; $("#employee-search").addEventListener("input", (event) => { clearTimeout(searchTimer); state.query = event.target.value; state.page = 1; searchTimer = setTimeout(loadEmployees, 230); });
$("#department-filter").addEventListener("change", (event) => { state.department = event.target.value; state.page = 1; loadEmployees(); });
$("#dashboard-search").addEventListener("keydown", (event) => { if (event.key === "Enter") { go("employees"); $("#employee-search").value = event.target.value; state.query = event.target.value; state.page = 1; loadEmployees(); } });

refresh().then(async () => {
  const filter = $("#department-filter"); filter.innerHTML = `<option value="">All departments</option>${state.departments.map((item) => `<option value="${item.id}">${escapeHtml(item.name)}</option>`).join("")}`;
});
