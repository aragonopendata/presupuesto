import json


class BudgetBreakdown:
    def __init__(self, criteria=[]):
        self.criteria = criteria
        self.names = []
        self.years = {}
        self.subtotals = {}
        self.total_expense = {}
        self.total_income = {}

    # Add a new budget item to the breakdown
    def add_item(self, column, item):
        # Check whether the column exist, and add if needed
        if not column in self.names:
            self.names.append(column)
            self.years[column] = item.year

        # Basic aggregation
        if item.expense:
            if column not in self.total_expense:
                self.total_expense[column] = 0
            self.total_expense[column] += item.amount
        else:
            if column not in self.total_income:
                self.total_income[column] = 0
            self.total_income[column] += item.amount

        # Breakdown aggregation
        if len(self.criteria) > 0:  # We have a criteria to classify on
            # Sometimes the criteria is not a string, but a lambda
            if hasattr(self.criteria[0], '__call__'):
                value = self.criteria[0](item)
            else:  # Sometimes it's just a string pointing to an attribute...
                value = getattr(item, self.criteria[0])
                # ...or a method
                if hasattr(value, '__call__'):
                    value = value()

            # Check we have an actual value for the given criteria
            if value == None:
                return

            if value not in self.subtotals:
                self.subtotals[value] = BudgetBreakdown(self.criteria[1:])
            self.subtotals[value].add_item(column, item)

    # Simplified JSON output, for cleaner view code
    def to_json(self, labels=None, uid=None):
        data = {
            'expense': self.total_expense,
            'income': self.total_income
        }
        # Add year information only at the root level, waste of space otherwise
        if not uid:
            data['years'] = self.years

        # Add a label to the item, if provided
        if labels and uid:
            data['label'] = labels.get(uid)

        # Iterate through the children. Let them know the uid they represent
        if len(self.subtotals) > 0:
            data['sub'] = {}
            for subtotal in self.subtotals:
                data['sub'][subtotal] = self.subtotals[subtotal].to_json(uid=subtotal, labels=labels)

        # Since we're calling this method recursively, we only convert to JSON
        # at the root level, i.e. when the uid is null
        return data if uid else json.dumps(data)
