import logging
import db.session
import db.schema
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.dialects.sqlite
import uuid
import crypto
import sqlalchemy.exc
import model.yearly_summary
import model.summary
import model.subcategory_usage_info


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
        raise Exception(f"{class_name} with {column}={value} doesn't exist")
    logging.debug(f'DB: {class_name} by {column}={value}: {rec}')
    return rec


async def get_one_by_id(session, class_name, id_):
    return await get_one_by_column(session, class_name, 'id', id_)


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


async def get_all_accounts(session):
    logging.info(f"DB: get_all_accounts")
    sql = sqlalchemy.select(db.schema.Account).order_by(db.schema.Account.name)
    recs = (await session.execute(sql)).scalars().unique().all()

    c = crypto.Crypto()

    # decrypt username and clear password
    for r in recs:
        r.username = c.decrypt(r.username)
        r.password = ''

    logging.debug(f'DB: get_all_accounts: {recs}')
    return recs


async def get_account_by_id(session, id_):
    rec = await get_one_by_column(session, "Account", 'id', id_)

    # decrypt username and clear password
    c = crypto.Crypto()
    rec.username = c.decrypt(rec.username)
    rec.password = ''
    return rec


async def create_account(session, name, source, username, password):
    # get the enum member by value
    source = db.schema.AccountSource(source)

    logging.info(f'Creating account: name={name} source={source}')

    # don't allow empty name
    _test_not_empty(name, "Account name")

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


async def update_account(session, account_id, name, source, username, password):
    logging.info(f'DB: update_account {account_id} {name} {source}')

    c = crypto.Crypto()
    values = {}

    if name is not None or \
        source is not None or \
        username is not None or \
        password is not None:

        if name is not None:
            # don't allow empty name
            _test_not_empty(name, "Account name")

            values['name'] = name

        if source is not None:
            values['source'] = source

        if username is not None:
            values['username'] = c.encrypt(username)

        if password is not None:
            values['password'] = c.encrypt(password)

        # update the account
        sql = sqlalchemy.update(db.schema.Account) \
            .where(db.schema.Account.id == account_id) \
            .values(**values)

        await session.execute(sql)
        await session.commit()

    rec = await get_account_by_id(session, account_id)
    logging.debug(f'update_account done: {rec}')
    return rec


async def delete_account(session, account_id):
    logging.info(f'DB: delete_account {account_id}')

    # count how many transactions use this account ID
    sql = sqlalchemy.select([sqlalchemy.func.count()]).select_from(db.schema.Transaction).\
        where(db.schema.Transaction.account_id == account_id)
    count = (await session.execute(sql)).scalar()
    logging.info(f'count={count}')
    if count > 0:
        raise Exception('Cannot delete account that is used by one or more transactions')

    sql = sqlalchemy.delete(db.schema.Account) \
        .where(db.schema.Account.id == account_id)

    await session.execute(sql)
    await session.commit()

    logging.debug(f'delete_account done')


async def create_category(session, name, is_expense, exclude_from_reports):
    logging.info(f'DB: create_category {name} is_expense={is_expense} '
                 f'exclude_from_reports={exclude_from_reports}')

    # don't allow empty name for category
    _test_not_empty(name, "Category name")

    # Check if a category with this name already exists
    await _test_doesnt_exist(session, "Category", "name", name)

    order = await _get_largest_category_order(session) + 1

    # add the category
    rec = db.schema.Category(name=name,
                             is_expense=is_expense,
                             order=order,
                             exclude_from_reports=exclude_from_reports)
    session.add(rec)
    await session.commit()
    logging.debug(f'create_category created: {rec}')
    return rec


async def update_category(session, category_id, name, is_expense, exclude_from_reports):
    logging.info(f'DB: update_category {category_id} {name} {is_expense} {exclude_from_reports}')

    # don't allow empty name
    _test_not_empty(name, "Category name")

    sql = sqlalchemy.update(db.schema.Category) \
        .where(db.schema.Category.id == category_id) \
        .values(name=name,
                is_expense=is_expense,
                exclude_from_reports=exclude_from_reports)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Category", category_id)
    logging.debug(f'update_category done: {rec}')
    return rec


async def delete_category(session, category_id):
    logging.info(f'DB: delete_category {category_id}')

    sql = sqlalchemy.delete(db.schema.Category) \
        .where(db.schema.Category.id == category_id)

    await session.execute(sql)
    await session.commit()

    logging.debug(f'delete_category done')


async def move_category(session, category_id, is_down):

    # get all categories from the db
    sql = sqlalchemy.select(db.schema.Category).order_by(db.schema.Category.order)
    recs = (await session.execute(sql)).scalars().unique().all()

    # check that the category exists
    category_idx = -1
    for i in range(len(recs)):
        if recs[i].id == category_id:
            category_idx = i
            break

    if category_idx == -1:
        raise Exception(f'Category with ID={category_id} does not exist')

    # check whether there's any category above/below it (depending on is_down)
    if is_down:
        if category_idx == len(recs) - 1:
            raise Exception(f'Category with ID={category_id} cannot be moved any further down')
    elif category_idx == 0:
        raise Exception(f'Category with ID={category_id} cannot be moved any further up')

    # get the order of the category, and the category below/above it
    # (according to the given is_down)
    current_order = recs[category_idx].order
    swap_idx = category_idx + 1 if is_down else category_idx - 1
    new_order = recs[swap_idx].order

    # swap order values between this category and the one below/above it
    sql = sqlalchemy.update(db.schema.Category) \
        .where(db.schema.Category.order == new_order) \
        .values(order=current_order)
    await session.execute(sql)

    sql = sqlalchemy.update(db.schema.Category) \
        .where(db.schema.Category.id == category_id) \
        .values(order=new_order)
    await session.execute(sql)

    await session.commit()


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


async def update_subcategory(session, subcategory_id, name, category_id):
    logging.info(f'DB: update_subcategory {subcategory_id} {name} {category_id}')

    # don't allow empty name
    _test_not_empty(name, "Subcategory name")

    sql = sqlalchemy.update(db.schema.Subcategory) \
        .where(db.schema.Subcategory.id == subcategory_id) \
        .values(name=name, category_id=category_id)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Subcategory", subcategory_id)
    logging.debug(f'update_subcategory done: {rec}')
    return rec


async def delete_subcategory(session, subcategory_id):
    logging.info(f'DB: delete_subcategory {subcategory_id}')

    sql = sqlalchemy.delete(db.schema.Subcategory) \
        .where(db.schema.Subcategory.id == subcategory_id)
    await session.execute(sql)

    # also delete any use of this subcategory ID in the payees and
    # transactions tables

    sql = sqlalchemy.update(db.schema.Payee) \
        .where(db.schema.Payee.subcategory_id == subcategory_id) \
        .values(subcategory_id=None)
    await session.execute(sql)

    sql = sqlalchemy.update(db.schema.Transaction) \
        .where(db.schema.Transaction.subcategory_id == subcategory_id) \
        .values(subcategory_id=None)
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


async def update_payee(session, payee_id, subcategory_id):
    logging.info(f'DB: update_payee payee_id={payee_id} '
                 f'subcategory_id={subcategory_id}')

    if subcategory_id is not None:
        # Check if a subcategory with this subcategory_id exists
        await _test_exists(session, "Subcategory", "id", subcategory_id)

    # set subcategory_id of the payee to null or a number
    sql = sqlalchemy.update(db.schema.Payee) \
        .where(db.schema.Payee.id == payee_id) \
        .values(subcategory_id=subcategory_id)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Payee", payee_id)
    logging.debug(f'update_payee done: {rec}')
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


async def update_transaction(session, transaction_id, override_subcategory, subcategory_id):
    logging.info(f'DB: update_transaction transaction_id={transaction_id} '
                 f'subcategory_id={subcategory_id}')

    if subcategory_id is not None:
        # Check if a subcategory with this subcategory_id exists
        await _test_exists(session, "Subcategory", "id", subcategory_id)

    values = {'subcategory_id': subcategory_id}

    if override_subcategory is not None:
        values['override_subcategory'] = override_subcategory

    sql = sqlalchemy.update(db.schema.Transaction) \
        .where(db.schema.Transaction.id == transaction_id) \
        .values(**values)

    await session.execute(sql)
    await session.commit()

    rec = await get_one_by_id(session, "Transaction", transaction_id)
    logging.debug(f'update_transaction done: {rec}')
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


async def get_yearly_summary(session, year):

    subcategories = await get_all(session, "Subcategory", "id")
    categories = await get_all(session, "Category", "id")
    payees = await get_all(session, "Payee", "id")

    # get all transactions for this year
    # (TODO: filter by year)
    sql = sqlalchemy.select(db.schema.Transaction)
    transactions = (await session.execute(sql)).scalars().unique().all()

    # Create the result yearly summary object.
    summary = model.yearly_summary.YearlySummary(year)

    # Add every subcategory to the summary
    for s in subcategories:
        summary.add_subcategory(s.id)

    # Sum the transaction in the appropriate subcategory and month.
    # Payees are needed in order to determine the subcategory_id of the transaction.
    summary.add_transactions(transactions, payees)

    return summary


async def get_summary(session, start_date, end_date, group_by, is_expense=True):

    subcategories = await get_all(session, 'Subcategory', 'id')

    # get all expense/income categories (depending on is_expense)
    # that are not "excluded from reports"
    sql = sqlalchemy.select(db.schema.Category)\
        .where(db.schema.Category.is_expense == is_expense) \
        .where(db.schema.Category.exclude_from_reports == False) \
        .order_by(db.schema.Category.order)
    categories = (await session.execute(sql)).scalars().unique().all()

    # get all payees (in order to determine the transactions' subcategories)
    payees = await get_all(session, 'Payee', 'id')

    # get all transactions between start and end date
    sql = sqlalchemy.select(db.schema.Transaction)\
        .where(db.schema.Transaction.date >= start_date)\
        .where(db.schema.Transaction.date <= end_date)
    transactions = (await session.execute(sql)).scalars().unique().all()

    # only the subset of subcategories that belong to the filtered categories
    subcategories = _order_subcategories_by_categories(subcategories, categories)

    # Create the result summary object.
    summary = model.summary.Summary(start_date, end_date, group_by, is_expense, payees, subcategories)

    # Add every (expense/income) subcategory/category to the summary
    if group_by == 'category':
        for c in categories:
            summary.add_group(c.id, c.name)
    else:
        for s in subcategories:
            summary.add_group(s.id, s.name)

    # Sum the transaction in the appropriate group and month.
    # Payees are needed in order to determine the subcategory_id/category_id
    # of the transaction.
    summary.add_transactions(transactions)

    return summary


async def get_subcategory_usage_info(session, subcategory_id):

    # this will raise an exception if the subcategory doesn't exist
    subcategory = await get_one_by_id(session, 'Subcategory', subcategory_id)

    # count how many payees use this subcategory ID
    sql = sqlalchemy.select([sqlalchemy.func.count()]).select_from(db.schema.Payee).\
        where(db.schema.Payee.subcategory_id == subcategory_id)
    count = (await session.execute(sql)).scalar()

    if count == 0:
        # count how many transactions use this subcategory ID
        sql = sqlalchemy.select([sqlalchemy.func.count()]).select_from(db.schema.Transaction).\
            where(db.schema.Transaction.subcategory_id == subcategory_id)
        count = (await session.execute(sql)).scalar()

    res = model.subcategory_usage_info.SubcategoryUsageInfo()
    res.is_used = (count > 0)
    return res


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


async def _get_largest_category_order(session):
    categories = await get_all(session, "Category", "order")
    if len(categories) == 0:
        return 0
    return categories[len(categories) - 1].order


def _order_subcategories_by_categories(subcategories, categories):
    # order the subcategories by the categories' order
    category_id_to_subcategories = {c.id: [] for c in categories}
    for s in subcategories:
        category = category_id_to_subcategories.get(s.category_id)
        if category is not None:
            category_id_to_subcategories[s.category_id].append(s)

    res = []
    for c, subcategories in category_id_to_subcategories.items():
        res += subcategories

    return res
