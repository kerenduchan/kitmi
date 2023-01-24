import strawberry
import db.transactions_filter


@strawberry.input
class TransactionsFilter:
    categorized: bool | None
    payee_id: strawberry.ID | None

    def __init__(self,
                 categorized: bool | None = None,
                 payee_id: str | None = None):
        self.categorized = categorized
        self.payee_id = payee_id

    def to_db_filter(self) -> db.transactions_filter.TransactionsFilter:
        return db.transactions_filter.TransactionsFilter(
            categorized=self.categorized,
            payee_id=self.payee_id)
