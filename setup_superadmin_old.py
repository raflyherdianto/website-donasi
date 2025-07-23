from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

# Buat instance aplikasi untuk mendapatkan konteks
app = create_app()

with app.app_context():
    # Cek apakah superadmin sudah ada
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