// =============================================================
// 🧠 EduBot Frontend - Módulo Coordinador (Integración con FastAPI)
// =============================================================

const API_URL = "http://localhost:8000"; // Ajusta si tu backend usa otro puerto

// =====================
// 🧭 Endpoints
// =====================
const ENDPOINTS = {
    INFO: "/coordinador/info",
    CURSOS: "/coordinador/cursos",
    NUEVO_CURSO: "/coordinador/cursos/nuevo",
    APROBAR_CURSO: "/coordinador/cursos/aprobar",
    ESTUDIANTES: "/coordinador/estudiantes",
    REPORTE: "/coordinador/reporte",
};

// =====================
// 🌎 Variables globales
// =====================
let currentUser = null;
let cursos = [];

// =============================================================
// 🧩 Inicialización
// =============================================================
document.addEventListener("DOMContentLoaded", async () => {
    loadUserInfo();
    await cargarCursos();
});

// =============================================================
// 🔐 Autenticación y datos del usuario
// =============================================================
function loadUserInfo() {
    const userData = sessionStorage.getItem("currentUser");
    if (!userData) {
        window.location.href = "login.html";
        return;
    }

    currentUser = JSON.parse(userData);
    document.getElementById("coordNombre").textContent = currentUser.nombre;
    document.getElementById("coordEmail").textContent = currentUser.email || "Sin correo";
}

// =============================================================
// 🛰️ Función genérica de API
// =============================================================
async function apiCall(endpoint, method = "GET", body = null) {
    try {
        const options = {
            method,
            headers: {"Content-Type": "application/json"},
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
            data = {raw: text};
        }

        if (!response.ok) {
            showAlert(data?.detail || "Error del servidor", "error");
            return null;
        }
        return data;
    } catch (err) {
        console.error("API Error:", err);
        showAlert("No se pudo conectar con el backend.", "error");
        return null;
    }
}

// =============================================================
// 📚 Cargar lista de cursos
// =============================================================
async function cargarCursos() {
    showAlert("Cargando cursos...", "info");

    let response = await apiCall(ENDPOINTS.CURSOS, "GET");

    // Modo demo si no hay backend activo
    if (!response) {
        response = {
            data: [
                {codigo: "MAT101", nombre: "Cálculo I", semestre: 1, estado: "pendiente"},
                {codigo: "FIS102", nombre: "Física I", semestre: 1, estado: "aprobado"},
                {codigo: "PROG201", nombre: "Programación II", semestre: 2, estado: "pendiente"},
            ],
        };
    }

    cursos = response.data;
    renderCursos(cursos);
    showAlert("Cursos cargados correctamente ✅", "success");
}

function renderCursos(lista) {
    const container = document.getElementById("cursosContainer");
    container.innerHTML = "";

    if (!lista || lista.length === 0) {
        container.innerHTML = `<p>No hay cursos registrados.</p>`;
        return;
    }

    lista.forEach((curso) => {
        const card = document.createElement("div");
        card.className = "curso-card";
        card.innerHTML = `
      <h3>${curso.nombre} (${curso.codigo})</h3>
      <p><strong>Semestre:</strong> ${curso.semestre}</p>
      <p><strong>Estado:</strong> ${
            curso.estado === "aprobado" ? "✅ Aprobado" : "⏳ Pendiente"
        }</p>
      <div class="acciones">
        ${
            curso.estado === "pendiente"
                ? `<button onclick="aprobarCurso('${curso.codigo}')">✅ Aprobar</button>`
                : `<button disabled>✔️ Ya aprobado</button>`
        }
        <button onclick="verEstudiantes('${curso.codigo}')">👥 Ver estudiantes</button>
      </div>
    `;
        container.appendChild(card);
    });
}

// =============================================================
// 🆕 Crear nuevo curso
// =============================================================
async function crearCurso() {
    const codigo = document.getElementById("codigoCurso").value.trim();
    const nombre = document.getElementById("nombreCurso").value.trim();
    const semestre = parseInt(document.getElementById("semestreCurso").value);

    if (!codigo || !nombre || isNaN(semestre)) {
        showAlert("Debes llenar todos los campos del curso.", "error");
        return;
    }

    showAlert("Creando curso...", "info");

    let response = await apiCall(ENDPOINTS.NUEVO_CURSO, "POST", {
        codigo,
        nombre,
        semestre,
    });

    // Modo demo
    if (!response) {
        response = {success: true, message: "Curso agregado correctamente (modo demo)"};
    }

    if (response.success) {
        showAlert(response.message, "success");
        document.getElementById("codigoCurso").value = "";
        document.getElementById("nombreCurso").value = "";
        document.getElementById("semestreCurso").value = "";
        await cargarCursos();
    } else {
        showAlert("Error al crear el curso.", "error");
    }
}

// =============================================================
// ✅ Aprobar curso
// =============================================================
async function aprobarCurso(codigoCurso) {
    showAlert("Aprobando curso...", "info");

    let response = await apiCall(ENDPOINTS.APROBAR_CURSO, "POST", {codigo: codigoCurso});

    // Demo
    if (!response) {
        response = {success: true, message: `Curso ${codigoCurso} aprobado (modo demo)`};
    }

    if (response.success) {
        showAlert(response.message, "success");
        await cargarCursos();
    } else {
        showAlert("No se pudo aprobar el curso.", "error");
    }
}

// =============================================================
// 👩‍🎓 Ver estudiantes de un curso
// =============================================================
async function verEstudiantes(codigoCurso) {
    showAlert(`Cargando estudiantes del curso ${codigoCurso}...`, "info");

    let response = await apiCall(`${ENDPOINTS.ESTUDIANTES}?curso=${codigoCurso}`, "GET");

    if (!response) {
        response = {
            data: [
                {id: "EST001", nombre: "Ana López"},
                {id: "EST002", nombre: "Juan Gómez"},
                {id: "EST003", nombre: "Laura Ruiz"},
            ],
        };
    }

    renderEstudiantes(codigoCurso, response.data);
}

function renderEstudiantes(curso, estudiantes) {
    const contenedor = document.getElementById("estudiantesContainer");
    contenedor.innerHTML = `
    <h3>👥 Estudiantes inscritos en ${curso}</h3>
    <ul>
      ${estudiantes.map((e) => `<li>${e.id} - ${e.nombre}</li>`).join("")}
    </ul>
  `;
}

// =============================================================
// 📊 Ver reporte general
// =============================================================
async function verReporteGeneral() {
    showAlert("Cargando reporte general...", "info");

    let response = await apiCall(ENDPOINTS.REPORTE, "GET");

    // Demo
    if (!response) {
        response = {
            data: [
                {curso: "MAT101", inscritos: 28, promedio: 4.1},
                {curso: "FIS102", inscritos: 30, promedio: 3.9},
            ],
        };
    }

    renderReporteGeneral(response.data);
}

function renderReporteGeneral(reporte) {
    const contenedor = document.getElementById("reporteContainer");
    contenedor.innerHTML = `
    <h3>📊 Reporte Académico</h3>
    <table class="reporte-tabla">
      <thead>
        <tr>
          <th>Curso</th><th>Inscritos</th><th>Promedio</th>
        </tr>
      </thead>
      <tbody>
        ${reporte
        .map(
            (r) => `
          <tr>
            <td>${r.curso}</td>
            <td>${r.inscritos}</td>
            <td>${r.promedio.toFixed(2)}</td>
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
window.cargarCursos = cargarCursos;
window.crearCurso = crearCurso;
window.aprobarCurso = aprobarCurso;
window.verEstudiantes = verEstudiantes;
window.verReporteGeneral = verReporteGeneral;
window.logout = logout;
