import typing


class YearlySummaryRow:
    category_id: int
    subcategory_id: int
    monthly_sums: typing.List[int]
    total_sum: int

    def __init__(self, category_id, subcategory_id):
        self.category_id = category_id
        self.subcategory_id = subcategory_id
        self.monthly_sums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        self.total_sum = 300


class YearlySummary:
    year: int
    income_rows: typing.List[YearlySummaryRow]
    expense_rows: typing.List[YearlySummaryRow]

    def __init__(self, year):
        self.year = year
        self.income_rows = [YearlySummaryRow(1, 1)]
        self.expense_rows = [YearlySummaryRow(2, 2)]
