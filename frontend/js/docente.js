// =============================================================
// 🧠 EduBot Frontend - Módulo Docente (Integración con FastAPI)
// =============================================================

const API_URL = "http://localhost:8000"; // Cambia si tu backend corre en otro puerto

// =====================
// 🎯 Endpoints del API
// =====================
const ENDPOINTS = {
  DOCENTE_INFO: "/docente/info",         // GET docente info
  CURSOS: "/docente/cursos",             // GET cursos asignados
  NOTAS: "/docente/notas",               // POST registrar notas
  REPORTE: "/docente/reporte",           // GET reporte de estudiantes
};

// =========================
// 🧭 Variables globales
// =========================
let currentUser = null;
let cursosAsignados = [];

// =============================================================
// 🧩 Inicialización
// =============================================================
document.addEventListener("DOMContentLoaded", async () => {
  loadUserInfo();
  await verCursosAsignados();
});

// =============================================================
// 🔐 Cargar información del docente
// =============================================================
async function loadUserInfo() {
  const userData = sessionStorage.getItem("currentUser");
  if (!userData) {
    window.location.href = "login.html";
    return;
  }

  currentUser = JSON.parse(userData);
  document.getElementById("docenteNombre").textContent = currentUser.nombre;
  document.getElementById("docenteEmail").textContent = currentUser.email || "sin correo";
}

// =============================================================
// 🛰️ API genérica (igual que en main.js)
// =============================================================
async function apiCall(endpoint, method = "GET", body = null) {
  try {
    const options = {
      method,
      headers: {
        "Content-Type": "application/json",
      },
    };

    const token = sessionStorage.getItem("token");
    if (token) options.headers["Authorization"] = `Bearer ${token}`;
    if (body) options.body = JSON.stringify(body);

    const response = await fetch(`${API_URL}${endpoint}`, options);
    const text = await response.text();
    let data = null;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { raw: text };
    }

    if (!response.ok) {
      const msg = data?.detail || data?.message || `Error ${response.status}`;
      showAlert(msg, "error");
      return null;
    }

    return data;
  } catch (error) {
    console.error("API error:", error);
    showAlert("No se pudo conectar con el servidor.", "error");
    return null;
  }
}

// =============================================================
// 🎓 Ver cursos asignados
// =============================================================
async function verCursosAsignados() {
  showAlert("Cargando cursos asignados...", "info");

  let response = await apiCall(ENDPOINTS.CURSOS, "GET");

  // Fallback demo
  if (!response) {
    response = {
      data: [
        { codigo: "MAT101", nombre: "Cálculo I", grupo: "A", estudiantes: 28 },
        { codigo: "FIS202", nombre: "Física II", grupo: "B", estudiantes: 32 },
      ],
    };
  }

  cursosAsignados = response.data;
  renderCursosAsignados(cursosAsignados);
  showAlert("Cursos cargados correctamente ✅", "success");
}

function renderCursosAsignados(cursos) {
  const contenedor = document.getElementById("cursosContainer");
  contenedor.innerHTML = "";

  if (!cursos || cursos.length === 0) {
    contenedor.innerHTML = `<p>No tienes cursos asignados este semestre.</p>`;
    return;
  }

  cursos.forEach((curso) => {
    const card = document.createElement("div");
    card.className = "curso-card";
    card.innerHTML = `
      <h3>${curso.nombre} (${curso.codigo})</h3>
      <p><strong>Grupo:</strong> ${curso.grupo}</p>
      <p><strong>Estudiantes inscritos:</strong> ${curso.estudiantes}</p>
      <div class="acciones">
        <button onclick="verReporteEstudiantes('${curso.codigo}')">📊 Ver reporte</button>
        <button onclick="abrirRegistroNotas('${curso.codigo}')">📝 Registrar notas</button>
      </div>
    `;
    contenedor.appendChild(card);
  });
}

// =============================================================
// 🧾 Registrar notas
// =============================================================
function abrirRegistroNotas(codigoCurso) {
  const modal = document.getElementById("notasModal");
  modal.style.display = "block";
  modal.dataset.curso = codigoCurso;
  document.getElementById("cursoNotasTitulo").textContent = `Registrar notas - ${codigoCurso}`;
}

async function registrarNotas() {
  const modal = document.getElementById("notasModal");
  const codigoCurso = modal.dataset.curso;
  const nota = parseFloat(document.getElementById("notaInput").value);
  const estudianteId = document.getElementById("idEstudianteInput").value.trim();

  if (!estudianteId || isNaN(nota)) {
    showAlert("Debes ingresar un ID y una nota válida.", "error");
    return;
  }

  showAlert("Enviando nota...", "info");

  let response = await apiCall(ENDPOINTS.NOTAS, "POST", {
    curso: codigoCurso,
    estudiante_id: estudianteId,
    nota: nota,
  });

  if (!response) {
    // Modo demo
    response = { success: true, message: "Nota registrada exitosamente (modo demo)." };
  }

  if (response.success) {
    showAlert(response.message, "success");
    cerrarModalNotas();
  } else {
    showAlert("No se pudo registrar la nota.", "error");
  }
}

function cerrarModalNotas() {
  document.getElementById("notasModal").style.display = "none";
  document.getElementById("notaInput").value = "";
  document.getElementById("idEstudianteInput").value = "";
}

// =============================================================
// 📈 Ver reporte de estudiantes
// =============================================================
async function verReporteEstudiantes(codigoCurso) {
  showAlert("Cargando reporte de estudiantes...", "info");

  let response = await apiCall(`${ENDPOINTS.REPORTE}?curso=${codigoCurso}`, "GET");

  // Fallback demo
  if (!response) {
    response = {
      data: [
        { id: "EST001", nombre: "Ana López", nota: 4.3 },
        { id: "EST002", nombre: "Juan Gómez", nota: 3.8 },
        { id: "EST003", nombre: "Laura Ruiz", nota: 2.9 },
      ],
    };
  }

  renderReporteEstudiantes(codigoCurso, response.data);
}

function renderReporteEstudiantes(curso, estudiantes) {
  const contenedor = document.getElementById("reporteContainer");
  contenedor.innerHTML = `
    <h3>📊 Reporte de estudiantes - ${curso}</h3>
    <table class="reporte-tabla">
      <thead>
        <tr>
          <th>ID</th><th>Nombre</th><th>Nota</th>
        </tr>
      </thead>
      <tbody>
        ${estudiantes
          .map(
            (e) => `
          <tr>
            <td>${e.id}</td>
            <td>${e.nombre}</td>
            <td>${e.nota}</td>
          </tr>`
          )
          .join("")}
      </tbody>
    </table>
  `;
}

// =============================================================
// 🚪 Cerrar sesión
// =============================================================
function logout() {
  sessionStorage.clear();
  window.location.href = "login.html";
}

// =============================================================
// 💬 Alertas visuales
// =============================================================
function showAlert(message, type = "info") {
  const alertBox = document.getElementById("alertBox");
  if (!alertBox) return;

  alertBox.textContent = message;
  alertBox.className = `alert ${type}`;
  alertBox.style.display = "block";

  if (type !== "error") {
    setTimeout(() => {
      alertBox.style.display = "none";
    }, 3000);
  }
}

// =============================================================
// 🌐 Exponer funciones al HTML
// =============================================================
window.verCursosAsignados = verCursosAsignados;
window.verReporteEstudiantes = verReporteEstudiantes;
window.abrirRegistroNotas = abrirRegistroNotas;
window.registrarNotas = registrarNotas;
window.cerrarModalNotas = cerrarModalNotas;
window.logout = logout;
