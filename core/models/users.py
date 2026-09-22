from sqlalchemy import Column, String, Boolean, DateTime, text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import validates
from core.database import Base
from passlib.context import CryptContext
from uuid6 import uuid7
import enum


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserType(enum.Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"


class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid7)
    username = Column(String(255), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    type = Column(String(255), nullable=False,
                  server_default=text(f"'{UserType.CUSTOMER.value}'"))
    is_active = Column(Boolean, server_default=text("true"))
    is_profile_complete = Column(Boolean, server_default=text("false"))
    created_date = Column(DateTime(timezone=True), server_default=func.now())
    updated_date = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


    def hash_password(self, plain_password: str) -> str:
        """hashed the given password using bcrypt"""
        return pwd_context.hash(plain_password)

    def verify_password(self, plain_password: str) -> bool:
        """verified the given password against the stored hash"""
        return pwd_context.verify(plain_password, self.password)

    def set_password(self, plain_text: str) -> None:
        self.password = self.hash_password(plain_text)

    @validates("type")
    def validate_admin(self, key, value):
        if value == UserType.ADMIN:
            from sqlalchemy.orm import Session
            session = Session.object_session(self)
            count = session.query(UserModel).filter(UserModel.type == UserType.ADMIN).count()
            if count > 0 and not self.id:
                raise ValueError("Only one admin is allowed in the system.")
        return value