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
- [API Endpoints](#-api-endpoints)
- [Troubleshooting](#-troubleshooting)

## 🚀 Fitur Utama

### Untuk Donatur (Pengguna Umum)
- **Registrasi & Login**: Sistem autentikasi pengguna dengan enkripsi password
- **Formulir Donasi**: Interface yang user-friendly untuk mengisi data donasi buku dengan multiple subjek
- **Bukti Donasi PDF**: Sistem otomatis menghasilkan bukti donasi dalam format PDF
- **Konfirmasi Donasi**: Upload bukti pengiriman dengan validasi file gambar
- **Transparansi**: Halaman untuk melihat riwayat dan transparansi donasi dengan detail distribusi
- **Portal Berita**: Sistem berita dengan search functionality dan pagination
- **FAQ & Panduan**: Informasi lengkap tentang cara berdonasi
- **Directory Perpustakaan**: Daftar lengkap perpustakaan desa dengan informasi detail

### Untuk Admin Perpustakaan Desa
- **Dashboard Admin**: Panel kontrol dengan statistik kunjungan dan kegiatan perpustakaan
- **Profil Perpustakaan**: Pengelolaan informasi dan profil perpustakaan lengkap dengan foto dan lokasi GPS
- **Pengajuan Kebutuhan**: Sistem untuk mengajukan kebutuhan koleksi buku dengan prioritas
- **Manajemen Kegiatan**: Upload dan kelola berita/kegiatan perpustakaan
- **Riwayat Distribusi**: Monitoring distribusi buku yang diterima
- **Analytics Kunjungan**: Pencatatan dan monitoring kunjungan perpustakaan harian/bulanan

### Untuk Super Admin (Dinas)
- **Dashboard Komprehensif**: Statistik lengkap donasi, distribusi, dan perpustakaan
- **Manajemen Donasi**: Verifikasi, penolakan, dan distribusi donasi dengan detail lengkap
- **Manajemen Perpustakaan**: CRUD operations dengan import Excel dan bulk operations
- **Verifikasi Admin**: Sistem verifikasi untuk admin perpustakaan baru
- **Riwayat Distribusi**: Monitoring distribusi dengan status tracking
- **Pengajuan Kebutuhan**: Review dan approve pengajuan dari perpustakaan
- **Subjek Buku**: Manajemen kategori subjek buku
- **Statistik**: Dashboard dengan data statistik real-time dan charts
- **Data Tables**: Interface modern dengan sorting, filtering, dan pagination

## 🛠 Tumpukan Teknologi (Tech Stack)

### Backend
- **Flask 3.0.3**: Web framework utama
- **Flask-SQLAlchemy**: ORM untuk database operations
- **Flask-Migrate**: Database migration management
- **Flask-Login**: User session management
- **SQLite**: Database (production-ready untuk skala menengah)
- **Werkzeug**: Security utilities dan file handling

### Frontend
- **Jinja2**: Template engine dengan macro system
- **TailwindCSS**: Modern utility-first CSS framework
- **DataTables**: Enhanced table functionality dengan responsive design
- **Font Awesome**: Icon library
- **Chart.js**: Data visualization (untuk dashboard statistik)
- **JavaScript ES6+**: Modern JavaScript untuk interaktivitas

### Libraries & Tools
- **Pandas**: Data processing untuk import Excel
- **pdfkit**: PDF generation untuk bukti donasi
- **Pillow (PIL)**: Image processing untuk upload gambar
- **python-slugify**: SEO-friendly URL generation
- **OpenPyXL**: Excel file handling

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
Copy file `.env.example` menjadi `.env` dan isi dengan nilai yang sesuai:
```bash
# Copy template environment file
cp .env.example .env

# Edit file .env dengan editor favorit Anda
# Windows
notepad .env
# Linux/macOS
nano .env
# atau gunakan VS Code
code .env
```

Pastikan untuk mengisi nilai yang sesuai di file `.env`, terutama:
- Email configuration untuk notifikasi
- Secret key untuk production
- Path wkhtmltopdf sesuai sistem Anda

Opsional: Buat file `.flaskenv` di root directory untuk konfigurasi Flask development:
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
- Import subjek buku default

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
│   ├── models.py            # Database models (12+ models)
│   ├── routes/              # Route handlers (terorganisir per modul)
│   │   ├── __init__.py      # Route registration
│   │   ├── public.py        # Public routes
│   │   ├── admin.py         # Admin perpustakaan routes
│   │   └── superadmin.py    # Superadmin routes
│   ├── commands.py          # CLI commands untuk setup
│   ├── static/              # Asset files
│   │   ├── css/             # Custom stylesheets
│   │   ├── js/              # JavaScript files
│   │   ├── images/          # Static images
│   │   ├── uploads/         # User uploaded files
│   │   │   ├── bukti_pengiriman/  # Bukti pengiriman donasi
│   │   │   ├── berita/            # Gambar berita
│   │   │   └── profil_perpus/     # Foto profil perpustakaan
│   │   └── pdf/             # Generated PDF files
│   └── templates/           # Jinja2 templates dengan macro system
│       ├── pengguna/        # User-facing templates
│       │   ├── base_public.html
│       │   ├── content_wrapper.html  # Reusable macros
│       │   └── ...
│       ├── admin/           # Admin perpustakaan templates
│       │   ├── base_admin.html
│       │   ├── content_wrapper.html
│       │   └── ...
│       └── superadmin/      # Superadmin templates
│           ├── base_superadmin.html
│           ├── content_wrapper.html
│           └── ...
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
| URL | Deskripsi | Status |
|-----|-----------|---------|
| `/` | Halaman utama dengan berita terkini | ✅ |
| `/register` | Registrasi pengguna baru | ✅ |
| `/login` | Login pengguna | ✅ |
| `/formulir-donasi` | Form donasi buku multi-subjek | ✅ |
| `/konfirmasi-donasi/<id>` | Upload bukti pengiriman | ✅ |
| `/unduh-bukti-donasi/<id>` | Download PDF bukti donasi | ✅ |
| `/riwayat-transparansi` | Transparansi donasi dengan detail distribusi | ✅ |
| `/perpusdes` | Directory perpustakaan desa | ✅ |
| `/berita` | Portal berita dengan search & pagination | ✅ |
| `/berita/<perpus_slug>/<slug>` | Detail berita | ✅ |
| `/profil` | Profil pengembang | ✅ |

### Admin Perpustakaan
| URL | Deskripsi | Status |
|-----|-----------|---------|
| `/login-admin` | Login admin | ✅ |
| `/admin/dashboard` | Dashboard dengan statistik | ✅ |
| `/admin/profil-perpustakaan` | Manajemen profil perpustakaan | ✅ |
| `/admin/kebutuhan-koleksi` | Pengajuan kebutuhan koleksi | ✅ |
| `/admin/kunjungan-perpus` | Manajemen data kunjungan | ✅ |
| `/admin/berita-kegiatan` | Manajemen berita/kegiatan | ✅ |
| `/admin/riwayat-distribusi` | Monitoring distribusi | ✅ |

### Super Admin
| URL | Deskripsi | Status |
|-----|-----------|---------|
| `/superadmin/login` | Login superadmin | ✅ |
| `/superadmin/dashboard` | Dashboard komprehensif | ✅ |
| `/superadmin/donasi` | Manajemen donasi lengkap | ✅ |
| `/superadmin/perpusdes` | Manajemen perpustakaan | ✅ |
| `/superadmin/verifikasi-admin` | Verifikasi admin baru | ✅ |
| `/superadmin/riwayat-distribusi` | Manajemen distribusi | ✅ |
| `/superadmin/pengajuan-perpusdes` | Review pengajuan kebutuhan | ✅ |
| `/superadmin/subjek-buku` | Manajemen kategori subjek | ✅ |

## 🗄 Database

### Models Utama
- **User**: Data pengguna dan kredensial login
- **Donasi**: Data donasi utama dengan status tracking
- **DetailDonasi**: Detail buku per subjek yang didonasikan
- **BuktiPengiriman**: Bukti pengiriman dengan validasi gambar
- **PerpusDesa**: Data perpustakaan desa lengkap
- **AdminPerpus**: Admin perpustakaan dengan verifikasi
- **KebutuhanKoleksi**: Pengajuan kebutuhan dengan prioritas
- **DetailKebutuhan**: Detail buku yang dibutuhkan per subjek
- **Kunjungan**: Data kunjungan harian perpustakaan
- **RiwayatDistribusi**: Tracking distribusi buku
- **DetailRiwayatDistribusi**: Detail distribusi per subjek
- **SubjekBuku**: Master data kategori subjek buku
- **Berita**: Sistem berita dengan slug dan metadata

### Database Migration
```bash
# Membuat migration baru setelah perubahan model
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade

# Check migration status
flask db current
flask db history
```

## 🔌 API Endpoints

### Public API
- `GET /api/perpustakaan` - Daftar perpustakaan dengan pagination
- `GET /api/berita` - Daftar berita publik

### Admin API
- `GET /admin/api/kunjungan-chart` - Data chart kunjungan

### Superadmin API
- `GET /superadmin/api/subjects` - Daftar subjek buku
- `GET /superadmin/api/available-donations` - Donasi tersedia untuk distribusi
- `POST /superadmin/api/bulk-delete` - Bulk operations

## 🐛 Troubleshooting

### Error: "wkhtmltopdf not found"
**Solusi**: 
- Pastikan wkhtmltopdf terinstall
- Periksa path di `config.py` atau environment variables
- Windows: Pastikan installed di `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
- Restart aplikasi setelah instalasi

### Error Database Migration
**Solusi**:
```bash
# Backup data jika ada
cp instance/users.db instance/users_backup.db

# Reset migrations
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Re-import data
python setup.py
```

### Error Import Excel
**Solusi**:
- Pastikan file `DATA PERPUSDES & TBM.xlsx` ada di root directory
- Periksa format kolom Excel sesuai dengan yang expected
- Install dependencies: `pip install pandas openpyxl`
- Periksa encoding file Excel (gunakan UTF-8)

### Upload File Error
**Solusi**:
- Pastikan folder `app/static/uploads/` dan subdirectories exists
- Periksa permissions folder uploads
- Validasi file size dan format yang didukung
- Check disk space

### DataTables Not Loading
**Solusi**:
- Pastikan jQuery loaded sebelum DataTables
- Check console untuk JavaScript errors
- Verify CDN links accessibility
- Clear browser cache

### PDF Generation Issues
**Solusi**:
```bash
# Test wkhtmltopdf installation
wkhtmltopdf --version

# Check path configuration
python -c "import pdfkit; print(pdfkit.configuration())"

# Install with specific path
pip install pdfkit --upgrade
```

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

## 🚀 Production Deployment

### Environment Setup
```bash
# Set production environment
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key

# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

### Database Optimization
```bash
# Enable SQLite WAL mode for better performance
sqlite3 instance/users.db "PRAGMA journal_mode=WAL;"

# Analyze database
sqlite3 instance/users.db "ANALYZE;"
```

### Security Checklist
- [ ] Change default admin passwords
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS in production
- [ ] Configure proper file upload limits
- [ ] Set up regular database backups
- [ ] Monitor application logs

## 📊 Monitoring & Analytics

### Key Metrics
- Total donasi received & distributed
- Active perpustakaan count
- User engagement metrics
- Distribution efficiency
- Popular subjek categories

### Log Files
- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Access logs: Web server dependent

## 📞 Support & Contributing

### Getting Help
1. Periksa bagian [Troubleshooting](#-troubleshooting)
2. Review existing GitHub issues
3. Create detailed bug report dengan steps to reproduce
4. Hubungi tim development

### Development Guidelines
- Follow PEP 8 Python style guide
- Use meaningful commit messages
- Write tests for new features
- Update documentation for changes
- Use virtual environment for development

### Technology Decisions
- **Flask**: Lightweight, flexible, mature ecosystem
- **SQLite**: Zero-configuration, reliable, sufficient for project scale
- **TailwindCSS**: Utility-first, responsive, maintainable
- **DataTables**: Feature-rich, accessible, mobile-friendly

## 📄 License & Credits

### Developer Information
- **Developer**: Salma Acacia Prasasta
- **Institution**: Universitas Negeri Malang
- **Program**: D4 Perpustakaan Digital
- **Supervisor**: Lidya Amalia Rahmania, S.Kom, M.Kom.

### Acknowledgments
- Dinas Kearsipan dan Perpustakaan Kabupaten Lumajang
- Tim perpustakaan desa se-Kabupaten Lumajang
- Masyarakat donatur

Project ini dikembangkan sebagai Tugas Akhir untuk memajukan literasi masyarakat melalui optimalisasi perpustakaan desa di Kabupaten Lumajang.

---

**Developed with ❤️ for Kabupaten Lumajang**

*"Donasikan buku Anda, hidupkan literasi di perpustakaan desa. Bersama kita maju bersama."*
