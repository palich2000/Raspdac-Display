#!/usr/bin/python
#
# Author : Matt Hawkins
# Date   : 06/04/2015
# http://www.raspberrypi-spy.co.uk/
#
# Author : Robert Coward/Paul Carpenter (based on driver by Matt Hawkins/)
# https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=68055
# Date   : 02/03/2014
#
# Author : Audiophonics
# Date   : 23/09/2015 (V1.0)
# http://www.audiophonics.fr
# http://forum.audiophonics.fr/viewtopic.php?f=4&t=1492
#--------------------------------------

# The wiring for the LCD is as follows:
# 1 : GND
# 2 : 5V
# 3 : Contrast (0-5V)*
# 4 : RS (Register Select)
# 5 : R/W (Read Write)       - GROUND THIS PIN
# 6 : Enable or Strobe
# 7 : Data Bit 0             - NOT USED
# 8 : Data Bit 1             - NOT USED
# 9 : Data Bit 2             - NOT USED
# 10: Data Bit 3             - NOT USED
# 11: Data Bit 4
# 12: Data Bit 5
# 13: Data Bit 6
# 14: Data Bit 7
# 15: LCD Backlight +5V**
# 16: LCD Backlight GND

#import
import RPi.GPIO as GPIO
import time
import subprocess;
import os;
from decimal import Decimal, ROUND_DOWN
process_name= "mpdlcd"

# Define GPIO to LCD mapping
LCD_RS = 7
LCD_E  = 8
LCD_D4 = 25
LCD_D5 = 24
LCD_D6 = 23
# LCD_D7 = 15
LCD_D7 = 27

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.001

def main():
  # Main program block

  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7

  # Initialise display
  lcd_init()
  lcd_byte(0x01,True)
  lcd_string("Starting....",LCD_LINE_1)

def lcd_init():
  # Initialise display
  lcd_byte(0x33,False) # 110011 Initialise
  lcd_byte(0x32,False) # 110010 Initialise
  lcd_byte(0x06,False) # 000110 Cursor move direction  
  lcd_byte(0x0C,False) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,False) # 101000 Data length, number of lines, font size
  lcd_byte(0x08,False) # Display off OLED ADD
  lcd_byte(0x01,False) # 000001 Clear display
  time.sleep(0.01)
  # extra steps required for OLED initialisation (no effect on LCD)
  lcd_byte(0x17, False)    # character mode, power on      OLED ADD

  # now turn on the display, ready for use - IMPORTANT!
  lcd_byte(0x0C, False)    # display on, cursor/blink off     OLED ADD

def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command

  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):
  # Send string to display

  message = message.center(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)
  if not LCD_CMD:
      for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]),LCD_CHR)

if __name__ == '__main__':

  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    GPIO.cleanup()
