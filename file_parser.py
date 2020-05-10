from enum import Enum
import re
import datetime
from purchase import *
class FileTypes(Enum):
  Statement = 0
  ScottExpense = 1
  Savings = 2


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