from .models import db, User, AdminPerpus, PerpusDesa
from werkzeug.security import generate_password_hash
import pandas as pd

def setup_database():
    """Fungsi ini membuat superadmin dan mengimpor data perpustakaan."""
    
    # --- Bagian 1: Setup Superadmin ---
    if User.query.filter_by(username='superadmin').first():
        print("⚠️  Superadmin 'superadmin' sudah ada.")
    else:
        user = User(
            username='superadmin',
            full_name='Super Admin',
            email='admin@lumajang.go.id',
            password=generate_password_hash('admin123'),
            role='superadmin'
        )
        db.session.add(user)
        db.session.commit()
        print("✅ Superadmin 'superadmin' berhasil dibuat.")

    # --- Bagian 2: Impor Data Perpustakaan ---
    try:
        df = pd.read_excel("DATA PERPUSDES & TBM.xlsx")
    except FileNotFoundError:
        print("❌ ERROR: File 'DATA PERPUSDES & TBM.xlsx' tidak ditemukan.")
        return

    df.columns = df.columns.str.strip()
    print("⏳ Mulai mengimpor data perpustakaan...")
    
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
            db.session.rollback()

    db.session.commit()
    print("✅ Semua data perpustakaan berhasil dimasukkan ke database.")