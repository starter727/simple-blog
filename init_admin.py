"""Initialize the admin user. Run once after first start."""

from app.database import SessionLocal, init_db
from app.models.user import User
from app.services.permission import hash_password
from app.config import settings


def main():
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if existing:
            print(f"User '{settings.ADMIN_USERNAME}' already exists.")
            return
        user = User(
            username=settings.ADMIN_USERNAME,
            password_hash=hash_password(settings.ADMIN_PASSWORD),
            is_admin=True,
        )
        db.add(user)
        db.commit()
        print(f"Admin user '{settings.ADMIN_USERNAME}' created.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
