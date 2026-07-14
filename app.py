import streamlit as st
import datetime
from Bio import Entrez

# Sayfa Tasarımı ve Başlık
st.set_page_config(page_title="Pediatri Romatoloji Literatür", page_icon="🩺", layout="centered")

# Sitenin arka planını sarı yapan ve mobil uyumlu beyaz kartlar oluşturan gelişmiş CSS
st.markdown(
    """
    <style>
    /* Ana arka planı yumuşak bir sarı yapar */
    .stApp {
        background-color: #FEF9E7;
    }
    
    /* Mobil uyumlu, beyaz gölgeli makale kutuları */
    .makale-kart {
        background-color: #FFFFFF;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 6px solid #F1C40F; /* Sol kenardaki sarı çizgi */
        word-wrap: break-word; /* Mobilde uzun kelimelerin taşmasını önler */
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
    
    /* Mobil ekranlar için yazı boyutu optimizasyonu */
    @media (max-width: 640px) {
        .makale-kart h3 {
            font-size: 1.1em !important;
        }
        .makale-kart p {
            font-size: 0.85em !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🩺 Günlük Literatür Takibi")
st.write("PubMed'e dün yüklenen **Pediatrik Romatoloji** makalelerini tek tuşla listeleyin.")

Entrez.email = "doktor@email.com"

# Tarama Butonu
if st.button("Dünün Hasılatını Getir", type="primary"):
    with st.spinner("PubMed taranıyor, lütfen bekleyin..."):
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
        
        # PubMed Sorgusu
        handle = Entrez.esearch(db="pubmed", term=arama_terimi, retmax=50)
        id_listesi = Entrez.read(handle)["IdList"]
        handle.close()
        
        if not id_listesi:
            st.info(f"Dün ({dun.strftime('%d.%m.%Y')}) yeni makale yüklenmemiş.")
        else:
            st.success(f"Dün yüklenen {len(id_listesi)} yeni makale bulundu!")
            
            id_string = ",".join(id_listesi)
            handle = Entrez.efetch(db="pubmed", id=id_string, retmode="xml")
            makale_detaylari = Entrez.read(handle)
            handle.close()
            
            for i, makale in enumerate(makale_detaylari['PubmedArticle']):
                try:
                    medline_citation = makale['MedlineCitation']
                    article = medline_citation['Article']
                    baslik = article['ArticleTitle']
                    dergi = article['Journal']['Title']
                    pmid = medline_citation['PMID'] # PubMed ID (Link oluşturmak için)
                    
                    # Merkez bilgisi
                    merkez = "Merkez bilgisine ulaşılamadı."
                    author_list = article.get('AuthorList', [])
                    if author_list:
                        first_author = author_list[0]
                        affiliation_info = first_author.get('AffiliationInfo', [])
                        if affiliation_info:
                            merkez = affiliation_info[0]['Affiliation']
                    
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
                    
                    # PubMed Abstract linki oluşturma
                    pubmed_linki = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    
                    # HTML ile mobil uyumlu beyaz kart tasarımı
                    kart_icerigi = f"""
                    <div class="makale-kart">
                        <h3 style="margin-top: 0; color: #2C3E50; font-size: 1.25em;">{i+1}. {baslik}</h3>
                        <p style="margin: 5px 0; color: #7F8C8D; font-size: 0.9em;"><b>Dergi:</b> {dergi}</p>
                        <p style="margin: 5px 0; color: #7F8C8D; font-size: 0.9em;"><b>Merkez:</b> {merkez}</p>
                        <hr style="border: 0; border-top: 1px solid #ECF0F1; margin: 12px 0;">
                    """
                    
                    if yontem:
                        kart_icerigi += f"<p style='margin: 10px 0; color: #34495E;'><b>[Yöntem]:</b> {' '.join(yontem)}</p>"
                    if sonuc:
                        kart_icerigi += f"<p style='margin: 10px 0; color: #27AE60;'><b>[Sonuç]:</b> {' '.join(sonuc)}</p>"
                    if not yontem and not sonuc and duz_abstract:
                        kart_icerigi += f"<p style='margin: 10px 0; color: #34495E;'><b>[Özet]:</b> {' '.join(duz_abstract)}</p>"
                    
                    # "Makaleye Git" butonu kartın altına eklendi
                    kart_icerigi += f"""
                        <div style="text-align: right; margin-top: 15px;">
                            <a href="{pubmed_linki}" target="_blank" class="makale-link">Makaleye Git ↗</a>
                        </div>
                    </div>
                    """
                    
                    st.markdown(kart_icerigi, unsafe_allow_html=True)
                except:
                    continue
