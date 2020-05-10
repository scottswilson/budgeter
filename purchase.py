
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

