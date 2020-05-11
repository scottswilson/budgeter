from file_parser import *
from categories import *
from purchase import *
from analysis_set import *
from dateutil.relativedelta import relativedelta
from utils import increment_month

if __name__ == '__main__':
  categories = Categories()
  analyzer = AnalysisSet('set0', categories)
  analyzer.analyze()


 
