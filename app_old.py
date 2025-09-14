from flask import Flask, render_template, redirect, url_for, session, request, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from authlib.integrations.flask_client import OAuth
from datetime import datetime
from sqlalchemy import func
import os
import pdfkit

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from functools import wraps  # ✅ WAJIB, karena decorator butuh ini

from app.models import db, User, Donasi, DetailDonasi, BuktiPengiriman, KebutuhanKoleksi, Kunjungan, PerpusDesa, AdminPerpus

app = Flask(__name__)
app.config['SECRET_KEY'] = 'rahasia123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = 'static/uploads/resi'
PDF_FOLDER = 'static/pdf'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(PDF_FOLDER, exist_ok=True)

db.init_app(app)
from flask_migrate import Migrate
migrate = Migrate(app, db)
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id='ISI_CLIENT_ID',
    client_secret='ISI_CLIENT_SECRET',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'role' not in session or session['role'] != 'superadmin':
            flash("Anda tidak memiliki izin akses sebagai superadmin.", "danger")
            return redirect(url_for('login_superadmin'))
        return f(*args, **kwargs)
    return decorated_function

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

with app.app_context():
    db.create_all()

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_request():
    return dict(request=request)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['nama'] = user.full_name
            return redirect(url_for('home'))
        flash("Login gagal.")
        return redirect(url_for('login'))
    return render_template('pengguna/login.html')  

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        password = request.form.get('password')
        terms = request.form.get('terms')

        if not terms:
            flash("Anda harus menyetujui Syarat.")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash("Email sudah terdaftar.")
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password)
        user = User(full_name=full_name, phone_number=phone_number, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Registrasi berhasil!")
        return redirect(url_for('login'))
    return render_template('pengguna/register.html') 

@app.route('/google_login')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/google_authorize')
def google_authorize():
    token = google.authorize_access_token()
    user_info = google.get('userinfo').json()
    email = user_info['email']
    full_name = user_info.get('name', 'Pengguna Google')

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(full_name=full_name, phone_number='', email=email, password='')
        db.session.add(user)
        db.session.commit()

    session['user_id'] = user.id
    session['nama'] = user.full_name
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/formulir-donasi', methods=['GET', 'POST'])
def formulir_donasi():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        if not request.form.get('setuju_syarat') or not request.form.get('setuju_pengiriman'):
            flash("Persetujuan diperlukan.")
            return redirect(url_for('formulir_donasi'))

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
        return redirect(url_for('konfirmasi_donasi', id=donasi.id))

    return render_template('pengguna/form_donasi.html', user=user)

@app.route('/konfirmasi-donasi/<int:id>', methods=['GET', 'POST'])
def konfirmasi_donasi(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    donasi = Donasi.query.get_or_404(id)
    if request.method == 'POST':
        bukti_resi = request.files.get('bukti_resi')
        tanggal_pengiriman = request.form.get('tanggal_pengiriman')
        if not bukti_resi or not allowed_file(bukti_resi.filename):
            flash("File tidak valid.")
            return redirect(url_for('konfirmasi_donasi', id=id))

        filename = secure_filename(bukti_resi.filename)
        bukti_resi.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        bukti = BuktiPengiriman(
            donasi_id=id,
            bukti_resi=filename,
            tanggal_pengiriman=datetime.strptime(tanggal_pengiriman, '%Y-%m-%d').date()
        )
        db.session.add(bukti)
        db.session.commit()
        return redirect(url_for('konfirmasi_berhasil'))

    return render_template('pengguna/konfirmasi_donasi.html', donasi=donasi)

@app.route('/konfirmasi-berhasil')
def konfirmasi_berhasil():
    return render_template('pengguna/konfirmasi_berhasil.html')

from datetime import datetime

@app.route('/donasi-sukses')
def donasi_sukses():
    current_year = datetime.now().year
    return render_template('donasi_berhasil.html', current_year=current_year)

@app.route('/bukti-donasi')
def bukti_donasi():
    if 'user_id' not in session or 'last_donation_id' not in session:
        return redirect(url_for('login'))

    donasi_id = session['last_donation_id']
    donasi = Donasi.query.get_or_404(donasi_id)
    detail = DetailDonasi.query.filter_by(donasi_id=donasi_id).all()
    bukti = BuktiPengiriman.query.filter_by(donasi_id=donasi_id).first()
    nomor_donasi = f"DN-{donasi.tanggal.strftime('%Y%m%d')}-{str(donasi.id).zfill(3)}"

    return render_template('pengguna/bukti_donasi.html', donasi=donasi, detail_buku=detail, bukti=bukti, nomor_donasi=nomor_donasi)

@app.route('/unduh-bukti-donasi')
def generate_pdf():
    if 'user_id' not in session or 'last_donation_id' not in session:
        return redirect(url_for('login'))

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

    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    pdf_path = os.path.join(PDF_FOLDER, f'bukti_donasi_{donasi_id}.pdf')
    pdfkit.from_string(
        rendered,
        pdf_path,
        configuration=config,
        options={'enable-local-file-access': ''}
    )

    return send_file(pdf_path, as_attachment=True)


@app.route('/')
def home():
    return render_template('pengguna/index.html')

@app.route('/syarat')
def syarat(): return render_template('pengguna/syarat_ketentuan.html')

@app.route('/transparansi')
def transparansi():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pengguna/transparansi_donasi.html')

@app.route('/riwayat')
def riwayat():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('pengguna/riwayat_transparansi.html')

@app.route('/faq')
def faq(): return render_template('pengguna/faq.html')

@app.route('/kontak')
def kontak(): return render_template('pengguna/kontak.html')

@app.route('/profil')
def profil(): return render_template('pengguna/profil.html')

@app.route('/panduan-donasi')
def panduan_donasi(): return render_template('pengguna/panduan_donasi.html')

@app.route('/perpusdes')
def perpusdes():
    return render_template('pengguna/perpusdes.html',
        kecamatan_list=['Tempeh', 'Lumajang', 'Yosowilangun'],
        desa_list=['Desa A', 'Desa B', 'Desa C'],
        perpustakaan_list=['Perpus A', 'Perpus B', 'Perpus C']
    )

@app.route('/admin/tambah-kunjungan', methods=['POST'])
def tambah_kunjungan():
    kunjungan = Kunjungan()
    db.session.add(kunjungan)
    db.session.commit()
    flash("Kunjungan berhasil ditambahkan!", "success")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/kurangi-kunjungan', methods=['POST'])
def kurangi_kunjungan():
    kunjungan_terakhir = Kunjungan.query.order_by(Kunjungan.id.desc()).first()
    if kunjungan_terakhir:
        db.session.delete(kunjungan_terakhir)
        db.session.commit()
        flash("Kunjungan berhasil dikurangi!", "success")
    else:
        flash("Tidak ada kunjungan yang bisa dikurangi.", "warning")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    from sqlalchemy import extract
    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year

    total_buku_pusat = 120
    total_donasi_buku = DetailDonasi.query.count()
    total_kegiatan = 5
    persentase_kenaikan_koleksi = 10
    total_kunjungan_bulan_ini = Kunjungan.query.filter(
        extract('month', Kunjungan.tanggal) == bulan_ini,
        extract('year', Kunjungan.tanggal) == tahun_ini
    ).count()

    return render_template('admin/dashboard.html',
        total_buku_pusat=total_buku_pusat,
        total_donasi_buku=total_donasi_buku,
        total_kegiatan=total_kegiatan,
        persentase_kenaikan_koleksi=persentase_kenaikan_koleksi,
        total_kunjungan_bulan_ini=total_kunjungan_bulan_ini,
        notif_koleksi_pending="2 kebutuhan koleksi menunggu verifikasi.",
        notif_distribusi_pending="1 distribusi buku belum dikonfirmasi.",
        notif_kegiatan_blm_lengkap="Lengkapi data kegiatan perpustakaan untuk laporan tahunan."
    )

@app.route('/admin/profil-perpustakaan', methods=['GET', 'POST'])
def admin_profil_perpustakaan():
    if request.method == 'POST':
        print("Data masuk:")
        print("Nama Perpus:", request.form.get('nama'))
        print("perpustakaan:", request.form.get('jumlah_perpustakaan'))
        flash("Data berhasil disimpan!", "success")
        return redirect(url_for('admin_profil_perpustakaan'))
    return render_template('admin/profil_perpustakaan.html')

@app.route('/admin/simpan-profil', methods=['POST'])
def simpan_profil_perpus():
    penanggung_jawab = request.form.get('penanggung_jawab')
    deskripsi = request.form.get('deskripsi')
    foto = request.files.get('foto')

    if foto:
        filename = secure_filename(foto.filename)
        foto.save(os.path.join('static/uploads/foto_profil', filename))

    flash("Profil perpustakaan berhasil diunggah.")
    return redirect(url_for('admin_profil_perpustakaan'))

@app.route('/admin/kebutuhan-koleksi', methods=['GET', 'POST'])
def kebutuhan_koleksi():
    if request.method == 'POST':
        nama_perpus = request.form.get('nama_perpustakaan')
        subjek = request.form.get('subjek')
        jumlah = request.form.get('jumlah_buku')
        prioritas = request.form.get('prioritas')
        lokasi = request.form.get('lokasi')
        alasan = request.form.get('alasan')

        if not nama_perpus or not subjek or not jumlah or not prioritas:
            flash("Semua field wajib diisi.", "error")
            return redirect(url_for('kebutuhan_koleksi'))

        kebutuhan = KebutuhanKoleksi(
            nama_perpustakaan=nama_perpus,
            subjek=subjek,
            jumlah_buku=int(jumlah),
            prioritas=prioritas,
            lokasi=lokasi,
            alasan=alasan
        )
        db.session.add(kebutuhan)
        db.session.commit()
        flash("Pengajuan kebutuhan berhasil dikirim.", "success")
        return redirect(url_for('kebutuhan_koleksi'))

    return render_template('admin/kebutuhan_koleksi.html')

@app.route('/admin/lihat-kebutuhan-koleksi')
def lihat_kebutuhan_koleksi():
    data_kebutuhan = KebutuhanKoleksi.query.order_by(KebutuhanKoleksi.tanggal_pengajuan.desc()).all()
    return render_template('admin/lihat_kebutuhan_koleksi.html', data_kebutuhan=data_kebutuhan)

@app.route('/admin/kegiatan-perpus', methods=['GET', 'POST'])
def kegiatan_perpus():
    return render_template('admin/kegiatan_perpus.html')

@app.route('/admin/riwayat-distribusi')
def riwayat_distribusi():
    return render_template('admin/riwayat_distribusi.html')

@app.route('/superadmin/tampilan_depan')
@super_admin_required
def tampilan_depan():
    if 'user_id' not in session or session.get('role') != 'superadmin':
        flash('Anda harus login sebagai Super Admin.', 'danger')
        return redirect(url_for('login'))

    try:
        from sqlalchemy import func
        from datetime import datetime

        total_donatur = User.query.filter((User.role == None) | (User.role == 'user')).count()
        total_buku = db.session.query(func.sum(DetailDonasi.jumlah)).scalar() or 0
        total_perpus = PerpusDesa.query.count()

        permintaan_list = KebutuhanKoleksi.query.order_by(
            KebutuhanKoleksi.tanggal_pengajuan.desc()
        ).limit(3).all()

        # ✅ Bagian yang penting ini:
        riwayat_donasi_raw = (
            db.session.query(DetailDonasi, Donasi)
            .join(Donasi, Donasi.id == DetailDonasi.donasi_id)
            .order_by(Donasi.tanggal.desc())
            .limit(3)
            .all()
        )

        # Format agar tidak error di template
        riwayat_donasi = [{
            'subjek': d.subjek_buku,
            'jumlah': d.jumlah,
            'donatur': {'full_name': donasi.nama}
        } for d, donasi in riwayat_donasi_raw]

        current_year = datetime.now().year

        return render_template(
            'superadmin/tampilan_depan.html',
            total_donatur=total_donatur,
            total_buku=total_buku,
            total_perpus=total_perpus,
            permintaan_list=permintaan_list,
            riwayat_donasi=riwayat_donasi,
            current_year=current_year
        )
    except Exception as e:
        import traceback
        return f"<h3>❌ ERROR:</h3><pre>{traceback.format_exc()}</pre>"

@app.route('/superadmin/login', methods=['GET', 'POST'])
def login_superadmin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username, role='superadmin').first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['role'] = user.role
            return redirect(url_for('tampilan_depan'))
        else:
            flash("Login gagal. Username atau password salah.")
            return render_template('superadmin/login.html')  # tampilkan form lagi kalau gagal

    return render_template('superadmin/login.html')  # tampilkan form login pertama kali

# Lihat Daftar Perpustakaan
@app.route('/superadmin/perpusdes')
def daftar_perpustakaan():
    # Cek apakah user sudah login dan peran adalah superadmin
    if 'user_id' not in session or session.get('role') != 'superadmin':
        flash('Anda tidak memiliki akses ke halaman ini.', 'danger')
        return redirect(url_for('login'))

    # Ambil data perpustakaan dan admin yang terkait
    data_perpus = db.session.query(PerpusDesa, AdminPerpus).join(AdminPerpus, AdminPerpus.perpus_id == PerpusDesa.id).all()
    
    return render_template('superadmin/perpusdesa.html', data_perpus=data_perpus)

@app.route('/tambah-perpustakaan', methods=['GET', 'POST'])
def tambah_perpus():
    if request.method == 'POST':
        nama_perpus = request.form['nama_perpus']
        kecamatan = request.form['kecamatan']
        desa = request.form['desa']
        username = request.form['username']
        password = request.form['password']

        admin = AdminPerpus(
            nama_perpus=nama_perpus,
            kecamatan=kecamatan,
            desa=desa,
            username=username
        )
        admin.set_password(password)

        db.session.add(admin)
        db.session.commit()
        flash('Data perpustakaan berhasil ditambahkan')
        return redirect(url_for('tambah_perpus'))
    
    return render_template('superadmin/tambah_perpustakaan.html')

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, role='admin').first()
        if user and user.is_verified and check_password_hash(user.password, password):
            session['admin_id'] = user.id
            if user.perpus:
                session['nama_perpus'] = user.perpus.nama
                session['perpus_id'] = user.perpus.id
            return redirect(url_for('dashboard_admin'))
        else:
            flash('Login gagal. Username atau password salah.')
            return redirect(url_for('login_admin'))

    return render_template('admin/login_admin.html')

@app.route('/logout-admin', endpoint='admin_logout')
def logout_admin():
    session.pop('admin_id', None)
    return redirect(url_for('login_admin'))

@app.route('/superadmin/data-admin')
@super_admin_required
def data_admin():
    return render_template('superadmin/data_admin.html')


@app.route('/halaman-privat')
@login_required
def halaman_privat():
    return render_template('privat.html')

@app.route('/superadmin/verifikasi-admin')
@super_admin_required
def verifikasi_admin():
    return render_template('superadmin/verifikasi_admin.html')


if __name__ == '__main__':
    app.run(debug=True)
