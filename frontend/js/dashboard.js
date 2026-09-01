const API = API_BASE + "/api";
const formatoMoneda = new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 });

let token = localStorage.getItem("kitty_token") || null;
let usuario = JSON.parse(localStorage.getItem("kitty_usuario") || "null");
let chartDona = null;
let chartLinea = null;

const $ = (id) => document.getElementById(id);

function mostrarError(msg) {
  const t = $("global-error");
  t.textContent = msg;
  t.hidden = false;
  clearTimeout(t._id);
  t._id = setTimeout(() => (t.hidden = true), 3500);
}

async function request(ruta, opciones = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(API + ruta, { ...opciones, headers });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) {
    if (res.status === 401 && token) { cerrarSesion(); }
    const err = new Error(data.error || "Error de servidor");
    err.status = res.status;
    throw err;
  }
  return data;
}

/* ---------- AUTH / SESIÓN ---------- */
function cerrarSesion() {
  localStorage.removeItem("kitty_token");
  localStorage.removeItem("kitty_usuario");
  window.location.href = "index.html";
}

$("logout-btn").addEventListener("click", cerrarSesion);

/* ---------- DATOS ---------- */
async function cargarTodo() {
  setLoader(true);
  try {
    await Promise.all([cargarCategorias(), cargarResumen(), cargarPrediccion(),
      cargarGraficos(), cargarAnomalias(), cargarMovimientos()]);
  } catch (e) {
    mostrarError(e.message);
  } finally {
    setLoader(false);
  }
}
function setLoader(activo) {
  document.querySelector(".main").style.opacity = activo ? ".5" : "1";
  document.querySelector(".main").style.pointerEvents = activo ? "none" : "auto";
}

async function cargarCategorias() {
  const cats = await request(`/categorias?id_usuario=${usuario.id}`);
  $("f-categoria").innerHTML = '<option value="">Categoría</option>'
    + cats.map((c) => `<option value="${c.id}">${c.nombre}</option>`).join("");
}
async function cargarResumen() {
  const r = await request(`/resumen?id_usuario=${usuario.id}`);
  $("card-ingresos").textContent = formatoMoneda.format(r.ingresos);
  $("card-gastos").textContent = formatoMoneda.format(r.gastos);
  $("card-balance").textContent = formatoMoneda.format(r.balance);
}
async function cargarPrediccion() {
  const p = await request(`/analitica/prediccion?id_usuario=${usuario.id}`);
  $("card-prediccion").textContent = p.prediccion_proximo_mes != null
    ? formatoMoneda.format(p.prediccion_proximo_mes) + " (" + p.confianza + ")"
    : "Sin datos";
}
async function cargarGraficos() {
  const e = await request(`/analitica/estadisticas?id_usuario=${usuario.id}`);
  const ctxD = $("chart-dona").getContext("2d");
  const ctxL = $("chart-linea").getContext("2d");
  if (chartDona) chartDona.destroy();
  if (chartLinea) chartLinea.destroy();
  const colores = ["#fd9132", "#d14835", "#6ee7a0", "#87ceeb", "#fee085", "#b8acd6", "#ff6b81", "#87e0fd"];
  chartDona = new Chart(ctxD, {
    type: "doughnut",
    data: {
      labels: e.por_categoria.map((c) => c.categoria),
      datasets: [{ data: e.por_categoria.map((c) => c.total), backgroundColor: colores }],
    },
  });
  chartLinea = new Chart(ctxL, {
    type: "line",
    data: {
      labels: e.tendencia.map((t) => t.mes),
      datasets: [
        { label: "Ingresos", data: e.tendencia.map((t) => t.ingresos), borderColor: "#6ee7a0", tension: .3 },
        { label: "Gastos", data: e.tendencia.map((t) => t.gastos), borderColor: "#ff6b81", tension: .3 },
      ],
    },
  });
}
async function cargarAnomalias() {
  const an = await request(`/analitica/anomalias?id_usuario=${usuario.id}`);
  $("lista-anomalias").innerHTML = an.length
    ? an.map((a) => `<li>${a.fecha} · ${a.categoria}: ${formatoMoneda.format(a.monto)} (media ${formatoMoneda.format(a.media_categoria)})</li>`).join("")
    : "<li>Sin anomalías detectadas 🐾</li>";
}
async function cargarMovimientos() {
  const ms = await request(`/movimientos?id_usuario=${usuario.id}`);
  $("tabla-movimientos").innerHTML = ms.map((m) => `
    <tr>
      <td>${m.fecha}</td><td>${m.categoria}</td><td>${m.tipo}</td>
      <td class="${m.tipo === "ingreso" ? "monto-ingreso" : "monto-gasto"}">${formatoMoneda.format(m.monto)}</td>
      <td>${m.descripcion || ""}</td>
      <td><button class="boton elim" data-id="${m.id}">Eliminar</button></td>
    </tr>`).join("") || "<tr><td colspan='6'>Sin movimientos</td></tr>";
  document.querySelectorAll(".elim").forEach((b) =>
    b.addEventListener("click", () => eliminarMovimiento(b.dataset.id)));
}

$("form-movimiento").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const payload = {
    id_usuario: usuario.id,
    id_categoria: Number($("f-categoria").value),
    tipo: $("f-tipo").value,
    monto: Number($("f-monto").value),
    fecha: $("f-fecha").value,
    descripcion: $("f-descripcion").value,
  };
  if (!payload.id_categoria || !payload.fecha || payload.monto <= 0) {
    mostrarError("Completa categoría, monto y fecha.");
    return;
  }
  try {
    await request("/movimientos", { method: "POST", body: JSON.stringify(payload) });
    ev.target.reset();
    await cargarTodo();
  } catch (e) { mostrarError(e.message); }
});

$("form-categoria").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    await request("/categorias", {
      method: "POST",
      body: JSON.stringify({ id_usuario: usuario.id, nombre: $("f-nueva-cat").value }),
    });
    ev.target.reset();
    await cargarCategorias();
  } catch (e) { mostrarError(e.message); }
});

async function eliminarMovimiento(id) {
  try {
    await request(`/movimientos/${id}`, { method: "DELETE" });
    await cargarTodo();
  } catch (e) { mostrarError(e.message); }
}

/* ---------- CHATBOT KITTY ---------- */
$("kitty-fab").addEventListener("click", () => {
  $("kitty-chat").hidden = !$("kitty-chat").hidden;
  if (!$("kitty-chat").hidden && !$("chat-body").children.length) {
    agregarMsg("kitty", "¡Miau! Soy Kitty 🐾 ¿Quieres consejos sobre ahorro, tus gastos o tu estado general?");
  }
});
$("chat-close").addEventListener("click", () => ($("kitty-chat").hidden = true));

function agregarMsg(quien, texto) {
  const div = document.createElement("div");
  div.className = "msg " + quien;
  div.textContent = texto;
  $("chat-body").appendChild(div);
  $("chat-body").scrollTop = $("chat-body").scrollHeight;
}

$("chat-form").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const txt = $("chat-text").value.trim();
  if (!txt) return;
  agregarMsg("user", txt);
  $("chat-text").value = "";
  try {
    const r = await request("/chatbot", { method: "POST", body: JSON.stringify({ mensaje: txt }) });
    r.respuestas.forEach((m, i) => setTimeout(() => agregarMsg("kitty", m), i * 600));
  } catch (e) { agregarMsg("kitty", "Perdón, no pude responder. Revisa la conexión 🐾"); }
});

/* ---------- INICIO ---------- */
if (!token || !usuario) {
  window.location.href = "index.html";
} else {
  $("user-name").textContent = usuario.nombre;
  cargarTodo();
}
