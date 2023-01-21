from dataclasses import dataclass
from db.i_db_filter import IDbFilter
from db.schema import Transaction


@dataclass
class TransactionsFilter(IDbFilter):
    categorized: bool | None

    def apply(self, stmt):
        if self.categorized is not None:
            if self.categorized:
                stmt = stmt.where(Transaction.subcategory_id != None)
            else:
                stmt = stmt.where(Transaction.subcategory_id == None)
        return stmt
