from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User

DEFAULT_PASSWORDS = {
    UserRole.IT_MANAGER: "ChangeMe_Manager123",
    UserRole.IT_SUPPORT: "ChangeMe_Support123",
    UserRole.LAB_STAFF: "ChangeMe_LabStaff123",
}


def run():
    db = SessionLocal()
    try:
        for role, pwd in DEFAULT_PASSWORDS.items():
            if db.query(User).filter(User.role == role).first():
                print(f"skip: {role.value} already exists")
                continue
            db.add(User(username=role.value, hashed_password=hash_password(pwd), role=role, is_active=True))
            print(f"created: {role.value} / {pwd}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()