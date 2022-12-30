import enum
import sqlalchemy.ext.declarative

Base = sqlalchemy.ext.declarative.declarative_base()


class AccountSource(enum.Enum):
    max = "max"
    leumi = "leumi"


class Account(Base):
    __tablename__ = "accounts"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    source = sqlalchemy.Column(sqlalchemy.Enum(AccountSource), nullable=False)
    username = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    last_synced = sqlalchemy.Column(sqlalchemy.Date, nullable=True)

    def __repr__(self):
        return f'<Account id={self.id} name={self.name} source={self.source} last_synced={self.last_synced}>'


class Category(Base):
    __tablename__ = "categories"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    is_expense = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    order = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    exclude_from_reports = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<Category id={self.id} name={self.name} is_expense={self.is_expense}>'


class Subcategory(Base):
    __tablename__ = "subcategories"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    category_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Category.id), nullable=False)

    def __repr__(self):
        return f'<Subcategory id={self.id} name={self.name} category_id={self.category_id}>'


class Payee(Base):
    __tablename__ = "payees"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False, unique=True)
    subcategory_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Subcategory.id), nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String, default="")

    def __repr__(self):
        return f'<Payee id={self.id} name={self.name} ' \
               f'subcategory_id={self.subcategory_id} note={self.note}>'


class Transaction(Base):
    __tablename__ = "transactions"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    date = sqlalchemy.Column(sqlalchemy.Date, nullable=False)
    amount = sqlalchemy.Column(sqlalchemy.Float, nullable=False)
    account_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Account.id), nullable=False)
    payee_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Payee.id), nullable=False)
    subcategory_id = sqlalchemy.Column(
        sqlalchemy.Integer, sqlalchemy.ForeignKey(Subcategory.id), nullable=True)
    note = sqlalchemy.Column(sqlalchemy.String, default="")

    def __repr__(self):
        return f'<Transaction id={self.id} date={self.date} amount={self.amount} ' \
               f'account_id={self.account_id} payee_id={self.payee_id} ' \
               f'subcategory_id={self.subcategory_id} note={self.note}>'
