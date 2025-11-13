// Library Management JavaScript

const API_BASE = window.location.origin;
let allSources = [];
let currentDeleteId = null;

// Load library on page load
window.addEventListener('load', async () => {
    await loadStats();
    await loadLibrary();
});

// Filter change
document.getElementById('filterType').addEventListener('change', filterLibrary);

// Search input
document.getElementById('searchFilter').addEventListener('input', filterLibrary);

async function loadStats() {
    try {
        const response = await fetch(`${API_BASE}/api/library/stats`);
        if (!response.ok) throw new Error('Failed to load stats');
        
        const stats = await response.json();
        
        document.getElementById('totalSources').textContent = stats.total_sources;
        document.getElementById('totalWords').textContent = formatNumber(stats.total_words);
        document.getElementById('totalIndexed').textContent = stats.total_indexed;
        document.getElementById('storageUsed').textContent = `${stats.storage_used_mb} MB`;
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

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
        // Harrison's is not deletable, only viewable
        actionsHtml = `
            <button class="btn btn-view btn-small" disabled style="opacity: 0.5;">
                View Chapters (Coming soon)
            </button>
        `;
    } else if (source.type === 'independent_pdf') {
        actionsHtml = `
            <button class="btn btn-view btn-small" onclick="viewPDF('${source.id}')">
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
    
    message.innerHTML = '⏳ Deleting...';
    
    try {
        const response = await fetch(`${API_BASE}/api/library/${currentDeleteId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to delete');
        }
        
        const result = await response.json();
        
        // Close modal
        modal.classList.remove('active');
        currentDeleteId = null;
        
        // Show success message
        message.innerHTML = `✅ ${result.message}`;
        
        // Reload library
        await loadStats();
        await loadLibrary();
        
    } catch (error) {
        console.error('Delete error:', error);
        message.innerHTML = `❌ Error: ${error.message}`;
        
        setTimeout(() => {
            modal.classList.remove('active');
            currentDeleteId = null;
        }, 3000);
    }
}

function viewPDF(sourceId) {
    // Get the source to find filename
    const source = allSources.find(s => s.id === sourceId);
    if (!source) return;
    
    // For now, just alert - full implementation would open the PDF viewer
    alert(`View PDF: ${source.title}\n\nFull implementation coming soon!`);
    // TODO: Open independent PDF viewer with the source
}

function viewNote(noteId) {
    alert(`View note: ${noteId}\n\nFull implementation coming in Phase 2!`);
    // TODO: Open note viewer
}

function editNote(noteId) {
    alert(`Edit note: ${noteId}\n\nFull implementation coming in Phase 2!`);
    // TODO: Open note editor
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

