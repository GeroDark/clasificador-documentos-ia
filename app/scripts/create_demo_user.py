import argparse

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User

DEFAULT_EMAIL = "demo@example.com"
DEFAULT_PASSWORD = "DemoPass123!"
DEFAULT_FULL_NAME = "Demo Local User"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or reset a local demo user for API evaluation.",
    )
    parser.add_argument("--email", default=DEFAULT_EMAIL, help="Demo user email.")
    parser.add_argument(
        "--password",
        default=DEFAULT_PASSWORD,
        help="Demo user password.",
    )
    parser.add_argument(
        "--full-name",
        default=DEFAULT_FULL_NAME,
        help="Demo user display name.",
    )
    return parser.parse_args()


def create_or_reset_demo_user(email: str, password: str, full_name: str) -> tuple[User, bool]:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        created = user is None

        if user is None:
            user = User(
                email=email,
                full_name=full_name,
                password_hash=hash_password(password),
                is_active=True,
            )
            db.add(user)
        else:
            user.full_name = full_name
            user.password_hash = hash_password(password)
            user.is_active = True
            db.add(user)

        db.commit()
        db.refresh(user)
        return user, created


def main() -> None:
    args = parse_args()
    user, created = create_or_reset_demo_user(
        email=args.email,
        password=args.password,
        full_name=args.full_name,
    )

    action = "created" if created else "updated"
    print(f"Demo user {action}:")
    print(f"  id: {user.id}")
    print(f"  email: {user.email}")
    print(f"  full_name: {user.full_name}")
    print("  password: (the value passed to --password)")
    print("")
    print("Local demo credentials:")
    print(f"  email: {args.email}")
    print(f"  password: {args.password}")
    print("")
    print("Next step:")
    print("  POST /api/auth/login to obtain a Bearer token.")


if __name__ == "__main__":
    main()
