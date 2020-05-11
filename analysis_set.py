import json
import os
import datetime
from file_parser import *
from purchase import *
from utils import *
class DataFile(object):
  def __init__(self, json_input = {}):
    self.fp = json_input.get('fp', None)
    self.type = json_input.get('type', None)

  def to_json(self):
    output = {}
    output['fp'] = self.fp
    output['type'] = self.type
    return output


class AnalysisRange(object):
  def __init__(self, json_input):
    self.start = datetime.datetime.strptime(json_input.get('start'), "%Y-%m").date()
    self.end = datetime.datetime.strptime(json_input.get('end'), "%Y-%m").date()
    self.category_labels = json_input.get('category_labels')

  def add_category(self, new_cat):
    self.category_labels.append(new_cat)

  def remove_category(self, bad_cat):
    self.category_labels.remove(bad_cat)

  def to_json(self):
    output = {}
    output['start'] = self.start.strftime('%Y-%m')
    output['end'] = self.end.strftime('%Y-%m')
    output['category_labels'] = self.category_labels
    return output


class AnalysisSet(object):
  TEMPLATE = 'analysis-template.json'
  def __init__(self, label, categories):
    self.categories = categories
    self.label = label
    self.files = []
    self.ranges = []
    self.reload()

  def analyze(self):
    purchases = Purchases()


    for datafile in self.files:
      parser = id_to_parser(datafile.type)
      purchases.add_purchases(parser(datafile.fp, self.categories).purchases)

    print('Parsed {} purchases!'.format(len(purchases.data)))
    purchases = purchases.remove_category('Discard')
    income = purchases.get_category('Salary')
    expenses = purchases.remove_category('Salary')
    expenses = expenses.remove_category('Payments')

    print("Total earned: {:10.2f}".format(-income.sum()))
    print("Total spent:  {:10.2f}".format(expenses.sum()))

    for range in self.ranges:
      start_month = (range.start.year, range.start.month)
      end_month = (range.end.year, range.end.month)\

      months = [start_month]
      while(start_month != end_month):
        start_month = increment_month(*start_month)
        months.append(start_month)

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

      for category in range.category_labels:
        args = []
        for month in months:
          monthly_expenses = purchases.month(*month)
          args.append(monthly_expenses.get_category(category).sum())
        if not all([x == 0 for x in args]):
          print(format_float.format(category, *args))

  @property
  def fp(self):
    return self.label + '.json'

  def save(self):
    with open(self.fp, 'w+') as f:
      f.write(json.dumps(self.to_json(), indent=2))

  def reload(self):
    if not os.path.exists(self.fp):
      with open(self.TEMPLATE, 'r') as template:
        with open(self.fp, 'w+') as f:
          for line in template:
            f.write(line)

    with open(self.fp, 'r') as f:
      self.from_json(json.loads(f.read()))
    
  def from_json(self, data):
    self.files = [DataFile(f) for f in data.get('files')]
    self.ranges = [AnalysisRange(r) for r in data.get('ranges')]


  def to_json(self):
    output = {}
    output['files'] = [f.to_json() for f in self.files]
    output['ranges'] = [r.to_json() for r in self.ranges]
    return output