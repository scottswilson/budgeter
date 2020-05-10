from enum import Enum
import matplotlib.pyplot as plt
import datetime
import json
import re
from collections import namedtuple

Category = namedtuple('Category', ('label', 'known_associations', 'need'))

class Categories(object):
  FP = 'categories.json'
  def __init__(self):
    self.data = []
    self.reload()

  def __str__(self):
    output = []
    output.append("Categories:")
    for i, item in enumerate(self.data):
      output.append("{:d}: {:s}".format(i, item.label))
    return '\n'.join(output)

  def __getitem__(self, idx):
    if type(idx) == int:
      return self.data[idx]
    if type(idx) == str:
      return self.get_category_by_label(idx)
    raise IndexError("Unknown index {}".format(idx))

  def get_category_by_label(self, label):
    for category in self.data:
      if category.label.lower() == label.lower():
        return category
    return None

  def append(self, new):
    self.data.append(new)

  def save(self):
    output = []
    for item in self.data:
      output.append({
        'label': item.label,
        'known_associations': item.known_associations,
        'need': item.need,
      })
    
    with open(self.FP, 'w+') as f:
      f.write(json.dumps(output, indent=2))

  def reload(self):
    self.data = []
    with open(self.FP, 'r') as f:
      for category in json.loads(f.read()):
        self.append(Category(
          category['label'],
          category['known_associations'],
          category['need'],
        ))


class Purchase(object):
  def __init__(self, date, label, amount):
    self.date = date
    self.label = label
    self.amount = amount
    self.category = None

  def try_to_categorize(self, categories):
    for category in categories:
      if self.label in category.known_associations:
        self.category = category
        return

  def __str__(self):
    return "{:s}, {:s} for {:4.2f}".format(
      "{}-{}-{}".format(self.date.year, self.date.month, self.date.day),
      self.label, 
      self.amount
    )

class Purchases(object):
  def __init__(self, purchases = []):
    self.data = purchases

  def add_purchase(self, purchase):
    self.data.append(purchase)

  def get_by_impl(self, func = lambda x: True):
    return Purchases([x for x in self.data if func(x)])

  def get_category(self, label):
    return self.get_by_impl(lambda x: x.category.label == label)

  def remove_category(self, label):
    return self.get_by_impl(lambda x: x.category.label != label)

  def get_month(self, year, month):
    return self.get_by_impl(
      lambda x: x.date.year == year and x.date.month == month
    )
    
  def get_needs(self):
    return self.get_by_impl(lambda x: x.category.need)

  def get_wants(self):
    return self.get_by_impl(lambda x: not x.category.need)
    
  def total_spent(self):
    return sum([x.amount for x in self.data])

def parse_line(line, type):
  line = sanitize_line(line)
  line = line.split(',')

  if type == FileTypes.Statement:
    return parse_from_statement(line)
  elif type == FileTypes.ScottExpense:
    return parse_from_expense(line)
  elif type == FileTypes.Savings:
    return parse_from_savings(line)
  else:
    raise TypeError('Unknown file type {}'.format(type))

def sanitize_line(line):
  search = re.search('(".*")', line)

  if not search:
    return line

  for group in search.groups():
    group_replacement = group.replace('"', '').replace(',', '')
    line = line.replace(group, group_replacement)

  return line

def parse_from_statement(line):
  if line[0] == '':
    return

  date = datetime.datetime.strptime(line[0], '%m/%d/%Y')
  label = line[1]
  spent = line[2]
  gained = line[3]
  if not len(spent):
    spent = 0
  if not len(gained):
    gained = 0
  amount = float(spent) - float(gained)
  return date, label, amount

def parse_from_expense(line):
  if line[0] == '':
    return None

  date = datetime.datetime.strptime(line[0], '%d/%m/%Y')
  label = line[1]
  spent = float(line[7])
  return date, label, spent

def parse_from_savings(line):
  return parse_from_statement(line)


class FileTypes(Enum):
  Statement = 0
  ScottExpense = 1
  Savings = 2

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

def parse_file(f, type, categories, purchases):
  for line in f:
    result = parse_line(line, type)
    if result is None:
      continue
    purchase = Purchase(*result)
    purchase.try_to_categorize(categories)
    if purchase.category is None:
      while(True):
        try:
          idx = input('Unkown entry category: {}\n'.format(str(purchase)))
          purchase.category = categories[idx]
          categories[idx].known_associations.append(purchase.label)
          categories.save()
          break
        except NameError:
          print(categories)
        except IndexError:
          print(categories)
        except Exception as unkown_error:
          raise unkown_error
    purchases.add_purchase(purchase)

if __name__ == '__main__':
  month = (2019, 12)
  end_month = (2020, 5)

  categories = Categories()
  purchases = Purchases()

  for fp in statements:
    with open(fp, 'r') as f:
      parse_file(f, FileTypes.Statement, categories, purchases)

  for fp in expenses:
    with open(fp, 'r') as f:
      next(f)
      parse_file(f, FileTypes.ScottExpense, categories, purchases)

  for fp in savings:
    with open(fp, 'r') as f:
      parse_file(f, FileTypes.Savings, categories, purchases)

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