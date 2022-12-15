import typing


class YearlySummaryRow:
    category_id: int
    subcategory_id: int
    monthly_sums: typing.List[int]
    total_sum: int

    def __init__(self, category_id, subcategory_id):
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.monthly_sums = [0 for i in range(12)]
        self.total_sum = 0


class YearlySummary:
    year: int
    income_rows: typing.List[YearlySummaryRow]
    expense_rows: typing.List[YearlySummaryRow]

    def __init__(self, year):
        self.year = year
        self.income_rows = []
        self.expense_rows = []
