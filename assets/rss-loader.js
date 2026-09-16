document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('rss-feed-grid');
  if (!container) return;

  try {
    const response = await fetch('assets/rss-feed.json', { cache: 'no-store' });
    if (!response.ok) throw new Error('RSS feed could not be loaded');

    const data = await response.json();
   const allItems = Array.isArray(data.items) ? data.items : [];

   const thirtyDaysAgo = new Date();
   thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

   const items = allItems
   .filter(item => {
    if (!item.published) return false;
    const publishedDate = new Date(item.published);
    return publishedDate >= thirtyDaysAgo;
  })
  .sort((a, b) => {
    return new Date(b.published) - new Date(a.published);
  });

    if (!items.length) {
      container.innerHTML = '<p class="rss-empty">Güncel içerik bulunamadı.</p>';
      return;
    }

    container.innerHTML = items.map((item) => {
      const published = item.published ? new Date(item.published).toLocaleDateString('tr-TR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      }) : 'Yakın tarih';

      const source = (item.source || 'Kaynak').trim();
      const title = (item.title || 'Güncel gelişme').trim();
      const summary = (item.summary || '').trim();
      const link = item.link || '#';

      return `
        <a class="rss-item" href="${link}" target="_blank" rel="noopener noreferrer">
          <span class="rss-source">${source}</span>
          <strong>${title}</strong>
          <span class="rss-meta">${published}${summary ? ' · ' + summary : ''}</span>
        </a>
      `;
    }).join('');
  } catch (error) {
    console.error('RSS loader failed:', error);
    container.innerHTML = '<p class="rss-empty">Güncel içerik yüklenemedi.</p>';
  }
});
