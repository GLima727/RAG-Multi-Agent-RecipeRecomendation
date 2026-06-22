# In-memory user store: email -> hashed_password
# Replace with a real database (SQLite, Postgres) when persisting users matters.
_users: dict[str, str] = {}


def get_user(email: str) -> str | None:
    return _users.get(email)


def user_exists(email: str) -> bool:
    return email in _users


def create_user(email: str, hashed_password: str) -> None:
    _users[email] = hashed_password
