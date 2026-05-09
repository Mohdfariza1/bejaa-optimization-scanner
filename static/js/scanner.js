/* Bejaa Digital — Scanner Dashboard JS */

const CAT_CONFIG = {
  seo:            { label: 'SEO',          icon: 'fa-search',           color: '#818cf8', bg: 'rgba(99,102,241,.2)' },
  performance:    { label: 'Performance',  icon: 'fa-bolt',             color: '#f59e0b', bg: 'rgba(245,158,11,.2)' },
  security:       { label: 'Security',     icon: 'fa-shield-alt',       color: '#10b981', bg: 'rgba(16,185,129,.2)' },
  mobile:         { label: 'Mobile',       icon: 'fa-mobile-alt',       color: '#60a5fa', bg: 'rgba(59,130,246,.2)' },
  accessibility:  { label: 'Accessibility',icon: 'fa-universal-access', color: '#c084fc', bg: 'rgba(168,85,247,.2)' },
  technical_seo:  { label: 'Tech SEO',     icon: 'fa-code',             color: '#f87171', bg: 'rgba(239,68,68,.2)'  },
  uiux:           { label: 'UI/UX',        icon: 'fa-paint-brush',      color: '#fb923c', bg: 'rgba(251,146,60,.2)' },
};

const STEPS = [
  'Connecting to website...',
  'Analyzing SEO tags...',
  'Measuring performance...',
  'Scanning security headers...',
  'Testing mobile layout...',
  'Checking accessibility...',
  'Auditing technical SEO...',
  'Evaluating UI/UX patterns...',
];

let overallChart = null;
const donutCharts = {};
let allInsights = [];

// ── INIT ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('scanButton').addEventListener('click', startScan);
  document.getElementById('websiteUrl').addEventListener('keydown', e => { if (e.key === 'Enter') startScan(); });
  document.getElementById('btnNewScan').addEventListener('click', resetToHero);
  document.getElementById('btnDownload').addEventListener('click', downloadJSON);
  document.getElementById('btnShare').addEventListener('click', shareWhatsApp);

  document.querySelectorAll('.rec-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.rec-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      filterRecs(tab.dataset.prio);
    });
  });
});

// ── SCAN ──────────────────────────────────────────────────
async function startScan() {
  const url = document.getElementById('websiteUrl').value.trim();
  if (!url) { showToast('Please enter a website URL.'); return; }

  let normalized = url;
  if (!/^https?:\/\//i.test(url)) normalized = 'https://' + url;

  showLoading();
  const progressInterval = animateLoading();

  try {
    const res = await fetch('/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: normalized }),
    });
    const data = await res.json();
    clearInterval(progressInterval);

    if (!res.ok) {
      hideLoading();
      showToast(data.error || 'Scan failed. Check the URL and try again.');
      resetToHero();
      return;
    }

    finishLoading(() => { hideLoading(); renderDashboard(data); });

  } catch (err) {
    clearInterval(progressInterval);
    hideLoading();
    showToast('Network error. Make sure the server is running.');
  }
}

// ── LOADING ───────────────────────────────────────────────
function showLoading() {
  document.getElementById('loadingOverlay').style.display = 'flex';
  document.getElementById('featuresSection').style.display = 'none';
  document.getElementById('dashboard').style.display = 'none';
  document.querySelectorAll('.lstep').forEach(s => s.classList.remove('active', 'done'));
  setRingProgress(0);
}

function hideLoading() {
  document.getElementById('loadingOverlay').style.display = 'none';
}

function animateLoading() {
  let step = 0;
  const steps = document.querySelectorAll('.lstep');
  const total = STEPS.length;

  const tick = () => {
    if (step > 0) {
      steps[step - 1]?.classList.remove('active');
      steps[step - 1]?.classList.add('done');
    }
    if (step < total) {
      steps[step]?.classList.add('active');
      document.getElementById('loadStep').textContent = STEPS[step];
      setRingProgress(Math.round(((step + 1) / (total + 1)) * 90));
      step++;
    }
  };

  tick();
  return setInterval(tick, 1400);
}

function finishLoading(cb) {
  document.querySelectorAll('.lstep').forEach(s => { s.classList.remove('active'); s.classList.add('done'); });
  setRingProgress(100);
  setTimeout(cb, 500);
}

function setRingProgress(pct) {
  const circ = 213.6;
  const offset = circ - (pct / 100) * circ;
  document.getElementById('loadRing').style.strokeDashoffset = offset;
  document.getElementById('loadPct').textContent = pct + '%';
}

// ── RENDER DASHBOARD ──────────────────────────────────────
function renderDashboard(data) {
  const cats = data.categories || {};
  const scores = data.category_scores || {};

  document.getElementById('dashUrl').textContent = data.url || '';
  document.getElementById('dashDate').textContent = data.scan_date
    ? new Date(data.scan_date).toLocaleString() : '';

  const overall = data.overall_score || 0;
  const grade   = data.grade || 'F';
  animateNumber('overallScore', overall);
  document.getElementById('scoreGrade').textContent = grade;
  document.getElementById('scoreLabel').textContent = scoreLabel(overall);

  renderOverallDonut(overall);

  // score glow pulse after donut finishes
  setTimeout(() => {
    const wrap = document.querySelector('.score-donut-wrap');
    if (wrap) { wrap.classList.add('score-glow'); setTimeout(() => wrap.classList.remove('score-glow'), 1200); }
  }, 1100);

  Object.entries(CAT_CONFIG).forEach(([key]) => {
    const sc = scores[key] ?? cats[key]?.score ?? 0;
    const fill = document.getElementById('sfill-' + key);
    const val  = document.getElementById('sval-' + key);
    if (fill) { fill.style.background = scoreColor(sc); setTimeout(() => fill.style.width = sc + '%', 100); }
    if (val)  animateNumber('sval-' + key, sc);
  });

  renderDonutsGrid(cats, scores);
  renderStats(data);
  renderCatCards(cats);
  renderFixes(data.priority_fixes || []);

  allInsights = data.actionable_insights || [];
  renderRecs(allInsights);

  document.querySelectorAll('.rec-tab').forEach(t => t.classList.remove('active'));
  const allTab = document.querySelector('.rec-tab[data-prio="all"]');
  if (allTab) allTab.classList.add('active');

  document.getElementById('dashboard').style.display = 'block';
  window.currentData = data;

  setTimeout(() => {
    document.getElementById('dashboard').scrollIntoView({ behavior: 'smooth' });
    initScrollAnimations();
  }, 50);
}

// ── SCROLL ANIMATIONS ─────────────────────────────────────
function initScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.fade-up').forEach(el => observer.observe(el));
}

// ── OVERALL DONUT ─────────────────────────────────────────
function renderOverallDonut(score) {
  const ctx = document.getElementById('overallDonut').getContext('2d');
  if (overallChart) overallChart.destroy();

  const color = scoreColor(score);
  overallChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [score, 100 - score],
        backgroundColor: [color, '#1a2340'],
        borderWidth: 0,
        hoverOffset: 0,
      }]
    },
    options: {
      cutout: '78%',
      animation: { duration: 1000, easing: 'easeInOutQuart' },
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      events: [],
    }
  });
}

// ── CATEGORY DONUTS ───────────────────────────────────────
function renderDonutsGrid(cats, scores) {
  const grid = document.getElementById('donutsGrid');
  grid.innerHTML = '';

  Object.entries(CAT_CONFIG).forEach(([key, cfg]) => {
    const sc = scores[key] ?? cats[key]?.score ?? 0;
    const color = scoreColor(sc);

    const item = document.createElement('div');
    item.className = 'donut-item fade-up';
    item.innerHTML = `
      <div class="donut-wrap">
        <canvas id="donut-${key}" width="78" height="78"></canvas>
        <div class="donut-center" style="color:${color}">${sc}</div>
      </div>
      <div class="donut-name">${cfg.label}</div>
    `;
    grid.appendChild(item);

    setTimeout(() => {
      const c = document.getElementById('donut-' + key);
      if (!c) return;
      if (donutCharts[key]) donutCharts[key].destroy();
      donutCharts[key] = new Chart(c.getContext('2d'), {
        type: 'doughnut',
        data: {
          datasets: [{ data: [sc, 100 - sc], backgroundColor: [color, '#1a2340'], borderWidth: 0 }]
        },
        options: {
          cutout: '72%',
          animation: { duration: 900 },
          plugins: { legend: { display: false }, tooltip: { enabled: false } },
          events: [],
        }
      });
    }, 50);
  });
}

// ── QUICK STATS ───────────────────────────────────────────
function renderStats(data) {
  const conn = data.connectivity || {};
  const perf = data.categories?.performance?.metrics || {};
  const sec  = data.categories?.security?.checks || {};
  const seo  = data.categories?.seo?.checks || {};

  const stats = [
    { icon: 'fa-clock',       bg: 'rgba(245,158,11,.2)',  color: '#f59e0b', name: 'Load Time',    val: perf.page_load_time ? perf.page_load_time + 's' : '—' },
    { icon: 'fa-weight',      bg: 'rgba(99,102,241,.2)',  color: '#818cf8', name: 'Page Size',    val: perf.page_size_kb ? perf.page_size_kb + ' KB' : '—' },
    { icon: 'fa-lock',        bg: 'rgba(16,185,129,.2)',  color: '#10b981', name: 'HTTPS',        val: sec.https ? 'Enabled' : 'Disabled' },
    { icon: 'fa-compress',    bg: 'rgba(59,130,246,.2)',  color: '#60a5fa', name: 'Compression',  val: perf.compression || '—' },
    { icon: 'fa-server',      bg: 'rgba(168,85,247,.2)',  color: '#c084fc', name: 'Server',       val: conn.server || '—' },
    { icon: 'fa-exchange-alt',bg: 'rgba(239,68,68,.2)',   color: '#f87171', name: 'Redirects',    val: conn.redirects != null ? conn.redirects + ' redirect(s)' : '—' },
    { icon: 'fa-images',      bg: 'rgba(245,158,11,.2)',  color: '#f59e0b', name: 'Images',       val: seo.images ? `${seo.images.with_alt}/${seo.images.total} with alt` : '—' },
    { icon: 'fa-tachometer-alt', bg: 'rgba(16,185,129,.2)', color: '#10b981', name: 'HTTP Status', val: conn.status_code || '—' },
  ];

  document.getElementById('statsList').innerHTML = stats.map(s => `
    <div class="stat-item">
      <div class="stat-icon" style="background:${s.bg};color:${s.color}"><i class="fas ${s.icon}"></i></div>
      <div class="stat-body">
        <div class="stat-name">${s.name}</div>
        <div class="stat-val">${s.val}</div>
      </div>
    </div>
  `).join('');
}

// ── CATEGORY CARDS (expandable accordion) ─────────────────
function renderCatCards(cats) {
  const grid = document.getElementById('catGrid');
  grid.innerHTML = '';

  Object.entries(CAT_CONFIG).forEach(([key, cfg], idx) => {
    const d = cats[key] || {};
    const sc = d.score ?? 0;
    const color = scoreColor(sc);
    const badgeClass = sc >= 80 ? 'badge-good' : (sc >= 50 ? 'badge-ok' : 'badge-poor');
    const cardId = `cat-card-${key}`;

    const issues   = (d.issues || []);
    const warnings = (d.warnings || []);
    const recs     = (d.recommendations || []);
    const hasExpand = issues.length > 0 || warnings.length > 0 || recs.length > 0;

    const expandHtml = hasExpand ? `
      <div class="cat-expand-body">
        ${issues.map(i => `<div class="expand-item expand-issue"><i class="fas fa-times-circle"></i><span>${i}</span></div>`).join('')}
        ${warnings.map(w => `<div class="expand-item expand-warn"><i class="fas fa-exclamation-triangle"></i><span>${w}</span></div>`).join('')}
        ${recs.map(r => `<div class="expand-item expand-rec"><i class="fas fa-arrow-right"></i><span>${r}</span></div>`).join('')}
      </div>
      <button class="cat-expand-toggle" onclick="toggleCard('${cardId}')">
        <i class="fas fa-chevron-down"></i> Show full details
      </button>
    ` : '';

    const card = document.createElement('div');
    card.className = 'cat-card fade-up';
    card.id = cardId;
    card.style.animationDelay = `${idx * 60}ms`;
    card.innerHTML = `
      <div class="cat-card-header ${hasExpand ? 'expandable' : ''}" ${hasExpand ? `onclick="toggleCard('${cardId}')"` : ''}>
        <div class="cat-card-title">
          <div class="cat-icon" style="background:${cfg.bg};color:${cfg.color}"><i class="fas ${cfg.icon}"></i></div>
          <span class="cat-name">${cfg.label}</span>
        </div>
        <div class="cat-header-right">
          <span class="cat-badge ${badgeClass}">${sc}/100</span>
          ${hasExpand ? '<i class="fas fa-chevron-down cat-chevron"></i>' : ''}
        </div>
      </div>
      <div class="cat-mini-bar"><div class="cat-mini-fill" style="background:${color};width:0%" data-w="${sc}%"></div></div>
      <div class="cat-details">${getCatDetails(key, d)}</div>
      ${expandHtml}
    `;
    grid.appendChild(card);
  });

  setTimeout(() => {
    document.querySelectorAll('.cat-mini-fill').forEach(el => { el.style.width = el.dataset.w; });
  }, 100);
}

function toggleCard(cardId) {
  const card = document.getElementById(cardId);
  if (!card) return;
  const body    = card.querySelector('.cat-expand-body');
  const chevron = card.querySelector('.cat-chevron');
  const toggle  = card.querySelector('.cat-expand-toggle');
  if (!body) return;

  const isOpen = body.classList.contains('open');
  body.classList.toggle('open');
  if (chevron) chevron.classList.toggle('rotated');
  if (toggle) toggle.innerHTML = isOpen
    ? '<i class="fas fa-chevron-down"></i> Show full details'
    : '<i class="fas fa-chevron-up"></i> Hide details';
}

function getCatDetails(key, d) {
  const m = d.metrics || {};
  const c = d.checks || {};

  switch (key) {
    case 'seo': {
      const imgs = c.images || {}; const links = c.links || {}; const heads = c.headings || {};
      return [
        { i: 'fa-tags',   t: `Meta tags: ${d.present_tags?.length || 0} present, ${d.missing_tags?.length || 0} missing` },
        { i: 'fa-image',  t: `Images: ${imgs.with_alt || 0} with alt / ${imgs.total || 0} total` },
        { i: 'fa-heading',t: `H1: ${heads.h1 || 0} | H2: ${heads.h2 || 0} | H3: ${heads.h3 || 0}` },
        { i: 'fa-link',   t: `Links: ${links.internal || 0} internal, ${links.external || 0} external` },
      ].map(row).join('');
    }
    case 'performance': {
      const res = m.resources || {};
      return [
        { i: 'fa-clock',   t: `Load time: ${m.page_load_time || 0}s` },
        { i: 'fa-weight',  t: `Page size: ${m.page_size_kb || 0} KB` },
        { i: 'fa-ban',     t: `Render-blocking scripts: ${m.render_blocking_scripts || 0}` },
        { i: 'fa-compress',t: `Compression: ${m.compression || 'None'}` },
        { i: 'fa-images',  t: `Images: ${res.images || 0} | Scripts: ${res.scripts || 0} | CSS: ${res.stylesheets || 0}` },
      ].map(row).join('');
    }
    case 'security': {
      const ssl = c.ssl_cert || {};
      return [
        { i: 'fa-lock',      t: `HTTPS: ${c.https ? 'Yes' : 'No'}` },
        { i: 'fa-certificate', t: `SSL: ${ssl.valid ? 'Valid — ' + ssl.days_remaining + ' days left' : ssl.valid === false ? 'Invalid' : 'Not checked'}` },
        { i: 'fa-shield',    t: `Security headers: ${d.headers_present?.length || 0}/${(d.headers_present?.length || 0) + (d.headers_missing?.length || 0)}` },
        { i: 'fa-code',      t: `Mixed content: ${c.mixed_content || 0} issues` },
      ].map(row).join('');
    }
    case 'mobile': {
      const imgs = c.images || {};
      return [
        { i: 'fa-mobile',   t: `Viewport: ${c.viewport ? 'Present' : 'Missing'}` },
        { i: 'fa-th-large', t: `Responsive CSS: ${c.responsive_css ? 'Detected' : 'Not found'}` },
        { i: 'fa-expand',   t: `Fixed-width elements: ${c.large_fixed_width_elements || 0}` },
        { i: 'fa-images',   t: `Responsive images: ${imgs.responsive || 0}/${imgs.total || 0}` },
      ].map(row).join('');
    }
    case 'accessibility': {
      const imgs = c.images || {}; const forms = c.form_labels || {}; const lm = c.landmarks || {};
      return [
        { i: 'fa-language', t: `Lang attribute: ${c.lang_attribute ? 'Present' : 'Missing'}` },
        { i: 'fa-image',    t: `Images with alt: ${imgs.with_alt || 0}/${imgs.total || 0}` },
        { i: 'fa-edit',     t: `Unlabeled inputs: ${forms.unlabeled || 0}` },
        { i: 'fa-map',      t: `Landmarks: ${Object.values(lm).filter(Boolean).length}/4` },
      ].map(row).join('');
    }
    case 'technical_seo': {
      const sd = c.structured_data || {}; const og = c.open_graph || {};
      return [
        { i: 'fa-robot',   t: `robots.txt: ${c.robots_txt?.exists ? 'Found' : 'Missing'}` },
        { i: 'fa-sitemap', t: `sitemap.xml: ${c.sitemap_xml?.exists ? 'Found' : 'Missing'}` },
        { i: 'fa-link',    t: `Canonical tag: ${c.canonical ? 'Present' : 'Missing'}` },
        { i: 'fa-code',    t: `Structured data: ${sd.count || 0} JSON-LD block(s)` },
        { i: 'fa-share',   t: `Open Graph: ${og.complete ? 'Complete' : 'Incomplete'}` },
      ].map(row).join('');
    }
    case 'uiux': {
      const ts  = c.trust_signals || {};
      const mod = c.modernity || {};
      return [
        { i: 'fa-mouse-pointer', t: `CTA buttons: ${c.cta_buttons || 0} found` },
        { i: 'fa-bars',          t: `Nav links: ${c.nav_links || 0}` },
        { i: 'fa-star',          t: `Social proof: ${c.social_proof ? 'Detected' : 'Not found'}` },
        { i: 'fa-phone',         t: `Phone number: ${ts.phone_number ? 'Present' : 'Missing'}` },
        { i: 'fa-palette',       t: `Modern CSS: ${mod.css_custom_properties || mod.custom_fonts || mod.css_framework ? 'Yes' : 'No'}` },
        { i: 'fa-cookie',        t: `Cookie notice: ${c.cookie_notice ? 'Present' : 'Missing'}` },
      ].map(row).join('');
    }
    default: return '';
  }
}

function row({ i, t }) {
  return `<div class="cat-detail"><i class="fas ${i}"></i><span>${t}</span></div>`;
}

// ── PRIORITY FIXES ────────────────────────────────────────
function renderFixes(fixes) {
  document.getElementById('fixCount').textContent = fixes.length;
  const list = document.getElementById('fixesList');

  if (!fixes.length) {
    list.innerHTML = '<div class="fix-item fade-up"><div class="fix-body" style="color:var(--green)"><i class="fas fa-check-circle"></i> No critical issues found. Great work!</div></div>';
    return;
  }

  list.innerHTML = fixes.map((f, i) => `
    <div class="fix-item fade-up" style="animation-delay:${i * 40}ms">
      <span class="fix-sev ${f.severity === 'critical' ? 'sev-critical' : 'sev-major'}">${f.severity}</span>
      <div class="fix-body">
        <div class="fix-cat">${CAT_CONFIG[f.category]?.label || f.category}</div>
        <div class="fix-text">${f.issue}</div>
      </div>
    </div>
  `).join('');
}

// ── RECOMMENDATIONS + FILTER ──────────────────────────────
function filterRecs(prio) {
  const filtered = prio === 'all' ? allInsights : allInsights.filter(i => i.priority === prio);
  renderRecs(filtered);
  setTimeout(initScrollAnimations, 50);
}

function renderRecs(insights) {
  const grid = document.getElementById('recsGrid');

  if (!insights.length) {
    grid.innerHTML = '<div class="rec-card fade-up"><div class="rec-body" style="color:var(--green)">No issues in this priority level.</div></div>';
    return;
  }

  grid.innerHTML = insights.map((ins, i) => `
    <div class="rec-card fade-up" style="animation-delay:${i * 40}ms">
      <div class="rec-prio-dot prio-${ins.priority}"></div>
      <div class="rec-body">
        <div class="rec-cat">${CAT_CONFIG[ins.category]?.label || ins.category} · ${ins.priority} priority</div>
        <div class="rec-text">${ins.insight}</div>
      </div>
    </div>
  `).join('');
}

// ── UTILITIES ─────────────────────────────────────────────
function scoreColor(sc) {
  if (sc >= 80) return '#10b981';
  if (sc >= 60) return '#f59e0b';
  if (sc >= 40) return '#f97316';
  return '#ef4444';
}

function scoreLabel(sc) {
  if (sc >= 90) return 'Excellent — well optimized';
  if (sc >= 80) return 'Very good — minor tweaks needed';
  if (sc >= 70) return 'Good — some improvements possible';
  if (sc >= 50) return 'Fair — significant issues found';
  return 'Poor — requires urgent attention';
}

function animateNumber(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const dur = 900;
  const startTime = performance.now();
  const tick = (now) => {
    const p = Math.min((now - startTime) / dur, 1);
    el.textContent = Math.round(target * easeOut(p));
    if (p < 1) requestAnimationFrame(tick);
  };
  requestAnimationFrame(tick);
}
function easeOut(t) { return 1 - Math.pow(1 - t, 3); }

function shareWhatsApp() {
  if (!window.currentData) return;
  const url   = window.currentData.url;
  const score = window.currentData.overall_score;
  const grade = window.currentData.grade;
  const msg = `🔍 *Website Scan Results*\n\n📊 Score: *${score}/100* (Grade: *${grade}*)\n🌐 ${url}\n\nScanned free by Bejaa Digital 👉 https://bejaadigital.com`;
  window.open(`https://wa.me/?text=${encodeURIComponent(msg)}`, '_blank');
}

function resetToHero() {
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('featuresSection').style.display = 'block';
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function downloadJSON() {
  if (!window.currentData) return;
  const clean = Object.fromEntries(
    Object.entries(window.currentData).filter(([k]) => !['html_content', 'response_headers'].includes(k))
  );
  const blob = new Blob([JSON.stringify(clean, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `scan-${new URL(window.currentData.url).hostname}-${Date.now()}.json`;
  a.click();
}

function showToast(msg) {
  const t = document.createElement('div');
  t.className = 'toast';
  t.innerHTML = `
    <i class="fas fa-exclamation-circle toast-err"></i>
    <div class="toast-body">
      <div class="toast-title">Scan Error</div>
      <div class="toast-msg">${msg}</div>
    </div>
    <button class="toast-close" onclick="this.closest('.toast').remove()"><i class="fas fa-times"></i></button>
  `;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 6000);
}
