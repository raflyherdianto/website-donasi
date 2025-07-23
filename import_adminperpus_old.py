import pandas as pd
from werkzeug.security import generate_password_hash
from app import create_app, db
from app.models import AdminPerpus, PerpusDesa

# Buat instance aplikasi untuk mendapatkan konteks
app = create_app()

with app.app_context():
    try:
        df = pd.read_excel("DATA PERPUSDES & TBM.xlsx")
    except FileNotFoundError:
        print("❌ ERROR: File 'DATA PERPUSDES & TBM.xlsx' tidak ditemukan.")
        exit()

    df.columns = df.columns.str.strip()

    for index, row in df.iterrows():
        try:
            nama_perpus_raw = row.get('NAMA PESPUSTAKAAN')
            desa_raw = row.get('DESA/KEL')
            kecamatan_raw = row.get('KECAMATAN')

            if pd.isna(nama_perpus_raw) or pd.isna(desa_raw) or pd.isna(kecamatan_raw):
                continue

            nama_perpus = str(nama_perpus_raw).strip()
            desa = str(desa_raw).replace("Desa ", "").replace("Kelurahan ", "").strip()
            kecamatan = str(kecamatan_raw).strip()
            
            perpus = PerpusDesa.query.filter_by(nama=nama_perpus, desa=desa, kecamatan=kecamatan).first()
            if not perpus:
                perpus = PerpusDesa(nama=nama_perpus, desa=desa, kecamatan=kecamatan)
                db.session.add(perpus)
                db.session.flush()

            username = nama_perpus.lower().replace(" ", "_") + "_" + kecamatan.lower()
            if AdminPerpus.query.filter_by(username=username).first():
                continue

            password_plain = desa.lower().replace(" ", "") + "123"
            password_hashed = generate_password_hash(password_plain)

            admin = AdminPerpus(
                username=username,
                password=password_hashed,
                perpus_id=perpus.id,
                verified=True
            )
            db.session.add(admin)

        except Exception as e:
            print(f"❌ Error pada baris {index + 2}: {e}")
            db.session.rollback()

    try:
        db.session.commit()
        print("✅ Semua data perpustakaan berhasil dimasukkan ke database.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Gagal menyimpan ke database: {e}")