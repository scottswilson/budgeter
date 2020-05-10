from file_parser import *
from categories import *
from purchase import *
from utils import increment_month

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


if __name__ == '__main__':
  start_month = (2019, 12)
  end_month = (2020, 5)
  
  months = [start_month]
  while(start_month != end_month):
    start_month = increment_month(*start_month)
    months.append(start_month)

  categories = Categories()
  purchases = Purchases()

  for fp in statements:
    with open(fp, 'r') as f:
      purchases.add_purchases(StatementParser(f, categories).purchases)

  for fp in expenses:
    with open(fp, 'r') as f:
      next(f)
      purchases.add_purchases(ExpenseParser(f, categories).purchases)

  for fp in savings:
    with open(fp, 'r') as f:
      purchases.add_purchases(StatementParser(f, categories).purchases)

  print('Parsed {} purchases!'.format(len(purchases.data)))
  purchases = purchases.remove_category('Discard')
  income = purchases.get_category('Salary')
  expenses = purchases.remove_category('Salary')
  expenses = expenses.remove_category('Payments')

  print("Total earned: {:10.2f}".format(-income.sum()))
  print("Total spent:  {:10.2f}".format(expenses.sum()))

  format_str = '{:>30s}'
  format_float = '{:>30s}'
  format_percent = '{:>30s} '
  args = []
  month = start_month
  for month in months:
    format_str += (' {:>10s}')
    format_float += (' {:10.2f}')
    format_percent += (' {:9.2f}%')
    args.append('{}/{}'.format(*month))

    
  print(format_str.format('Category', *args))

  print(format_str.format(*["------"]*(len(months)+1)))

  print(format_float.format("Income", *[-income.month(*month).sum() for month in months]))
  print(format_float.format("Expenditures", *[expenses.month(*month).sum() for month in months]))
  print(format_percent.format("% Saved", *[100*(1+expenses.month(*month).sum()/(income.month(*month).sum()+1)) for month in months]))
  print(format_float.format("Needs", *[expenses.month(*month).needs().sum() for month in months]))
  print(format_float.format("Wants", *[expenses.month(*month).wants().sum() for month in months]))
  print(format_percent.format("% Needs", *[100*(expenses.month(*month).needs().sum()/(expenses.month(*month).sum())) for month in months]))
  
  print(format_str.format(*["-----"]*(len(months)+1)))

  purchases = purchases.remove_category("Salary")

  for category in categories.data:
    args = []
    for month in months:
      monthly_expenses = purchases.month(*month)
      args.append(monthly_expenses.get_category(category.label).sum())
    if not all([x == 0 for x in args]):
      print(format_float.format(category.label, *args))
