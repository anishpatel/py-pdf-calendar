# Python: 2.7.3
# PyCairo: 1.8.8

# Py Cairo: http://cairographics.org/documentation/pycairo/2/reference/context.html#cairo.Context.rectangle
# Cairo concepts: http://www.cairographics.org/tutorial/

__author__ = "mc"
__date__ = "$May 11, 2012 4:47:10 PM$"

import cairo
import calendar
import platform
calendar.setfirstweekday(calendar.SUNDAY)

from pdf_calendar_classes import *

# Fill in a single block of a month grid with a day
def draw_day(context, pdf, position, width, height, text):
  context.set_line_width(1)
  (x, y) = position
  # Draw a rectangle
  context.set_source_rgb(0, 0, 0)
  context.rectangle(x, y, width, height)
  context.stroke()
  # Fill in the background of the rectangle
  context.set_source_rgb(1, 1, 1)
  context.rectangle(x, y, width, height)
  context.fill()
  # Draw text for the day
  draw_text(context, text, (x + 4, y + 14))

def draw_day_of_week_label(context, pdf):
  pass

def draw_text(context, text, position):
  # default font size is 10...
  black = (0, 0, 0)
  context.select_font_face('Sans')
  #context.set_font_size(60) # em-square height is 90 pixels
  context.move_to(*position) # move to point (x, y) = (10, 90)
  context.set_source_rgb(*black)
  context.show_text(text)

def draw_all(context, pdf):
  """ Draw everything... """

  # Map start of week with Monday first [0-6] to Sunday first [1-7]
  # The calendar module has a bug that does not correct this when
  # setfirstweekday(day) is used
  days_of_week = [2, 3, 4, 5, 6, 7, 1]

  year = 2012    

  # 7 days per month times 4 months plus 3 gutters = 31
  day_width = (pdf.width - pdf.margin_left - pdf.margin_right) / 31
  # 3 rows of months times 8 rows per month plus 2 gutters = 26
  day_height = (pdf.height - pdf.margin_top - pdf.margin_bottom) / 26

  row = -1
  column = -1
       
  # Iterate over each of the months
  for count, month in enumerate(calendar.month_name):
    # The months start at index 1.
    if count is 0:
      continue
    # Reset the counters used later
    start_day_count = day_count = 1
    start_of_month, length_of_month = calendar.monthrange(year, count)
    # Update to the desired convention Sunday to Saturday ([1-7])
    start_of_month = days_of_week[start_of_month]
    # Put four months in each row.
    if count % 4 is 1:
      row = row + 1
      column = -1
    # Set the offset to go to the next column
    column = column + 1
    # A grid of 0-55 is used for positioning
    for grid_position in range (56):
      x = pdf.margin_left + column * (day_width * 8)
      y = pdf.margin_top + row * (day_height * 9)
      x = x + grid_position % 7 * day_width
      y = y + int(grid_position / 7) * day_height
      position = (x, y)
      # Draw the label for the month.
      if grid_position is 0:
        x, y = position
        y = y + 16
        position = (x, y)
        draw_text(context, month, position)
      # The first row is resevered for the month's label
      if grid_position in range(0, 7):
        continue
      # Draw the labels for each day of the week
      if grid_position in range(7, 14):
        text = calendar.day_abbr[grid_position-8][0:2]
      else:
        if start_day_count >= start_of_month and day_count <= length_of_month:
          text = str(day_count)
          day_count = day_count + 1
        else:
          start_day_count = start_day_count + 1
          text = ''                
      draw_day(context, pdf, position, day_width, day_height, text)

def main():
  """ The main execution part ... """

  # Create a PDF object.
  pdf = PDF('calendar.pdf')
  # Setup Cairo with a PDF Surface.
  surface = cairo.PDFSurface(pdf.filename, pdf.width, pdf.height)
  cr_context = cairo.Context(surface)
  # Prepare the source, paths, and mask for the destination surface.
  draw_all(cr_context, pdf)
  # Generate the PDF file.
  surface.show_page()
  # Print the name of the file generated to the command line.
  print ('Generated calendar: ' + pdf.filename)

if __name__ == "__main__":
  print ('Python version: ' + platform.python_version())
  print ('PyCairo version: ' + cairo.version)
  main()
