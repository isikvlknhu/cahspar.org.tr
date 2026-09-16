document.addEventListener('DOMContentLoaded', async () => {
  const container = document.getElementById('rss-feed-grid');
  if (!container) return;

  try {
    const response = await fetch('assets/rss-feed.json', { cache: 'no-store' });

    if (!response.ok) {
      throw new Error('RSS feed could not be loaded');
    }

    const data = await response.json();
    const allItems = Array.isArray(data.items) ? data.items : [];

    // Son 30 gün
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    // İlgisiz içerikleri dışarıda bırakacak kelimeler
    const excludedKeywords = [
      'ziyaret',
      'heyet',
      'bakan',
      'toplantı',
      'kabul',
      'tebrik',
      'taziye',
      'sertifikalandırma',
      'sertifika',
      'eğitim başvurusu',
      'başvuru',
      'personeli giriş sınavı',
      'giriş sınavı',
      'sınav sonuçları',
      'ilaç listesi',
      'bedeli ödenecek ilaçlar',
      'duyuru',
      'etkinlik',
      'programı',
      'programına',
      'açılış',
      'ziyaretlerde bulundu'
    ];

    // Çalışma hayatı ve sosyal politika açısından
    // öncelikli içerik başlıkları
    const relevantKeywords = [
      'istihdam',
      'işgücü',
      'iş gücü',
      'işsizlik',
      'ücret',
      'maaş',
      'gelir',
      'yoksulluk',
      'sosyal politika',
      'sosyal koruma',
      'sosyal güvenlik',
      'emeklilik',
      'emekli',
      'çalışma hayatı',
      'çalışma yaşamı',
      'çalışma koşulları',
      'çalışan',
      'işçi',
      'işveren',
      'işgücü piyasası',
      'iş gücü piyasası',
      'iş piyasası',
      'iş ilanı',
      'işsizlik oranı',
      'istihdam oranı',
      'işgücüne katılım',
      'iş gücüne katılım',
      'kadın istihdamı',
      'genç istihdamı',
      'genç işsizliği',
      'ne eğitimde ne istihdamda',
      'neet',
      'toplumsal cinsiyet',
      'kadın',
      'eşitsizlik',
      'göç',
      'mülteci',
      'uyum',
      'sosyal hizmet',
      'sosyal harcama',
      'refah',
      'iş sağlığı',
      'iş güvenliği',
      'iş kazası',
      'meslek hastalığı',
      'asgari ücret',
      'sendika',
      'sendikal',
      'toplu sözleşme',
      'sosyal diyalog',
      'çalışma süresi',
      'uzaktan çalışma',
      'esnek çalışma',
      'dijital dönüşüm',
      'yapay zekâ',
      'yapay zeka',
      'geleceğin işleri',
      'yeşil iş',
      'beceri',
      'verimlilik',
      'labour market',
      'labor market',
      'employment',
      'unemployment',
      'workforce',
      'wages',
      'earnings',
      'social protection',
      'social security',
      'poverty',
      'inequality',
      'labour force',
      'labor force',
      'working conditions',
      'gender',
      'migration',
      'social policy',
      'job vacancy',
      'job vacancies'
    ];

    const items = allItems
      .filter(item => {
        if (!item.published) return false;

        const publishedDate = new Date(item.published);

        if (isNaN(publishedDate.getTime())) return false;

        // Son 30 gün kontrolü
        if (publishedDate < thirtyDaysAgo) return false;

        // Başlık + özet + kaynak birlikte değerlendiriliyor
        const text = [
          item.title || '',
          item.summary || '',
          item.source || ''
        ]
          .join(' ')
          .toLocaleLowerCase('tr-TR');

        // Önce açıkça ilgisiz içerikleri çıkar
        const isExcluded = excludedKeywords.some(keyword =>
          text.includes(keyword.toLocaleLowerCase('tr-TR'))
        );

        if (isExcluded) return false;

        // Sonra çalışma hayatı / sosyal politika ile
        // ilişkili içerikleri seç
        const isRelevant = relevantKeywords.some(keyword =>
          text.includes(keyword.toLocaleLowerCase('tr-TR'))
        );

        return isRelevant;
      })
      // En yeni içerik en üstte
      .sort((a, b) => {
        return new Date(b.published) - new Date(a.published);
      });

    if (!items.length) {
      container.innerHTML =
        '<p class="rss-empty">Son 30 günde yayımlanan uygun içerik bulunamadı.</p>';
      return;
    }

    container.innerHTML = items.map((item) => {
      const published = item.published
        ? new Date(item.published).toLocaleDateString('tr-TR', {
            day: 'numeric',
            month: 'short',
            year: 'numeric'
          })
        : 'Yakın tarih';

      const source = (item.source || 'Kaynak').trim();
      const category = (item.category || '').trim();
      const title = (item.title || 'Güncel yayın').trim();
      const link = item.link || '#';

      return `
        <a
          class="rss-item"
          href="${link}"
          target="_blank"
          rel="noopener noreferrer"
        >
          <span class="rss-source">${source}</span>

          <strong>${title}</strong>

          <span class="rss-meta">
            ${category ? category + ' · ' : ''}${published}
          </span>
        </a>
      `;
    }).join('');

  } catch (error) {
    console.error('RSS loader failed:', error);

    container.innerHTML =
      '<p class="rss-empty">Güncel içerik yüklenemedi.</p>';
  }
});
