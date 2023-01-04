import model.summary
import datetime
import db.schema


class Payee:
    def __init__(self, id, subcategory_id=None):
        self.id = id
        self.subcategory_id = subcategory_id


class Subcategory:
    def __init__(self, id, name, category_id):
        self.id = id
        self.name = name
        self.category_id = category_id


class Transaction:
    def __init__(self, payee_id, amount, date, subcategory_id=None):
        self.payee_id = payee_id
        self.subcategory_id = subcategory_id
        self.amount = amount
        self.date = date


def test_summary():

    payees = [
        Payee(id=1, subcategory_id=1)
    ]

    subcategories = [
        Subcategory(name="s1", id=1, category_id=1),
        Subcategory(name="s2", id=2, category_id=1),
        Subcategory(name="s3", id=3, category_id=1)
    ]

    transactions = [
        Transaction(
            payee_id=1,
            amount=100.21,
            date=datetime.date.fromisoformat('2022-02-01')),
        Transaction(
            payee_id=1,
            subcategory_id=2,
            amount=1,
            date=datetime.date.fromisoformat('2022-02-02')),
        Transaction(
            payee_id=1,
            subcategory_id=3,
            amount=2,
            date=datetime.date.fromisoformat('2022-02-03'))
    ]

    # Create the result summary object.
    summary = model.summary.Summary(
        start_date=datetime.date.fromisoformat('2022-02-01'),
        end_date=datetime.date.fromisoformat('2022-02-25'),
        group_by='subcategory',
        is_reverse_sign=False,
        payees=payees,
        subcategories=subcategories)

    # add a group to the summary per subcategory
    for s in subcategories:
        summary.add_group(s.id, s.name)

    summary.add_transactions(transactions)

    print(summary)


if __name__ == "__main__":
    test_summary()
