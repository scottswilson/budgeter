import json
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