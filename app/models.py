
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship 
from sqlalchemy import ForeignKey, String, Float, DateTime
from typing import List 
from datetime import datetime 


# Create base class
class Base(DeclarativeBase): 
    pass 

db = SQLAlchemy(model_class = Base)

# User Table 
class User(Base): 
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(100), nullable = False)
    email: Mapped[str] = mapped_column(String(200), unique = True)
    password: Mapped[str] = mapped_column(String(30))
    role: Mapped[str] = mapped_column(String(20), default = "user")

    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates = "user")

# Plan Table 
class Plan(Base): 
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key = True)
    name: Mapped[str] = mapped_column(String(100), nullable = False)
    price: Mapped[float] = mapped_column(Float)
    billing_cycle: Mapped[str] = mapped_column(String(15))

    subscriptions: Mapped[List["Subscription"]] = relationship(back_populates = "plan")

# Subscription Table 
class Subscription(Base): 
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(primary_key = True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    status: Mapped [str] = mapped_column(String(20), default = "active")
    start_date: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates = "subscriptions")
    plan: Mapped["Plan"] = relationship(back_populates = "subscriptions")
    payments: Mapped[List["Payment"]] = relationship(back_populates = "subscription")
    invoices: Mapped[List["Invoice"]] = relationship(back_populates = "subscription")

# Payment Table 
class Payment(Base): 
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key = True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    amount: Mapped[float] = mapped_column(Float)
    payment_date: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    subscription: Mapped["Subscription"] = relationship(back_populates = "payments")

# Invoice Table 
class Invoice(Base): 
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key = True)
    subscription_id: Mapped[int] = mapped_column(ForeignKey("subscriptions.id"))
    amount: Mapped[float] = mapped_column(Float)
    issued_date: Mapped[datetime] = mapped_column(DateTime, default = datetime.utcnow)

    subscription: Mapped["Subscription"] = relationship(back_populates = "invoices")