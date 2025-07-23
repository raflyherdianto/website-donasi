import os
from datetime import datetime
import pdfkit
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for, session, flash,
    send_file, current_app
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import func, extract

# Impor db dan semua model dari file models.py
from .models import (
    db, User, Donasi, DetailDonasi, BuktiPengiriman, KebutuhanKoleksi,
    Kunjungan, PerpusDesa, AdminPerpus
)

# Buat Blueprint utama
bp = Blueprint('main', __name__)

# --- DECORATORS & HELPER FUNCTIONS ---

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'superadmin':
            flash("Anda tidak memiliki izin akses sebagai superadmin.", "danger")
            return redirect(url_for('main.login_superadmin'))
        return f(*args, **kwargs)
    return decorated_function

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- PENGGUNA UMUM (PUBLIC) ROUTES ---

@bp.route('/')
def home():
    return render_template('pengguna/index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['nama'] = user.full_name
            return redirect(url_for('main.home'))
        flash("Login gagal.")
        return redirect(url_for('main.login'))
    return render_template('pengguna/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        username = email.split('@')[0] # Membuat username default dari email

        if User.query.filter_by(email=email).first():
            flash("Email sudah terdaftar.")
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)
        user = User(
            full_name=full_name,
            email=email,
            username=username,
            password=hashed_password,
            role='user'
        )
        db.session.add(user)
        db.session.commit()
        flash("Registrasi berhasil!")
        return redirect(url_for('main.login'))
    return render_template('pengguna/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))

@bp.route('/syarat')
def syarat():
    return render_template('pengguna/syarat_ketentuan.html')

@bp.route('/transparansi')
def transparansi():
    return render_template('pengguna/transparansi_donasi.html')

@bp.route('/riwayat')
def riwayat():
    return render_template('pengguna/riwayat_transparansi.html')

@bp.route('/faq')
def faq():
    return render_template('pengguna/faq.html')

@bp.route('/kontak')
def kontak():
    return render_template('pengguna/kontak.html')

@bp.route('/profil')
def profil():
    return render_template('pengguna/profil.html')

@bp.route('/panduan-donasi')
def panduan_donasi():
    return render_template('pengguna/panduan_donasi.html')

@bp.route('/perpusdes')
def perpusdes():
    return render_template('pengguna/perpusdes.html')

# --- DONASI ROUTES ---

@bp.route('/formulir-donasi', methods=['GET', 'POST'])
def formulir_donasi():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        if not request.form.get('setuju_syarat') or not request.form.get('setuju_pengiriman'):
            flash("Persetujuan diperlukan.")
            return redirect(url_for('main.formulir_donasi'))

        donasi = Donasi(
            nama=user.full_name,
            email=request.form['email'],
            whatsapp=request.form['whatsapp'],
            alamat="Jl. Hayam Wuruk No.1, Kepuharjo, Lumajang",
            metode=request.form['metode_pengiriman'],
            catatan=request.form['catatan']
        )
        db.session.add(donasi)
        db.session.commit()

        for subjek, jumlah in zip(request.form.getlist('subjek_buku[]'), request.form.getlist('jumlah[]')):
            if subjek and jumlah.isdigit():
                db.session.add(DetailDonasi(donasi_id=donasi.id, subjek_buku=subjek, jumlah=int(jumlah)))
        db.session.commit()

        session['last_donation_id'] = donasi.id
        return redirect(url_for('main.konfirmasi_donasi', id=donasi.id))

    return render_template('pengguna/form_donasi.html', user=user)


@bp.route('/konfirmasi-donasi/<int:id>', methods=['GET', 'POST'])
def konfirmasi_donasi(id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    donasi = Donasi.query.get_or_404(id)
    if request.method == 'POST':
        bukti_resi = request.files.get('bukti_resi')
        tanggal_pengiriman = request.form.get('tanggal_pengiriman')
        if not bukti_resi or not allowed_file(bukti_resi.filename):
            flash("File tidak valid atau tidak diunggah.")
            return redirect(url_for('main.konfirmasi_donasi', id=id))

        filename = secure_filename(bukti_resi.filename)
        # Gunakan 'current_app' untuk mengakses config
        bukti_resi.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        bukti = BuktiPengiriman(
            donasi_id=id,
            bukti_resi=filename,
            tanggal_pengiriman=datetime.strptime(tanggal_pengiriman, '%Y-%m-%d').date()
        )
        db.session.add(bukti)
        db.session.commit()
        return redirect(url_for('main.konfirmasi_berhasil'))

    return render_template('pengguna/konfirmasi_donasi.html', donasi=donasi)

@bp.route('/konfirmasi-berhasil')
def konfirmasi_berhasil():
    return render_template('pengguna/konfirmasi_berhasil.html')

@bp.route('/unduh-bukti-donasi')
def generate_pdf():
    if 'user_id' not in session or 'last_donation_id' not in session:
        return redirect(url_for('main.login'))

    donasi_id = session['last_donation_id']
    donasi = Donasi.query.get_or_404(donasi_id)
    detail = DetailDonasi.query.filter_by(donasi_id=donasi_id).all()
    bukti = BuktiPengiriman.query.filter_by(donasi_id=donasi_id).first()
    nomor_donasi = f"DN-{donasi.tanggal.strftime('%Y%m%d')}-{str(donasi.id).zfill(3)}"

    rendered = render_template(
        'pengguna/bukti_donasi_pdf.html',
        donasi=donasi,
        detail_buku=detail,
        bukti=bukti,
        nomor_donasi=nomor_donasi
    )

    PDF_FOLDER = os.path.join(current_app.root_path, 'static', 'pdf')
    os.makedirs(PDF_FOLDER, exist_ok=True)
    
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_path = os.path.join(PDF_FOLDER, f'bukti_donasi_{donasi_id}.pdf')
    pdfkit.from_string(
        rendered,
        pdf_path,
        configuration=config,
        options={'enable-local-file-access': ''}
    )

    return send_file(pdf_path, as_attachment=True)


# --- ADMIN PERPUS ROUTES ---

@bp.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = AdminPerpus.query.filter_by(username=username).first()
        if admin and admin.verified and check_password_hash(admin.password, password):
            session['admin_id'] = admin.id
            session['nama_perpus'] = admin.perpus.nama
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash('Login gagal. Username/password salah atau akun belum diverifikasi.')
            return redirect(url_for('main.login_admin'))

    return render_template('admin/login_admin.html')

@bp.route('/logout-admin')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('nama_perpus', None)
    return redirect(url_for('main.login_admin'))

@bp.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))

    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year

    total_kunjungan_bulan_ini = Kunjungan.query.filter(
        extract('month', Kunjungan.tanggal) == bulan_ini,
        extract('year', Kunjungan.tanggal) == tahun_ini
    ).count()

    return render_template('admin/dashboard.html',
        total_buku_pusat=0,
        total_donasi_buku=0,
        total_kegiatan=0,
        persentase_kenaikan_koleksi=0,
        total_kunjungan_bulan_ini=total_kunjungan_bulan_ini,
        notif_koleksi_pending="Placeholder notifikasi.",
        notif_distribusi_pending="Placeholder notifikasi.",
        notif_kegiatan_blm_lengkap="Placeholder notifikasi."
    )

@bp.route('/admin/tambah-kunjungan', methods=['POST'])
def tambah_kunjungan():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    kunjungan = Kunjungan()
    db.session.add(kunjungan)
    db.session.commit()
    flash("Kunjungan berhasil ditambahkan!", "success")
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/kurangi-kunjungan', methods=['POST'])
def kurangi_kunjungan():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    kunjungan_terakhir = Kunjungan.query.order_by(Kunjungan.id.desc()).first()
    if kunjungan_terakhir:
        db.session.delete(kunjungan_terakhir)
        db.session.commit()
        flash("Kunjungan berhasil dikurangi!", "success")
    else:
        flash("Tidak ada kunjungan yang bisa dikurangi.", "warning")
    return redirect(url_for('main.admin_dashboard'))

@bp.route('/admin/profil-perpustakaan', methods=['GET', 'POST'])
def admin_profil_perpustakaan():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    if request.method == 'POST':
        flash("Data berhasil disimpan!", "success")
        return redirect(url_for('main.admin_profil_perpustakaan'))
    return render_template('admin/profil_perpustakaan.html')


@bp.route('/admin/kebutuhan-koleksi', methods=['GET', 'POST'])
def kebutuhan_koleksi():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    if request.method == 'POST':
        kebutuhan = KebutuhanKoleksi(
            nama_perpustakaan=request.form.get('nama_perpustakaan'),
            subjek=request.form.get('subjek'),
            jumlah_buku=int(request.form.get('jumlah_buku')),
            prioritas=request.form.get('prioritas'),
            lokasi=request.form.get('lokasi'),
            alasan=request.form.get('alasan')
        )
        db.session.add(kebutuhan)
        db.session.commit()
        flash("Pengajuan kebutuhan berhasil dikirim.", "success")
        return redirect(url_for('main.kebutuhan_koleksi'))
    return render_template('admin/kebutuhan_koleksi.html')

@bp.route('/admin/lihat-kebutuhan-koleksi')
def lihat_kebutuhan_koleksi():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    data_kebutuhan = KebutuhanKoleksi.query.order_by(KebutuhanKoleksi.tanggal_pengajuan.desc()).all()
    return render_template('admin/lihat_kebutuhan_koleksi.html', data_kebutuhan=data_kebutuhan)

@bp.route('/admin/kegiatan-perpus')
def kegiatan_perpus():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    return render_template('admin/kegiatan_perpus.html')

@bp.route('/admin/riwayat-distribusi')
def riwayat_distribusi():
    if 'admin_id' not in session:
        return redirect(url_for('main.login_admin'))
    return render_template('admin/riwayat_distribusi.html')

# --- SUPERADMIN ROUTES ---

@bp.route('/superadmin/login', methods=['GET', 'POST'])
def login_superadmin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, role='superadmin').first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('main.tampilan_depan'))
        else:
            flash("Login gagal. Username atau password salah.")
    return render_template('superadmin/login.html')


@bp.route('/superadmin/tampilan_depan')
@super_admin_required
def tampilan_depan():
    total_donatur = User.query.filter(User.role != 'superadmin').count()
    total_buku = db.session.query(func.sum(DetailDonasi.jumlah)).scalar() or 0
    total_perpus = PerpusDesa.query.count()
    return render_template('superadmin/tampilan_depan.html',
                           total_donatur=total_donatur,
                           total_buku=total_buku,
                           total_perpus=total_perpus)

@bp.route('/superadmin/perpusdes')
@super_admin_required
def daftar_perpustakaan():
    data_perpus = db.session.query(PerpusDesa, AdminPerpus).join(AdminPerpus, AdminPerpus.perpus_id == PerpusDesa.id).all()
    return render_template('superadmin/perpusdesa.html', data_perpus=data_perpus)

@bp.route('/tambah-perpustakaan', methods=['GET', 'POST'])
@super_admin_required
def tambah_perpus():
    if request.method == 'POST':
        nama_perpus = request.form['nama_perpus']
        kecamatan = request.form['kecamatan']
        desa = request.form['desa']
        username = request.form['username']
        password = request.form['password']

        # 1. Buat entri PerpusDesa
        perpus = PerpusDesa(nama=nama_perpus, kecamatan=kecamatan, desa=desa)
        db.session.add(perpus)
        db.session.flush() # Untuk mendapatkan ID perpus yang baru dibuat

        # 2. Buat entri AdminPerpus yang terhubung
        admin = AdminPerpus(
            username=username,
            password=generate_password_hash(password),
            perpus_id=perpus.id
        )
        db.session.add(admin)
        db.session.commit()
        flash('Data perpustakaan berhasil ditambahkan')
        return redirect(url_for('main.tambah_perpus'))
    return render_template('superadmin/tambah_perpustakaan.html')

@bp.route('/superadmin/verifikasi-admin')
@super_admin_required
def verifikasi_admin():
    # Ini harusnya mem-filter AdminPerpus, bukan User
    daftar_admin = AdminPerpus.query.filter_by(verified=False).all()
    return render_template('superadmin/verifikasi_admin.html', daftar_admin=daftar_admin)

@bp.route('/superadmin/verifikasi-admin/<int:admin_id>')
@super_admin_required
def verifikasi_admin_proses(admin_id):
    admin = AdminPerpus.query.get_or_404(admin_id)
    admin.verified = True
    db.session.commit()
    flash(f"Admin {admin.username} berhasil diverifikasi.")
    return redirect(url_for('main.verifikasi_admin'))