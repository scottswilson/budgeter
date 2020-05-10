from file_parser import *
from categories import *
from purchase import *

statements = [
  'statement_dec_2019.csv',
  'statement_jan_2020.csv',
  'statement_feb_2020.csv',
  'statement_mar_2020.csv',
  'statement_apr_2020.csv',
]

expenses = [
  'expenses_jan.csv',
  'expenses_feb.csv',
  'expenses_mar.csv',
  'expenses_apr.csv',
]

savings = [
  'savings_dec_2019.csv',
  'savings_jan_2020.csv',
  'savings_feb_2020.csv',
  'savings_mar_2020.csv',
  'savings_apr_2020.csv',
]

def increment_month(year, month):
  if (month != 12):
    return year, month+1
  else:
    return year+1, 1

if __name__ == '__main__':
  month = (2019, 12)
  end_month = (2020, 5)

  categories = Categories()
  purchases = Purchases()

  for fp in statements:
    with open(fp, 'r') as f:
      parse_file(f, parse_from_statement, categories, purchases)

  for fp in expenses:
    with open(fp, 'r') as f:
      next(f)
      parse_file(f, parse_from_expense, categories, purchases)

  for fp in savings:
    with open(fp, 'r') as f:
      parse_file(f, parse_from_savings, categories, purchases)

  print('Parsed {} purchases!'.format(len(purchases.data)))
  purchases = purchases.remove_category('Discard')
  income = purchases.get_category('Salary')
  expenses = purchases.remove_category('Salary')
  expenses = expenses.remove_category('Payments')

  print("Total spent: {}".format(expenses.total_spent()))

  end_month = increment_month(*end_month)
  while(month != end_month):
    monthly_incomes = income.get_month(*month)
    monthly_expenses = expenses.get_month(*month)
    income_total = -monthly_incomes.total_spent() + 1e-9
    expenditure_total = monthly_expenses.total_spent()
    wants_total = monthly_expenses.get_wants().total_spent()
    needs_total = monthly_expenses.get_needs().total_spent()

    saving_percent = (1 - expenditure_total/income_total) * 100

    print(" Month: {}-{}".format(*month))
    print(" Monthly Income:       {:8.2f} ({:.2f}% saved)".format(income_total, saving_percent))
    print(" Monthly expenditures: {:8.2f} ({:.2f}% spent)".format(expenditure_total, (100 - saving_percent)))
    print(" Monthly wants:        {:8.2f} ({:.2f}%)".format(wants_total, wants_total / expenditure_total * 100))
    print(" Monthly needs:        {:8.2f} ({:.2f}%)".format(needs_total, needs_total / expenditure_total * 100))

    for category in categories.data:
      spent = monthly_expenses.get_category(category.label).total_spent()
      if spent: 
        print("{:8.2f}: {:s}".format(
          spent,
          category.label,
        ))

    month = increment_month(*month)