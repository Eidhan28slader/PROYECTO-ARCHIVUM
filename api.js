const API_URL = window.location.port === "8000"
  ? window.location.origin
  : "http://127.0.0.1:8000";

function getUsuarioActual() {
  const usuarioGuardado = localStorage.getItem("usuarioActual");
  return usuarioGuardado ? JSON.parse(usuarioGuardado) : null;
}

function guardarUsuarioActual(usuario) {
  localStorage.setItem("usuarioActual", JSON.stringify(usuario));
}

function cerrarSesion() {
  localStorage.removeItem("usuarioActual");
  window.location.href = "login.html";
}

function obtenerParametro(nombre) {
  return new URLSearchParams(window.location.search).get(nombre);
}

function escaparHtml(texto) {
  return String(texto || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function apiGet(ruta) {
  return $.ajax({
    url: API_URL + ruta,
    method: "GET",
    dataType: "json",
  });
}

function apiPost(ruta, datos) {
  return $.ajax({
    url: API_URL + ruta,
    method: "POST",
    contentType: "application/json",
    data: JSON.stringify(datos),
    dataType: "json",
  });
}

function apiPut(ruta, datos) {
  return $.ajax({
    url: API_URL + ruta,
    method: "PUT",
    contentType: "application/json",
    data: JSON.stringify(datos),
    dataType: "json",
  });
}

function apiDelete(ruta) {
  return $.ajax({
    url: API_URL + ruta,
    method: "DELETE",
    dataType: "json",
  });
}

function mostrarMensaje(selector, texto, tipo = "info") {
  $(selector)
    .removeClass("mensaje-error mensaje-exito mensaje-info")
    .addClass("mensaje-" + tipo)
    .text(texto)
    .hide()
    .fadeIn(150);
}

function actualizarNavbar() {
  const usuarioActual = getUsuarioActual();
  if (usuarioActual) {
    $(".link-login").hide();
    $(".link-register").hide();
    $(".link-usuario").show();
    $(".link-salir").show();
    $(".nav-user").text("@" + usuarioActual.usuario).show();
  } else {
    $(".link-login").show();
    $(".link-register").show();
    $(".link-usuario").hide();
    $(".link-salir").hide();
    $(".nav-user").hide();
  }
}

$(document).ready(function () {
  actualizarNavbar();

  $(document).on("click", ".link-salir", function (event) {
    event.preventDefault();
    cerrarSesion();
  });
});
