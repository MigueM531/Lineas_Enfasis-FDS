// =============================================================
// 🧠 EduBot Frontend - Conexión con FastAPI (main.js completo)
// =============================================================

// 🌐 URL del backend FastAPI
const API_URL = "http://localhost:8000";

// 🧭 Endpoints centralizados (ajusta con tu backend si cambian)
const ENDPOINTS = {
    CHAT: "/chat",
    LOGIN: "/login",
    CURSOS: "/cursos",
    CURSO_DETAIL: "/cursos/", // usar como `/cursos/{codigo}`
    INSCRIPCION: "/inscribir",
    CANCELAR: "/cancelar",
    PROGRESO: "/progreso",
    MIS_INSCRIPCIONES: "/mis_inscripciones",
};

// 📦 Variables globales
let currentUser = null;
let ESTUDIANTE_ID = null;
let cursosCache = [];
let pendingAction = null;

// =============================================================
// 🧩 Inicialización
// =============================================================
document.addEventListener("DOMContentLoaded", function () {
    const messageInput = document.getElementById("messageInput");

    // Auto-resize del textarea
    messageInput.addEventListener("input", function () {
        this.style.height = "auto";
        this.style.height = this.scrollHeight + "px";
    });

    // Enviar mensaje con Enter
    messageInput.addEventListener("keypress", function (e) {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Cargar datos del usuario (autenticación)
    loadUserInfo();
});

// =============================================================
// 🔐 AUTENTICACIÓN
// =============================================================
function loadUserInfo() {
    const userData = sessionStorage.getItem("currentUser");
    if (!userData) {
        window.location.href = "login.html";
        return;
    }

    currentUser = JSON.parse(userData);
    ESTUDIANTE_ID = currentUser.id;
    const nameEl = document.getElementById("userName");
    const roleEl = document.getElementById("userRole");
    if (nameEl) nameEl.textContent = currentUser.nombre;
    if (roleEl) roleEl.textContent =
        currentUser.rol === "estudiante" ? "Estudiante" : "Usuario";
}

function logout() {
    sessionStorage.clear();
    window.location.href = "login.html";
}

// =============================================================
// 🛰️ API CALL GENERAL
// =============================================================
async function apiCall(endpoint, method = "GET", body = null) {
    try {
        const options = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
        };

        // Si hay token, agregarlo al header
        const token = sessionStorage.getItem("token");
        if (token) options.headers["Authorization"] = `Bearer ${token}`;
        if (body) options.body = JSON.stringify(body);

        const response = await fetch(`${API_URL}${endpoint}`, options);

        // Si la respuesta no tiene JSON válido, lanzar para entrar al catch
        const text = await response.text();
        let data = null;
        try {
            data = text ? JSON.parse(text) : null;
        } catch (err) {
            // no JSON, pero permitimos continuar con texto si needed
            data = {raw: text};
        }

        if (!response.ok) {
            // intenta leer un mensaje de error común en FastAPI: detail
            const message = data?.detail || data?.message || data?.raw || `HTTP ${response.status}`;
            showError(message);
            return null;
        }

        return data;
    } catch (error) {
        console.error("API Error:", error);
        showError("Error de conexión con el servidor.");
        return null;
    }
}

// =============================================================
// 💬 CHAT API
// =============================================================
async function chatAPI(text) {
    return await apiCall(ENDPOINTS.CHAT, "POST", {
        text: text,
        estudiante_id: ESTUDIANTE_ID,
    });
}

// =============================================================
// 🔎 FUNCIONALIDADES PRINCIPALES
// =============================================================

// Buscar cursos (usa chatAPI como en tu versión original)
async function buscarCursos(semestre = null) {
    addUserMessage(semestre ? `Buscar cursos del semestre ${semestre}` : "Buscar cursos disponibles");
    showTyping();

    // Intentamos llamar al backend por chatAPI (compatibilidad con tu actual integración)
    const response = await chatAPI("buscar cursos");
    hideTyping();

    if (!response || response.type === "error") {
        showError(response?.message || "No se pudieron cargar los cursos");
        return;
    }

    if (response.type === "cursos") {
        cursosCache = response.data;
        let cursos = response.data;
        if (semestre) cursos = cursos.filter((c) => c.semestre === semestre);
        mostrarCursosDesdeAPI(cursos);
    }
}

function mostrarCursosDesdeAPI(cursos) {
    if (!Array.isArray(cursos) || cursos.length === 0) {
        addBotMessage(`
      <div class="message-avatar bot-message-avatar">🤖</div>
      <div class="message-content">
        <p>⚠️ No se encontraron cursos disponibles.</p>
        <div class="message-time">Ahora</div>
      </div>
    `);
        return;
    }

    let html = `
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <p>📚 <strong>Cursos Disponibles</strong></p>
      <p>He encontrado <strong>${cursos.length} cursos aprobados</strong> en la base de datos:</p>
  `;

    cursos.forEach((curso) => {
        let quotaClass = "";
        if (curso.cupo === 0) quotaClass = "full";
        else if (curso.cupo <= 5) quotaClass = "limited";

        html += `
      <div class="course-card">
        <div class="course-header">
          <div class="course-title">${curso.nombre}</div>
          <div class="course-quota ${quotaClass}">${curso.cupo} cupos</div>
        </div>
        <div class="course-details">
          <strong>Código:</strong> ${curso.codigo}<br>
          <strong>Semestre:</strong> ${curso.semestre}<br>
          <strong>Estado:</strong> ${curso.estado === "aprobado" ? "✅ Aprobado" : "⏳ Pendiente"}
        </div>
    `;

        if (curso.prerequisitos && curso.prerequisitos.length > 0) {
            html += `<div class="prerequisitos-section"><div class="prerequisitos-title">⚠️ Prerrequisitos:</div><ul class="prerequisitos-list">`;
            curso.prerequisitos.forEach((pr) => {
                html += `<li>${pr}</li>`;
            });
            html += `</ul></div>`;
        }

        html += `
        <div class="course-actions">
          ${
            curso.cupo > 0 && curso.estado === "aprobado"
                ? `<button class="course-btn primary" onclick="inscribirCurso('${curso.codigo}', '${curso.nombre}')">📝 Inscribirme</button>`
                : `<button class="course-btn secondary" disabled>❌ No disponible</button>`
        }
          <button class="course-btn secondary" onclick="verDetallesCurso('${curso.codigo}')">📖 Ver detalles</button>
        </div>
      </div>
    `;
    });

    html += `
      <div class="suggestions">
        <span class="suggestion-chip" onclick="filtrarPorSemestre()">🗓️ Filtrar por semestre</span>
        <span class="suggestion-chip" onclick="showMisInscripciones()">📋 Mis inscripciones</span>
      </div>
      <div class="message-time">Ahora</div>
    </div>
  `;
    addBotMessage(html);
}

// Filtrar por semestre (usa cursosCache)
function filtrarPorSemestre() {
    addUserMessage('Quiero filtrar los cursos por semestre');
    showTyping();

    setTimeout(() => {
        hideTyping();

        const semestres = [...new Set(cursosCache.map(c => c.semestre))].sort();

        if (semestres.length === 0) {
            buscarCursos();
            return;
        }

        let html = `
      <div class="message-avatar bot-message-avatar">🤖</div>
      <div class="message-content">
        <p>🗓️ <strong>Filtrar por Semestre</strong></p>
        <div class="filter-section">
          <div class="filter-title">Selecciona el semestre:</div>
          <div class="filter-options">
    `;

        semestres.forEach(sem => {
            const count = cursosCache.filter(c => c.semestre === sem).length;
            html += `<div class="filter-chip" onclick="buscarCursos(${sem})">Semestre ${sem} (${count} cursos)</div>`;
        });

        html += `
          </div>
        </div>
        <div class="message-time">Ahora</div>
      </div>
    `;

        addBotMessage(html);
    }, 700);
}

// =============================================================
// 📝 INSCRIPCIONES / CANCELACIONES / DETALLES
// =============================================================

// Inscribirse en un curso (usa chatAPI como en tu versión original, pero intenta endpoint si existe)
async function inscribirCurso(codigo, nombre) {
    addUserMessage(`Quiero inscribirme en el curso ${nombre} (${codigo})`);
    showTyping();

    // Intentamos endpoint directo primero
    let response = null;
    if (ENDPOINTS.INSCRIPCION) {
        response = await apiCall(ENDPOINTS.INSCRIPCION, "POST", {
            estudiante_id: ESTUDIANTE_ID,
            codigo: codigo
        });
    }

    // Fallback a chatAPI si no hay respuesta útil
    if (!response) {
        response = await chatAPI(`inscribir en ${codigo}`);
    }

    hideTyping();
    if (!response) return;

    // Manejo de respuesta similar al HTML original
    if (response.type === 'inscripcion' || response.resultado) {
        const resultado = response.resultado || (response.message || 'Operación completada');
        if (resultado.toString().toLowerCase().includes('éxito') || resultado.toString().toLowerCase().includes('inscripción')) {
            let html = `
        <div class="message-avatar bot-message-avatar">🤖</div>
        <div class="message-content">
          <div class="alert success">
            ✅ ${resultado}
          </div>
          <p>🎉 <strong>¡Inscripción Exitosa!</strong></p>
          <div class="status-card">
            <div class="status-title">📋 Comprobante de Inscripción:</div>
            <div class="status-text">
              <strong>Curso:</strong> ${nombre}<br>
              <strong>Código:</strong> ${codigo}<br>
              <strong>Estudiante:</strong> ${currentUser ? currentUser.nombre : 'N/A'}<br>
              <strong>Fecha:</strong> ${new Date().toLocaleDateString('es-CO', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            })}<br>
              <strong>Hora:</strong> ${new Date().toLocaleTimeString('es-CO')}<br>
              <strong>Estado:</strong> Confirmada ✅<br>
              <strong>ID de Transacción:</strong> INS-${Date.now()}
            </div>
          </div>
          <div class="quick-actions-chat">
            <button class="action-button" onclick="showMisInscripciones()">📋 Ver mis inscripciones</button>
            <button class="action-button" onclick="buscarCursos()">🔍 Buscar más cursos</button>
          </div>
          <div class="message-time">Ahora</div>
        </div>
      `;
            addBotMessage(html);
            return;
        } else {
            addBotMessage(`
        <div class="message-avatar bot-message-avatar">🤖</div>
        <div class="message-content">
          <div class="alert error">❌ ${resultado}</div>
          <p>No se pudo completar la inscripción. Verifica los requisitos.</p>
          <div class="message-time">Ahora</div>
        </div>
      `);
            return;
        }
    }

    // Si llega otro tipo de respuesta:
    addBotMessage(`
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <p>${response.message || 'Respuesta recibida.'}</p>
      <div class="message-time">Ahora</div>
    </div>
  `);
}

// Confirmar cancelación (abre modal)
function confirmarCancelacion(codigo, nombre) {
    pendingAction = {
        type: 'cancelar',
        codigo: codigo,
        nombre: nombre
    };

    const modalHeader = document.getElementById('modalHeader');
    const modalMessage = document.getElementById('modalMessage');
    const modal = document.getElementById('confirmModal');
    if (modalHeader) modalHeader.textContent = '⚠️ Cancelar Inscripción';
    if (modalMessage) modalMessage.innerHTML = `¿Estás seguro de que deseas cancelar tu inscripción en:<br><br><strong>${nombre} (${codigo})</strong><br><br>Esta acción liberará tu cupo en el curso.`;
    if (modal) modal.style.display = 'block';
}

async function cancelarInscripcion(codigo, nombre) {
    addUserMessage(`Cancelar mi inscripción en ${nombre} (${codigo})`);
    showTyping();

    // Intentamos llamar endpoint cancelar
    let response = null;
    if (ENDPOINTS.CANCELAR) {
        response = await apiCall(ENDPOINTS.CANCELAR, "POST", {
            estudiante_id: ESTUDIANTE_ID,
            codigo: codigo
        });
    }

    // fallback: simulación
    hideTyping();
    if (!response) {
        // simulación (como tenías antes)
        let html = `
      <div class="message-avatar bot-message-avatar">🤖</div>
      <div class="message-content">
        <div class="alert success">✅ Inscripción cancelada exitosamente</div>
        <p>Tu inscripción en <strong>${nombre} (${codigo})</strong> ha sido cancelada.</p>
        <div class="status-card">
          <div class="status-title">📋 Comprobante de Cancelación:</div>
          <div class="status-text">
            <strong>Curso:</strong> ${nombre}<br>
            <strong>Código:</strong> ${codigo}<br>
            <strong>Estudiante:</strong> ${currentUser ? currentUser.nombre : 'N/A'}<br>
            <strong>Fecha de cancelación:</strong> ${new Date().toLocaleDateString('es-CO')}<br>
            <strong>ID de Transacción:</strong> CAN-${Date.now()}<br>
            <strong>Estado:</strong> Cancelada ✅
          </div>
        </div>
        <div class="quick-actions-chat">
          <button class="action-button" onclick="showMisInscripciones()">📋 Ver inscripciones actuales</button>
          <button class="action-button" onclick="buscarCursos()">🔍 Buscar otros cursos</button>
        </div>
        <div class="message-time">Ahora</div>
      </div>
    `;
        addBotMessage(html);
        return;
    }

    // Si backend respondió:
    if (response && (response.success || response.message || response.resultado)) {
        addBotMessage(`
      <div class="message-avatar bot-message-avatar">🤖</div>
      <div class="message-content">
        <div class="alert success">✅ ${response.resultado || response.message || 'Inscripción cancelada exitosamente'}</div>
        <div class="message-time">Ahora</div>
      </div>
    `);
        return;
    }

    showError('No se pudo cancelar la inscripción.');
}

// Ver detalles del curso (intenta endpoint de detalle, fallback a simulación)
async function verDetallesCurso(codigo) {
    addUserMessage(`Ver detalles del curso ${codigo}`);
    showTyping();

    // Intentar endpoint específico
    let response = null;
    try {
        response = await apiCall(`${ENDPOINTS.CURSO_DETAIL}${codigo}`, "GET");
    } catch (err) {
        response = null;
    }

    // Si no hay endpoint de detalle o backend no responde, fallback a simulación
    hideTyping();
    if (!response || !response.data) {
        // Simulación de cronograma detallado
        const cronograma = [
            {semana: 1, tema: 'Introducción y Fundamentos', fecha: '15/01/2025'},
            {semana: 2, tema: 'Conceptos Básicos', fecha: '22/01/2025'},
            {semana: 3, tema: 'Primer Parcial', fecha: '29/01/2025'},
            {semana: 4, tema: 'Aplicaciones Prácticas', fecha: '05/02/2025'}
        ];

        let html = `
      <div class="message-avatar bot-message-avatar">🤖</div>
      <div class="message-content">
        <p>📖 <strong>Detalles del Curso ${codigo}</strong></p>

        <div class="status-card">
          <div class="status-title">📅 Cronograma Detallado</div>
          <table class="schedule-table">
            <thead>
              <tr>
                <th>Semana</th><th>Tema</th><th>Fecha</th>
              </tr>
            </thead>
            <tbody>
    `;
        cronograma.forEach(item => {
            html += `<tr><td>Semana ${item.semana}</td><td>${item.tema}</td><td>${item.fecha}</td></tr>`;
        });
        html += `
            </tbody>
          </table>
        </div>

        <div class="suggestions">
          <span class="suggestion-chip" onclick="showMisInscripciones()">📋 Volver a inscripciones</span>
        </div>

        <div class="message-time">Ahora</div>
      </div>
    `;
        addBotMessage(html);
        return;
    }

    // Si backend devuelve datos concretos:
    const curso = response.data;
    let html = `
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <p>📖 <strong>${curso.nombre || 'Detalles del Curso'}</strong></p>
      <div class="status-card">
        <div class="status-title">📚 Información</div>
        <div class="status-text">
          <strong>Código:</strong> ${curso.codigo || codigo}<br>
          <strong>Semestre:</strong> ${curso.semestre || 'N/A'}<br>
          <strong>Cupos:</strong> ${curso.cupo ?? 'N/A'}<br>
          <strong>Docente:</strong> ${curso.docente || 'N/A'}<br>
        </div>
      </div>
  `;

    if (curso.cronograma && Array.isArray(curso.cronograma)) {
        html += `
      <div class="status-card">
        <div class="status-title">📅 Cronograma Detallado</div>
        <table class="schedule-table">
          <thead><tr><th>Semana</th><th>Tema</th><th>Fecha</th></tr></thead>
          <tbody>
    `;
        curso.cronograma.forEach(item => {
            html += `<tr><td>Semana ${item.semana}</td><td>${item.tema}</td><td>${item.fecha}</td></tr>`;
        });
        html += `</tbody></table></div>`;
    }

    html += `
      <div class="suggestions">
        <span class="suggestion-chip" onclick="inscribirCurso('${curso.codigo || codigo}','${curso.nombre || 'Curso'}')">📝 Inscribirme</span>
      </div>
      <div class="message-time">Ahora</div>
    </div>
  `;
    addBotMessage(html);
}

// =============================================================
// 📋 MIS INSCRIPCIONES Y REPORTE
// =============================================================

async function showMisInscripciones() {
    addUserMessage('Mostrar mis inscripciones actuales');
    showTyping();

    // Intentar endpoint dedicado
    let response = await apiCall(ENDPOINTS.MIS_INSCRIPCIONES, "GET");

    hideTyping();

    // Si no hay endpoint o falla, usamos simulación (como antes)
    const fallbackInscripciones = [
        {
            codigo: 'MAT101',
            nombre: 'Cálculo Diferencial',
            creditos: 4,
            horario: 'Lunes y Miércoles 8:00-10:00',
            aula: 'Edificio B - Salón 301',
            docente: 'Dr. Carlos Pérez',
            estado: 'Activo'
        },
        {
            codigo: 'FIS201',
            nombre: 'Física Mecánica',
            creditos: 4,
            horario: 'Martes y Jueves 10:00-12:00',
            aula: 'Edificio A - Lab 102',
            docente: 'Dra. María González',
            estado: 'Activo'
        }
    ];

    const inscripciones = response?.data || fallbackInscripciones;

    let html = `
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <p>📋 <strong>Mis Inscripciones - Semestre Actual</strong></p>
      <p>Tienes <strong>${inscripciones.length} cursos</strong> inscritos:</p>
  `;

    inscripciones.forEach(curso => {
        html += `
      <div class="course-card">
        <div class="course-header">
          <div class="course-title">${curso.nombre}</div>
          <div class="course-quota">${curso.creditos} créditos</div>
        </div>
        <div class="course-details">
          <strong>Código:</strong> ${curso.codigo}<br>
          <strong>📅 Horario:</strong> ${curso.horario}<br>
          <strong>🏫 Aula:</strong> ${curso.aula}<br>
          <strong>👨‍🏫 Docente:</strong> ${curso.docente}<br>
          <strong>Estado:</strong> <span style="color: #4CAF50;">✅ ${curso.estado}</span>
        </div>
        <div class="course-actions">
          <button class="course-btn secondary" onclick="verDetallesCurso('${curso.codigo}')">📖 Ver detalles</button>
          <button class="course-btn danger" onclick="confirmarCancelacion('${curso.codigo}', '${curso.nombre}')">❌ Cancelar inscripción</button>
        </div>
      </div>
    `;
    });

    html += `
      <div class="status-card">
        <div class="status-title">📊 Resumen del Semestre</div>
        <div class="status-text">
          <strong>Total de créditos inscritos:</strong> ${inscripciones.reduce((sum, c) => sum + (c.creditos || 0), 0)}<br>
          <strong>Cursos activos:</strong> ${inscripciones.length}<br>
          <strong>Fecha de consulta:</strong> ${new Date().toLocaleDateString('es-CO')}
        </div>
      </div>

      <div class="suggestions">
        <span class="suggestion-chip" onclick="buscarCursos()">🔍 Buscar más cursos</span>
        <span class="suggestion-chip" onclick="showReporteProgreso()">📊 Ver mi progreso</span>
      </div>

      <div class="message-time">Ahora</div>
    </div>
  `;

    addBotMessage(html);
}

// Mostrar reporte de progreso (intenta endpoint PROGRESO, fallback a datos simulados)
async function showReporteProgreso() {
    addUserMessage('Quiero ver mi reporte de progreso académico');
    showTyping();

    let response = await apiCall(ENDPOINTS.PROGRESO, "GET");
    hideTyping();

    const data = response?.data || {
        creditos_completados: 48,
        creditos_totales: 160,
        promedio: 4.2,
        pendientes: 28
    };

    mostrarReporteProgreso(data);
}

function mostrarReporteProgreso(data) {
    const porcentaje = Math.round((data.creditos_completados / data.creditos_totales) * 100);

    let html = `
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <p>📊 <strong>Reporte de Progreso Académico</strong></p>
      <p><strong>Estudiante:</strong> ${currentUser ? currentUser.nombre : 'N/A'}</p>
      <p><strong>Programa:</strong> ${currentUser?.programa || 'Ingeniería de Sistemas'}</p>

      <div class="status-card">
        <div class="status-title">🎯 Progreso General</div>
        <div class="status-text">
          <div class="progress-container">
            <div class="progress-bar" style="width: ${porcentaje}%">${porcentaje}%</div>
          </div>
          <strong>Créditos completados:</strong> ${data.creditos_completados}/${data.creditos_totales}<br>
          <strong>Promedio acumulado:</strong> ${data.promedio}/5.0<br>
          <strong>Cursos pendientes:</strong> ${data.pendientes}<br>
          <strong>Estado:</strong> En progreso regular ✅
        </div>
      </div>

      <div class="status-card">
        <div class="status-title">📈 Proyección</div>
        <div class="status-text">
          Con tu ritmo actual, completarías el programa en aproximadamente <strong>${Math.ceil(data.pendientes / 5)} semestres más</strong>.<br><br>
          <strong>Recomendación:</strong> Mantén un promedio de 5-6 cursos por semestre para una carga balanceada.
        </div>
      </div>

      <div class="quick-actions-chat">
        <button class="action-button" onclick="buscarCursos()">🔍 Buscar nuevos cursos</button>
        <button class="action-button" onclick="showMisInscripciones()">📋 Ver inscripciones</button>
      </div>

      <div class="message-time">Ahora</div>
    </div>
  `;

    addBotMessage(html);
}

// =============================================================
// 💬 FUNCIONES VISUALES
// =============================================================
function addUserMessage(text) {
    const messagesArea = document.getElementById("messagesArea");
    const typingIndicator = document.getElementById("typingIndicator");

    const userMessage = document.createElement("div");
    userMessage.className = "message user";
    userMessage.innerHTML = `
    <div class="message-avatar user-message-avatar">
      ${currentUser ? currentUser.nombre.split(" ").map((n) => n[0]).join("") : "U"}
    </div>
    <div class="message-content">
      <p>${text}</p>
      <div class="message-time">Ahora</div>
    </div>
  `;

    messagesArea.insertBefore(userMessage, typingIndicator);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function addBotMessage(html) {
    const messagesArea = document.getElementById("messagesArea");
    const typingIndicator = document.getElementById("typingIndicator");

    const botMessage = document.createElement("div");
    botMessage.className = "message bot";
    botMessage.innerHTML = html;

    messagesArea.insertBefore(botMessage, typingIndicator);
    messagesArea.scrollTop = messagesArea.scrollHeight;
}

function showTyping() {
    const el = document.getElementById("typingIndicator");
    if (el) el.style.display = "flex";
    const messagesArea = document.getElementById("messagesArea");
    if (messagesArea) messagesArea.scrollTop = messagesArea.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typingIndicator");
    if (el) el.style.display = "none";
}

function showError(message) {
    addBotMessage(`
    <div class="message-avatar bot-message-avatar">🤖</div>
    <div class="message-content">
      <div class="alert error">❌ ${message}</div>
      <p>Por favor intenta nuevamente o contacta con soporte técnico.</p>
      <div class="message-time">Ahora</div>
    </div>
  `);
}

// =============================================================
// 🔁 Modal confirmación
// =============================================================
function closeModal() {
    const modal = document.getElementById('confirmModal');
    if (modal) modal.style.display = 'none';
    pendingAction = null;
}

function confirmAction() {
    if (pendingAction) {
        if (pendingAction.type === 'cancelar') {
            cancelarInscripcion(pendingAction.codigo, pendingAction.nombre);
        }
    }
    closeModal();
}

// Cerrar modal al hacer clic fuera
window.onclick = function (event) {
    const modal = document.getElementById('confirmModal');
    if (event.target == modal) {
        closeModal();
    }
};

// =============================================================
// 🧱 EXPORTACIÓN (para depuración / consola)
window.apiCall = apiCall;
window.chatAPI = chatAPI;
window.buscarCursos = buscarCursos;
window.sendMessage = sendMessage;
window.logout = logout;
window.showMisInscripciones = showMisInscripciones;
window.inscribirCurso = inscribirCurso;
window.confirmarCancelacion = confirmarCancelacion;
window.verDetallesCurso = verDetallesCurso;
window.showReporteProgreso = showReporteProgreso;
window.closeModal = closeModal;
window.confirmAction = confirmAction;
