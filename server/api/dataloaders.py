from typing import List, Dict, TypeVar
from strawberry.dataloader import DataLoader
import db.schema
from sqlalchemy import select
import db.globals


def get_all_dataloaders() -> Dict[str, DataLoader]:
    return {

        "account_by_id":
            DataLoader(load_fn=_build_id_fn(db.schema.Account)),

        "category_by_id":
            DataLoader(load_fn=_build_id_fn(db.schema.Category)),

        "subcategory_by_id":
            DataLoader(load_fn=_build_id_fn(db.schema.Subcategory)),

        "payee_by_id":
            DataLoader(load_fn=_build_id_fn(db.schema.Payee)),

        "transaction_by_id":
            DataLoader(load_fn=_build_id_fn(db.schema.Transaction)),

        "transactions_by_account_id":
            DataLoader(load_fn=_build_column_fn(db.schema.Transaction, "account_id")),

        "transactions_by_payee_id":
            DataLoader(load_fn=_build_column_fn(db.schema.Transaction, "payee_id")),

        "subcategories_by_category_id":
            DataLoader(load_fn=_build_column_fn(db.schema.Subcategory, "category_id")),

        "payees_by_subcategory_id":
            DataLoader(load_fn=_build_column_fn(db.schema.Payee, "subcategory_id")),

    }


DbTableClass = TypeVar("DbTableClass")


def _build_id_fn(class_: DbTableClass):
    """ return a dataloader function for getting all objects of
    the given class by the given list of IDs """

    async def get_by_ids(ids: List[str]) -> List[class_]:
        async with db.globals.session_maker() as session:
            sql = select(class_).where(class_.id.in_(ids))
            res = await session.execute(sql)
            recs = res.scalars().all()
        # order the result in the same order as the given ids list
        recs_dict = {r.id: r for r in recs}
        ordered = []
        for id_ in ids:
            ordered.append(recs_dict.get(id_))
        return ordered

    return get_by_ids


def _build_column_fn(class_: DbTableClass, column_name: str):
    """ return a dataloader function for getting all objects of
    the given class whose column value is in the given list of values """

    async def get_by_column(values: List[str]) -> List[class_]:
        column = getattr(class_, column_name)
        async with db.globals.session_maker() as session:
            sql = select(class_).where(column.in_(values))
            res = await session.execute(sql)
            recs = res.scalars().all()

            # order the results in the same order as the given values list
            groups = {v: [] for v in values}
            for rec in recs:
                groups[getattr(rec, column_name)].append(rec)
            return list(groups.values())

    return get_by_column
