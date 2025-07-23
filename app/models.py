from . import db
from flask_login import UserMixin
from sqlalchemy.schema import UniqueConstraint
from datetime import datetime

# Model User
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
    )

class Donasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    whatsapp = db.Column(db.String(20), nullable=False)
    alamat = db.Column(db.Text, nullable=False)
    metode = db.Column(db.String(100), nullable=False)
    catatan = db.Column(db.Text)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)

class DetailDonasi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donasi_id = db.Column(db.Integer, db.ForeignKey('donasi.id'), nullable=False)
    subjek_buku = db.Column(db.String(100), nullable=False)
    jumlah = db.Column(db.Integer, nullable=False)

class BuktiPengiriman(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donasi_id = db.Column(db.Integer, db.ForeignKey('donasi.id'), nullable=False)
    bukti_resi = db.Column(db.String(255))
    tanggal_pengiriman = db.Column(db.Date, nullable=False)

class KebutuhanKoleksi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama_perpustakaan = db.Column(db.String(100), nullable=False)
    subjek = db.Column(db.String(100), nullable=False)
    jumlah_buku = db.Column(db.Integer, nullable=False)
    prioritas = db.Column(db.String(20), nullable=False)
    lokasi = db.Column(db.String(100))
    alasan = db.Column(db.Text)
    tanggal_pengajuan = db.Column(db.DateTime, default=datetime.utcnow)

class Kunjungan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tanggal = db.Column(db.Date, default=datetime.utcnow)

class PerpusDesa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    kecamatan = db.Column(db.String(100), nullable=False)
    desa = db.Column(db.String(100), nullable=False)

class AdminPerpus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    verified = db.Column(db.Boolean, default=False)
    
    # Foreign Key ke PerpusDesa
    perpus_id = db.Column(db.Integer, db.ForeignKey('perpus_desa.id'))
    perpus = db.relationship('PerpusDesa', backref='admin')