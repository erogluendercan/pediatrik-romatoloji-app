import streamlit as st
import datetime
from Bio import Entrez

# Sayfa Tasarımı ve Başlık
st.set_page_config(page_title="Pediatri Romatoloji Literatür", page_icon="🩺", layout="centered")

# Sitenin arka planını sarı yapan, yazıları siyaha sabitleyen ve hafif kemik silüeti ekleyen gelişmiş CSS
st.markdown(
    """
    <style>
    /* Ana arka planı yumuşak bir sarı yapar ve hafif kemik deseni ekler */
    .stApp {
        background-color: #FEF9E7;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'><path d='M35,15 C35,12 30,12 30,15 C30,18 35,18 35,15 M45,15 C45,12 50,12 50,15 C50,18 45,18 45,15 M32,16 L48,16 C48,22 32,22 32,16 M38,15 L42,15 L42,35 L38,35 Z' fill='%23F1C40F' fill-opacity='0.15' transform='rotate(45 40 25)'/></svg>");
        background-repeat: repeat;
    }
    
    /* Üst taraftaki tüm yazıların, butonların ve radyo butonlarının her koşulda koyu renk kalmasını sağlar */
    h1, h2, h3, p, span, label, div, .stMarkdown, .stRadio {
        color: #2C3E50 !important;
    }
    
    /* Mobil uyumlu, beyaz gölgeli makale kutuları */
    .makale-kart {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 6px solid #F1C40F;
        word-wrap: break-word;
    }
    
    /* Makaleye Git link butonunun modern tasarımı */
    .makale-link {
        display: inline-block;
        background-color: #3498db;
        color: white !important;
        padding: 8px 16px;
        font-size: 0.85em;
        font-weight: bold;
        text-decoration: none;
        border-radius: 6px;
        margin-top: 10px;
        transition: background-color 0.2s ease;
    }
    .makale-link:hover {
        background-color: #2980b9;
    }
    
    @media (max-width: 640px) {
        .makale-kart h3 { font-size: 1.1em !important; }
        .makale-kart p { font-size: 0.85em !important; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 1. ADIM: En Başta Dil Seçimi
dil = st.radio("Language / Dil Seçimi", ["Türkçe", "English"], horizontal=True)

# Dil seçimine göre dinamik metinlerin ayarlanması
if dil == "Türkçe":
    baslik = "🩺 Günlük Literatür Takibi"
    acıklama = "PubMed'e dün yüklenen **Pediatrik Romatoloji** makalelerini tek tuşla listeleyin."
    buton_metni = "Dünün Hasılatını Getir"
    yukleniyor_metni = "PubMed taranıyor, lütfen bekleyin..."
    bulunamadi_metni = "Dün yeni makale yüklenmemiş."
    bulundu_metni = "Dün yüklenen {} yeni makale bulundu!"
    dergi_etiket = "Dergi"
    merkez_etiket = "Merkez"
    yayin_tarihi_etiket = "Yayınlanma Tarihi"
    pubmed_tarihi_etiket = "PubMed Giriş Tarihi"
    git_butonu_metni = "Makaleye Git ↗"
    yontem_etiket = "Yöntem"
    sonuc_etiket = "Sonuç"
    ozet_etiket = "Özet"
else:
    baslik = "🩺 Daily Literature Tracking"
    acıklama = "List **Pediatric Rheumatology** papers uploaded to PubMed yesterday with a single click."
    buton_metni = "Bring Me Yesterday's Goods ↗"
    yukleniyor_metni = "Scanning PubMed, please wait..."
    bulunamadi_metni = "No new papers uploaded yesterday."
    bulundu_metni = "{} new papers found from yesterday!"
    dergi_etiket = "Journal"
    merkez_etiket = "Center"
    yayin_tarihi_etiket = "Date of Publication"
    pubmed_tarihi_etiket = "PubMed Entry Date"
    git_butonu_metni = "Go to Article ↗"
    yontem_etiket = "Methods"
    sonuc_etiket = "Conclusions"
    ozet_etiket = "Abstract"

# Arayüz Başlıkları
st.title(baslik)
st.write(acıklama)

Entrez.email = "doktor@email.com"

# Tarama Butonu
if st.button(buton_metni, type="primary"):
    with st.spinner(yukleniyor_metni):
        bugun = datetime.date.today()
        dun = bugun - datetime.timedelta(days=1)
        dun_str = dun.strftime("%Y/%m/%d")
        tarih_sorgusu = f'("{dun_str}"[Entrez Date] : "{dun_str}"[Entrez Date])'
        
        terimler = [
            '"pediatric rheumatology"', '"behçet"', '"juvenile idiopathic arthritis"',
            '"familial mediterranean fever"', '"systemic lupus erythematosus"',
            '"kawasaki disease"', '"juvenile dermatomyositis"', '"pediatric vasculitis"',
            '"systemic sclerosis"', '"localized scleroderma"', '"IgA vasculitis"'
        ]
        
        arama_terimi = f'({" OR ".join(terimler)}) AND {tarih_sorgusu}'
        
        handle = Entrez.esearch(db="pubmed", term=arama_terimi, retmax=50)
        id_listesi = Entrez.read(handle)["IdList"]
        handle.close()
        
        if not id_listesi:
            st.info(bulunamadi_metni)
        else:
            st.success(bulundu_metni.format(len(id_listesi)))
            
            id_string = ",".join(id_listesi)
            handle = Entrez.efetch(db="pubmed", id=id_string, retmode="xml")
            makale_detaylari = Entrez.read(handle)
            handle.close()
            
            for i, makale in enumerate(makale_detaylari['PubmedArticle']):
                try:
                    medline_citation = makale['MedlineCitation']
                    article = medline_citation['Article']
                    baslik_metni = article['ArticleTitle']
                    dergi_metni = article['Journal']['Title']
                    pmid = medline_citation['PMID']
                    
                    # Tarih bilgilerini güvenli bir şekilde çekme
                    yayin_tarihi = "Bilinmiyor / Unknown"
                    if 'JournalIssue' in article['Journal'] and 'PubDate' in article['Journal']['JournalIssue']:
                        pub_date = article['Journal']['JournalIssue']['PubDate']
                        if 'Year' in pub_date:
                            yayin_tarihi = pub_date['Year']
                            if 'Month' in pub_date: yayin_tarihi += f" {pub_date['Month']}"
                            if 'Day' in pub_date: yayin_tarihi += f" {pub_date['Day']}"
                    
                    pubmed_giris_tarihi = dun.strftime('%d.%m.%Y') # Sorguladığımız günün kendisi
                    
                    # Merkez bilgisi
                    merkez_metni = "Merkez bilgisine ulaşılamadı / Center info not found."
                    author_list = article.get('AuthorList', [])
                    if author_list:
                        first_author = author_list[0]
                        affiliation_info = first_author.get('AffiliationInfo', [])
                        if affiliation_info:
                            merkez_metni = affiliation_info[0]['Affiliation']
                    
                    # Abstract ayrıştırma
                    yontem, sonuc, duz_abstract = [], [], []
                    if 'Abstract' in article:
                        for elem in article['Abstract']['AbstractText']:
                            label = getattr(elem, 'attributes', {}).get('Label', '').upper()
                            text = str(elem)
                            if not label:
                                duz_abstract.append(text)
                            elif 'METHOD' in label or 'DESIGN' in label:
                                yontem.append(text)
                            elif 'CONCLUSION' in label:
                                sonuc.append(text)
                    
                    pubmed_linki = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    
                    # HTML Kart Tasarımı (Tarihler alt alta eklendi)
                    kart_icerigi = f"""
                    <div class="makale-kart">
                        <h3 style="margin-top: 0; font-size: 1.25em;">{i+1}. {baslik_metni}</h3>
                        <p style="margin: 3px 0; font-size: 0.9em;"><b>{dergi_etiket}:</b> {dergi_metni}</p>
                        <p style="margin: 3px 0; font-size: 0.9em;"><b>{yayin_tarihi_etiket}:</b> {yayin_tarihi}</p>
                        <p style="margin: 3px 0; font-size: 0.9em;"><b>{pubmed_tarihi_etiket}:</b> {pubmed_giris_tarihi}</p>
                        <p style="margin: 3px 0; font-size: 0.9em;"><b>{merkez_etiket}:</b> {merkez_metni}</p>
                        <hr style="border: 0; border-top: 1px solid #ECF0F1; margin: 12px 0;">
                    """
                    
                    if yontem:
                        kart_icerigi += f"<p style='margin: 10px 0;'><b>[{yontem_etiket}]:</b> {' '.join(yontem)}</p>"
                    if sonuc:
                        kart_icerigi += f"<p style='margin: 10px 0; color: #27AE60;'><b>[{sonuc_etiket}]:</b> {' '.join(sonuc)}</p>"
                    if not yontem and not sonuc and duz_abstract:
                        kart_icerigi += f"<p style='margin: 10px 0;'><b>[{ozet_etiket}]:</b> {' '.join(duz_abstract)}</p>"
                    
                    kart_icerigi += f"""
                        <div style="text-align: right; margin-top: 15px;">
                            <a href="{pubmed_linki}" target="_blank" class="makale-link">{git_butonu_metni}</a>
                        </div>
                    </div>
                    """
                    
                    st.markdown(kart_icerigi, unsafe_allow_html=True)
                except:
                    continue
