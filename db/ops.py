import db.session
import db.schema
import sqlalchemy
import uuid

async def get_all(class_name, order_by_column_name):
    print(f"DB: get_all {class_name} order by {order_by_column_name}")
    db_schema_class = getattr(db.schema, class_name)
    order_by_column = getattr(db_schema_class, order_by_column_name)

    async with db.session.get_session() as s:
        sql = sqlalchemy.select(db_schema_class).order_by(order_by_column)
        recs = (await s.execute(sql)).scalars().unique().all()
        print(f'DB: get all {class_name} ordered by {order_by_column_name}:', recs)
        return recs


async def get_one_by_id(class_name, id_):
    db_schema_class = getattr(db.schema, class_name)

    async with db.session.get_session() as s:
        sql = sqlalchemy.select(db_schema_class).where(db_schema_class.id == int(id_))
        rec = (await s.execute(sql)).scalars().unique().first()
        if rec is None:
            raise Exception(f"DB: {class_name} with ID {id_} doesn't exist")
        print(f'DB: {class_name} by ID={id_}:', rec)
        return rec


async def create_account(name, source, username, password):
    print(f'DB: create_account {name} {source}')

    # don't allow empty name
    _test_not_empty(name, "Account name")

    # Check that source is valid
    all_valid_sources = ['max', 'leumi']
    if source not in all_valid_sources:
        raise Exception(f"Invalid source '{source}'. Must be one of: {all_valid_sources}")

    async with db.session.get_session() as s:

        # Check if an account with this name already exists
        await _test_doesnt_exist(s, "Account", "name", name)

        # add the account
        # TODO: encrypt username and password
        # TODO: check an account with the same source + username + password doesn't exist
        rec = db.schema.Account(name=name, source=source, username=username, password=password)
        s.add(rec)
        await s.commit()
        print(f'create_account created:', rec)
        return rec


async def create_category(name):
    print(f'DB: create_category {name}')

    # don't allow empty name for category
    _test_not_empty(name, "Category name")

    async with db.session.get_session() as s:

        # Check if a category with this name already exists
        await _test_doesnt_exist(s, "Category", "name", name)

        # add the category
        rec = db.schema.Category(name=name)
        s.add(rec)
        await s.commit()
        print(f'create_category created:', rec)
        return rec


async def create_subcategory(name, category_id):
    print(f'DB: create_subcategory {name} {category_id}')

    # don't allow empty name
    _test_not_empty(name, "Subcategory name")

    async with db.session.get_session() as s:

        # Check if a subcategory with this name already exists
        await _test_doesnt_exist(s, "Subcategory", "name", name)

        # Check if a category with this category_id exists
        await _test_exists(s, "Category", "id", category_id)

        # add the subcategory
        rec = db.schema.Subcategory(name=name, category_id=category_id)
        s.add(rec)
        await s.commit()
        print(f'create_subcategory created:', rec)
        return rec


async def create_payee(name, subcategory_id):
    print(f'DB: create_payee {name} {subcategory_id}')

    # don't allow empty name for payee
    _test_not_empty(name, "Payee name")

    async with db.session.get_session() as s:

        # Check if a payee with this name already exists
        await _test_doesnt_exist(s, "Payee", "name", name)

        if subcategory_id is not None:
            # Check if a subcategory with this subcategory_id exists
            await _test_exists(s, "Subcategory", "id", subcategory_id)

        # add the payee
        rec = db.schema.Payee(name=name, subcategory_id=subcategory_id)
        s.add(rec)
        await s.commit()
        print(f'create_payee created:', rec)
        return rec


async def create_transaction(date, amount, account_id, payee_id, subcategory_id):
    print(f'DB: create_transaction {date} {amount} {account_id} {payee_id} {subcategory_id}')

    uid = str(uuid.uuid4())

    async with db.session.get_session() as s:

        # Check if an account with this account_id exists
        await _test_exists(s, "Account", "id", account_id)

        # Check if a payee with this payee_id exists
        await _test_exists(s, "Payee", "id", payee_id)

        if subcategory_id is not None:
            # Check if a subcategory with this subcategory_id exists
            await _test_exists(s, "Subcategory", "id", subcategory_id)

        # create the transaction
        rec = db.schema.Transaction(id=uid,
                                    date=date,
                                    amount=amount,
                                    account_id=account_id,
                                    payee_id=payee_id,
                                    subcategory_id=subcategory_id)
        s.add(rec)
        await s.commit()
        print(f'create_transaction created:', rec)
        return rec


def _test_not_empty(val, desc):
    if len(val) == 0:
        raise Exception(f"Error: {desc} cannot be empty")


async def _test_doesnt_exist(session, class_name, column_name, val):
    class_ = getattr(db.schema, class_name)
    column = getattr(class_, column_name)

    sql = sqlalchemy.select(class_).where(column == val)
    existing = (await session.execute(sql)).first()
    if existing is not None:
        raise Exception(f"{class_name} with {column_name}='{val}' already exists.")


async def _test_exists(session, class_name, column_name, val):
    class_ = getattr(db.schema, class_name)
    column = getattr(class_, column_name)

    sql = sqlalchemy.select(class_).where(column == val)
    existing = (await session.execute(sql)).first()
    if existing is None:
        raise Exception(f"{class_name} with {column_name}='{val}' does not exist.")
