import enum
import sqlalchemy.ext.declarative
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
Base = sqlalchemy.ext.declarative.declarative_base()


class AccountSource(enum.Enum):
    max = "max"
    leumi = "leumi"


class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    source = Column(Enum(AccountSource), nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    last_synced = Column(Date, nullable=True)

    def __repr__(self):
        return f'<Account id={self.id} name={self.name} source={self.source} last_synced={self.last_synced}>'


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    is_expense = Column(sqlalchemy.Boolean, nullable=False)
    order = Column(Integer, nullable=False)
    exclude_from_reports = Column(sqlalchemy.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Category id={self.id} name={self.name} is_expense={self.is_expense}>'


class Subcategory(Base):
    __tablename__ = "subcategories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    category_id = Column(
        Integer, ForeignKey(Category.id), nullable=False)

    def __repr__(self):
        return f'<Subcategory id={self.id} name={self.name} category_id={self.category_id}>'


class Payee(Base):
    __tablename__ = "payees"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    subcategory_id = Column(
        Integer, ForeignKey(Subcategory.id), nullable=True)
    note = Column(String, default="")
    transactions = relationship("Transaction", back_populates="payee")

    def __repr__(self):
        return f'<Payee id={self.id} name={self.name} ' \
               f'subcategory_id={self.subcategory_id} note={self.note}>'


class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True)
    date = Column(Date, nullable=False)
    amount = Column(sqlalchemy.Float, nullable=False)
    account_id = Column(
        Integer, ForeignKey(Account.id), nullable=False)
    payee_id = Column(
        Integer, ForeignKey(Payee.id), nullable=False)
    override_subcategory = Column(sqlalchemy.Boolean, nullable=False, default=False)
    subcategory_id = Column(
        Integer, ForeignKey(Subcategory.id), nullable=True)
    note = Column(String, default="")
    payee = relationship("Payee", back_populates="transactions")


    def __repr__(self):
        return f'<Transaction id={self.id} date={self.date} amount={self.amount} ' \
               f'account_id={self.account_id} payee_id={self.payee_id} ' \
               f'subcategory_id={self.subcategory_id} note={self.note}>'
