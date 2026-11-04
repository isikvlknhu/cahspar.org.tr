# Türkiye Working Life Pilotu — İlk Gerçek Veri Sürümü

Sürüm 0.1 · Veri kontrolü: 4 Kasım 2026

İlk gerçek veriye dayalı boyut **Working Life / Çalışma Hayatı** olarak kuruldu. Veriler [TÜİK'in 57996 sayılı yıllık bülteninden](https://veriportali.tuik.gov.tr/tr/press/57996) alındı. Gözlem yılı 2025, yayım tarihi 25 Mart 2026. Resmî portal ve metaveri sekmesi doğrudan tarayıcıda incelendi.

| Gösterge | 2025 | Yayımlanan yıllık değişim | Rol |
|---|---:|---:|---|
| İstihdam oranı | %49,0 | −0,5 yüzde puan | Temel gözlem |
| İşsizlik oranı | %8,3 | −0,4 yüzde puan | Temel gözlem |
| Atıl işgücü oranı | %29,7 | +3,0 yüzde puan | Temel gözlem |
| İşgücüne katılma oranı | %53,5 | −0,7 yüzde puan | Bağlam |
| Genç işsizlik oranı | %15,3 | −1,0 yüzde puan | Bağlam |

Genç işsizliği 15–24, diğer göstergeler 15+ yaş kapsamındadır. Göstergelerin paydaları farklıdır. Veriler örnekleme dayalı resmî tahminlerdir; tam sayım değildir.

## Veri ve yöntem kararları

- Tek yıllık bültenin yayımlandığı sürüm kaydedildi; sonraki revizyonların tarandığı iddia edilmiyor.
- Değişimler bültenden doğrudan alındı. Yuvarlanmış kişi sayılarından oran hesaplanmadı; 2024 değerleri geriye doğru türetilmedi.
- İşsizlik ile atıl işgücü birbirini kapsadığından göstergeler ortalanmadı. Toplam puan, sıralama ve ağırlık üretilmedi.
- İşgücüne katılım ile genç işsizliği bağlam olarak gösterildi; diğer boyutlarda ikinci kez puanlanacak göstergeler olarak kabul edilmedi.
- Ücret, aşırı çalışma süresi, kayıt dışılık ve iş güvenliği henüz toplanmadı. Bu ilk sürüm bütün çalışma hayatı kalitesini temsil etmiyor.
- Güven aralığı veya anlamlılık testi üretilmedi. Düşüş veya artışların istatistiksel anlamlılığına ilişkin iddia yok.

İşsizlikteki düşüşü tek başına iyileşme saymıyoruz: aynı dönemde istihdam ve katılım gerilerken atıl işgücü yükseliyor. Bu, göstergeleri birlikte okuma gerekçesidir; nedensellik analizi değildir.

## İzlenebilirlik

`data/working-life/turkiye-2025.json` ana kayıttır. Kaynak başlığı, bülten kimliği, gözlem yılı, yayım/erişim tarihleri, yaş grubu, ölçü birimi ve tanımlar tutulur. WL kimlikleri ÇAHSPAR'ın iç kimlikleridir; resmî TÜİK seri kodu değildir. Seri kodu doğrulanmadığından boş bırakıldı. CSV, JSON ve sayfa paneli aynı kayıttan üretilir.

Uluslararası temsili demo kapalı başlar ve gerçek gözlemleri içermez. Sosyal ekonomi çalışması ayrı bir araştırma tasarımı olarak korunur. Bu sürüm, dernek üyelerinin inceleme ve görüşlerine açılan pilot yayınıdır. Görüşler Index sayfasındaki e-posta bağlantısıyla info@cahspar.org.tr adresine iletilebilir.

Sonraki aşama: özgün yıllık tablolar ve seri kodları; geçmiş dönem/revizyon uyumu; çalışma süresi, kayıt dışılık, ücret ve güvenlik göstergelerinin veri denetimi; ardından puanlama yönteminin kararlaştırılması.
