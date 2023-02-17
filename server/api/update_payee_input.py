import strawberry
import db.schema


@strawberry.input
class UpdatePayeeInput:
    id: strawberry.ID
    subcategory_id: strawberry.ID | None

    def to_db(self):
        return db.schema.Payee(
            id=self.id,
            subcategory_id=self.subcategory_id)
