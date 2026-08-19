/**
 * Lean Manufacturing Knowledge Base - Frontend Logic
 *
 * Provides Alpine.js component definitions and utility functions
 * for search, navigation, and interactivity.
 */

// ==================== Alpine.js Components ====================

/**
 * Dashboard page component
 */
function dashboard() {
    return {
        searchQuery: '',
        searchResults: [],
        isSearching: false,

        async performSearch() {
            if (this.searchQuery.length < 1) {
                this.searchResults = [];
                return;
            }
            this.isSearching = true;
            try {
                const response = await fetch(`/api/search?q=${encodeURIComponent(this.searchQuery)}`);
                const data = await response.json();
                this.searchResults = data.results || [];
            } catch (e) {
                console.error('Search failed:', e);
                this.searchResults = [];
            } finally {
                this.isSearching = false;
            }
        },
    };
}

/**
 * Knowledge browser page component
 */
function knowledgeBrowser() {
    return {
        expandedDirs: {},
        filterQuery: '',

        toggleDir(dirName) {
            this.expandedDirs[dirName] = !this.expandedDirs[dirName];
        },

        isExpanded(dirName) {
            return this.expandedDirs[dirName] !== false;
        },

        init() {
            // Expand all directories by default
            document.querySelectorAll('[x-data]').forEach((el) => {
                const dirs = el.querySelectorAll('[data-dir]');
                dirs.forEach((dir) => {
                    const name = dir.getAttribute('data-dir');
                    if (name) {
                        this.expandedDirs[name] = true;
                    }
                });
            });
        },
    };
}

/**
 * Training page component
 */
function trainingPage() {
    return {
        activeTab: 'levels',
    };
}

/**
 * Assessment page component
 */
function assessmentPage() {
    return {
        activeSection: 'model',
    };
}

/**
 * Implementation page component
 */
function implementationPage() {
    return {
        activePhase: 1,
    };
}

// ==================== Utility Functions ====================

/**
 * Debounce function - delays execution until after wait period
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Format file size in human-readable format
 */
function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

/**
 * Get file extension icon
 */
function getFileIcon(ext) {
    const icons = {
        '.md': '📝',
        '.docx': '📘',
        '.xlsx': '📗',
        '.pptx': '📙',
        '.pdf': '📕',
    };
    return icons[ext] || '📄';
}

// ==================== Keyboard Shortcuts ====================

document.addEventListener('keydown', function (e) {
    // Ctrl+K or Cmd+K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }
});

// ==================== Download Tracking ====================

/**
 * Track file downloads (localStorage based)
 */
const DownloadTracker = {
    KEY: 'lean_download_history',

    getHistory() {
        try {
            const raw = localStorage.getItem(this.KEY);
            return raw ? JSON.parse(raw) : [];
        } catch {
            return [];
        }
    },

    track(filePath) {
        const history = this.getHistory();
        const entry = {
            path: filePath,
            timestamp: Date.now(),
        };
        // Remove duplicate if exists
        const filtered = history.filter((h) => h.path !== filePath);
        filtered.unshift(entry);
        // Keep only last 50 entries
        const trimmed = filtered.slice(0, 50);
        localStorage.setItem(this.KEY, JSON.stringify(trimmed));
    },

    getRecent(count = 10) {
        return this.getHistory().slice(0, count);
    },
};

// Track downloads when download links are clicked
document.addEventListener('click', function (e) {
    const link = e.target.closest('a[href^="/download/"]');
    if (link) {
        const filePath = link.getAttribute('href').replace('/download/', '');
        DownloadTracker.track(filePath);
    }
});

// ==================== Smooth Scroll ====================

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            e.preventDefault();
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start',
            });
        }
    });
});
