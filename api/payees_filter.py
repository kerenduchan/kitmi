import strawberry
import db.payees_filter


@strawberry.input
class PayeesFilter:
    categorized: bool | None

    def to_db_filter(self) -> db.payees_filter.PayeesFilter:
        return db.payees_filter.PayeesFilter(categorized=self.categorized)
