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

function requiereSesion() {
  const usuarioActual = getUsuarioActual();

  if (!usuarioActual) {
    alert("Debes iniciar sesión para realizar esta acción.");
    window.location.href = "login.html";
    return null;
  }

  return usuarioActual;
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
  const rutasProtegidas = ["/publicaciones/", "/comentarios/", "/denuncias/"];

  if (rutasProtegidas.includes(ruta)) {
    const usuarioActual = requiereSesion();

    if (!usuarioActual) {
      return $.Deferred().reject({
        responseJSON: { detail: "Debes iniciar sesión para realizar esta acción." },
      }).promise();
    }

    if (ruta === "/publicaciones/") {
      datos.usuario_id = usuarioActual.id;
    }

    if (ruta === "/comentarios/" && !datos.autor) {
      datos.autor = usuarioActual.usuario || usuarioActual.nombre || "Usuario";
    }

    if (ruta === "/denuncias/") {
      datos.usuario_id = usuarioActual.id;
    }
  }

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
  if (ruta.startsWith("/publicaciones/") && !ruta.includes("usuario_id=")) {
    const usuarioActual = requiereSesion();

    if (!usuarioActual) {
      return $.Deferred().reject({
        responseJSON: { detail: "Debes iniciar sesión para eliminar publicaciones." },
      }).promise();
    }

    const separador = ruta.includes("?") ? "&" : "?";
    ruta = ruta + separador + "usuario_id=" + usuarioActual.id;
  }

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

function insertarLinkNormas() {
  if ($('a[href="normas.html"]').length > 0) {
    return;
  }

  if ($("nav").length > 0) {
    $(".link-salir").before('<a href="normas.html">Normas y ética</a>');
  }
}

function activarBotonDenuncia() {
  if (!window.location.pathname.includes("detalle.html")) {
    return;
  }

  if ($("#btn-denunciar-etica").length > 0) {
    return;
  }

  const boton = `
    <div style="margin: 20px 0;">
      <button id="btn-denunciar-etica" type="button">
        Denunciar publicación
      </button>
      <p id="mensaje-denuncia-etica"></p>
    </div>
  `;

  if ($("main").length > 0) {
    $("main").append(boton);
  } else {
    $("body").append(boton);
  }

  $(document).on("click", "#btn-denunciar-etica", function () {
    const usuarioActual = requiereSesion();
    if (!usuarioActual) return;

    const publicacionId = Number(obtenerParametro("id"));

    if (!publicacionId) {
      $("#mensaje-denuncia-etica").text("No se pudo identificar la publicación.");
      return;
    }

    const motivo = prompt("Escribe el motivo de la denuncia:");

    if (!motivo || motivo.trim().length < 5) {
      alert("El motivo debe tener al menos 5 caracteres.");
      return;
    }

    apiPost("/denuncias/", {
      publicacion_id: publicacionId,
      usuario_id: usuarioActual.id,
      motivo: motivo,
    })
      .done(function (respuesta) {
        $("#mensaje-denuncia-etica").text(respuesta.message);
      })
      .fail(function (error) {
        const mensaje = error.responseJSON?.detail || "No se pudo registrar la denuncia.";
        $("#mensaje-denuncia-etica").text(mensaje);
      });
  });
}

$(document).ready(function () {
  insertarLinkNormas();
  actualizarNavbar();
  activarBotonDenuncia();

  $(document).on("click", ".link-salir", function (event) {
    event.preventDefault();
    cerrarSesion();
  });
});
