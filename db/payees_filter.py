from dataclasses import dataclass
from db.i_db_filter import IDbFilter
from db.schema import Payee


@dataclass
class PayeesFilter(IDbFilter):
    categorized: bool | None

    def apply(self, stmt):
        if self.categorized is not None:
            if self.categorized:
                stmt = stmt.where(Payee.subcategory_id != None)
            else:
                stmt = stmt.where(Payee.subcategory_id == None)
        return stmt
