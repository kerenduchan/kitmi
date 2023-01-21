from dataclasses import dataclass
from sqlalchemy import case
from db.i_db_filter import IDbFilter
from db.schema import Transaction, Payee


@dataclass
class TransactionsFilter(IDbFilter):
    categorized: bool | None
    payee_id: int | None

    def apply(self, stmt):

        print(f'TransactionsFilter {self.categorized} {self.payee_id}')

        if self.categorized is not None:
            # need the payee's subcategory for this
            stmt = stmt.join(Transaction.payee)
            if self.categorized:
                stmt = stmt.where(
                    case(
                        (Transaction.override_subcategory == True, Transaction.subcategory_id != None),
                        (Transaction.override_subcategory == False, Payee.subcategory_id != None)
                    ))
            else:
                stmt = stmt.where(
                    case(
                        (Transaction.override_subcategory == True, Transaction.subcategory_id == None),
                        (Transaction.override_subcategory == False, Payee.subcategory_id == None)
                    ))

        if self.payee_id is not None:
            stmt = stmt.where(Transaction.payee_id == self.payee_id)

        return stmt
