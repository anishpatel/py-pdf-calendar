# Python: 2.7.3
# PyCairo: 1.8.8

# Py Cairo: http://cairographics.org/documentation/pycairo/2/reference/context.html#cairo.Context.rectangle
# Cairo concepts: http://www.cairographics.org/tutorial/

import cairo
import calendar
import collections
from datetime import date
import platform

__author__ = "mc"
__date__ = "$May 13, 2012 5:32:26 PM$"

from pdf_calendar_classes import *

calendar.setfirstweekday(calendar.SUNDAY)


def build_calendar(pdf):

  # 7 days per month times 4 months plus 3 gutters = 31
  day_width = pdf.get_drawable_width() / 31
  # 3 rows of months times 8 rows per month plus 2 gutters = 26
  day_height = pdf.get_drawable_height() / 26

  # 7 days plus one day for a gutter
  month_width = day_width * 8
  # 8 days plus one day for a gutter
  month_height = day_height * 9

  # Map start of week with Monday first [0-6] to Sunday first
  # The calendar module has a bug that does not correct this when
  # setfirstweekday(day) is used
  days_of_week = [1, 2, 3, 4, 5, 6, 0]

  day_abbreviations = collections.deque(calendar.day_abbr)
  day_abbreviations.rotate(1)

  year = Year(2012, pdf.get_drawable_width(), pdf.get_drawable_height())
  # Generate a year with months and days
  for count, m in enumerate(calendar.month_name):
    # The months start at index 1
    if not m:
      continue
    # Calculate the upper-left-most corner position of the month for reference
    x = month_width * ((count-1) % 4) + pdf.margin_left
    y = month_height * int((count-1) / 4) + pdf.margin_top
    position = (x, y)
    month = Month(m, count, position, month_width, month_height, * calendar.monthrange(year.label, count))
    if date(year.label, month.int_repr, 1).month < date.today().month:
      month.crossed_out = True
    year.append_month(month)


    # Hack for now... Apply the months label as a day
    day = Day(m, (0, 0), day_width * 7, day_height)
    day.border_color = (1, 1, 1)
    month.append_day_label(day)


    # Add days to represent labels for the days of the week
    for count, d in enumerate(day_abbreviations):
      x_position = count * day_width
      # Add space for the month label
      y_position = day_height
      day = Day(d[0:2], (x_position, y_position), day_width, day_height)
      day.background_color = (.9, .9, .9)
      month.append_day_label(day)
    # Add each day of the month to the month
    for d in range(1, month.length + 1):
      # Update to the desired convention Sunday to Saturday ([1-7])
      start_day = days_of_week[month.start_day]
      # The starting reference points
      relative_position = start_day + d - 1
      x_position = relative_position % 7 * day_width
      # Add space for day of week labels and the month label
      y_position = int(relative_position / 7) * day_height + day_height * 2
      day = Day(d, (x_position, y_position), day_width, day_height)
      if date(year.label, month.int_repr, day.label) < date.today() and date(year.label, month.int_repr, day.label).month == date.today().month:
        day.crossed_out = True
      month.append_day(day)
  return year


def cal_abs_pos(global_position, local_position):
  global_x, global_y = global_position
  local_x, local_y = local_position
  x = global_x + local_x
  y = global_y + local_y
  return (x, y)

def draw_all(surface, year):

  # context.set_operator(cairo.OPERATOR_OVER)
  # context.set_operator(cairo.OPERATOR_CLEAR)
  
  # Setup Cairo with a PDF Surface.
  context = cairo.Context(surface)

  # Draw the current year in the background.
  context.select_font_face('Sans')
  context.set_font_size(270) # em-square height is 90 pixels
  context.move_to(50, 410) # move to point (x, y) = (10, 90)
  context.set_source_rgb(.95, .95, .95)
  context.show_text(str(year.label))

  # Iterate over all of the months drawing each day.
  for count, month in enumerate(year.months):
    # Draw the label for each month
    #print '\n', _month
    for day in month.day_labels:
      # Draw each day
      day.position = cal_abs_pos(month.position, day.position)
      draw_day(context, day)
    for day in month.days:
      # Draw each day
      day.position = cal_abs_pos(month.position, day.position)
      draw_day(context, day)
    # Draw a border around each month
    x, y = month.position
    # Start the border below the month's label
    y = y + day.height
    # Shrink the border around just the days    
    context.set_source_rgb(0, 0, 0)
    context.rectangle(x, y, month.width - day.width, month.height - day.height * 2)
    context.stroke()
    # If the month has passed cross it out
    if month.crossed_out:
      context.set_source_rgb(0, 0, 0)
      context.move_to(x, y)
      context.rel_line_to(month.width - day.width, month.height - day.height * 2)
      context.stroke()
      context.move_to(x + month.width - day.width, y)
      context.rel_line_to(-(month.width - day.width), month.height - day.height * 2)
      context.stroke()
  return context
      

def draw_text(context, text, position):
  # default font size is 10...
  black = (0, 0, 0)
  context.select_font_face('Sans')
  context.set_font_size(10) # em-square height is 90 pixels
  context.move_to(*position) # move to point (x, y) = (10, 90)
  context.set_source_rgb(*black)
  context.show_text(text)

# Fill in a single block of a month grid with a day
def draw_day(context, day):
  context.set_line_width(.5)
  (x, y) = day.position
  # Fill in the background of the rectangle
  context.set_source_rgb(*day.background_color)
  context.rectangle(x, y, day.width, day.height)
  if(day.background_color != (1, 1, 1)):
    context.fill()
  # Highlight the background if stated to do so
  if day.highlighted:
    context.set_source_rgb(*day.highlight_color)
    context.rectangle(x, y, day.width, day.height)
    context.fill()
  # Draw a rectangle
  context.set_source_rgb(*day.border_color)
  context.rectangle(x, y, day.width, day.height)
  context.stroke()
  # Draw text for the day
  draw_text(context, str(day.label), (x + 4, y + 14))
  if day.crossed_out:
    context.move_to(x, y)
    context.rel_line_to(day.width, day.height)
    context.stroke()
    context.move_to(x + day.width, y)
    context.rel_line_to(-day.width, day.height)
    context.stroke()

def main():

  pdf = PDF('test_calendar.pdf')
  surface = cairo.PDFSurface(pdf.filename, pdf.width, pdf.height)
  year = build_calendar(pdf)

  # Hightlight a days, months and days start at zero (0) not one (1).
  year.months[7].days[19].highlighted = True
  year.months[7].days[28].highlighted = True
  year.months[8].days[14].highlighted = True
  year.months[9].days[0].highlighted = True
  year.months[9].days[7].highlighted = True
  year.months[9].days[8].highlighted = True

  year.months[10].days[14].highlighted = True
  year.months[10].days[20].highlighted = True
  year.months[10].days[21].highlighted = True
  year.months[10].days[22].highlighted = True

  year.months[11].days[4].highlighted = True
  year.months[11].days[14].highlighted = True
  
  context = draw_all(surface, year)

  # Draw a border around the edge of the page
  # context.set_source_rgb(0, 0, 0)
  # context.rectangle(pdf.margin_left, pdf.margin_top, pdf.get_drawable_width(), pdf.get_drawable_height())
  # context.stroke()


  # Generate the PDF file.
  surface.show_page()

  # Print the name of the file generated to the command line.
  print ('Generated calendar: ' + pdf.filename)


  # Print out the year structure
  for _month in year.months:
    print '\n\nMonth:', _month, '\nDay labels: ',
    for _day in _month.day_labels:
      print _day,
    print '\nDays: ',
    for _day in _month.days:
      print _day,




if __name__ == "__main__":
  print ('Python version: ' + platform.python_version())
  print ('PyCairo version: ' + cairo.version)
  main()
