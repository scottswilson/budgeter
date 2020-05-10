import re

def increment_month(year, month):
  if (month != 12):
    return year, month+1
  else:
    return year+1, 1

    
def sanitize_line(line):
  search = re.search('(".*")', line)

  if not search:
    return line

  for group in search.groups():
    group_replacement = group.replace('"', '').replace(',', '')
    line = line.replace(group, group_replacement)

  return line