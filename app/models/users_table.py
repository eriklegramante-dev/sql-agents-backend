import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, Date, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserRole(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    cpf = Column(String(11), nullable=False, unique=True)
    birth_date = Column(Date, nullable=False)
    password = Column(String(128), nullable=False)
    country = Column(String(50), nullable=True)
    role = Column(
        Enum(UserRole, name="userrole"), nullable=False, default=UserRole.USER
    )
    status = Column(
        Enum(UserStatus, name="userstatus"),
        nullable=False,
        default=UserStatus.ACTIVE,
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
