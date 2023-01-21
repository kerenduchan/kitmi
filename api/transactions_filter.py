import strawberry
import db.transactions_filter


@strawberry.input
class TransactionsFilter:
    categorized: bool | None

    def to_db_filter(self) -> db.transactions_filter.TransactionsFilter:
        return db.transactions_filter.TransactionsFilter(categorized=self.categorized)
