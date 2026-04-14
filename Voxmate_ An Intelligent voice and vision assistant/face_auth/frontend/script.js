// script.js (replace your current file with this)
const video = document.getElementById('video');
const statusEl = document.getElementById('status');
const userIdInput = document.getElementById('userId');

function setStatus(text, cls = '') {
  statusEl.className = cls;
  statusEl.textContent = text;
}

// ✅ Access webcam (served over http)
async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
  } catch (err) {
    console.error("Camera error:", err);
    alert('Could not access webcam: ' + err);
    setStatus('Camera error: ' + err.message, 'error');
  }
}
startCamera();

// Capture current frame as Blob
function captureFrame() {
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth || 640;
  canvas.height = video.videoHeight || 480;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg', 0.9));
}

// helper to print server JSON nicely
async function fetchJson(url, options) {
  try {
    const res = await fetch(url, options);
    const text = await res.text();
    let parsed;
    try { parsed = JSON.parse(text); } catch(e){ parsed = text; }
    return { ok: res.ok, status: res.status, body: parsed };
  } catch (err) {
    return { ok: false, status: 0, error: err.message };
  }
}

// ✅ Sign Up — capture 4 photos
async function signup() {
  const userId = userIdInput.value.trim();
  if (!userId) return alert('Please enter user ID');

  setStatus("Capturing 4 photos...", '');
  const files = [];

  for (let i = 0; i < 4; i++) {
    const blob = await captureFrame();
    files.push(new File([blob], `photo_${i+1}.jpg`, { type: 'image/jpeg' }));
    await new Promise(r => setTimeout(r, 600));
  }

  const formData = new FormData();
  formData.append('user_id', userId);
  // IMPORTANT: backend expects the field name 'files' for multiple files
  files.forEach(f => formData.append('files', f));

  setStatus("Uploading to server...", '');
  const result = await fetchJson("http://127.0.0.1:8000/enroll", {
    method: "POST",
    body: formData
  });

  console.log("/enroll result:", result);

  if (!result.ok) {
    // If server returned JSON error, show it
    const msg = result.body && result.body.message ? result.body.message : `HTTP ${result.status} ${result.body || result.error || ''}`;
    setStatus(msg, 'error');
  } else {
    // success
    const message = (result.body && result.body.message) ? result.body.message : 'Signup success';
    setStatus(message, 'success');
  }
}

// ✅ Login — capture 1 photo and verify
async function login() {
  const userId = userIdInput.value.trim();
  if (!userId) return alert('Please enter user ID');

  const blob = await captureFrame();
  const formData = new FormData();
  formData.append('user_id', userId);
  // backend expects 'file' for single file param
  formData.append('file', new File([blob], 'login.jpg', { type: 'image/jpeg' }));

  setStatus("Verifying...", '');
  const result = await fetchJson("http://127.0.0.1:8000/verify", {
    method: "POST",
    body: formData
  });

  console.log("/verify result:", result);

  if (!result.ok) {
    const msg = result.body && result.body.message ? result.body.message : `HTTP ${result.status} ${result.body || result.error || ''}`;
    setStatus(msg, 'error');
    return;
  }

  const data = result.body;
  if (data.match) {
    setStatus(`✅ Login successful! (Similarity: ${Number(data.similarity).toFixed(3)})`, 'success');

    // Redirect to NLP / LiveKit front-end after 1.5s so user sees message
    setTimeout(() => {
      // change this to your NLP / LiveKit URL if needed
      window.location.href = "https://voxmate-y9p17u0c.livekit.cloud";
    }, 1500);
  } else {
    // show server message or similarity
    const sim = typeof data.similarity !== 'undefined' ? Number(data.similarity).toFixed(3) : 'n/a';
    const msg = data.message || `Login failed. (Similarity: ${sim})`;
    setStatus(msg, 'error');
  }
}

document.getElementById('signupBtn').addEventListener('click', signup);
document.getElementById('loginBtn').addEventListener('click', login);
