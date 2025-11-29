from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)

    def __repr__(self):
        return f"<User {self.username}>"
