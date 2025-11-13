// Library Management JavaScript

const API_BASE = window.location.origin;
let allSources = [];
let currentDeleteId = null;
let currentUploadFile = null;

// Load library on page load
window.addEventListener('load', async () => {
    await loadLibrary();
    setupUploadZone();
});

// Filter change
document.getElementById('filterType').addEventListener('change', filterLibrary);

// Search input
document.getElementById('searchFilter').addEventListener('input', filterLibrary);

async function loadLibrary() {
    const loading = document.getElementById('loading');
    const contentList = document.getElementById('contentList');
    
    loading.style.display = 'block';
    contentList.innerHTML = '';
    
    try {
        const response = await fetch(`${API_BASE}/api/library`);
        if (!response.ok) throw new Error('Failed to load library');
        
        const data = await response.json();
        allSources = data.sources;
        
        // Update storage info in header
        const stats = await fetch(`${API_BASE}/api/library/stats`).then(r => r.json());
        document.getElementById('storageUsed').textContent = `${stats.storage_used_mb} MB`;
        
        loading.style.display = 'none';
        
        if (allSources.length === 0) {
            contentList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📚</div>
                    <div class="empty-state-text">No content sources found</div>
                </div>
            `;
            return;
        }
        
        displaySources(allSources);
    } catch (error) {
        console.error('Error loading library:', error);
        loading.innerHTML = `
            <div style="color: #c62828;">
                ❌ Error loading library: ${error.message}
            </div>
        `;
    }
}

function displaySources(sources) {
    const contentList = document.getElementById('contentList');
    contentList.innerHTML = '';
    
    if (sources.length === 0) {
        contentList.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">No sources match your filter</div>
            </div>
        `;
        return;
    }
    
    sources.forEach(source => {
        const card = createSourceCard(source);
        contentList.appendChild(card);
    });
}

function createSourceCard(source) {
    const card = document.createElement('div');
    card.className = 'content-card';
    card.dataset.type = source.type;
    card.dataset.title = source.title.toLowerCase();
    
    // Type badge
    const typeClass = source.type === 'harrison' ? 'type-harrison' : 
                      source.type === 'independent_pdf' ? 'type-pdf' : 'type-note';
    const typeLabel = source.type === 'harrison' ? '📖 Harrison\'s' : 
                      source.type === 'independent_pdf' ? '📄 PDF' : '📝 Note';
    
    // Metadata
    let metaHtml = '';
    if (source.type === 'harrison') {
        metaHtml = `
            <span>📑 ${source.total_chapters} chapters</span>
            <span>📄 ${source.total_pages} pages</span>
            <span>📊 ${formatNumber(source.word_count)} words</span>
            <span>✅ Indexed</span>
        `;
    } else if (source.type === 'independent_pdf') {
        metaHtml = `
            <span>📄 ${source.total_pages} pages</span>
            <span>📊 ${formatNumber(source.word_count)} words</span>
            <span>💾 ${formatBytes(source.file_size)}</span>
            <span>✅ Indexed</span>
        `;
    } else if (source.type === 'personal_note') {
        const tags = source.tags && source.tags.length > 0 ? 
            source.tags.map(t => `<span style="background:#f3e5f5;padding:2px 8px;border-radius:10px;font-size:12px;">#${t}</span>`).join(' ') : '';
        metaHtml = `
            <span>📊 ${formatNumber(source.word_count)} words</span>
            <span>📅 ${formatDate(source.created_at)}</span>
            ${tags}
        `;
    }
    
    // Actions
    let actionsHtml = '';
    if (source.type === 'harrison') {
        // Harrison's - no actions
        actionsHtml = '';
    } else if (source.type === 'independent_pdf') {
        actionsHtml = `
            <button class="btn btn-view btn-small" onclick="viewPDF('${source.id}', '${escapeHtml(source.filename)}')">
                📖 View PDF
            </button>
            <button class="btn btn-delete btn-small" onclick="showDeleteConfirm('${source.id}', '${escapeHtml(source.title)}', '${source.type}')">
                🗑️ Delete
            </button>
        `;
    } else if (source.type === 'personal_note') {
        actionsHtml = `
            <button class="btn btn-view btn-small" onclick="viewNote('${source.id}')">
                📖 View Note
            </button>
            <button class="btn btn-view btn-small" onclick="editNote('${source.id}')">
                ✏️ Edit
            </button>
            <button class="btn btn-delete btn-small" onclick="showDeleteConfirm('${source.id}', '${escapeHtml(source.title)}', '${source.type}')">
                🗑️ Delete
            </button>
        `;
    }
    
    card.innerHTML = `
        <div class="content-header">
            <div class="content-title">${escapeHtml(source.title)}</div>
            <span class="content-type ${typeClass}">${typeLabel}</span>
        </div>
        <div class="content-meta">
            ${metaHtml}
        </div>
        <div class="content-actions">
            ${actionsHtml}
        </div>
    `;
    
    return card;
}

function filterLibrary() {
    const filterType = document.getElementById('filterType').value;
    const searchQuery = document.getElementById('searchFilter').value.toLowerCase();
    
    let filtered = allSources;
    
    // Filter by type
    if (filterType !== 'all') {
        filtered = filtered.filter(s => s.type === filterType);
    }
    
    // Filter by search query
    if (searchQuery) {
        filtered = filtered.filter(s => {
            // Search in title
            if (s.title.toLowerCase().includes(searchQuery)) return true;
            
            // Search in content for notes
            if (s.type === 'personal_note' && s.content) {
                if (s.content.toLowerCase().includes(searchQuery)) return true;
            }
            
            // Search in tags for notes
            if (s.type === 'personal_note' && s.tags) {
                if (s.tags.some(tag => tag.toLowerCase().includes(searchQuery))) return true;
            }
            
            return false;
        });
    }
    
    displaySources(filtered);
}

// Upload Zone Setup
function setupUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    
    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File selected
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            const file = e.dataTransfer.files[0];
            if (file.type === 'application/pdf') {
                handleFileSelect(file);
            } else {
                alert('Please upload a PDF file');
            }
        }
    });
}

function handleFileSelect(file) {
    currentUploadFile = file;
    
    // Show upload modal with filename
    const modal = document.getElementById('uploadModal');
    document.getElementById('originalFilename').textContent = file.name;
    
    // Pre-fill with filename (without .pdf extension)
    const defaultName = file.name.replace('.pdf', '');
    document.getElementById('pdfNameInput').value = defaultName;
    
    modal.classList.add('active');
}

function cancelUpload() {
    currentUploadFile = null;
    document.getElementById('uploadModal').classList.remove('active');
    document.getElementById('fileInput').value = '';
    document.getElementById('uploadProgress').style.display = 'none';
    document.getElementById('uploadProgressBar').style.width = '0%';
    document.getElementById('uploadStatus').style.display = 'none';
}

async function confirmUpload() {
    if (!currentUploadFile) return;
    
    const pdfName = document.getElementById('pdfNameInput').value.trim();
    if (!pdfName) {
        alert('Please enter a name for your PDF');
        return;
    }
    
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadProgress = document.getElementById('uploadProgress');
    const uploadProgressBar = document.getElementById('uploadProgressBar');
    const uploadBtn = document.getElementById('uploadConfirmBtn');
    const cancelBtn = document.getElementById('uploadCancelBtn');
    
    // Disable buttons during upload
    uploadBtn.disabled = true;
    cancelBtn.disabled = true;
    uploadBtn.style.opacity = '0.5';
    cancelBtn.style.opacity = '0.5';
    uploadBtn.style.cursor = 'not-allowed';
    cancelBtn.style.cursor = 'not-allowed';
    
    // Show progress
    uploadProgress.style.display = 'block';
    uploadStatus.style.display = 'block';
    uploadStatus.style.color = '#666';
    uploadStatus.textContent = '📤 Uploading...';
    uploadProgressBar.style.width = '20%';
    
    // Simulate progress updates
    setTimeout(() => {
        uploadProgressBar.style.width = '35%';
        uploadStatus.textContent = '⚙️ Indexing...';
    }, 500);
    
    setTimeout(() => {
        uploadProgressBar.style.width = '50%';
        uploadStatus.textContent = '🔍 Processing chunks...';
    }, 1500);
    
    setTimeout(() => {
        uploadProgressBar.style.width = '70%';
        uploadStatus.textContent = '☁️ Saving to RAG...';
    }, 3000);
    
    setTimeout(() => {
        uploadProgressBar.style.width = '85%';
        uploadStatus.textContent = '🔄 Redeploying ChromaDB...';
    }, 4500);
    
    try {
        // Create form data
        const formData = new FormData();
        formData.append('file', currentUploadFile);
        formData.append('pdf_name', pdfName);
        
        // Upload PDF
        const response = await fetch(`${API_BASE}/api/upload-pdf`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }
        
        const result = await response.json();
        
        uploadProgressBar.style.width = '100%';
        uploadStatus.style.color = '#4caf50';
        uploadStatus.textContent = `✅ File saved on RAG!`;
        
        // Wait a bit, then close and reload
        setTimeout(async () => {
            // Re-enable buttons before closing
            uploadBtn.disabled = false;
            cancelBtn.disabled = false;
            uploadBtn.style.opacity = '1';
            cancelBtn.style.opacity = '1';
            uploadBtn.style.cursor = 'pointer';
            cancelBtn.style.cursor = 'pointer';
            
            cancelUpload();
            await loadLibrary();
        }, 2000);
        
    } catch (error) {
        console.error('Upload error:', error);
        uploadStatus.style.color = '#c62828';
        uploadStatus.textContent = `❌ Error: ${error.message}`;
        uploadProgressBar.style.width = '0%';
        
        // Re-enable buttons after error
        uploadBtn.disabled = false;
        cancelBtn.disabled = false;
        uploadBtn.style.opacity = '1';
        cancelBtn.style.opacity = '1';
        uploadBtn.style.cursor = 'pointer';
        cancelBtn.style.cursor = 'pointer';
    }
}

// Delete functions
function showDeleteConfirm(sourceId, title, type) {
    currentDeleteId = sourceId;
    const modal = document.getElementById('deleteModal');
    const message = document.getElementById('deleteMessage');
    
    const typeLabel = type === 'independent_pdf' ? 'PDF' : 'note';
    message.innerHTML = `
        You are about to delete:<br><br>
        <strong>"${title}"</strong><br><br>
        This will:<br>
        • Remove from search index<br>
        • Delete the ${typeLabel} file<br>
        • Remove all embeddings<br><br>
        <strong>This action cannot be undone.</strong>
    `;
    
    modal.classList.add('active');
}

function cancelDelete() {
    currentDeleteId = null;
    document.getElementById('deleteModal').classList.remove('active');
}

async function confirmDelete() {
    if (!currentDeleteId) return;
    
    const modal = document.getElementById('deleteModal');
    const message = document.getElementById('deleteMessage');
    const confirmBtn = document.getElementById('deleteConfirmBtn');
    const cancelBtn = document.getElementById('deleteCancelBtn');
    
    // Disable buttons and gray out
    confirmBtn.disabled = true;
    cancelBtn.disabled = true;
    confirmBtn.style.opacity = '0.5';
    cancelBtn.style.opacity = '0.5';
    confirmBtn.style.cursor = 'not-allowed';
    cancelBtn.style.cursor = 'not-allowed';
    
    message.innerHTML = '⏳ Deleting from GCS...';
    
    try {
        const response = await fetch(`${API_BASE}/api/library/${currentDeleteId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete');
        }
        
        const result = await response.json();
        
        message.innerHTML = '✅ Deleted successfully!';
        
        // Wait a moment to show success, then close and reload
        setTimeout(async () => {
            // Re-enable buttons
            confirmBtn.disabled = false;
            cancelBtn.disabled = false;
            confirmBtn.style.opacity = '1';
            cancelBtn.style.opacity = '1';
            confirmBtn.style.cursor = 'pointer';
            cancelBtn.style.cursor = 'pointer';
            
            // Close modal
            modal.classList.remove('active');
            currentDeleteId = null;
            
            // Reload library
            await loadLibrary();
        }, 1000);
        
    } catch (error) {
        console.error('Delete error:', error);
        message.innerHTML = `❌ Error: ${error.message}`;
        
        // Re-enable buttons after error
        confirmBtn.disabled = false;
        cancelBtn.disabled = false;
        confirmBtn.style.opacity = '1';
        cancelBtn.style.opacity = '1';
        confirmBtn.style.cursor = 'pointer';
        cancelBtn.style.cursor = 'pointer';
        
        setTimeout(() => {
            modal.classList.remove('active');
            currentDeleteId = null;
        }, 3000);
    }
}

// View functions
function viewPDF(sourceId, filename) {
    // Get the source to find the actual page count
    const source = allSources.find(s => s.id === sourceId);
    if (!source) {
        console.error('Source not found:', sourceId);
        return;
    }
    
    // Extract just the filename without the pdf_ prefix
    const actualFilename = filename || sourceId.replace('pdf_', '');
    
    // Use actual page count
    const totalPages = source.total_pages || 1;
    
    // Open in independent viewer with correct page range
    window.open(`/viewer/independent?start=1&end=${totalPages}&pdf=${encodeURIComponent(actualFilename)}`, '_blank');
}

function viewNote(noteId) {
    alert(`View note: ${noteId}\n\nNote viewer coming in Phase 2!`);
}

function editNote(noteId) {
    alert(`Edit note: ${noteId}\n\nNote editor coming in Phase 2!`);
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

function formatBytes(bytes) {
    if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
    if (bytes >= 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return bytes + ' B';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) return 'Today';
    if (days === 1) return 'Yesterday';
    if (days < 7) return `${days} days ago`;
    
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
