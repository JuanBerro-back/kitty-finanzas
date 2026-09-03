const API = API_BASE + "/api";

const $ = (id) => document.getElementById(id);

let token = localStorage.getItem("kitty_token") || null;
let usuario = JSON.parse(localStorage.getItem("kitty_usuario") || "null");

async function request(ruta, opciones = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = "Bearer " + token;
  const res = await fetch(API + ruta, { ...opciones, headers });
  if (res.status === 204) return null;
  const data = await res.json();
  if (!res.ok) {
    const err = new Error(data.error || "Error de servidor");
    err.status = res.status;
    throw err;
  }
  return data;
}

function guardarSesion(data) {
  localStorage.setItem("kitty_token", data.token);
  localStorage.setItem("kitty_usuario", JSON.stringify(data.usuario));
  window.location.href = "dashboard.html";
}

function setAuthError(msg) {
  const e = $("auth-error");
  e.textContent = msg;
  e.hidden = !msg;
}

function activarTab(registro) {
  $("tab-login").classList.toggle("is-active", !registro);
  $("tab-register").classList.toggle("is-active", registro);
  document.querySelector(".forms-slider").classList.toggle("mostrar-registro", registro);
  setAuthError("");
}
$("tab-login").addEventListener("click", () => activarTab(false));
$("tab-register").addEventListener("click", () => activarTab(true));

$("form-login").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    const data = await request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email: $("li-email").value, password: $("li-password").value }),
    });
    guardarSesion(data);
  } catch (e) { setAuthError(e.message); }
});

$("form-register").addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    const data = await request("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        nombre: $("rg-nombre").value,
        email: $("rg-email").value,
        password: $("rg-password").value,
      }),
    });
    guardarSesion(data);
  } catch (e) { setAuthError(e.message); }
});

/* ---------- LOGIN CON GOOGLE (GIS) ---------- */
const GOOGLE_CLIENT_ID = "61510338551-29nagua32pgrm0j3ckjo6b3d550jkcgl.apps.googleusercontent.com";

function mostrarAuthError(msg) {
  const el = $("google-auth-hint");
  el.textContent = msg || "";
  el.hidden = !msg;
}

function initGoogleButton() {
  const contenedor = $("googleSignInDiv");
  if (!contenedor) return;
  window.google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: async (resp) => {
      try {
        if (!resp || !resp.credential) throw new Error("No se recibió credencial de Google");
        const res = await fetch(API + "/auth/google", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ id_token: resp.credential }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Error al iniciar sesión con Google");
        guardarSesion(data);
      } catch (e) {
        setAuthError(e.message);
      }
    },
    auto_select: false,
    cancel_on_tap_outside: true,
  });
  window.google.accounts.id.renderButton(contenedor, {
    theme: "filled_black",
    size: "large",
    shape: "pill",
    text: "signin_with",
    width: 320,
    logo_alignment: "left",
  });
}

function setupGoogleSignIn() {
  if (window.google && window.google.accounts) {
    initGoogleButton();
    return;
  }
  let reintentos = 0;
  const esperar = setInterval(() => {
    if (window.google && window.google.accounts) {
      clearInterval(esperar);
      initGoogleButton();
    } else if (++reintentos >= 20) {
      clearInterval(esperar);
      mostrarAuthError("Google no está disponible. Revisa tu conexión o usa email y contraseña.");
    }
  }, 300);
}

document.addEventListener("DOMContentLoaded", setupGoogleSignIn);

/* ---------- CHATBOT LOCAL (sin sesión) ---------- */
function kittyLocal(texto) {
  const t = texto.toLowerCase();
  if (["hola", "buenas", "hey", "hi", "que tal"].some((p) => t.includes(p)))
    return "Hola! Soy Kitty. Crea tu cuenta o inicia sesion para que pueda analizar tus finanzas y darte consejos con tus datos reales.";
  if (["gracias", "chao", "adios", "bye", "nos vemos"].some((p) => t.includes(p)))
    return "De nada! Te espero dentro, me encantara ayudarte con tus finanzas.";
  if (["que puedes", "ayuda", "help", "que haces", "funciones", "puedes hacer"].some((p) => t.includes(p)))
    return "Una vez dentro del panel puedo decirte tu balance, ahorro, categoria mas costosa, prediccion y anomalias. Aqui todavia no tienes sesion; registrate o entra para empezar.";
  if (["consejo", "tip", "recomenda", "sugerencia"].some((p) => t.includes(p)))
    return "Mini consejo: separa al menos un 20% de cada ingreso para ahorro y anota todos tus gastos. Crea tu cuenta para que te ayude con numeros reales.";
  return "Puedo saludarte y darte consejos generales aqui. Para ver tu situacion con datos reales, crea una cuenta o inicia sesion.";
}

$("kitty-fab").addEventListener("click", () => {
  $("kitty-chat").hidden = !$("kitty-chat").hidden;
  if (!$("kitty-chat").hidden && !$("chat-body").children.length) {
    agregarMsgLocal("kitty", t('kitty-greeting-auth'));
  }
});
$("chat-close").addEventListener("click", () => ($("kitty-chat").hidden = true));

function agregarMsgLocal(quien, texto) {
  const div = document.createElement("div");
  div.className = "msg " + quien;
  div.textContent = texto;
  $("chat-body").appendChild(div);
  $("chat-body").scrollTop = $("chat-body").scrollHeight;
}

$("chat-form").addEventListener("submit", (ev) => {
  ev.preventDefault();
  const txt = $("chat-text").value.trim();
  if (!txt) return;
  agregarMsgLocal("user", txt);
  $("chat-text").value = "";
  setTimeout(() => agregarMsgLocal("kitty", kittyLocal(txt)), 500);
});

/* ---------- INICIO ---------- */
if (token && usuario) {
  window.location.href = "dashboard.html";
}
