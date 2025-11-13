/**
 * Add Content Modal - JavaScript
 * Handles multimodal content upload (notes, images, drawings, audio)
 */

// Global state
let currentAudioBlob = null;
let mediaRecorder = null;
let recordingStartTime = null;
let recordingInterval = null;
let drawingHistory = [];
let isDrawing = false;
let lastX = 0;
let lastY = 0;

// Modal control
function openAddContentModal() {
    document.getElementById('addContentModal').style.display = 'block';
    showContentTypeSelection();
}

function closeAddContentModal() {
    document.getElementById('addContentModal').style.display = 'none';
    resetAllInterfaces();
}

function showContentTypeSelection() {
    // Hide all interfaces
    document.getElementById('contentTypeSelection').style.display = 'block';
    document.getElementById('noteInterface').style.display = 'none';
    document.getElementById('imageInterface').style.display = 'none';
    document.getElementById('drawingInterface').style.display = 'none';
    document.getElementById('audioInterface').style.display = 'none';
}

function showInterface(type) {
    document.getElementById('contentTypeSelection').style.display = 'none';
    document.getElementById(`${type}Interface`).style.display = 'block';
    
    // Initialize canvas if drawing
    if (type === 'drawing') {
        initDrawingCanvas();
    }
}

function resetAllInterfaces() {
    // Reset note
    document.getElementById('noteTitle').value = '';
    document.getElementById('noteText').value = '';
    document.getElementById('noteTags').value = '';
    document.getElementById('noteMarkdown').checked = false;
    
    // Reset image
    document.getElementById('imageFile').value = '';
    document.getElementById('imageCaption').value = '';
    document.getElementById('imageTags').value = '';
    document.getElementById('imagePreview').style.display = 'none';
    document.getElementById('saveImage').disabled = true;
    
    // Reset drawing
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    drawingHistory = [];
    document.getElementById('drawingCaption').value = '';
    document.getElementById('drawingTags').value = '';
    
    // Reset audio
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    currentAudioBlob = null;
    document.getElementById('audioFile').value = '';
    document.getElementById('audioPreview').style.display = 'none';
    document.getElementById('audioTitle').value = '';
    document.getElementById('audioDescription').value = '';
    document.getElementById('audioTags').value = '';
    document.getElementById('saveAudio').disabled = true;
    document.getElementById('startRecording').style.display = 'inline-block';
    document.getElementById('stopRecording').style.display = 'none';
    document.getElementById('recordingTime').style.display = 'none';
    
    // Hide all status messages
    document.querySelectorAll('.status').forEach(el => el.style.display = 'none');
}

// ===========================================================================
// NOTE INTERFACE
// ===========================================================================

async function saveNote() {
    const title = document.getElementById('noteTitle').value.trim();
    const text = document.getElementById('noteText').value.trim();
    const tags = document.getElementById('noteTags').value.trim();
    const isMarkdown = document.getElementById('noteMarkdown').checked;
    
    if (!title || !text) {
        showStatus('noteStatus', 'error', 'Please enter both title and text');
        return;
    }
    
    showStatus('noteStatus', 'loading', 'Saving note...');
    document.getElementById('saveNote').disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('content_type', 'note');
        formData.append('text_content', text);
        formData.append('title', title);
        formData.append('is_markdown', isMarkdown);
        if (tags) formData.append('tags', tags);
        
        const response = await fetch(`${API_BASE}/api/content/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        showStatus('noteStatus', 'success', `✅ ${result.message}`);
        
        setTimeout(() => {
            closeAddContentModal();
        }, 2000);
        
    } catch (error) {
        console.error('Save note error:', error);
        showStatus('noteStatus', 'error', '❌ Failed to save note');
    } finally {
        document.getElementById('saveNote').disabled = false;
    }
}

// ===========================================================================
// IMAGE INTERFACE
// ===========================================================================

function selectImage() {
    document.getElementById('imageFile').click();
}

function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('previewImg').src = e.target.result;
        document.getElementById('imagePreview').style.display = 'block';
        document.getElementById('saveImage').disabled = false;
    };
    reader.readAsDataURL(file);
}

async function saveImage() {
    const file = document.getElementById('imageFile').files[0];
    const caption = document.getElementById('imageCaption').value.trim();
    const tags = document.getElementById('imageTags').value.trim();
    
    if (!file) {
        showStatus('imageStatus', 'error', 'Please select an image');
        return;
    }
    
    showStatus('imageStatus', 'loading', 'Uploading image...');
    document.getElementById('saveImage').disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('content_type', 'image');
        formData.append('file', file);
        if (caption) formData.append('caption', caption);
        if (tags) formData.append('tags', tags);
        formData.append('perform_ocr', 'true');
        
        const response = await fetch(`${API_BASE}/api/content/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        showStatus('imageStatus', 'success', `✅ ${result.message}`);
        
        setTimeout(() => {
            closeAddContentModal();
        }, 2000);
        
    } catch (error) {
        console.error('Save image error:', error);
        showStatus('imageStatus', 'error', '❌ Failed to upload image');
    } finally {
        document.getElementById('saveImage').disabled = false;
    }
}

// ===========================================================================
// DRAWING INTERFACE
// ===========================================================================

function initDrawingCanvas() {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas background to white
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Drawing settings
    ctx.strokeStyle = '#000';
    ctx.lineWidth = 2;
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    
    // Save initial state
    drawingHistory = [canvas.toDataURL()];
    
    // Touch/mouse event handlers
    canvas.addEventListener('touchstart', startDrawing);
    canvas.addEventListener('touchmove', draw);
    canvas.addEventListener('touchend', stopDrawing);
    canvas.addEventListener('mousedown', startDrawing);
    canvas.addEventListener('mousemove', draw);
    canvas.addEventListener('mouseup', stopDrawing);
    canvas.addEventListener('mouseout', stopDrawing);
}

function getCanvasCoordinates(e) {
    const canvas = document.getElementById('drawingCanvas');
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    
    if (e.touches) {
        return {
            x: (e.touches[0].clientX - rect.left) * scaleX,
            y: (e.touches[0].clientY - rect.top) * scaleY
        };
    } else {
        return {
            x: (e.clientX - rect.left) * scaleX,
            y: (e.clientY - rect.top) * scaleY
        };
    }
}

function startDrawing(e) {
    e.preventDefault();
    isDrawing = true;
    const pos = getCanvasCoordinates(e);
    lastX = pos.x;
    lastY = pos.y;
}

function draw(e) {
    if (!isDrawing) return;
    e.preventDefault();
    
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    const pos = getCanvasCoordinates(e);
    
    ctx.beginPath();
    ctx.moveTo(lastX, lastY);
    ctx.lineTo(pos.x, pos.y);
    ctx.stroke();
    
    lastX = pos.x;
    lastY = pos.y;
}

function stopDrawing(e) {
    if (isDrawing) {
        isDrawing = false;
        // Save state for undo
        const canvas = document.getElementById('drawingCanvas');
        drawingHistory.push(canvas.toDataURL());
    }
}

function clearCanvas() {
    const canvas = document.getElementById('drawingCanvas');
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    drawingHistory = [canvas.toDataURL()];
}

function undoCanvas() {
    if (drawingHistory.length > 1) {
        drawingHistory.pop(); // Remove current state
        const canvas = document.getElementById('drawingCanvas');
        const ctx = canvas.getContext('2d');
        const img = new Image();
        img.onload = () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0);
        };
        img.src = drawingHistory[drawingHistory.length - 1];
    }
}

async function saveDrawing() {
    const caption = document.getElementById('drawingCaption').value.trim();
    const tags = document.getElementById('drawingTags').value.trim();
    
    showStatus('drawingStatus', 'loading', 'Saving drawing...');
    document.getElementById('saveDrawing').disabled = true;
    
    try {
        const canvas = document.getElementById('drawingCanvas');
        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
        
        const formData = new FormData();
        formData.append('content_type', 'drawing');
        formData.append('file', blob, 'drawing.png');
        if (caption) formData.append('caption', caption);
        if (tags) formData.append('tags', tags);
        
        const response = await fetch(`${API_BASE}/api/content/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        showStatus('drawingStatus', 'success', `✅ ${result.message}`);
        
        setTimeout(() => {
            closeAddContentModal();
        }, 2000);
        
    } catch (error) {
        console.error('Save drawing error:', error);
        showStatus('drawingStatus', 'error', '❌ Failed to save drawing');
    } finally {
        document.getElementById('saveDrawing').disabled = false;
    }
}

// ===========================================================================
// AUDIO INTERFACE
// ===========================================================================

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        
        mediaRecorder = new MediaRecorder(stream);
        const audioChunks = [];
        
        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };
        
        mediaRecorder.onstop = () => {
            currentAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            
            // Show preview
            const audioURL = URL.createObjectURL(currentAudioBlob);
            const audioPreview = document.getElementById('audioPreview');
            audioPreview.src = audioURL;
            audioPreview.style.display = 'block';
            
            document.getElementById('saveAudio').disabled = false;
            
            // Stop all tracks
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        
        // Update UI
        document.getElementById('startRecording').style.display = 'none';
        document.getElementById('stopRecording').style.display = 'inline-block';
        document.getElementById('recordingTime').style.display = 'block';
        
        // Start timer
        recordingStartTime = Date.now();
        recordingInterval = setInterval(updateRecordingTime, 100);
        
    } catch (error) {
        console.error('Recording error:', error);
        showStatus('audioStatus', 'error', '❌ Microphone access denied or not available');
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
    }
    
    // Stop timer
    clearInterval(recordingInterval);
    
    // Update UI
    document.getElementById('startRecording').style.display = 'inline-block';
    document.getElementById('stopRecording').style.display = 'none';
    document.getElementById('recordingTime').style.display = 'none';
}

function updateRecordingTime() {
    const elapsed = Math.floor((Date.now() - recordingStartTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('recordingTime').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

function selectAudio() {
    document.getElementById('audioFile').click();
}

function handleAudioSelect(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    currentAudioBlob = file;
    
    // Show preview
    const audioURL = URL.createObjectURL(file);
    const audioPreview = document.getElementById('audioPreview');
    audioPreview.src = audioURL;
    audioPreview.style.display = 'block';
    
    document.getElementById('saveAudio').disabled = false;
}

async function saveAudio() {
    const title = document.getElementById('audioTitle').value.trim();
    const description = document.getElementById('audioDescription').value.trim();
    const tags = document.getElementById('audioTags').value.trim();
    
    if (!currentAudioBlob) {
        showStatus('audioStatus', 'error', 'Please record or select audio');
        return;
    }
    
    showStatus('audioStatus', 'loading', 'Uploading audio...');
    document.getElementById('saveAudio').disabled = true;
    
    try {
        const formData = new FormData();
        formData.append('content_type', 'audio');
        
        // Determine filename
        let filename = 'recording.webm';
        if (currentAudioBlob instanceof File) {
            filename = currentAudioBlob.name;
        }
        
        formData.append('file', currentAudioBlob, filename);
        if (title) formData.append('title', title);
        if (description) formData.append('description', description);
        if (tags) formData.append('tags', tags);
        formData.append('transcribe', 'true');
        
        const response = await fetch(`${API_BASE}/api/content/upload`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const result = await response.json();
        
        showStatus('audioStatus', 'success', `✅ ${result.message}`);
        
        setTimeout(() => {
            closeAddContentModal();
        }, 2000);
        
    } catch (error) {
        console.error('Save audio error:', error);
        showStatus('audioStatus', 'error', '❌ Failed to upload audio');
    } finally {
        document.getElementById('saveAudio').disabled = false;
    }
}

// ===========================================================================
// UTILITY FUNCTIONS
// ===========================================================================

function showStatus(elementId, type, message) {
    const statusEl = document.getElementById(elementId);
    statusEl.className = `status ${type}`;
    statusEl.textContent = message;
    statusEl.style.display = 'block';
}

// ===========================================================================
// EVENT LISTENERS
// ===========================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Open modal
    document.getElementById('addContentBtn').addEventListener('click', openAddContentModal);
    
    // Close modal
    document.getElementById('closeAddContentModal').addEventListener('click', closeAddContentModal);
    document.getElementById('addContentModal').addEventListener('click', (e) => {
        if (e.target.id === 'addContentModal') {
            closeAddContentModal();
        }
    });
    
    // Content type selection
    document.querySelectorAll('.content-type-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const type = btn.dataset.type;
            showInterface(type);
        });
    });
    
    // Back buttons
    document.querySelectorAll('.back-btn').forEach(btn => {
        btn.addEventListener('click', showContentTypeSelection);
    });
    
    // Note interface
    document.getElementById('saveNote').addEventListener('click', saveNote);
    
    // Image interface
    document.getElementById('selectImage').addEventListener('click', selectImage);
    document.getElementById('imageFile').addEventListener('change', handleImageSelect);
    document.getElementById('saveImage').addEventListener('click', saveImage);
    
    // Drawing interface
    document.getElementById('clearCanvas').addEventListener('click', clearCanvas);
    document.getElementById('undoCanvas').addEventListener('click', undoCanvas);
    document.getElementById('saveDrawing').addEventListener('click', saveDrawing);
    
    // Audio interface
    document.getElementById('startRecording').addEventListener('click', startRecording);
    document.getElementById('stopRecording').addEventListener('click', stopRecording);
    document.getElementById('selectAudio').addEventListener('click', selectAudio);
    document.getElementById('audioFile').addEventListener('change', handleAudioSelect);
    document.getElementById('saveAudio').addEventListener('click', saveAudio);
});

