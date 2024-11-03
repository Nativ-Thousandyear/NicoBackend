from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='regular_user')

    def is_active(self) -> bool:
        """Return True if the user is active."""
        return True

    def set_password(self, password: str) -> None:
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check the user's password against the stored password hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User id={self.id}, username={self.username}, role={self.role}>'