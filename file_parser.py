from enum import Enum
import datetime
from purchase import *
from utils import sanitize_line


class BaseParser:
  def __init__(self, f, categories):
    self.f = f
    self.categories = categories
    self.purchases = self.parse_file()

  def GetPurchases(self): 
    return self.purchases

  def parse_file(self):
    temp_purchases = Purchases([])
    for line in self.f:
      result = self.parse_line(line)
      if result is None:
        continue
      purchase = Purchase(*result)
      purchase.try_to_categorize(self.categories)
      if purchase.category is None:
        while(True):
          try:
            idx = input('Unkown entry category: {} (enter any invalid input for help)\n'.format(str(purchase)))
            purchase.category = self.categories[idx]
            self.categories[idx].known_associations.append(purchase.label)
            self.categories.save()
            break
          except NameError:
            print(self.categories)
          except IndexError:
            print(self.categories)
          except Exception as unkown_error:
            raise unkown_error
      temp_purchases.add_purchase(purchase)
    return temp_purchases
    
  def parse_line(self, line):
    line = sanitize_line(line)
    line = line.split(',')
    return self.parse_func(line)

  def parse_func(self, line):
    raise("Use a derived class")


class StatementParser(BaseParser):
  def parse_func(self, line):
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

class ExpenseParser(BaseParser):
  def parse_func(self, line):
    if line[0] == '':
      return None

    date = datetime.datetime.strptime(line[0], '%d/%m/%Y')
    label = line[1]
    spent = float(line[7])
    return date, label, spent