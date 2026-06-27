// ==========================================================================
// CONFIGURACIÓN
// ==========================================================================
const API_URL = "https://asistencia.develorian.dev/api/v1"; // Reemplaza por tu URL actual si cambia
let currentLocation = "Ubicación desconocida";
let isEntrySelected = true;

// Elementos del DOM
const video = document.getElementById('webcam');
const canvas = document.getElementById('canvas');
const toastContainer = document.getElementById('toast-container');
const btnEntrada = document.getElementById('btn-entrada');
const btnSalida = document.getElementById('btn-salida');
const inputReason = document.getElementById('reason');

// ==========================================================================
// MÓDULO DE SONIDOS (Sintetizador Web Audio API)
// ==========================================================================
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

function playSound(type) {
    if (audioCtx.state === 'suspended') audioCtx.resume();
    const osc = audioCtx.createOscillator();
    const gainNode = audioCtx.createGain();
    
    osc.connect(gainNode);
    gainNode.connect(audioCtx.destination);
    
    if (type === 'click') {
        osc.type = 'sine';
        osc.frequency.setValueAtTime(800, audioCtx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(300, audioCtx.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.5, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
        osc.start(); osc.stop(audioCtx.currentTime + 0.1);
    } else if (type === 'shutter') {
        osc.type = 'square';
        osc.frequency.setValueAtTime(150, audioCtx.currentTime);
        gainNode.gain.setValueAtTime(0.3, audioCtx.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
        osc.start(); osc.stop(audioCtx.currentTime + 0.15);
    }
}

// ==========================================================================
// INTERFAZ DE USUARIO & RELOJ
// ==========================================================================
function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit', hour12: false });
    const dateStr = now.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' }).replace('.', '');
    
    document.getElementById('clock-time').textContent = `${timeStr} HRS`;
    document.getElementById('clock-date').textContent = dateStr;
}
setInterval(updateClock, 1000);
updateClock();

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toastContainer.appendChild(toast);
    
    // Auto-eliminar después de 4 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Lógica de los botones Toggle (Entrada/Salida)
function openTab(evt, tabName) {
    playSound('click');
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(tab => tab.classList.remove('active'));

    document.getElementById(tabName).classList.add('active');
    evt.currentTarget.classList.add('active'); // Esto ilumina la pestaña estilo folder
}

btnEntrada.addEventListener('click', () => {
    playSound('click');
    isEntrySelected = true;
    btnEntrada.setAttribute('data-state', 'active');
    btnSalida.setAttribute('data-state', 'inactive');
    inputReason.value = "Ingreso a labores";
});

btnSalida.addEventListener('click', () => {
    playSound('click');
    isEntrySelected = false;
    btnSalida.setAttribute('data-state', 'active');
    btnEntrada.setAttribute('data-state', 'inactive');
    inputReason.value = "Término de labores";
});

// ==========================================================================
// HARDWARE (Cámara y GPS)
// ==========================================================================
navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } })
    .then(stream => { video.srcObject = stream; })
    .catch(err => { showToast("Error de cámara. Revisa los permisos.", "error"); });

navigator.geolocation.getCurrentPosition(async (position) => {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    try {
        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
        const data = await response.json();
        const city = data.address.city || data.address.town || data.address.village || "Municipio desconocido";
        const state = data.address.state || "Estado desconocido";
        currentLocation = `${city}, ${state}`;
        document.getElementById('location-display').innerText = `📍 ${currentLocation}`;
    } catch (error) {
        document.getElementById('location-display').innerText = "📍 Falla al resolver ubicación.";
    }
}, () => {
    document.getElementById('location-display').innerText = "📍 GPS Denegado.";
});

function captureFrame() {
    playSound('shutter');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg');
}

// ==========================================================================
// CONEXIÓN CON LA API (Arquitectura Hexagonal Backend)
// ==========================================================================
document.getElementById('btn-registrar').addEventListener('click', async () => {
    const base64Image = captureFrame();
    const reason = inputReason.value;

    showToast("Analizando biometría facial...", "info");

    try {
        const response = await fetch(`${API_URL}/attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                image_b64: base64Image, 
                is_entry: isEntrySelected, 
                reason: reason, 
                location: currentLocation 
            })
        });

        const data = await response.json();
        if (response.ok) {
            showToast(`✅ [${data.movimiento}] Autorizado: Matrícula ${data.user_id}`, "success");
        } else {
            showToast(`❌ Acceso Denegado: ${data.message}`, "error");
        }
    } catch (error) {
        showToast("Error de conexión con el servidor NIAS.", "error");
    }
});

document.getElementById('btn-alta').addEventListener('click', async () => {
    playSound('click');
    const base64Image = captureFrame();
    const id = document.getElementById('reg_id').value;
    const grade = document.getElementById('reg_grade').value;
    const name = document.getElementById('reg_name').value;
    
    if (!id || !name) {
        showToast("❌ Matrícula y Nombre son obligatorios.", "error");
        return;
    }

    showToast("Registrando en base de datos...", "info");

    try {
        const response = await fetch(`${API_URL}/users`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                image_b64: base64Image,
                id: id,
                grade: grade,
                name: name,
                assignment: document.getElementById('reg_assign').value,
                role: document.getElementById('reg_role').value
            })
        });

        const data = await response.json();
        if (response.ok) {
            showToast(`✅ Elemento ${name} registrado con éxito.`, "success");
            // Limpiar campos
            document.querySelectorAll('#reg_id, #reg_grade, #reg_name, #reg_assign, #reg_role').forEach(el => el.value = '');
        } else {
            showToast(`❌ Error: ${data.message}`, "error");
        }
    } catch (error) {
        showToast("Error de conexión con el servidor.", "error");
    }
});

/*
MEJORAS DE INTERACTIVIDAD v1.0.0:
Sonidos Nativos: Usamos la Web Audio API en el archivo app.js. Al presionar Entrada/Salida escucharás un beep de sistema, y al registrar, un sonido sintético de cámara, todo sin necesidad de archivos MP3.

Alertas Flotantes (Toasts): Ya no usamos las alertas rígidas que empujaban el diseño hacia abajo. Ahora, cuando escanees, la notificación subirá suavemente desde la parte inferior de la pantalla y desaparecerá sola.
*/