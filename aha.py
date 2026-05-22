"""
Dashboard Monitoring Stunting - Versi Profesional
Sistem Monitoring Stunting Terintegrasi Berbasis Web dan Data Analytics
Data dari Supabase | Standar WHO 2006
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client
import warnings
warnings.filterwarnings('ignore')

# ── Konfigurasi halaman ──────────────────────────────────────
st.set_page_config(
    page_title="Monitoring Stunting",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS Profesional ──────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .main-header {
        background: linear-gradient(135deg, #1a5276 0%, #2980b9 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(41,128,185,0.3);
    }
    .main-header h1 { font-size: 1.9rem; font-weight: 700; margin: 0 0 0.3rem; }
    .main-header p  { font-size: 0.95rem; opacity: 0.88; margin: 0; }
    .main-header .badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.8rem;
        margin-top: 0.6rem;
        margin-right: 6px;
    }

    .section-header {
        font-size: 1.1rem; font-weight: 600;
        color: #1a5276; border-left: 4px solid #2980b9;
        padding-left: 10px; margin: 1.5rem 0 0.8rem;
    }

    .info-box {
        background: #eaf4fb; border-left: 4px solid #2980b9;
        border-radius: 8px; padding: 0.8rem 1rem;
        font-size: 0.88rem; color: #1a5276;
        margin-bottom: 1rem;
    }
    .info-box.warning { background: #fef9e7; border-color: #f39c12; color: #7d6608; }
    .info-box.danger  { background: #fdedec; border-color: #e74c3c; color: #922b21; }
    .info-box.success { background: #eafaf1; border-color: #27ae60; color: #1e8449; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #2980b9;
        height: 100%;
    }
    .metric-card.green  { border-top-color: #27ae60; }
    .metric-card.orange { border-top-color: #e67e22; }
    .metric-card.red    { border-top-color: #e74c3c; }
    .metric-card.blue   { border-top-color: #2980b9; }
    .metric-card.purple { border-top-color: #8e44ad; }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #1a252f; }
    .metric-label { font-size: 0.85rem; color: #7f8c8d; margin-top: 4px; font-weight: 500; }
    .metric-sub   { font-size: 1rem; font-weight: 600; margin-top: 4px; }
    .metric-sub.green  { color: #27ae60; }
    .metric-sub.orange { color: #e67e22; }
    .metric-sub.red    { color: #e74c3c; }
    .metric-sub.blue   { color: #2980b9; }

    .chart-container {
        background: white; border-radius: 12px;
        padding: 1.2rem; box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .chart-title {
        font-size: 1rem; font-weight: 600; color: #1a5276;
        margin-bottom: 0.3rem;
    }
    .chart-desc {
        font-size: 0.8rem; color: #95a5a6; margin-bottom: 0.8rem;
    }

    .legend-item {
        display: inline-flex; align-items: center;
        margin-right: 16px; font-size: 0.82rem; color: #555;
    }
    .legend-dot {
        width: 12px; height: 12px; border-radius: 50%;
        display: inline-block; margin-right: 5px;
    }

    .stTabs [data-baseweb="tab"] {
        font-weight: 600; font-size: 0.9rem;
    }

    div[data-testid="metric-container"] {
        background: #f8f9fa; border-radius: 10px;
        padding: 0.8rem; border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# KONFIGURASI SUPABASE
# ============================================================
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ============================================================
# LOAD DATA DARI SUPABASE
# ============================================================
@st.cache_data(ttl=300)
def load_data():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    anak       = supabase.table("anak").select("*").execute().data
    pengukuran = supabase.table("pengukuran").select("*").execute().data
    status     = supabase.table("status_stunting").select("*").execute().data

    df_anak       = pd.DataFrame(anak)
    df_pengukuran = pd.DataFrame(pengukuran)
    df_status     = pd.DataFrame(status)

    df = df_pengukuran.merge(df_anak, on="id_anak", how="left")
    df = df.merge(df_status, on="id_pengukuran", how="left")

    df = df.rename(columns={
        "nama"           : "Nama",
        "umur_bulan"     : "Usia_Bulan",
        "berat_badan"    : "Berat_Kg",
        "tinggi_badan"   : "Tinggi_Cm",
        "lila"           : "LiLA_Cm",
        "status_stunting": "Status_Stunting",
        "keterangan"     : "Keterangan",
    })

    df = df.dropna(subset=["Usia_Bulan", "Berat_Kg", "Tinggi_Cm"])
    df["Usia_Bulan"] = df["Usia_Bulan"].astype(int)

    WHO_MEDIAN = {
        36:95.2, 37:96.1, 38:97.0, 39:97.9, 40:98.7,
        41:99.5, 42:100.3, 43:101.0, 44:101.8, 45:102.5,
        46:103.2, 47:103.9, 48:104.6, 49:105.2, 50:105.9,
        51:106.5, 52:107.2, 53:107.8, 54:108.4, 55:109.0,
        56:109.6, 57:110.2, 58:110.8, 59:111.3, 60:111.9
    }
    WHO_SD = 4.0

    def zscore(row):
        m = WHO_MEDIAN.get(int(row["Usia_Bulan"]), 105.2)
        return round((row["Tinggi_Cm"] - m) / WHO_SD, 2)

    def gz_label(row):
        bmi = row["Berat_Kg"] / ((row["Tinggi_Cm"] / 100) ** 2)
        if   bmi < 13.5: return "Sangat Kurus"
        elif bmi < 14.5: return "Kurus"
        elif bmi > 18.5: return "Gemuk"
        return "Normal"

    df["Z_Score"]     = df.apply(zscore, axis=1)
    df["Status_Gizi"] = df.apply(gz_label, axis=1)
    df["BMI"]         = (df["Berat_Kg"] / (df["Tinggi_Cm"] / 100) ** 2).round(2)

    return df


# Load data
with st.spinner("⏳ Memuat data dari Supabase..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"❌ Gagal memuat data: {e}")
        st.stop()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 🏥 Monitoring Stunting")
    st.markdown(f"**Sumber:** Supabase Cloud")
    st.markdown(f"**Total:** `{len(df):,}` anak terpantau")
    st.divider()

    st.markdown("### 🔍 Filter Data")
    usia_min = int(df["Usia_Bulan"].min())
    usia_max = int(df["Usia_Bulan"].max())
    usia_range = st.slider("Rentang Usia (Bulan)", usia_min, usia_max, (usia_min, usia_max))

    status_options = ["Semua"] + sorted(df["Status_Stunting"].dropna().unique().tolist())
    filter_status  = st.selectbox("Status Stunting", status_options)

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.markdown("### 📖 Panduan Klasifikasi")
    st.markdown("""
    Berdasarkan **Z-Score TB/U (WHO 2006)**:

    🔴 **Severe** → Z < -3 SD
    Anak sangat pendek, risiko tinggi,
    perlu intervensi segera.

    🟠 **Stunting** → -3 ≤ Z < -2 SD
    Anak pendek, perlu pemantauan
    dan asupan gizi ekstra.

    🟢 **Normal** → Z ≥ -2 SD
    Pertumbuhan sesuai standar WHO.

    ---
    📏 **LiLA Normal:** ≥ 12.5 cm
    📏 **LiLA Kurang Gizi:** < 12.5 cm
    📏 **LiLA Kritis:** < 11.5 cm

    ---
    *Ref: Permenkes RI No. 2/2020*
    """)

# Terapkan filter
df_filtered = df[
    (df["Usia_Bulan"] >= usia_range[0]) &
    (df["Usia_Bulan"] <= usia_range[1])
]
if filter_status != "Semua":
    df_filtered = df_filtered[df_filtered["Status_Stunting"] == filter_status]

# ============================================================
# HEADER UTAMA
# ============================================================
st.markdown(f"""
<div class="main-header">
    <h1>🏥 Sistem Monitoring Stunting Terintegrasi</h1>
    <p>Pemantauan status gizi dan pertumbuhan balita berbasis data real-time dari Supabase</p>
    <span class="badge">📊 {len(df_filtered):,} Data Aktif</span>
    <span class="badge">🗄️ Supabase Cloud</span>
    <span class="badge">📐 Standar WHO 2006</span>
    <span class="badge">📋 Permenkes RI No. 2/2020</span>
</div>
""", unsafe_allow_html=True)

if filter_status != "Semua" or usia_range != (usia_min, usia_max):
    st.markdown(f"""<div class="info-box">
        📌 <b>Filter aktif:</b> Usia {usia_range[0]}–{usia_range[1]} bulan
        {"| Status: <b>" + filter_status + "</b>" if filter_status != "Semua" else ""}
    </div>""", unsafe_allow_html=True)

# ============================================================
# SECTION 1: KARTU RINGKASAN
# ============================================================
st.markdown('<div class="section-header">📊 Ringkasan Status Gizi Balita</div>', unsafe_allow_html=True)
st.markdown("""<div class="info-box">
    Kartu di bawah menampilkan jumlah dan persentase balita berdasarkan status stunting.
    Prevalensi stunting dihitung dari total anak dengan status <b>Stunting</b> dan <b>Severe</b>
    dibagi total anak terpantau. WHO menetapkan ambang bahaya di angka <b>20%</b>.
</div>""", unsafe_allow_html=True)

total    = len(df_filtered)
n_norm   = (df_filtered["Status_Stunting"] == "Normal").sum()
n_stunt  = (df_filtered["Status_Stunting"] == "Stunting").sum()
n_severe = (df_filtered["Status_Stunting"] == "Severe").sum()
prev     = (n_stunt + n_severe) / total * 100 if total > 0 else 0

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class="metric-card blue">
        <div class="metric-value">{total:,}</div>
        <div class="metric-label">Total Anak Terpantau</div>
        <div class="metric-sub blue">100%</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card green">
        <div class="metric-value">{n_norm:,}</div>
        <div class="metric-label">🟢 Normal</div>
        <div class="metric-sub green">{n_norm/total*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card orange">
        <div class="metric-value">{n_stunt:,}</div>
        <div class="metric-label">🟠 Stunting</div>
        <div class="metric-sub orange">{n_stunt/total*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card red">
        <div class="metric-value">{n_severe:,}</div>
        <div class="metric-label">🔴 Severe</div>
        <div class="metric-sub red">{n_severe/total*100:.1f}%</div>
    </div>""", unsafe_allow_html=True)
with c5:
    color_prev = "red" if prev > 20 else ("orange" if prev > 10 else "green")
    st.markdown(f"""<div class="metric-card {color_prev}">
        <div class="metric-value">{prev:.1f}%</div>
        <div class="metric-label">⚠️ Prevalensi Stunting</div>
        <div class="metric-sub {color_prev}">{"🚨 Bahaya" if prev > 20 else ("⚠️ Waspada" if prev > 10 else "✅ Aman")}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if prev > 20:
    st.markdown("""<div class="info-box danger">
        🚨 <b>PERINGATAN:</b> Prevalensi stunting melebihi ambang batas WHO (20%).
        Diperlukan intervensi gizi segera seperti pemberian makanan tambahan,
        edukasi ibu, dan pemantauan intensif.
    </div>""", unsafe_allow_html=True)
elif prev > 10:
    st.markdown("""<div class="info-box warning">
        ⚠️ <b>PERHATIAN:</b> Prevalensi stunting antara 10–20%. Perlu pemantauan
        berkala dan program pencegahan stunting yang lebih aktif.
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""<div class="info-box success">
        ✅ <b>BAIK:</b> Prevalensi stunting di bawah 10%. Pertahankan program
        pemantauan dan pemenuhan gizi balita yang sudah berjalan.
    </div>""", unsafe_allow_html=True)

st.divider()

# ============================================================
# SECTION 2: DISTRIBUSI STATUS
# ============================================================
color_map_st = {"Normal": "#27ae60", "Stunting": "#e67e22", "Severe": "#e74c3c"}

st.markdown('<div class="section-header">📈 Distribusi Status Stunting & Gizi</div>', unsafe_allow_html=True)
st.markdown("""<div class="info-box">
    Pie chart menunjukkan proporsi status stunting berdasarkan Z-Score TB/U.
    Bar chart menunjukkan status gizi berdasarkan BMI (Indeks Massa Tubuh) per usia.
    Kedua grafik ini saling melengkapi untuk gambaran kondisi gizi secara menyeluruh.
</div>""", unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    dist_st = df_filtered["Status_Stunting"].value_counts().reset_index()
    dist_st.columns = ["Status", "Jumlah"]
    fig_pie = px.pie(
        dist_st, values="Jumlah", names="Status",
        color="Status", color_discrete_map=color_map_st, hole=0.42,
        title="Proporsi Status Stunting (TB/U)"
    )
    fig_pie.update_traces(textposition="outside", textinfo="percent+label", pull=[0.04]*len(dist_st))
    fig_pie.update_layout(height=380, margin=dict(t=50, b=20, l=20, r=20),
                          title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.caption("📌 Klasifikasi berdasarkan Z-Score Tinggi Badan menurut Umur (TB/U) WHO 2006")

with col_b:
    dist_gz = df_filtered["Status_Gizi"].value_counts().reset_index()
    dist_gz.columns = ["Status", "Jumlah"]
    color_map_gz = {"Normal":"#27ae60","Kurus":"#e67e22","Sangat Kurus":"#e74c3c","Gemuk":"#8e44ad"}
    fig_bar = px.bar(
        dist_gz, x="Status", y="Jumlah",
        color="Status", color_discrete_map=color_map_gz,
        text="Jumlah", title="Status Gizi Berdasarkan BMI/Usia"
    )
    fig_bar.update_traces(texttemplate="%{text}", textposition="outside")
    fig_bar.update_layout(showlegend=False, height=380,
                          xaxis_title="Status Gizi", yaxis_title="Jumlah Anak",
                          margin=dict(t=50, b=20), title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("📌 Status gizi dihitung dari BMI = Berat(kg) / Tinggi(m)². Normal BMI: 14.5–18.5")

st.divider()

# ============================================================
# SECTION 3: ANALISIS Z-SCORE & PERTUMBUHAN
# ============================================================
st.markdown('<div class="section-header">📉 Analisis Z-Score & Pola Pertumbuhan</div>', unsafe_allow_html=True)
st.markdown("""<div class="info-box">
    <b>Z-Score</b> adalah ukuran standar WHO untuk menilai pertumbuhan anak.
    Z-Score dihitung dari selisih tinggi anak dengan median tinggi WHO dibagi standar deviasi.
    Nilai di bawah <b>-2 SD</b> menandakan stunting, di bawah <b>-3 SD</b> menandakan severe stunting.
    Scatter plot memperlihatkan pola korelasi antara tinggi dan berat badan per status.
</div>""", unsafe_allow_html=True)

col_c, col_d = st.columns(2)

with col_c:
    fig_hist = px.histogram(
        df_filtered, x="Z_Score", nbins=40,
        color_discrete_sequence=["#3498db"],
        labels={"Z_Score": "Z-Score TB/U", "count": "Frekuensi"},
        title="Distribusi Z-Score Tinggi Badan/Umur"
    )
    for val, label, color in [
        (-3, "Severe (-3 SD)", "#e74c3c"),
        (-2, "Stunting (-2 SD)", "#e67e22"),
        (0,  "Median WHO", "#95a5a6"),
    ]:
        fig_hist.add_vline(x=val, line_dash="dash", line_color=color,
                           annotation_text=label, annotation_position="top",
                           annotation_font_size=10)
    fig_hist.update_layout(height=360, margin=dict(t=50, b=20),
                           title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_hist, use_container_width=True)
    st.caption("📌 Garis putus-putus menunjukkan ambang batas WHO. Kurva ideal berbentuk lonceng di sekitar Z=0")

with col_d:
    fig_sc = px.scatter(
        df_filtered, x="Tinggi_Cm", y="Berat_Kg",
        color="Status_Stunting", color_discrete_map=color_map_st,
        opacity=0.6, hover_data=["Nama", "Usia_Bulan"],
        labels={"Tinggi_Cm": "Tinggi Badan (cm)", "Berat_Kg": "Berat Badan (kg)"},
        title="Korelasi Tinggi vs Berat Badan per Status",
        trendline="ols"
    )
    fig_sc.update_layout(height=360, margin=dict(t=50, b=40),
                         legend=dict(orientation="h", y=-0.3),
                         title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption("📌 Garis tren menunjukkan hubungan linier tinggi-berat. Titik merah (Severe) cenderung berada di kiri bawah")

st.divider()

# ============================================================
# SECTION 4: BOX PLOT & HEATMAP
# ============================================================
st.markdown('<div class="section-header">📦 Sebaran Data & Korelasi Antar Variabel</div>', unsafe_allow_html=True)
st.markdown("""<div class="info-box">
    <b>Box Plot</b> memperlihatkan sebaran tinggi badan per kelompok status —
    median, kuartil, dan nilai ekstrem (outlier). <b>Heatmap Korelasi</b> menunjukkan
    kekuatan hubungan antar variabel (nilai mendekati 1 = korelasi positif kuat,
    mendekati -1 = korelasi negatif kuat, 0 = tidak berkorelasi).
</div>""", unsafe_allow_html=True)

col_e, col_f = st.columns(2)

with col_e:
    fig_box = px.box(
        df_filtered, x="Status_Stunting", y="Tinggi_Cm",
        color="Status_Stunting", color_discrete_map=color_map_st,
        points="outliers",
        labels={"Tinggi_Cm": "Tinggi Badan (cm)", "Status_Stunting": "Status"},
        title="Sebaran Tinggi Badan per Status Stunting"
    )
    fig_box.add_hline(y=105.2, line_dash="dot", line_color="#7f8c8d",
                      annotation_text="Median WHO (49 bln: 105.2 cm)", annotation_font_size=10)
    fig_box.update_layout(height=360, showlegend=False,
                          margin=dict(t=50, b=20), title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_box, use_container_width=True)
    st.caption("📌 Kotak menunjukkan rentang Q1–Q3. Garis tengah = median. Titik di luar = outlier")

with col_f:
    num_cols = ["Usia_Bulan", "Berat_Kg", "Tinggi_Cm", "LiLA_Cm", "Z_Score", "BMI"]
    num_cols_ada = [c for c in num_cols if c in df_filtered.columns]
    corr = df_filtered[num_cols_ada].corr().round(2)
    fig_heat = px.imshow(
        corr, text_auto=True, aspect="auto",
        color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
        title="Heatmap Korelasi Antar Variabel"
    )
    fig_heat.update_layout(height=360, margin=dict(t=50, b=20),
                           title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.caption("📌 Hijau = korelasi positif kuat. Merah = korelasi negatif. Z_Score & Tinggi_Cm seharusnya berkorelasi tinggi")

st.divider()

# ============================================================
# SECTION 5: GRAFIK LILA
# ============================================================
st.markdown('<div class="section-header">📏 Analisis LiLA (Lingkar Lengan Atas)</div>', unsafe_allow_html=True)
st.markdown("""<div class="info-box">
    <b>LiLA</b> (Lingkar Lengan Atas) adalah indikator cepat untuk mendeteksi kekurangan gizi akut pada anak.
    Pengukuran dilakukan di titik tengah lengan kiri atas.
    <br><br>
    📏 <b>≥ 12.5 cm</b> → Gizi Baik &nbsp;|&nbsp;
    📏 <b>11.5–12.5 cm</b> → Kurang Gizi (Waspada) &nbsp;|&nbsp;
    📏 <b>&lt; 11.5 cm</b> → Gizi Buruk (Kritis, perlu penanganan segera)
</div>""", unsafe_allow_html=True)

col_g, col_h = st.columns(2)

with col_g:
    fig_lila_hist = px.histogram(
        df_filtered, x="LiLA_Cm",
        color="Status_Stunting", color_discrete_map=color_map_st,
        nbins=25, barmode="overlay", opacity=0.75,
        labels={"LiLA_Cm": "LiLA (cm)", "count": "Jumlah Anak"},
        title="Distribusi Nilai LiLA per Status Stunting"
    )
    fig_lila_hist.add_vline(x=11.5, line_dash="dash", line_color="#e74c3c",
                             annotation_text="Gizi Buruk (<11.5 cm)", annotation_font_size=10)
    fig_lila_hist.add_vline(x=12.5, line_dash="dash", line_color="#e67e22",
                             annotation_text="Kurang Gizi (<12.5 cm)", annotation_font_size=10)
    fig_lila_hist.update_layout(height=360, margin=dict(t=50, b=20),
                                 legend=dict(orientation="h", y=-0.3),
                                 title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_lila_hist, use_container_width=True)
    st.caption("📌 Sebagian besar anak stunting/severe memiliki LiLA mendekati atau di bawah ambang batas")

with col_h:
    fig_lila_box = px.box(
        df_filtered, x="Status_Stunting", y="LiLA_Cm",
        color="Status_Stunting", color_discrete_map=color_map_st,
        points="outliers",
        labels={"LiLA_Cm": "LiLA (cm)", "Status_Stunting": "Status"},
        title="Sebaran LiLA per Status Stunting"
    )
    fig_lila_box.add_hline(y=12.5, line_dash="dot", line_color="#e67e22",
                            annotation_text="Ambang Kurang Gizi (12.5 cm)", annotation_font_size=10)
    fig_lila_box.add_hline(y=11.5, line_dash="dot", line_color="#e74c3c",
                            annotation_text="Ambang Gizi Buruk (11.5 cm)", annotation_font_size=10)
    fig_lila_box.update_layout(height=360, showlegend=False,
                                margin=dict(t=50, b=20), title_font_size=14, title_x=0.05)
    st.plotly_chart(fig_lila_box, use_container_width=True)
    st.caption("📌 Anak dengan status Severe cenderung memiliki LiLA lebih rendah dibanding Normal")

st.divider()

# ============================================================
# SECTION 6: TABEL DATA
# ============================================================
st.markdown('<div class="section-header">📋 Data Lengkap Balita</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📋 Semua Data", "📊 Statistik Deskriptif", "🚨 Data Prioritas Intervensi"])

with tab1:
    st.markdown(f"""<div class="info-box">
        Menampilkan <b>{len(df_filtered):,} data</b> balita sesuai filter aktif.
        Baris berwarna merah muda = Severe | Kuning muda = Stunting | Putih = Normal.
        Klik header kolom untuk mengurutkan data.
    </div>""", unsafe_allow_html=True)

    col_show = [c for c in ["Nama","Usia_Bulan","Berat_Kg","Tinggi_Cm",
                             "LiLA_Cm","Z_Score","Status_Stunting","Status_Gizi","BMI"]
                if c in df_filtered.columns]

    def color_row(row):
        c = {"Severe":"background-color:#fdecea","Stunting":"background-color:#fef3e2"}.get(row["Status_Stunting"],"")
        return [c]*len(row)

    styled = df_filtered[col_show].style.apply(color_row, axis=1)
    st.dataframe(styled, use_container_width=True, height=400)

    csv_bytes = df_filtered[col_show].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Data CSV", data=csv_bytes,
                       file_name="data_stunting.csv", mime="text/csv")

with tab2:
    st.markdown("""<div class="info-box">
        Statistik deskriptif menampilkan ringkasan numerik setiap variabel:
        rata-rata, standar deviasi, nilai minimum/maksimum, dan kuartil.
        Berguna untuk memahami sebaran dan keragaman data secara cepat.
    </div>""", unsafe_allow_html=True)
    num_cols3 = [c for c in ["Usia_Bulan","Berat_Kg","Tinggi_Cm","LiLA_Cm","Z_Score","BMI"]
                 if c in df_filtered.columns]
    desc = df_filtered[num_cols3].describe().round(2)
    desc.index = ["Jumlah","Rata-rata","Std Dev","Min","Q1 (25%)","Median","Q3 (75%)","Maks"]
    st.dataframe(desc, use_container_width=True)

with tab3:
    st.markdown("""<div class="info-box danger">
        🚨 <b>Data Prioritas Intervensi</b> — Daftar anak dengan status <b>Severe</b>
        (Z-Score &lt; -3 SD) yang memerlukan penanganan gizi segera.
        Urutkan berdasarkan Z-Score terendah untuk menentukan prioritas utama.
    </div>""", unsafe_allow_html=True)

    kritis_cols = [c for c in ["Nama","Usia_Bulan","Tinggi_Cm","Berat_Kg","LiLA_Cm","Z_Score","Status_Gizi"]
                   if c in df_filtered.columns]
    df_kritis = df_filtered[df_filtered["Status_Stunting"] == "Severe"][kritis_cols].copy()
    if "Z_Score" in df_kritis.columns:
        df_kritis = df_kritis.sort_values("Z_Score")
    st.dataframe(df_kritis, use_container_width=True, height=380)
    st.caption(f"⚠️ Total {len(df_kritis)} anak memerlukan intervensi segera")

    if len(df_kritis) > 0:
        csv_kritis = df_kritis.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Data Kritis", data=csv_kritis,
                           file_name="data_kritis_stunting.csv", mime="text/csv")

# ── Footer ───────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style='text-align:center; color:#95a5a6; font-size:0.82rem; padding: 0.5rem 0 1rem'>
    🏥 <b>Sistem Monitoring Stunting Terintegrasi</b> &nbsp;•&nbsp;
    Proyek Teknologi Informasi &nbsp;•&nbsp;
    Data real-time dari Supabase Cloud &nbsp;•&nbsp;
    Standar WHO 2006 (Permenkes RI No. 2/2020)
</div>
""", unsafe_allow_html=True)
