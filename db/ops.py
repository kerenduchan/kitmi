import db.session
import db.schema
import sqlalchemy
import sqlalchemy.orm
import uuid
import crypto
import sqlalchemy.exc


async def get_all(session, class_name, order_by_column_name):
    print(f"DB: get_all {class_name} order by {order_by_column_name}")
    db_schema_class = getattr(db.schema, class_name)
    order_by_column = getattr(db_schema_class, order_by_column_name)

    sql = sqlalchemy.select(db_schema_class).order_by(order_by_column)
    recs = (await session.execute(sql)).scalars().unique().all()
    print(f'DB: get all {class_name} ordered by {order_by_column_name}:', recs)
    return recs


async def get_one_by_column(session, class_name, column, value):
    db_schema_class = getattr(db.schema, class_name)
    column = getattr(db_schema_class, column)
    sql = sqlalchemy.select(db_schema_class).where(column == value)
    rec = (await session.execute(sql)).scalars().unique().first()
    if rec is None:
        raise Exception(f"DB: {class_name} with {column}={value} doesn't exist")
    print(f'DB: {class_name} by {column}={value}:', rec)
    return rec


async def get_one_by_id(session, class_name, id_):
    return await get_one_by_column(session, class_name, 'id', int(id_))


async def get_all_transaction_ids(session, account_id, start_date):
    """ Get the IDs of all transactions from the db that belong
    to the given account ID and are newer than the given date. """
    sql = sqlalchemy.select(db.schema.Transaction.id)\
        .where(db.schema.Transaction.account_id == account_id)
    if start_date is not None:
        sql = sql.where(db.schema.Transaction.date >= start_date)
    recs = (await session.execute(sql)).scalars().unique().all()
    print('get_all_transaction_ids', recs)
    return recs


async def create_account(session, name, source, username, password):
    print(f'DB: create_account {name} {source}')

    # don't allow empty name
    _test_not_empty(name, "Account name")

    # Check that source is valid
    all_valid_sources = ['max', 'leumi']
    if source not in all_valid_sources:
        raise Exception(f"Invalid source '{source}'. Must be one of: {all_valid_sources}")

    # Check if an account with this name already exists
    await _test_doesnt_exist(session, "Account", "name", name)

    # add the account
    c = crypto.Crypto()
    rec = db.schema.Account(name=name,
                            source=source,
                            username=c.encrypt(username),
                            password=c.encrypt(password))
    session.add(rec)
    await session.commit()
    print(f'create_account created:', rec)
    return rec


async def create_category(session, name):
    print(f'DB: create_category {name}')

    # don't allow empty name for category
    _test_not_empty(name, "Category name")

    # Check if a category with this name already exists
    await _test_doesnt_exist(session, "Category", "name", name)

    # add the category
    rec = db.schema.Category(name=name)
    session.add(rec)
    await session.commit()
    print(f'create_category created:', rec)
    return rec


async def create_subcategory(session, name, category_id):
    print(f'DB: create_subcategory {name} {category_id}')

    # don't allow empty name
    _test_not_empty(name, "Subcategory name")

    # Check if a subcategory with this name already exists
    await _test_doesnt_exist(session, "Subcategory", "name", name)

    # Check if a category with this category_id exists
    await _test_exists(session, "Category", "id", category_id)

    # add the subcategory
    rec = db.schema.Subcategory(name=name, category_id=category_id)
    session.add(rec)
    await session.commit()
    print(f'create_subcategory created:', rec)
    return rec


async def create_payee(session, name, subcategory_id):
    print(f'DB: create_payee {name} {subcategory_id}')

    # don't allow empty name for payee
    _test_not_empty(name, "Payee name")

    # Check if a payee with this name already exists
    await _test_doesnt_exist(session, "Payee", "name", name)

    if subcategory_id is not None:
        # Check if a subcategory with this subcategory_id exists
        await _test_exists(session, "Subcategory", "id", subcategory_id)

    # add the payee
    rec = db.schema.Payee(name=name, subcategory_id=subcategory_id)
    session.add(rec)
    await session.commit()
    print(f'create_payee created:', rec)
    return rec


async def create_transaction(session, date, amount, account_id, payee_id, subcategory_id):
    print(f'DB: create_transaction {date} {amount} {account_id} {payee_id} {subcategory_id}')

    uid = str(uuid.uuid4())

    # Check if an account with this account_id exists
    await _test_exists(session, "Account", "id", account_id)

    # Check if a payee with this payee_id exists
    await _test_exists(session, "Payee", "id", payee_id)

    if subcategory_id is not None:
        # Check if a subcategory with this subcategory_id exists
        await _test_exists(session, "Subcategory", "id", subcategory_id)

    # create the transaction
    rec = db.schema.Transaction(id=uid,
                                date=date,
                                amount=amount,
                                account_id=account_id,
                                payee_id=payee_id,
                                subcategory_id=subcategory_id)
    session.add(rec)
    await session.commit()
    print(f'create_transaction created:', rec)
    return rec


async def insert_only_new_payees(session, names):
    """ Insert the given payee names into the payees table,
    if they don't already exist.
    Return a map of payee name => id, for each of the given names """

    payees = {}
    for name in names:
        try:
            payee = db.schema.Payee(name=name, subcategory_id=None)
            session.add(payee)

            # push the payee into the DB, so it'll get an id
            await session.flush()

            # refresh the payee in memory with its state in the db,
            # so we now have its id
            await session.refresh(payee)
            payees[name] = payee.id
            await session.commit()

        except sqlalchemy.exc.IntegrityError as e:
            # payee already exists in db - get its ID
            await session.rollback()

            if "UNIQUE constraint failed" in str(e):
                # return id of existing record
                payee = await get_one_by_column(session, "Payee", "name", name)
                payees[name] = payee.id

    return payees


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
