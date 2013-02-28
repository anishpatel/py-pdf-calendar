# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "mc"
__date__ = "$May 13, 2012 5:16:19 PM$"

class Year:

  def __init__(self, label, width, height, columns=4):
    self.label = label
    self.width = width
    self.height = height
    self.columns = columns
    self.months = []

  def append_month(self, month):
    self.months.append(month)

class Month:

  def __init__(self, label, int_repr, position, width, height, start_day, length, days=[]):
    self.label = label
    self.int_repr = int_repr
    self.position = position
    self.width = width
    self.height = height
    self.start_day = start_day
    self.length = length
    self.days = []
    self.day_labels = []
    self.crossed_out = False


  def __str__(self):
    return str(self.label)
  
  def append_day(self, day):
    self.days.append(day)

  def append_day_label(self, day):
    self.day_labels.append(day)


class Day:

  def __init__(self, label, position, width, height,
               background_color=(1, 1, 1)):
    # Must be declaired.
    self.label = label
    self.position = position
    self.width = width
    self.height = height
    # Optional to set.
    self.background_color = background_color
    self.font_face = 'Sans'
    self.font_color = (0, 0, 0)
    self.border_color = (0, 0, 0)
    self.crossed_out = False
    self.highlighted = False
    self.highlight_color = (0.8, 0.8, 0.9)

  def __str__(self):
    return str(self.label)

class PDF:
  """ Hold information about a PDF layout and provide helper functions """

  def __init__(self, filename):
    self.filename = filename
    # The standard unit of PDFs is PostScript Points.
    # Note: 25.4 mm = 1 inch, 72 pt = 1 inch.
    # Note: 0.5 in = 12.7 mm
    self.POINT_TO_MILIMETER = 72 / 25.4
    # Define margins
    half_inch = 12.7 * self.POINT_TO_MILIMETER
    self.margin_top = half_inch
    self.margin_right = half_inch
    self.margin_bottom = half_inch
    self.margin_left = half_inch
    # The standard US landscape layout,
    # 11 by 8.5 inches in points (1 inch = 72 points).
    self.width = 792
    self.height = 612

  def get_drawable_width(self):
    return self.width - self.margin_left - self.margin_right

  def get_drawable_height(self):
    return self.height - self.margin_top - self.margin_bottom


def main():
  import calendar
  pdf = PDF('test_calendar.pdf')
  year = Year(2012, pdf.get_drawable_width(), pdf.get_drawable_height())
  # Generate a year with months and days
  for count, m in enumerate(calendar.month_name):
    # The months start at index 1
    if not m:
      continue
    month = Month(m, *calendar.monthrange(year.label, count))
    year.append_month(month)    
    for d in range(1, month.length + 1):
      day = Day(d, (20, 20), 20, 15)
      month.append_day(day)
      
  # Print out the year structure
  for _month in year.months:
    print '\n', _month
    for _day in _month.days:
      print _day,

if __name__ == "__main__":
  main()
