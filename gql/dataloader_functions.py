import sqlalchemy
import db.session
import db.schema


async def get_categories_by_ids(ids):
    """ return the categories by the given category IDs,
    in the same order """
    return await _get_objects_by_ids("Category", ids)


async def get_subcategories_by_ids(ids):
    """ return the subcategories by the given subcategory IDs,
    in the same order """
    return await _get_objects_by_ids("Subcategory", ids)


async def get_payees_by_ids(ids):
    """ return the payees by the given payee IDs,
    in the same order """
    return await _get_objects_by_ids("Payee", ids)


async def get_accounts_by_ids(ids):
    """ return the accounts by the given account IDs,
    in the same order """
    return await _get_objects_by_ids("Account", ids)


async def get_transactions_by_account_ids(ids):
    """ return the transactions for each of the given account IDs,
    in the same order """
    return await _get_objects_by_column_value("Transaction", "account_id", ids)


async def get_subcategories_by_category_ids(ids):
    """ return the subcategories for each of the given category IDs,
    in the same order """
    return await _get_objects_by_column_value("Subcategory", "category_id", ids)


async def get_payees_by_subcategory_ids(ids):
    """ return the payees for each of the given subcategory IDs,
    in the same order """
    return await _get_objects_by_column_value("Payee", "subcategory_id", ids)


async def get_transactions_by_payee_ids(ids):
    """ return the transactions for each of the given payee IDs,
    in the same order """
    return await _get_objects_by_column_value("Transaction", "payee_id", ids)


async def _get_objects_by_ids(db_schema_class_name, ids):
    class_ = getattr(db.schema, db_schema_class_name)
    async with db.session.SessionMaker() as s:
        sql = sqlalchemy.select(class_).where(class_.id.in_(ids))
        recs = (await s.execute(sql)).scalars().unique().all()

        # order the result in the same order as the given ids list
        recs_dict = {r.id: r for r in recs}
        ordered = []
        for id_ in ids:
            ordered.append(recs_dict.get(id_))
        print(f'get {db_schema_class_name} by ids: {ids}:', ordered)
        return ordered


async def _get_objects_by_column_value(db_schema_class_name, column, values):
    class_ = getattr(db.schema, db_schema_class_name)
    async with db.session.SessionMaker() as s:
        sql = sqlalchemy.select(class_).\
            where(getattr(class_, column).in_(values))
        recs = (await s.execute(sql)).scalars().unique().all()

        # order the results in the same order as the given values list
        groups = {v: [] for v in values}
        for rec in recs:
            groups[getattr(rec, column)].append(rec)
        print(f'get {db_schema_class_name} by {column} {values}:', groups)
        return groups.values()
