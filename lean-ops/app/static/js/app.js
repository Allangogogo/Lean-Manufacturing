/* ============================================================
   LeanOps Core JS v2.0
   精益运营管理系统 — 核心交互工具
   ============================================================ */

// ---------- API Helper ----------
const API_BASE = '/api/v1';

const LeanOps = {
  token: localStorage.getItem('leanops_token'),
  user: JSON.parse(localStorage.getItem('leanops_user') || 'null'),
  factory: JSON.parse(localStorage.getItem('leanops_factory') || 'null'),

  async api(path, options = {}) {
    const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      ...options.headers,
    };

    const res = await fetch(url, { ...options, headers });

    if (res.status === 401) {
      this.logout();
      return;
    }

    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
      throw { status: res.status, detail: data.detail || data.message || '请求失败', data };
    }

    return data;
  },

  logout() {
    localStorage.removeItem('leanops_token');
    localStorage.removeItem('leanops_user');
    localStorage.removeItem('leanops_factory');
    window.location.href = '/login';
  },

  // ---------- Toast Notifications ----------
  toast(message, type = 'info', duration = 3000) {
    let container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const icons = {
      success: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 1a9 9 0 100 18 9 9 0 000-18zm3.7 7.3l-4 4a1 1 0 01-1.4 0l-2-2a1 1 0 011.4-1.4L9 10.6l3.3-3.3a1 1 0 011.4 1.4z"/></svg>',
      error: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 1a9 9 0 100 18 9 9 0 000-18zm1 12a1 1 0 01-2 0v-3a1 1 0 012 0v3zm0-6a1 1 0 01-2 0V5a1 1 0 012 0v2z"/></svg>',
      warning: '<svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor"><path d="M10 1a9 9 0 100 18 9 9 0 000-18zm1 12a1 1 0 01-2 0v-3a1 1 0 012 0v3zm0-6a1 1 0 01-2 0V5a1 1 0 012 0v2z"/></svg>',
    };

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span style="color: var(--color-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'}-500); flex-shrink: 0;">${icons[type] || icons.warning}</span><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  },

  // ---------- Format Helpers ----------
  fmtDate(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  },

  fmtDateTime(dateStr) {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    return `${this.fmtDate(dateStr)} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
  },

  fmtMoney(num) {
    if (num === null || num === undefined) return '—';
    return new Intl.NumberFormat('zh-CN', { style: 'currency', currency: 'CNY', minimumFractionDigits: 0 }).format(num);
  },

  fmtNumber(num) {
    if (num === null || num === undefined) return '—';
    return new Intl.NumberFormat('zh-CN').format(num);
  },

  // ---------- Status Helpers ----------
  statusBadge(status, map = {}) {
    const defaultMap = {
      draft: { label: '草稿', class: 'badge-gray' },
      pending: { label: '待审', class: 'badge-warning' },
      approved: { label: '已批', class: 'badge-success' },
      rejected: { label: '已拒', class: 'badge-danger' },
      active: { label: '进行中', class: 'badge-primary' },
      completed: { label: '已完成', class: 'badge-success' },
      cancelled: { label: '已取消', class: 'badge-gray' },
      planning: { label: '规划中', class: 'badge-info' },
      in_progress: { label: '进行中', class: 'badge-primary' },
      on_hold: { label: '暂停', class: 'badge-warning' },
      closed: { label: '已关闭', class: 'badge-gray' },
      open: { label: '待处理', class: 'badge-warning' },
      resolved: { label: '已解决', class: 'badge-success' },
    };
    const item = map[status] || defaultMap[status] || { label: status, class: 'badge-gray' };
    return `<span class="badge ${item.class}">${item.label}</span>`;
  },

  priorityBadge(priority) {
    const map = {
      low: { label: '低', class: 'badge-gray' },
      medium: { label: '中', class: 'badge-info' },
      high: { label: '高', class: 'badge-warning' },
      urgent: { label: '紧急', class: 'badge-danger' },
    };
    const item = map[priority] || { label: priority, class: 'badge-gray' };
    return `<span class="badge ${item.class}">${item.label}</span>`;
  },

  // ---------- Theme ----------
  initTheme() {
    const saved = localStorage.getItem('leanops_theme') || 'light';
    document.documentElement.setAttribute('data-theme', saved);
    return saved;
  },

  toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('leanops_theme', next);
    return next;
  },

  // ---------- Auth Guard ----------
  requireAuth() {
    if (!this.token) {
      window.location.href = '/login';
      return false;
    }
    return true;
  },

  // ---------- Initials ----------
  initials(name) {
    if (!name) return '?';
    return name.charAt(0).toUpperCase();
  },
};

// ---------- Init theme on load ----------
LeanOps.initTheme();

// ---------- Simple SVG Chart Helpers ----------
const Charts = {
  // Donut chart
  donut(data, size = 160, thickness = 24) {
    const total = data.reduce((s, d) => s + d.value, 0);
    const radius = (size - thickness) / 2;
    const circumference = 2 * Math.PI * radius;
    let offset = 0;

    const segments = data.map((d, i) => {
      const pct = total > 0 ? d.value / total : 0;
      const len = circumference * pct;
      const gap = circumference - len;
      const seg = `<circle cx="${size/2}" cy="${size/2}" r="${radius}" fill="none" stroke="${d.color}" stroke-width="${thickness}" stroke-dasharray="${len} ${gap}" stroke-dashoffset="${-offset}" transform="rotate(-90 ${size/2} ${size/2})"/>`;
      offset += len;
      return seg;
    }).join('');

    return `<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">${segments}<text x="50%" y="50%" text-anchor="middle" dy="0.35em" font-size="24" font-weight="700" fill="var(--text-primary)">${total}</text></svg>`;
  },

  // Bar chart
  bars(data, width = 400, height = 200) {
    const max = Math.max(...data.map(d => d.value), 1);
    const barWidth = (width - 40) / data.length * 0.7;
    const gap = (width - 40) / data.length * 0.3;
    const chartHeight = height - 40;

    const bars = data.map((d, i) => {
      const h = (d.value / max) * chartHeight;
      const x = 20 + i * (barWidth + gap);
      const y = chartHeight - h + 10;
      return `<rect x="${x}" y="${y}" width="${barWidth}" height="${h}" rx="4" fill="${d.color || 'var(--color-primary-500)'}"/><text x="${x + barWidth/2}" y="${height - 8}" text-anchor="middle" font-size="11" fill="var(--text-tertiary)">${d.label}</text>`;
    }).join('');

    return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">${bars}</svg>`;
  },

  // Line chart
  line(data, width = 400, height = 200) {
    if (!data.length) return '';
    const max = Math.max(...data.map(d => d.value), 1);
    const min = Math.min(...data.map(d => d.value), 0);
    const range = max - min || 1;
    const stepX = (width - 40) / Math.max(data.length - 1, 1);
    const chartHeight = height - 40;

    const points = data.map((d, i) => {
      const x = 20 + i * stepX;
      const y = chartHeight - ((d.value - min) / range) * chartHeight + 10;
      return `${x},${y}`;
    }).join(' ');

    const area = `M 20,${chartHeight + 10} L ${points.split(' ').join(' L ')} L ${20 + (data.length - 1) * stepX},${chartHeight + 10} Z`;

    return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}">
      <defs><linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="var(--color-primary-500)" stop-opacity="0.3"/>
        <stop offset="100%" stop-color="var(--color-primary-500)" stop-opacity="0"/>
      </linearGradient></defs>
      <path d="${area}" fill="url(#areaGrad)"/>
      <polyline points="${points}" fill="none" stroke="var(--color-primary-500)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
      ${data.map((d, i) => {
        const x = 20 + i * stepX;
        const y = chartHeight - ((d.value - min) / range) * chartHeight + 10;
        return `<circle cx="${x}" cy="${y}" r="3" fill="var(--color-primary-500)"/><text x="${x}" y="${height - 8}" text-anchor="middle" font-size="11" fill="var(--text-tertiary)">${d.label}</text>`;
      }).join('')}
    </svg>`;
  },
};
