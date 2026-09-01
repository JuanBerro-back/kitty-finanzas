// ── Traducciones ────────────────────────────────────────────────────────────
const TRANSLATIONS = {
  es: {
    // Auth
    "page-title-auth"     : "Kitty Finanzas · Iniciar sesión",
    "tab-login"           : "Iniciar sesión",
    "tab-register"        : "Registrarse",
    "li-email-ph"         : "Correo electrónico",
    "li-password-ph"      : "Contraseña",
    "btn-login"           : "Entrar",
    "rg-nombre-ph"        : "Nombre",
    "rg-email-ph"         : "Correo electrónico",
    "rg-password-ph"      : "Contraseña (mín. 6)",
    "btn-register"        : "Crear cuenta",
    "speech-bubble"       : "Bienvenido a tus finanzas",
    "sub-text"            : "Tu asistente financiera",
    "chat-ph"             : "Pregúntale a Kitty...",
    // Dashboard
    "page-title-dash"     : "Kitty Finanzas · Dashboard",
    "label-ingresos"      : "Ingresos",
    "label-gastos"        : "Gastos",
    "label-balance"       : "Balance",
    "label-prediccion"    : "Predicción mes",
    "h2-movimiento"       : "Registrar movimiento",
    "opt-categoria"       : "Categoría",
    "opt-tipo"            : "Tipo",
    "opt-gasto"           : "Gasto",
    "opt-ingreso"         : "Ingreso",
    "ph-monto"            : "Monto",
    "ph-descripcion"      : "Descripción (opcional)",
    "btn-guardar"         : "Guardar",
    "h2-nueva-cat"        : "Nueva categoría",
    "ph-nueva-cat"        : "Ej: Transporte",
    "btn-aniadir"         : "Añadir",
    "h3-dona"             : "Gastos por categoría",
    "h3-linea"            : "Ingresos vs Gastos",
    "h2-anomalias"        : "Anomalias detectadas",
    "h2-movimientos"      : "Movimientos recientes",
    "th-fecha"            : "Fecha",
    "th-categoria"        : "Categoría",
    "th-tipo"             : "Tipo",
    "th-monto"            : "Monto",
    "th-descripcion"      : "Descripción",
    "btn-cerrar-sesion"   : "Cerrar sesión",
    "btn-eliminar"        : "Eliminar",
    "sin-movimientos"     : "Sin movimientos",
    "sin-anomalias"       : "Sin anomalias detectadas",
    "err-form"            : "Completa categoria, tipo, monto y fecha.",
    "kitty-greeting-dash" : "Hola! Soy Kitty. Que quieres saber sobre ahorro, tus gastos o tu estado general?",
    "kitty-greeting-auth" : "Hola! Soy Kitty. Aqui te doy consejos generales. Registrate o inicia sesion para un analisis con tus datos.",
    "kitty-err"           : "Perdon, no pude responder. Revisa la conexion.",
    "consejera"           : "consejera de finanzas",
  },
  en: {
    // Auth
    "page-title-auth"     : "Kitty Finance · Sign in",
    "tab-login"           : "Sign in",
    "tab-register"        : "Register",
    "li-email-ph"         : "Email address",
    "li-password-ph"      : "Password",
    "btn-login"           : "Enter",
    "rg-nombre-ph"        : "Name",
    "rg-email-ph"         : "Email address",
    "rg-password-ph"      : "Password (min. 6)",
    "btn-register"        : "Create account",
    "speech-bubble"       : "Welcome to your finances",
    "sub-text"            : "Your personal finance assistant",
    "chat-ph"             : "Ask Kitty...",
    // Dashboard
    "page-title-dash"     : "Kitty Finance · Dashboard",
    "label-ingresos"      : "Income",
    "label-gastos"        : "Expenses",
    "label-balance"       : "Balance",
    "label-prediccion"    : "Monthly forecast",
    "h2-movimiento"       : "Record transaction",
    "opt-categoria"       : "Category",
    "opt-tipo"            : "Type",
    "opt-gasto"           : "Expense",
    "opt-ingreso"         : "Income",
    "ph-monto"            : "Amount",
    "ph-descripcion"      : "Description (optional)",
    "btn-guardar"         : "Save",
    "h2-nueva-cat"        : "New category",
    "ph-nueva-cat"        : "E.g.: Transport",
    "btn-aniadir"         : "Add",
    "h3-dona"             : "Expenses by category",
    "h3-linea"            : "Income vs Expenses",
    "h2-anomalias"        : "Detected anomalies",
    "h2-movimientos"      : "Recent transactions",
    "th-fecha"            : "Date",
    "th-categoria"        : "Category",
    "th-tipo"             : "Type",
    "th-monto"            : "Amount",
    "th-descripcion"      : "Description",
    "btn-cerrar-sesion"   : "Sign out",
    "btn-eliminar"        : "Delete",
    "sin-movimientos"     : "No transactions",
    "sin-anomalias"       : "No anomalies detected",
    "err-form"            : "Fill in category, type, amount and date.",
    "kitty-greeting-dash" : "Hi! I'm Kitty. What do you want to know about savings, expenses or your overall status?",
    "kitty-greeting-auth" : "Hi! I'm Kitty. I can give you general advice here. Register or sign in for a full analysis.",
    "kitty-err"           : "Sorry, I couldn't respond. Please check your connection.",
    "consejera"           : "finance advisor",
  }
};

// ── Estado global ────────────────────────────────────────────────────────────
let _lang = localStorage.getItem("kitty_lang") || "es";
let _theme = localStorage.getItem("kitty_theme") || "dark";

function t(key) {
  return (TRANSLATIONS[_lang] || TRANSLATIONS["es"])[key] || key;
}

// ── Aplicar idioma: actualiza data-i18n y placeholders ───────────────────────
function applyLang() {
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = t(key);
    } else {
      el.textContent = t(key);
    }
  });
  document.querySelectorAll("[data-i18n-ph]").forEach(el => {
    el.placeholder = t(el.dataset.i18nPh);
  });
  // Actualizar título de página
  const titleKey = document.body.dataset.titleKey;
  if (titleKey) document.title = t(titleKey);
  // Marcar botón activo
  document.querySelectorAll(".lang-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.lang === _lang);
  });
  localStorage.setItem("kitty_lang", _lang);
}

// ── Aplicar tema ─────────────────────────────────────────────────────────────
function applyTheme() {
  document.documentElement.setAttribute("data-theme", _theme);
  const icon = document.getElementById("theme-icon");
  if (icon) icon.textContent = _theme === "dark" ? "☀" : "☾";
  localStorage.setItem("kitty_theme", _theme);
}

// ── Inicializar controles ─────────────────────────────────────────────────────
function initControls() {
  // Botones de idioma
  document.querySelectorAll(".lang-btn").forEach(b => {
    b.addEventListener("click", () => {
      _lang = b.dataset.lang;
      applyLang();
    });
  });
  // Botón de tema
  const themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      _theme = _theme === "dark" ? "light" : "dark";
      applyTheme();
    });
  }
}

// ── Auto-init al cargar ───────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  applyTheme();
  applyLang();
  initControls();
});
