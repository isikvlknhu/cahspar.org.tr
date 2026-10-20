document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('rss-feed-grid');
  if (!container) return;

  const escapeHtml = (value) => String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');

  try {
    const response = await fetch('assets/rss-feed.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('RSS feed could not be loaded');

    const data = await response.json();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    // Python has already collected, source-checked and topic-filtered the
    // feed. The browser only applies the homepage display window and sorting.
    const items = (Array.isArray(data.items) ? data.items : [])
      .filter((item) => {
        const date = new Date(item.published);
        return item.title && item.link && !Number.isNaN(date.getTime()) && date >= thirtyDaysAgo;
      })
      .sort((a, b) => new Date(b.published) - new Date(a.published));

    if (!items.length) {
      container.innerHTML = '<p class="rss-empty">No relevant items have been published in the past 30 days.</p>';
      return;
    }

    container.innerHTML = items.map((item) => {
      const published = new Date(item.published).toLocaleDateString('en-GB', {
        day: 'numeric', month: 'short', year: 'numeric'
      });
      const source = escapeHtml((item.source || 'Source').trim());
      const category = escapeHtml((item.category || '').trim());
      const title = escapeHtml((item.title || 'Latest publication').trim());
      const link = escapeHtml(item.link || '#');

      return `
        <a class="rss-item" href="${link}" target="_blank" rel="noopener noreferrer">
          <span class="rss-source">${source}</span>
          <strong>${title}</strong>
          <span class="rss-meta">${category ? `${category} · ` : ''}${published}</span>
        </a>
      `;
    }).join('');
  } catch (error) {
    console.error('RSS loader failed:', error);
    container.innerHTML = '<p class="rss-empty">The latest updates could not be loaded.</p>';
  }
});
