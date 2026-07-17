# saarthiIQ-Backend\create_admin.py
from app.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password


def main():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if admin:
            print("Admin already exists:", admin.email)
            return

        admin_email = "admin@saarthiiq.local"
        admin_password = "Admin@123"  # change this if needed

        new_admin = User(
            full_name="Default Admin",
            email=admin_email,
            hashed_password=hash_password(admin_password),
            role="admin",
            is_active=True,
        )
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        print("Admin created:", new_admin.email)
    finally:
        db.close()


if __name__ == "__main__":
    main()
