"""
Script Upload Data Excel ke Supabase
Proyek: Stunting_db
Tabel: anak → pengukuran → status_stunting
Standar: WHO 2006 (Permenkes RI No. 2/2020)
"""

import pandas as pd
from supabase import create_client
import uuid
from dotenv import load_dotenv
import os

# ============================================================
# ⚙️  KONFIGURASI
# ============================================================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
NAMA_FILE_EXCEL = "Olah_Data.xlsx"
# ============================================================


# ── Tabel Median WHO 2006 (TB/U) ────────────────────────────
WHO_MEDIAN = {
    0: 49.9,  1: 54.7,  2: 58.4,  3: 61.4,  4: 63.9,
    5: 65.9,  6: 67.6,  7: 69.2,  8: 70.6,  9: 72.0,
    10: 73.3, 11: 74.5, 12: 75.7, 13: 76.9, 14: 78.0,
    15: 79.1, 16: 80.2, 17: 81.2, 18: 82.3, 19: 83.2,
    20: 84.2, 21: 85.1, 22: 86.0, 23: 86.9, 24: 87.8,
    25: 88.7, 26: 89.5, 27: 90.3, 28: 91.1, 29: 91.9,
    30: 92.7, 31: 93.4, 32: 94.1, 33: 94.8, 34: 95.5,
    35: 96.1, 36: 96.1, 37: 97.0, 38: 97.9, 39: 98.7,
    40: 99.5, 41: 100.3, 42: 101.0, 43: 101.8, 44: 102.5,
    45: 103.2, 46: 103.9, 47: 104.6, 48: 105.2, 49: 105.9,
    50: 106.5, 51: 107.2, 52: 107.8, 53: 108.4, 54: 109.0,
    55: 109.6, 56: 110.2, 57: 110.8, 58: 111.3, 59: 111.9,
    60: 112.4
}
WHO_SD = 4.0


def hitung_status_stunting(tinggi, umur_bulan):
    """
    Hitung status stunting berdasarkan Z-Score TB/U standar WHO 2006.
    Z-Score = (Tinggi Anak - Median WHO) / Standar Deviasi WHO
    """
    if tinggi is None or umur_bulan is None:
        return "Normal", "Data tidak lengkap", None

    umur   = min(int(umur_bulan), 60)
    median = WHO_MEDIAN.get(umur, 105.2)
    z      = round((tinggi - median) / WHO_SD, 2)

    if z < -3:
        return "Severe",   f"Sangat Pendek (Z-score: {z})", z
    elif z < -2:
        return "Stunting", f"Pendek (Z-score: {z})",        z
    else:
        return "Normal",   f"Normal (Z-score: {z})",        z


def upload_data():
    print("=" * 55)
    print("   UPLOAD DATA STUNTING KE SUPABASE")
    print("   Standar WHO 2006")
    print("=" * 55)

    # 1. Koneksi ke Supabase
    print("\n📡 Menghubungkan ke Supabase...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Berhasil terhubung!")
    except Exception as e:
        print(f"❌ Gagal terhubung: {e}")
        return

    # 2. Baca file Excel
    print(f"\n📂 Membaca file Excel: {NAMA_FILE_EXCEL}")
    try:
        df = pd.read_excel(NAMA_FILE_EXCEL)
        df.columns = df.columns.str.strip()
        print(f"✅ Berhasil baca {len(df)} baris data")
        print(f"   Kolom yang ditemukan: {list(df.columns)}")
    except FileNotFoundError:
        print(f"❌ File '{NAMA_FILE_EXCEL}' tidak ditemukan!")
        return
    except Exception as e:
        print(f"❌ Gagal baca Excel: {e}")
        return

    # 3. Bersihkan baris yang data wajibnya kosong
    sebelum = len(df)
    df = df.dropna(subset=["Berat(Kg)", "Tinggi(Cm)", "Usia(Bulan)"])
    sesudah = len(df)
    dilewati = sebelum - sesudah

    if dilewati > 0:
        print(f"\n⚠️  {dilewati} baris dilewati karena data tidak lengkap (Berat/Tinggi/Usia kosong)")

    print(f"📊 Total data yang akan diupload: {sesudah} baris\n")

    # 4. Preview distribusi status sebelum upload
    print("📋 Preview distribusi status stunting (estimasi):")
    normal_count  = 0
    stunting_count = 0
    severe_count  = 0
    for _, row in df.iterrows():
        tinggi = float(row['Tinggi(Cm)']) if pd.notna(row.get('Tinggi(Cm)')) else None
        umur   = int(row['Usia(Bulan)'])  if pd.notna(row.get('Usia(Bulan)')) else None
        status, _, _ = hitung_status_stunting(tinggi, umur)
        if status == "Normal":   normal_count  += 1
        elif status == "Stunting": stunting_count += 1
        elif status == "Severe": severe_count  += 1

    total = sesudah
    print(f"   🟢 Normal   : {normal_count:>4}  ({normal_count/total*100:.1f}%)")
    print(f"   🟠 Stunting : {stunting_count:>4}  ({stunting_count/total*100:.1f}%)")
    print(f"   🔴 Severe   : {severe_count:>4}  ({severe_count/total*100:.1f}%)")
    print(f"\n🚀 Mulai upload...\n")

    # 5. Upload baris per baris
    berhasil = 0
    gagal    = 0
    log_gagal = []

    for index, row in df.iterrows():
        nama = f"Anak_{index+1}"
        try:
            id_anak       = str(uuid.uuid4())
            id_pengukuran = str(uuid.uuid4())
            id_status     = str(uuid.uuid4())

            nama   = str(row.get('Nama', f'Anak_{index+1}')).strip()
            umur   = int(row['Usia(Bulan)'])   if pd.notna(row.get('Usia(Bulan)'))   else None
            berat  = float(row['Berat(Kg)'])   if pd.notna(row.get('Berat(Kg)'))     else None
            tinggi = float(row['Tinggi(Cm)'])  if pd.notna(row.get('Tinggi(Cm)'))    else None
            lila   = float(row['LiLA(Cm)'])    if pd.notna(row.get('LiLA(Cm)'))      else None

            # INSERT tabel anak
            supabase.table("anak").insert({
                "id_anak"       : id_anak,
                "nama"          : nama,
                "tanggal_lahir" : None,
                "jenis_kelamin" : None,
            }).execute()

            # INSERT tabel pengukuran
            supabase.table("pengukuran").insert({
                "id_pengukuran"     : id_pengukuran,
                "id_anak"           : id_anak,
                "tanggal_pengukuran": None,
                "berat_badan"       : berat,
                "tinggi_badan"      : tinggi,
                "umur_bulan"        : umur,
                "lila"              : lila,
            }).execute()

            # Hitung status stunting dengan standar WHO 2006
            status, keterangan, z_score = hitung_status_stunting(tinggi, umur)

            # INSERT tabel status_stunting
            supabase.table("status_stunting").insert({
                "id_status"      : id_status,
                "id_pengukuran"  : id_pengukuran,
                "status_stunting": status,
                "keterangan"     : keterangan,
            }).execute()

            berhasil += 1

            if (berhasil) % 100 == 0 or berhasil == sesudah:
                print(f"   ✔  {berhasil}/{sesudah} baris selesai diupload...")

        except Exception as e:
            gagal += 1
            log_gagal.append(f"Baris {index+1} ({nama}): {e}")
            print(f"   ❌ Baris {index+1} ({nama}) gagal: {e}")

    # 6. Ringkasan hasil
    print("\n" + "=" * 55)
    print("   HASIL UPLOAD")
    print("=" * 55)
    print(f"   ✅ Berhasil : {berhasil} data")
    print(f"   ❌ Gagal    : {gagal} data")
    print(f"   📊 Total    : {sesudah} data")
    print("=" * 55)

    if gagal == 0:
        print("\n🎉 Semua data berhasil diupload ke Supabase!")
        print("   Buka dashboard dan klik 🔄 Refresh Data\n")
    else:
        print(f"\n⚠️  Ada {gagal} data yang gagal:")
        for log in log_gagal:
            print(f"   • {log}")


if __name__ == "__main__":
    upload_data()