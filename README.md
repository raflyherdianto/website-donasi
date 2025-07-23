# Website Donasi Buku Kabupaten Lumajang

Aplikasi web berbasis Flask yang dirancang untuk memfasilitasi dan mengelola donasi buku dari masyarakat untuk disalurkan ke perpustakaan desa (perpusdes) di seluruh Kabupaten Lumajang.

## 📋 Daftar Isi
- [Fitur Utama](#-fitur-utama)
- [Tumpukan Teknologi](#-tumpukan-teknologi-tech-stack)
- [Prasyarat](#-prasyarat)
- [Instalasi dan Setup](#-instalasi-dan-setup-awal)
- [Menjalankan Aplikasi](#-menjalankan-aplikasi)
- [Struktur Proyek](#-struktur-proyek)
- [Kredensial Awal](#-kredensial-awal)
- [Fitur dan Halaman](#-fitur-dan-halaman)
- [Database](#-database)
- [Troubleshooting](#-troubleshooting)

## 🚀 Fitur Utama

### Untuk Donatur (Pengguna Umum)
- **Registrasi & Login**: Sistem autentikasi pengguna dengan enkripsi password
- **Formulir Donasi**: Interface yang user-friendly untuk mengisi data donasi buku
- **Bukti Donasi PDF**: Sistem otomatis menghasilkan bukti donasi dalam format PDF
- **Transparansi**: Halaman untuk melihat riwayat dan transparansi donasi
- **FAQ & Panduan**: Informasi lengkap tentang cara berdonasi

### Untuk Admin Perpustakaan Desa
- **Dashboard Admin**: Panel kontrol untuk mengelola data perpustakaan
- **Pengajuan Kebutuhan**: Sistem untuk mengajukan kebutuhan koleksi buku
- **Manajemen Kunjungan**: Pencatatan dan monitoring kunjungan perpustakaan
- **Profil Perpustakaan**: Pengelolaan informasi dan profil perpustakaan
- **Riwayat Distribusi**: Monitoring distribusi buku yang diterima

### Untuk Super Admin (Dinas)
- **Panel Superadmin**: Dashboard utama untuk monitoring seluruh sistem
- **Manajemen Perpustakaan**: CRUD operations untuk data perpustakaan desa
- **Verifikasi Admin**: Sistem verifikasi untuk admin perpustakaan baru
- **Import Data**: Bulk import data perpustakaan dari file Excel
- **Laporan & Statistik**: Dashboard dengan data statistik lengkap

## 🛠 Tumpukan Teknologi (Tech Stack)

### Backend
- **Flask 3.0.3**: Web framework utama
- **Flask-SQLAlchemy**: ORM untuk database operations
- **Flask-Migrate**: Database migration management
- **Flask-Login**: User session management
- **SQLite**: Database (production-ready untuk skala menengah)

### Frontend
- **Jinja2**: Template engine
- **HTML5 & CSS3**: Markup dan styling
- **JavaScript**: Interaktivitas frontend

### Libraries & Tools
- **Pandas**: Data processing untuk import Excel
- **pdfkit**: PDF generation
- **Werkzeug**: Security utilities
- **Authlib**: OAuth integration (untuk ekspansi masa depan)

## 📋 Prasyarat

Pastikan sistem Anda telah terinstal:

1. **Python 3.8+**: Preferably Python 3.10 atau lebih baru
2. **Git**: Untuk version control dan cloning repository
3. **wkhtmltopdf**: Required untuk PDF generation
   - Download dari [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)
   - **Windows**: Install di `C:\Program Files\wkhtmltopdf\`
   - **Linux**: `sudo apt-get install wkhtmltopdf` (Ubuntu/Debian)
   - **macOS**: `brew install wkhtmltopdf`

## 🔧 Instalasi dan Setup Awal

### 1. Clone Repository
```bash
git clone https://github.com/your-username/website-donasi.git
cd website-donasi
```

### 2. Buat Virtual Environment
```bash
# Menggunakan venv (built-in Python)
python -m venv venv

# Aktivasi environment
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# ATAU menggunakan conda
conda create --name donasi-env python=3.10
conda activate donasi-env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment
Buat file `.flaskenv` di root directory:
```
FLASK_APP=run.py
FLASK_ENV=development
```

### 5. Setup Database
```bash
# Initialize migration repository (only once)
flask db init

# Create initial migration
flask db migrate -m "Initial database migration"

# Apply migration to create tables
flask db upgrade
```

### 6. Import Data Awal
Pastikan file `DATA PERPUSDES & TBM.xlsx` ada di root directory, kemudian:
```bash
python setup.py
```

Script ini akan:
- Membuat akun superadmin default
- Import data perpustakaan dari Excel
- Setup admin untuk setiap perpustakaan

## 🚀 Menjalankan Aplikasi

### Development Mode
```bash
flask run --debug
```

### Production Mode
```bash
flask run --host=0.0.0.0 --port=80
```

Aplikasi akan berjalan di: **http://127.0.0.1:5000**

## 📁 Struktur Proyek

```
website-donasi/
├── app/
│   ├── __init__.py          # App factory dan konfigurasi
│   ├── models.py            # Database models
│   ├── routes.py            # Route handlers
│   ├── commands.py          # CLI commands
│   ├── static/              # CSS, JS, images
│   │   ├── uploads/         # Uploaded files
│   │   └── pdf/             # Generated PDFs
│   └── templates/           # Jinja2 templates
│       ├── pengguna/        # User templates
│       ├── admin/           # Admin templates
│       └── superadmin/      # Superadmin templates
├── instance/
│   └── users.db             # SQLite database
├── migrations/              # Database migrations
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
├── setup.py                # Initial setup script
└── README.md               # Project documentation
```

## 🔑 Kredensial Awal

### Super Admin
- **URL**: `/superadmin/login`
- **Username**: `superadmin`
- **Password**: `admin123`

### Admin Perpustakaan (Contoh)
- **URL**: `/login-admin`
- **Username**: Format: `{nama_perpus}_{kecamatan}` (lowercase, spasi jadi underscore)
- **Password**: Format: `{nama_desa_tanpa_spasi}123` (lowercase)

Contoh:
- **Username**: `ceria_candipuro`
- **Password**: `kloposawit123`

## 📱 Fitur dan Halaman

### Pengguna Umum
| URL | Deskripsi |
|-----|-----------|
| `/` | Halaman utama |
| `/register` | Registrasi pengguna baru |
| `/login` | Login pengguna |
| `/formulir-donasi` | Form donasi buku |
| `/konfirmasi-donasi/<id>` | Upload bukti pengiriman |
| `/unduh-bukti-donasi` | Download PDF bukti donasi |
| `/transparansi` | Transparansi donasi |
| `/perpusdes` | Info perpustakaan desa |

### Admin Perpustakaan
| URL | Deskripsi |
|-----|-----------|
| `/login-admin` | Login admin |
| `/admin/dashboard` | Dashboard admin |
| `/admin/profil-perpustakaan` | Manajemen profil |
| `/admin/kebutuhan-koleksi` | Pengajuan kebutuhan |
| `/admin/kegiatan-perpus` | Manajemen kegiatan |

### Super Admin
| URL | Deskripsi |
|-----|-----------|
| `/superadmin/login` | Login superadmin |
| `/superadmin/tampilan_depan` | Dashboard utama |
| `/superadmin/perpusdes` | Manajemen perpustakaan |
| `/tambah-perpustakaan` | Tambah perpustakaan baru |
| `/superadmin/verifikasi-admin` | Verifikasi admin |

## 🗄 Database

### Models Utama
- **User**: Data pengguna dan admin
- **Donasi**: Data donasi utama
- **DetailDonasi**: Detail buku yang didonasikan
- **BuktiPengiriman**: Bukti pengiriman donasi
- **PerpusDesa**: Data perpustakaan desa
- **AdminPerpus**: Admin perpustakaan
- **KebutuhanKoleksi**: Pengajuan kebutuhan buku
- **Kunjungan**: Data kunjungan perpustakaan

### Database Migration
```bash
# Membuat migration baru setelah perubahan model
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

## 🐛 Troubleshooting

### Error: "wkhtmltopdf not found"
**Solusi**: 
- Pastikan wkhtmltopdf terinstall
- Periksa path di `routes.py` pada bagian `pdfkit.configuration()`
- Windows: Pastikan installed di `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`

### Error Database Migration
**Solusi**:
```bash
# Hapus folder migrations dan database
rm -rf migrations/
rm instance/users.db

# Inisialisasi ulang
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python setup.py
```

### Error Import Excel
**Solusi**:
- Pastikan file `DATA PERPUSDES & TBM.xlsx` ada di root directory
- Periksa format kolom Excel sesuai dengan yang expected di `commands.py`
- Install openpyxl: `pip install openpyxl`

### Port Already in Use
**Solusi**:
```bash
# Gunakan port lain
flask run --port=8000

# Atau kill process yang menggunakan port 5000
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID_NUMBER> /F

# Linux/macOS
lsof -ti:5000 | xargs kill -9
```

## 📞 Support

Jika mengalami masalah atau memiliki pertanyaan:

1. Periksa bagian [Troubleshooting](#-troubleshooting)
2. Buat issue di GitHub repository
3. Hubungi developer atau tim IT

## 📄 License

Project ini dikembangkan untuk Dinas Kearsipan dan Perpustakaan Kabupaten Lumajang.

---

**Developed with ❤️ for Kabupaten Lumajang**
