from getpass import getpass

from sqlalchemy import select

from app.core.security import hash_password
from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User


USERS = [
    {
        "username": "labstaff",
        "full_name": "Lab Staff",
        "role": UserRole.LAB_STAFF,
    },
    {
        "username": "itsupport",
        "full_name": "IT Support",
        "role": UserRole.IT_SUPPORT,
    },
    {
        "username": "itmanager",
        "full_name": "IT Manager",
        "role": UserRole.IT_MANAGER,
    },
]


def create_users():
    db = SessionLocal()

    try:
        for user_data in USERS:
            print("\n" + "=" * 50)
            print(f"Creating account: {user_data['full_name']}")
            print("=" * 50)

            email = input("Gmail: ").strip().lower()
            password = getpass("Password: ")

            if len(password) < 8:
                print("Password must be at least 8 characters.")
                continue

            # Check whether email already exists
            existing_email = db.scalar(
                select(User).where(User.email == email)
            )

            if existing_email:
                print(f"User with {email} already exists. Skipping.")
                continue

            # Check whether username already exists
            existing_username = db.scalar(
                select(User).where(
                    User.username == user_data["username"]
                )
            )

            if existing_username:
                print(
                    f"Username '{user_data['username']}' already exists. "
                    "Skipping."
                )
                continue

            # Create user
            user = User(
                username=user_data["username"],
                email=email,
                full_name=user_data["full_name"],
                role=user_data["role"],
                hashed_password=hash_password(password),
                is_active=True,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            print(f"✓ {user_data['full_name']} account created successfully.")

        print("\nAll users processed.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_users()