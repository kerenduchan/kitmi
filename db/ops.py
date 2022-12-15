import logging
import db.session
import db.schema
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.dialects.sqlite
import uuid
import crypto
import sqlalchemy.exc
import model.summary


async def get_all(session, class_name, order_by_column_name):
    logging.info(f"DB: get_all {class_name} ordered by {order_by_column_name}")
    db_schema_class = getattr(db.schema, class_name)
    order_by_column = getattr(db_schema_class, order_by_column_name)

    sql = sqlalchemy.select(db_schema_class).order_by(order_by_column)
    recs = (await session.execute(sql)).scalars().unique().all()
    logging.debug(f'DB: get all {class_name} ordered by {order_by_column_name}: {recs}')
    return recs


async def get_one_by_column(session, class_name, column, value):
    db_schema_class = getattr(db.schema, class_name)
    column = getattr(db_schema_class, column)
    sql = sqlalchemy.select(db_schema_class).where(column == value)
    rec = (await session.execute(sql)).scalars().unique().first()
    if rec is None:
        raise Exception(f"DB: {class_name} with {column}={value} doesn't exist")
    logging.debug(f'DB: {class_name} by {column}={value}: {rec}')
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
    logging.debug(f'get_all_transaction_ids: {recs}')
    return recs


async def create_account(session, name, source, username, password):

    logging.info(f'Creating account: name={name} source={source}')

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

    logging.debug(f'Account created: {rec}')
    return rec


async def create_category(session, name, is_expense):
    logging.info(f'DB: create_category {name} is_expense={is_expense}')

    # don't allow empty name for category
    _test_not_empty(name, "Category name")

    # Check if a category with this name already exists
    await _test_doesnt_exist(session, "Category", "name", name)

    # add the category
    rec = db.schema.Category(name=name, is_expense=is_expense)
    session.add(rec)
    await session.commit()
    logging.debug(f'create_category created: {rec}')
    return rec


async def rename_category(session, category_id, name):
    logging.info(f'DB: rename_category {category_id} {name}')

    # don't allow empty name
    _test_not_empty(name, "Category name")

    sql = sqlalchemy.update(db.schema.Category) \
        .where(db.schema.Category.id == category_id) \
        .values(name=name)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Category", category_id)
    logging.debug(f'rename_category done: {rec}')
    return rec


async def delete_category(session, category_id):
    logging.info(f'DB: delete_category {category_id}')

    sql = sqlalchemy.delete(db.schema.Category) \
        .where(db.schema.Category.id == category_id)

    await session.execute(sql)
    await session.commit()

    logging.debug(f'delete_category done')


async def create_subcategory(session, name, category_id):
    logging.info(f'DB: create_subcategory {name} {category_id}')

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
    logging.debug(f'create_subcategory created: {rec}')
    return rec


async def rename_subcategory(session, subcategory_id, name):
    logging.info(f'DB: rename_subcategory {subcategory_id} {name}')

    # don't allow empty name
    _test_not_empty(name, "Subcategory name")

    sql = sqlalchemy.update(db.schema.Subcategory) \
        .where(db.schema.Subcategory.id == subcategory_id) \
        .values(name=name)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Subcategory", subcategory_id)
    logging.debug(f'rename_subcategory done: {rec}')
    return rec


async def delete_subcategory(session, subcategory_id):
    logging.info(f'DB: delete_subcategory {subcategory_id}')

    sql = sqlalchemy.delete(db.schema.Subcategory) \
        .where(db.schema.Subcategory.id == subcategory_id)

    await session.execute(sql)
    await session.commit()

    logging.debug(f'delete_subcategory done')


async def create_payee(session, name, subcategory_id, note):
    logging.info(f'DB: create_payee name={name} subcategory_id={subcategory_id} note={note}')

    # don't allow empty name for payee
    _test_not_empty(name, "Payee name")

    # Check if a payee with this name already exists
    await _test_doesnt_exist(session, "Payee", "name", name)

    if subcategory_id is not None:
        # Check if a subcategory with this subcategory_id exists
        await _test_exists(session, "Subcategory", "id", subcategory_id)

    # add the payee
    rec = db.schema.Payee(name=name,
                          subcategory_id=subcategory_id,
                          note=note)
    session.add(rec)
    await session.commit()
    logging.debug(f'create_payee created: {rec}')
    return rec


async def update_payee_subcategory(session, payee_id, subcategory_id):
    logging.info(f'DB: update_payee_subcategory payee_id={payee_id} '
                 f'subcategory_id={subcategory_id}')

    # Check if a subcategory with this subcategory_id exists
    await _test_exists(session, "Subcategory", "id", subcategory_id)

    sql = sqlalchemy.update(db.schema.Payee) \
        .where(db.schema.Payee.id == payee_id) \
        .values(subcategory_id=subcategory_id)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Payee", payee_id)
    logging.debug(f'update_payee_subcategory done: {rec}')
    return rec


async def create_transaction(session, date, amount, account_id, payee_id, subcategory_id, note):
    logging.info(f'DB: create_transaction date={date} amount={amount} account_id={account_id} '
                 f'payee_id={payee_id} subcategory_id={subcategory_id} note={note}')

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
                                subcategory_id=subcategory_id,
                                note=note)
    session.add(rec)
    await session.commit()
    logging.debug(f'create_transaction created: {rec}')
    return rec


async def create_payees_ignore_conflict(session, names):
    """ Insert the given payee names into the payees table,
    if they don't already exist. """

    if len(names) == 0:
        # nothing to do
        return

    # INSERT INTO payees VALUES ... ON CONFLICT DO NOTHING
    stmt = (sqlalchemy.dialects.sqlite.insert(db.schema.Payee)).on_conflict_do_nothing()
    values = [{'name': n} for n in names]
    await session.execute(stmt, values)
    await session.commit()


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


async def get_yearly_summary(session, year):
    summary = model.summary.YearlySummary(year)

    subcategories = await get_all(session, "Subcategory", "id")
    categories = await get_all(session, "Category", "id")

    # map category ID => is expense
    category_id_to_is_expense = {c.id: c.is_expense for c in categories}

    # add an income/expense row for each subcategory
    for s in subcategories:
        row = model.summary.YearlySummaryRow(s.category_id, s.id)
        is_expense = category_id_to_is_expense[s.category_id]
        if is_expense:
            summary.income_rows.append(row)
        else:
            summary.expense_rows.append(row)

    return summary
