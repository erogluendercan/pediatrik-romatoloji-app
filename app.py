import streamlit as st
import datetime
from Bio import Entrez
from deep_translator import GoogleTranslator
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Sayfa Tasarımı ve Başlık
st.set_page_config(page_title="Pediatri Romatoloji Literatür", page_icon="🩺", layout="centered")

# Sabit Google Sheets Linkiniz
TABLO_URL = "https://docs.google.com/spreadsheets/d/1PPJkcODWesAna4BlP7qFl59FfThZ5Kg-sWba5S-QDdk/edit?usp=sharing"

# Sitenin arka planını sarı yapan, yazıları siyaha sabitleyen ve mobil uyumluluk sağlayan CSS
st.markdown(
    """
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    
    <style>
    .stApp {
        background-color: #FEF9E7;
        background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80' viewBox='0 0 80 80'><path d='M35,15 C35,12 30,12 30,15 C30,18 35,18 35,15 M45,15 C45,12 50,12 50,15 C50,18 45,18 45,15 M32,16 L48,16 C48,22 32,22 32,16 M38,15 L42,15 L42,35 L38,35 Z' fill='%23F1C40F' fill-opacity='0.15' transform='rotate(45 40 25)'/></svg>");
        background-repeat: repeat;
    }
    h1, h2, h3, p, span, label, div, .stMarkdown, .stRadio {
        color: #2C3E50 !important;
    }
    .makale-kart {
        background-color: #FFFFFF;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 10px;
        border-left: 6px solid #F1C40F;
        word-wrap: break-word;
    }
    
    /* YÜKSEK KONTRASTLI VE ZIT RENKLİ BUTONLAR */
    .ozel-buton {
        display: inline-block;
        background-color: #1A252F !important;
        color: #FFFFFF !important;
        padding: 10px 20px;
        font-weight: bold !important;
        text-align: center;
        text-decoration: none;
        border-radius: 8px;
        border: 2px solid #F1C40F;
        margin-top: 5px;
        width: 100%;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
        transition: background-color 0.2s ease;
    }
    .ozel-buton:hover {
        background-color: #2C3E50 !important;
        color: #F1C40F !important;
    }
    
    /* Yan paneldeki Excel butonu için özel stil */
    .excel-buton {
        display: block;
        background-color: #27AE60 !important;
        color: #FFFFFF !important;
        padding: 12px;
        text-align: center;
        font-weight: bold !important;
        text-decoration: none;
        border-radius: 8px;
        border: 2px solid #2ECC71;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.15);
    }
    .excel-buton:hover {
        background-color: #219653 !important;
        color: #FFFFFF !important;
    }
    
    @media (max-width: 640px) {
        .makale-kart h3 { font-size: 1.1em !important; }
        .makale-kart p { font-size: 0.85em !important; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- GOOGLE SHEETS BAĞLANTISI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def favorileri_yukle():
    try:
        return conn.read(spreadsheet=TABLO_URL, ttl="0d")
    except:
        return pd.DataFrame(columns=["index", "pmid", "baslik", "dergi", "link", "ekleyen"])

def favori_ekle_sheets(index, pmid, baslik, dergi, link, ekleyen_kisi):
    df = favorileri_yukle()
    if str(pmid) not in df['pmid'].astype(str).values:
        yeni_satir = pd.DataFrame([{
            "index": index, 
            "pmid": str(pmid), 
            "baslik": baslik, 
            "dergi": dergi, 
            "link": link,
            "ekleyen": ekleyen_kisi if ekleyen_kisi else "Anonim/Anonymous"
        }])
        df = pd.concat([df, yeni_satir], ignore_index=True)
        conn.update(spreadsheet=TABLO_URL, data=df)

def favori_cikar_sheets(pmid):
    df = favorileri_yukle()
    df['pmid'] = df['pmid'].astype(str)
    df = df[df['pmid'] != str(pmid)]
    conn.update(spreadsheet=TABLO_URL, data=df)

# Yardımcı Çeviri Fonksiyonu
def ceviri_yap(metin, hedef_dil):
    if not metin or hedef_dil == "en":
        return metin
    try:
        return GoogleTranslator(source='auto', target='tr').translate(metin)
    except:
        return metin

# 1. ADIM: En Başta Dil Seçimi
dil = st.radio("Language / Dil Seçimi (Makale özetleri dahil çevrilir)", ["Türkçe", "English"], horizontal=True)

if dil == "Türkçe":
    hedef_dil_kodu = "tr"
    baslik = "🩺 Günlük Literatür Takibi"
    acıklama = "PubMed'e dün yüklenen **Pediatrik Romatoloji** makalelerini otomatik Türkçe çeviriyle listeleyin."
    buton_metni = "Dünün Hasılatını Getir (Çeviri aktif)"
    yukleniyor_metni = "PubMed taranıyor ve makaleler Türkçeye çevriliyor, lütfen bekleyin..."
    bulunamadi_metni = "Dün yeni makale yüklenmemiş."
    bulundu_metni = "Dün yüklenen {} yeni makale bulundu! Çeviriler hazırlanıyor..."
    dergi_etiket = "Dergi"
    merkez_etiket = "Merkez"
    yayin_tarihi_etiket = "Yayınlanma Tarihi"
    pubmed_tarihi_etiket = "PubMed Giriş Tarihi"
    git_butonu_metni = "Orijinal Makaleye Git (PubMed) ↗"
    yontem_etiket = "Yöntem"
    sonuc_etiket = "Sonuç"
    ozet_etiket = "Özet"
    abstract_yok_metni = "Bu yayının özet (abstract) verisi bulunmuyor."
    favori_ekle_etiket = "Drive'a Kaydet ⭐"
    favori_baslik = "📁 Kayıtlılara Eriş & Arşiv"
    excel_buton_metni = "Ortak Arşivi Excel Olarak Aç 📊"
    favori_bos_uyari = "Google Drive'da kayıtlı favori bulunamadı."
    kimsin_sorusu = "Sen Kimsin? (İsminizi yazın)"
    kimsin_placeholder = "Örn: Dr. Ahmet"
    ekleyen_etiket = "Ekleyen"
else:
    hedef_dil_kodu = "en"
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
    abstract_yok_metni = "No abstract available for this article."
    favori_ekle_etiket = "Save to Drive ⭐"
    favori_baslik = "📁 Saved Articles & Archive"
    excel_buton_metni = "Open Joint Archive in Excel 📊"
    favori_bos_uyari = "No favorites found on Google Drive."
    kimsin_sorusu = "Who are you? (Enter your name)"
    kimsin_placeholder = "e.g., Dr. John"
    ekleyen_etiket = "Added by"

# Arayüz Başlıkları
st.title(baslik)
st.write(acıklama)

# --- SEN KİMSİN? İSİM GİRİŞ ALANI ---
kullanici_adi = st.text_input(kimsin_sorusu, placeholder=kimsin_placeholder)

# --- Geliştirilmiş Sol Panel (Kayıtlılara Eriş & Excel Linki) ---
with st.sidebar:
    st.header(favori_baslik)
    
    # Doğrudan sizin verdiğiniz Google Sheets linkine yönlendirme
    excel_html = f'<a href="{TABLO_URL}" target="_blank" class="excel-buton">{excel_buton_metni}</a>'
    st.markdown(excel_html, unsafe_allow_html=True)
    
    st.write("---")
    
    favori_df = favorileri_yukle()
    if favori_df.empty:
        st.info(favori_bos_uyari)
    else:
        for idx, row in favori_df.iterrows():
            ekleyen_bilgisi = row.get('ekleyen', 'Bilinmiyor')
            st.markdown(f"**{row['index']}. {row['baslik']}**")
            st.write(f"_{row['dergi']}_")
            st.write(f"*{ekleyen_etiket}: {ekleyen_bilgisi}*")
            st.markdown(f"[Link]({row['link']})")
            if st.button(f"Sürücüden Sil / Delete", key=f"del_{row['pmid']}"):
                favori_cikar_sheets(row['pmid'])
                st.rerun()
            st.divider()

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
            
            st.session_state.son_aramalar = makale_detaylari['PubmedArticle']

# Eğer hafızada taranmış makaleler varsa ekrana bas
if 'son_aramalar' in st.session_state:
    favori_df = favorileri_yukle()
    kayitli_pmidler = favori_df['pmid'].astype(str).values if not favori_df.empty else []
    
    for i, makale in enumerate(st.session_state.son_aramalar):
        try:
            medline_citation = makale['MedlineCitation']
            article = medline_citation['Article']
            pmid = str(medline_citation['PMID'])
            
            baslik_metni = ceviri_yap(article['ArticleTitle'], hedef_dil_kodu)
            dergi_metni = article['Journal']['Title']
            
            # Gelişmiş Tarih Çekme Algoritması
            yayin_tarihi = "Bilinmiyor / Unknown"
            if 'JournalIssue' in article['Journal'] and 'PubDate' in article['Journal']['JournalIssue']:
                pub_date = article['Journal']['JournalIssue']['PubDate']
                if 'Year' in pub_date:
                    yayin_tarihi = pub_date['Year']
                    if 'Month' in pub_date: yayin_tarihi += f" {pub_date['Month']}"
                    if 'Day' in pub_date: yayin_tarihi += f" {pub_date['Day']}"
            
            if yayin_tarihi == "Bilinmiyor / Unknown" or len(yayin_tarihi) <= 4:
                article_date = article.get('ArticleDate', [])
                if article_date:
                    e_date = article_date[0]
                    if 'Year' in e_date and 'Month' in e_date and 'Day' in e_date:
                        yayin_tarihi = f"{e_date['Day']}.{e_date['Month']}.{e_date['Year']}"
            
            bugun_temp = datetime.date.today()
            dun_temp = bugun_temp - datetime.timedelta(days=1)
            pubmed_giris_tarihi = dun_temp.strftime('%d.%m.%Y')
            
            merkez_metni = "Merkez bilgisine ulaşılamadı / Center info not found."
            author_list = article.get('AuthorList', [])
            if author_list:
                first_author = author_list[0]
                affiliation_info = first_author.get('AffiliationInfo', [])
                if affiliation_info:
                    merkez_metni = affiliation_info[0]['Affiliation']
            
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
            
            yontem_metni = ceviri_yap(' '.join(yontem), hedef_dil_kodu) if yontem else ""
            sonuc_metni = ceviri_yap(' '.join(sonuc), hedef_dil_kodu) if sonuc else ""
            duz_abstract_metni = ceviri_yap(' '.join(duz_abstract), hedef_dil_kodu) if duz_abstract else ""
            
            pubmed_linki = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            
            # HTML Kart Tasarımı
            kart_html = f"""
            <div class="makale-kart">
                <h3 style="margin-top: 0; font-size: 1.25em; color: #2C3E50;">{i+1}. {baslik_metni}</h3>
                <p style="margin: 3px 0; font-size: 0.9em; color: #555;"><b>{dergi_etiket}:</b> {dergi_metni}</p>
                <p style="margin: 3px 0; font-size: 0.9em; color: #555;"><b>{yayin_tarihi_etiket}:</b> {yayin_tarihi}</p>
                <p style="margin: 3px 0; font-size: 0.9em; color: #555;"><b>{pubmed_tarihi_etiket}:</b> {pubmed_giris_tarihi}</p>
                <p style="margin: 3px 0; font-size: 0.9em; color: #555;"><b>{merkez_etiket}:</b> {merkez_metni}</p>
                <hr style="border: 0; border-top: 1px solid #ECF0F1; margin: 12px 0;">
            """
            
            if yontem_metni:
                kart_html += f"<p style='margin: 10px 0; color: #333;'><b>[{yontem_etiket}]:</b> {yontem_metni}</p>"
            if sonuc_metni:
                kart_html += f"<p style='margin: 10px 0; color: #27AE60;'><b>[{sonuc_etiket}]:</b> {sonuc_metni}</p>"
            if not yontem_metni and not sonuc_metni and duz_abstract_metni:
                kart_html += f"<p style='margin: 10px 0; color: #333;'><b>[{ozet_etiket}]:</b> {duz_abstract_metni}</p>"
            if not yontem_metni and not sonuc_metni and not duz_abstract_metni:
                kart_html += f"<p style='margin: 10px 0; color: #7F8C8D; font-style: italic;'>{abstract_yok_metni}</p>"
            
            kart_html += "</div>"
            
            st.markdown(kart_html, unsafe_allow_html=True)
            
            col1, col2 = st.columns([2, 1])
            with col1:
                # Koyu renkli yüksek kontrastlı "Makaleye Git" butonu
                buton_html = f'<a href="{pubmed_linki}" target="_blank" class="ozel-buton">{git_butonu_metni}</a>'
                st.markdown(buton_html, unsafe_allow_html=True)
            with col2:
                fav_durum = str(pmid) in kayitli_pmidler
                is_fav = st.checkbox(favori_ekle_etiket, value=fav_durum, key=f"fav_cb_{pmid}")
                
                if is_fav and str(pmid) not in kayitli_pmidler:
                    favori_ekle_sheets(i + 1, pmid, baslik_metni, dergi_metni, pubmed_linki, kullanici_adi)
                    st.rerun()
                elif not is_fav and str(pmid) in kayitli_pmidler:
                    favori_cikar_sheets(pmid)
                    st.rerun()
                    
            st.markdown("<br>", unsafe_allow_html=True)
            
        except Exception as e:
            continue
