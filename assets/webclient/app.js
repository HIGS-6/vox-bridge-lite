/* ─────────────────────────────────────────────────────────────
   AudioStream — app.js  (v3)

   Fixes vs v2:
   FIX-1  PITCH  — AudioContext created at server's sample rate (44100),
                   not the OS default (often 48000). Mismatch caused ~8.8%
                   pitch shift.
   FIX-2  CUTS   — Worklet now pre-buffers N chunks before starting output.
                   Eliminates underrun clicks from WiFi jitter.
   FIX-3  MOBILE — audioCtx.audioWorklet is undefined on HTTP (non-localhost).
                   Falls back automatically to ScriptProcessorNode.
───────────────────────────────────────────────────────────── */

"use strict";

// ── DOM refs ──────────────────────────────────────────────────
const $url = document.getElementById("ws-url");
const $connectBtn = document.getElementById("connect-btn");
const $badge = document.getElementById("status-badge");
const $badgeText = $badge.querySelector(".status-text");
const $livePanel = document.getElementById("live-panel");
const $statsGrid = document.getElementById("stats-grid");
const $guide = document.getElementById("guide");
const $errorBar = document.getElementById("error-bar");
const $volSlider = document.getElementById("volume-slider");
const $volDisplay = document.getElementById("volume-display");
const $muteBtn = document.getElementById("mute-btn");
const $bufFill = document.getElementById("buffer-fill");
const $bufDisplay = document.getElementById("buffer-display");
const $waveform = document.getElementById("waveform");
const $chunks = document.getElementById("stat-chunks");
const $bytes = document.getElementById("stat-bytes");

// ── Audio state ───────────────────────────────────────────────
const SERVER_SAMPLE_RATE = 44100; // FIX-1: must match server.py SAMPLE_RATE
const PREBUFFER_CHUNKS = 4; // FIX-2: wait for N chunks before playing (~50ms cushion)

let ws = null;
let audioCtx = null;
let gainNode = null;
let workletNode = null; // AudioWorklet path (secure context)
let scriptNode = null; // ScriptProcessor fallback (HTTP / mobile)
let useWorklet = false;
let serverConfig = null;
let muted = false;
let chunksRx = 0;
let bytesRx = 0;

// FIX-3 fallback: shared ring buffer used by ScriptProcessorNode
const SP_RING_SIZE = 32768;
const spRing = new Float32Array(SP_RING_SIZE);
let spWrite = 0;
let spRead = 0;
let spReady = false; // true once pre-buffer is full
let spChunkCount = 0;

// Waveform ring
const WAVE_SAMPLES = 512;
const waveRing = new Float32Array(WAVE_SAMPLES);
let wavePos = 0;
let rafId = null;

// ── Background canvas ─────────────────────────────────────────
(function initBg() {
  const cvs = document.getElementById("bg-canvas");
  const ctx = cvs.getContext("2d");
  function resize() {
    cvs.width = window.innerWidth;
    cvs.height = window.innerHeight;
    draw();
  }
  function draw() {
    ctx.clearRect(0, 0, cvs.width, cvs.height);
    ctx.strokeStyle = "rgba(240,165,0,0.04)";
    ctx.lineWidth = 1;
    const step = 44;
    for (let x = 0; x < cvs.width; x += step) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, cvs.height);
      ctx.stroke();
    }
    for (let y = 0; y < cvs.height; y += step) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(cvs.width, y);
      ctx.stroke();
    }
    const g = ctx.createRadialGradient(
      cvs.width / 2,
      cvs.height / 2,
      cvs.height * 0.2,
      cvs.width / 2,
      cvs.height / 2,
      cvs.height * 0.9,
    );
    g.addColorStop(0, "transparent");
    g.addColorStop(1, "rgba(0,0,0,0.55)");
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, cvs.width, cvs.height);
  }
  window.addEventListener("resize", resize);
  resize();
})();

// ── Audio init ────────────────────────────────────────────────
async function initAudio() {
  // FIX-1: force AudioContext to the server's sample rate.
  // Without this, the OS default (often 48000 Hz) causes pitch shift.
  audioCtx = new AudioContext({
    sampleRate: SERVER_SAMPLE_RATE,
    latencyHint: "interactive",
  });

  gainNode = audioCtx.createGain();
  gainNode.gain.value = muted ? 0 : parseFloat($volSlider.value);
  gainNode.connect(audioCtx.destination);

  // FIX-3: AudioWorklet requires a secure context (HTTPS or localhost).
  // On plain HTTP (mobile on LAN), fall back to ScriptProcessorNode.
  if (audioCtx.audioWorklet) {
    await initWorklet();
    useWorklet = true;
  } else {
    initScriptProcessor();
    useWorklet = false;
    console.warn(
      "AudioWorklet unavailable (HTTP context) — using ScriptProcessorNode fallback",
    );
  }
}

// ── Path A: AudioWorklet (localhost / HTTPS) ──────────────────
async function initWorklet() {
  const src = document.getElementById("worklet-src").textContent;
  const blob = new Blob([src], { type: "application/javascript" });
  const burl = URL.createObjectURL(blob);
  await audioCtx.audioWorklet.addModule(burl);
  URL.revokeObjectURL(burl);

  workletNode = new AudioWorkletNode(audioCtx, "asp");
  workletNode.connect(gainNode);

  workletNode.port.onmessage = (e) => {
    if (e.data.type === "stats") {
      const ms = Math.round((e.data.buffered / SERVER_SAMPLE_RATE) * 1000);
      updateBuffer(ms);
    }
  };
}

// ── Path B: ScriptProcessorNode fallback (HTTP / mobile) ─────
// Deprecated but universally supported, works on non-secure HTTP.
function initScriptProcessor() {
  const bufSize = 2048;
  scriptNode = audioCtx.createScriptProcessor(bufSize, 0, 1);
  scriptNode.connect(gainNode);
  spWrite = spRead = 0;
  spReady = false;
  spChunkCount = 0;

  scriptNode.onaudioprocess = (e) => {
    const out = e.outputBuffer.getChannelData(0);
    const avail = (spWrite - spRead + SP_RING_SIZE) % SP_RING_SIZE;

    if (!spReady) {
      // FIX-2 (fallback): silence until pre-buffer is full
      out.fill(0);
      return;
    }

    if (avail >= out.length) {
      for (let i = 0; i < out.length; i++) {
        out[i] = spRing[spRead];
        spRead = (spRead + 1) % SP_RING_SIZE;
      }
    } else {
      // Underrun — refill pre-buffer
      out.fill(0);
      spReady = false;
      spChunkCount = 0;
    }

    // Report buffer level
    const ms = Math.round(
      (((spWrite - spRead + SP_RING_SIZE) % SP_RING_SIZE) /
        SERVER_SAMPLE_RATE) *
        1000,
    );
    updateBuffer(ms);
  };
}

// ── Feed audio data (works for both paths) ───────────────────
function feedAudio(float32) {
  if (useWorklet) {
    // FIX-2 (worklet): pre-buffer handled inside the worklet processor
    workletNode.port.postMessage({ type: "chunk", samples: float32 }, [
      float32.buffer,
    ]);
  } else {
    // ScriptProcessor ring buffer
    for (let i = 0; i < float32.length; i++) {
      spRing[spWrite] = float32[i];
      spWrite = (spWrite + 1) % SP_RING_SIZE;
    }
    spChunkCount++;
    // FIX-2 (fallback): start playing after PREBUFFER_CHUNKS chunks
    if (!spReady && spChunkCount >= PREBUFFER_CHUNKS) {
      spReady = true;
    }
  }
}

// ── Connect / Disconnect ──────────────────────────────────────
async function connect() {
  const url = $url.value.trim();
  if (!url) return;

  setStatus("connecting");
  showError(null);

  try {
    await initAudio();
    audioCtx.resume();
  } catch (err) {
    setStatus("error");
    showError("Audio init failed: " + err.message);
    return;
  }

  ws = new WebSocket(url);
  ws.binaryType = "arraybuffer";

  ws.onopen = () => {
    setStatus("connected");
    showLive(true);
    resetStats();
    startWaveform();
  };

  ws.onclose = (e) => {
    setStatus("disconnected");
    showLive(false);
    stopWaveform();
    teardownAudio();
    ws = null;
    if (e.code !== 1000 && e.code !== 1005)
      showError(`WebSocket cerrado (código ${e.code})`);
  };

  ws.onerror = () => {
    setStatus("error");
    showError(
      "No se pudo conectar. Verifica la IP y que el servidor Python esté corriendo.",
    );
  };

  ws.onmessage = (event) => {
    if (typeof event.data === "string") {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "config") serverConfig = msg;
      } catch {}
      return;
    }

    bytesRx += event.data.byteLength;
    chunksRx++;
    updateStats();

    const int16 = new Int16Array(event.data);
    const float32 = new Float32Array(int16.length);
    for (let i = 0; i < int16.length; i++) float32[i] = int16[i] / 32768;

    // Waveform ring
    for (let i = 0; i < float32.length; i++) {
      waveRing[wavePos] = float32[i];
      wavePos = (wavePos + 1) % WAVE_SAMPLES;
    }

    feedAudio(float32);
  };
}

function disconnect() {
  if (ws) {
    ws.close(1000);
    ws = null;
  }
  teardownAudio();
  setStatus("disconnected");
  showLive(false);
  stopWaveform();
}

function teardownAudio() {
  if (workletNode) {
    workletNode.disconnect();
    workletNode = null;
  }
  if (scriptNode) {
    scriptNode.disconnect();
    scriptNode = null;
  }
  if (gainNode) {
    gainNode.disconnect();
    gainNode = null;
  }
  if (audioCtx) {
    audioCtx.close();
    audioCtx = null;
  }
  serverConfig = null;
  spReady = false;
  spWrite = spRead = spChunkCount = 0;
}

// ── UI helpers ────────────────────────────────────────────────
function setStatus(state) {
  $badge.dataset.state = state;
  $badgeText.textContent = state.toUpperCase();
  $url.disabled = state === "connected" || state === "connecting";

  if (state === "connected" || state === "connecting") {
    $connectBtn.textContent = state === "connecting" ? "CANCEL" : "DISCONNECT";
    $connectBtn.className =
      state === "connecting" ? "btn btn--cancel" : "btn btn--disconnect";
  } else {
    $connectBtn.textContent = "CONNECT";
    $connectBtn.className = "btn btn--connect";
  }
}

function showLive(on) {
  $livePanel.hidden = !on;
  $statsGrid.hidden = !on;
  $guide.hidden = on;
  if (on) requestAnimationFrame(resizeWaveform);
}

function showError(msg) {
  if (msg) {
    $errorBar.textContent = "⚠  " + msg;
    $errorBar.hidden = false;
  } else {
    $errorBar.hidden = true;
  }
}

function resetStats() {
  chunksRx = 0;
  bytesRx = 0;
  $chunks.textContent = "0";
  $bytes.textContent = "0 B";
}

function updateStats() {
  $chunks.textContent = chunksRx.toLocaleString();
  const b = bytesRx;
  $bytes.textContent =
    b < 1024
      ? b + " B"
      : b < 1048576
        ? (b / 1024).toFixed(1) + " KB"
        : (b / 1048576).toFixed(2) + " MB";
}

function updateBuffer(ms) {
  $bufDisplay.textContent = ms + "ms";
  const pct = Math.min(100, (ms / 200) * 100);
  $bufFill.style.width = pct + "%";
  $bufFill.style.background =
    ms < 20 ? "#e05252" : ms < 60 ? "#f0a500" : "#3ecf6e";
}

// ── Waveform ──────────────────────────────────────────────────
const wCtx = $waveform.getContext("2d");

function resizeWaveform() {
  const W = $waveform.offsetWidth;
  const H = $waveform.offsetHeight;
  if (!W || !H) return;
  const dpr = window.devicePixelRatio || 1;
  $waveform.width = W * dpr;
  $waveform.height = H * dpr;
  wCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener("resize", resizeWaveform);

function drawWaveform() {
  const W = $waveform.offsetWidth;
  const H = $waveform.offsetHeight;
  const mid = H / 2;
  wCtx.clearRect(0, 0, W, H);

  wCtx.strokeStyle = "rgba(255,255,255,0.04)";
  wCtx.lineWidth = 1;
  wCtx.beginPath();
  wCtx.moveTo(0, mid);
  wCtx.lineTo(W, mid);
  wCtx.stroke();

  const grad = wCtx.createLinearGradient(0, 0, W, 0);
  grad.addColorStop(0, "rgba(240,165,0,0)");
  grad.addColorStop(0.1, "rgba(240,165,0,0.8)");
  grad.addColorStop(0.9, "rgba(240,165,0,0.8)");
  grad.addColorStop(1, "rgba(240,165,0,0)");

  wCtx.strokeStyle = grad;
  wCtx.lineWidth = 1.5;
  wCtx.beginPath();
  const step = W / WAVE_SAMPLES;
  for (let i = 0; i < WAVE_SAMPLES; i++) {
    const idx = (wavePos + i) % WAVE_SAMPLES;
    const x = i * step;
    const y = mid + waveRing[idx] * mid * 0.85;
    i === 0 ? wCtx.moveTo(x, y) : wCtx.lineTo(x, y);
  }
  wCtx.stroke();
  rafId = requestAnimationFrame(drawWaveform);
}

function startWaveform() {
  if (!rafId) rafId = requestAnimationFrame(drawWaveform);
}

function stopWaveform() {
  if (rafId) {
    cancelAnimationFrame(rafId);
    rafId = null;
  }
  const W = $waveform.offsetWidth,
    H = $waveform.offsetHeight;
  wCtx.clearRect(0, 0, W, H);
  wCtx.strokeStyle = "rgba(255,255,255,0.06)";
  wCtx.lineWidth = 1;
  wCtx.beginPath();
  wCtx.moveTo(0, H / 2);
  wCtx.lineTo(W, H / 2);
  wCtx.stroke();
}

// ── Volume & mute ─────────────────────────────────────────────
$volSlider.addEventListener("input", () => {
  const v = parseFloat($volSlider.value);
  $volDisplay.textContent = Math.round(v * 100) + "%";
  if (gainNode && !muted) gainNode.gain.value = v;
});

$muteBtn.addEventListener("click", () => {
  muted = !muted;
  $muteBtn.textContent = muted ? "🔇" : "🔊";
  if (gainNode) gainNode.gain.value = muted ? 0 : parseFloat($volSlider.value);
});

// ── Connect button & Enter key ────────────────────────────────
$connectBtn.addEventListener("click", () => {
  const s = $badge.dataset.state;
  s === "disconnected" || s === "error" ? connect() : disconnect();
});

$url.addEventListener("keydown", (e) => {
  if (e.key === "Enter") {
    const s = $badge.dataset.state;
    if (s === "disconnected" || s === "error") connect();
  }
});
