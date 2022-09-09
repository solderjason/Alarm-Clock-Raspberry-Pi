from machine import Pin, I2C
from machine import Pin, PWM
import time
from ssd1306 import SSD1306_SPI
import framebuf
from time import sleep
from utime import sleep_ms
import utime
from machine import Pin, SPI
from urtc import DS1307


class Radio:

    def __init__( self, NewFrequency, NewVolume, NewMute ):

#
# set the initial values of the radio
#
        self.Volume = 2
        self.Frequency = 88
        self.Mute = False
#
# Update the values with the ones passed in the initialization code
#
        self.SetVolume( NewVolume )
        self.SetFrequency( NewFrequency )
        self.SetMute( NewMute )


# Initialize I/O pins associated with the radio's I2C interface

        self.i2c_sda = Pin(26)
        self.i2c_scl = Pin(27)

#
# I2C Device ID can be 0 or 1. It must match the wiring.
#
# The radio is connected to device number 1 of the I2C device
#
        self.i2c_device = 1
        self.i2c_device_address = 0x10

#
# Array used to configure the radio
#
        self.Settings = bytearray( 8 )


        self.radio_i2c = I2C( self.i2c_device, scl=self.i2c_scl, sda=self.i2c_sda, freq=200000)
        self.ProgramRadio()

    def SetVolume( self, NewVolume ):
#
# Conver t the string into a integer
#
        try:
            NewVolume = int( NewVolume )

        except:
            return( False )

#
# Validate the type and range check the volume
#
        if ( not isinstance( NewVolume, int )):
            return( False )

        if (( NewVolume < 0 ) or ( NewVolume >= 16 )):
            return( False )

        self.Volume = NewVolume
        return( True )



    def SetFrequency( self, NewFrequency ):
#
# Convert the string into a floating point value
#
        try:
            NewFrequency = float( NewFrequency )

        except:
            return( False )
#
# validate the type and range check the frequency
#
        if ( not ( isinstance( NewFrequency, float ))):
            return( False )

        if (( NewFrequency < 88.0 ) or ( NewFrequency > 108.0 )):
            return( False )

        self.Frequency = NewFrequency
        return( True )

    def SetMute( self, NewMute ):

        try:
            self.Mute = bool( int( NewMute ))

        except:
            return( False )

        return( True )

#
# convert the frequency to 10 bit value for the radio chip
#
    def ComputeChannelSetting( self, Frequency ):
        Frequency = int( Frequency * 10 ) - 870

        ByteCode = bytearray( 2 )
#
# split the 10 bits into 2 bytes
#
        ByteCode[0] = ( Frequency >> 2 ) & 0xFF
        ByteCode[1] = (( Frequency & 0x03 ) << 6 ) & 0xC0
        return( ByteCode )

#
# Configure the settings array with the mute, frequency and volume settings
#
    def UpdateSettings( self ):

        if ( self.Mute ):
            self.Settings[0] = 0x80
        else:
            self.Settings[0] = 0xC0

        self.Settings[1] = 0x09 | 0x04
        self.Settings[2:3] = self.ComputeChannelSetting( self.Frequency )
        self.Settings[3] = self.Settings[3] | 0x10
        self.Settings[4] = 0x04
        self.Settings[5] = 0x00
        self.Settings[6] = 0x84
        self.Settings[7] = 0x80 + self.Volume

#
# Update the settings array and transmitt it to the radio
#
    def ProgramRadio( self ):

        self.UpdateSettings()
        self.radio_i2c.writeto( self.i2c_device_address, self.Settings )

#
# Extract the settings from the radio registers
#
    def GetSettings( self ):
#
# Need to read the entire register space. This is allow access to the mute and volume settings
# After and address of 255 the
#
        self.RadioStatus = self.radio_i2c.readfrom( self.i2c_device_address, 256 )

        if (( self.RadioStatus[0xF0] & 0x40 ) != 0x00 ):
            MuteStatus = False
        else:
            MuteStatus = True

        VolumeStatus = self.RadioStatus[0xF7] & 0x0F

 #
 # Convert the frequency 10 bit count into actual frequency in Mhz
 #
        FrequencyStatus = (( self.RadioStatus[0x00] & 0x03 ) << 8 ) | ( self.RadioStatus[0x01] & 0xFF )
        FrequencyStatus = ( FrequencyStatus * 0.1 ) + 87.0

        if (( self.RadioStatus[0x00] & 0x04 ) != 0x00 ):
            StereoStatus = True
        else:
            StereoStatus = False

        return( MuteStatus, VolumeStatus, FrequencyStatus, StereoStatus )

buzzer = PWM(Pin(15))
tones = {
"C3": 131,
"CS3": 139,
"D3": 147,
"DS3": 156,
"E3": 165,
"F3": 175,
"FS3": 185,
"G3": 196,
"GS3": 208,
"A3": 220,
"AS3": 233,
"B3": 247,
"C4": 262,
"CS4": 277,
"D4": 294,
"DS4": 311,
"E4": 330,
"F4": 349,
"FS4": 370,
"G4": 392,
"GS4": 415,
"A4": 440,
"AS4": 466,
"B4": 494,
"C5": 523,
"CS5": 554,
"D5": 587,
"DS5": 622,
"E5": 659,
"F5": 698,
"FS5": 740,
"G5": 784,
"GS5": 831,
"A5": 880,
"AS5": 932,
"B5": 988,
"C6": 1047,
"CS6": 1109,
"D6": 1175,
"DS6": 1245,
"E6": 1319,
"F6": 1397,
"FS6": 1480,
"G6": 1568,
"GS6": 1661,
"A6": 1760,
"AS6": 1865,
"B6": 1976
}
song = ["D4","P","D4","P","A4","P","P","D4","P","D4","P","AS4","P","P","D4","P","D4","P","A4","P","P","D4","P",
        "D4","P","CS4","P","P","P","D4","P","D4","P","A4","P","P","P","D4","P","D4","P","CS5","P","P","P","D5","P","P","P",
        "P","P","P","P","FS5","D6","P","P","P","P","P","G3","B3","D4","FS4","G4",
        "P","P","P","G4","P","P","P","P","P","G4","G4",
        "G4","P","P","P","G4","P","P","P","F4","F4","P","F4","F4","P","FS4","G4","P","P","P","P","P",
        "B4","P","D5","P","P","P","P","P","P","P","F4","P","P","P","P","P","A4","P","F5","P","P","P","P","P","E5","DS5",
        "D5","P","P","P","P","P","P","F4","P","P","P","P","P","E4","DS4","D4","P","P","P","P","P","P","P","C4","P",
        "P","B3","P","C4","P","P","G4","P","P","P","P","P","B4","P","D5","P","P","P","P","P","P","P","F4","P","P","P",
        "P","P","P","P","C5","P","P","A4","P","C5","P","P","D5","P","P","P","P","P","P","P","F4","P","P","E4","P","C4",
        "P","P","D4","P","P","P","P","P","P","P","P","B3","P","C4","P","D4","P","G4","P","P","P","P","P","B4","P",
        "D5","P","P","P","P","P","P","F4","P","P","P","P","P","A4","P","F5","P","P","P","P","P","E5","DS5","D5","P",
        "P","P","P","P","P","P","F4","P","P","P","P","P","E4","DS4","D4","P","P","P","P","P","P","P","C4","P","P","B3",
        "P","C4","P","G4","P","P","P","P","P","B4","P","D5","P","P","P","P","P","F4","P","P","P","P",
        "P","P","F5","P","P","E5","P","F5","P","P","G5","P","P","P","P","P","AS5","P","G5"]

def playtone(frequency):
    buzzer.duty_u16(1000)
    buzzer.freq(frequency)

def bequiet():
    buzzer.duty_u16(0)

stop=0
def playsong(mysong):
    Mute = 1
    if ( fm_radio.SetMute( Mute ) == True ):
        fm_radio.ProgramRadio()
    global stop
    for i in range(len(mysong)):
        if (stop==1):
            break
        else:
            if (mysong[i] == "P"):
                bequiet()
            else:
                playtone(tones[mysong[i]])
            sleep(0.09)
    bequiet()

#
# initialize the FM radio
#

spi = SPI(0, 100000, mosi=Pin(19), sck=Pin(18))
display = SSD1306_SPI(128, 64, spi, Pin(17),Pin(20), Pin(16))
fm_radio = Radio( 101.9, 2, False )

button1 = Pin(2, Pin.IN)  # gp2 number pin is input
button2 = Pin(3, Pin.IN)  # gp3 number pin is input
button3 = Pin(4, Pin.IN)  # gp4 number pin is input
button4 = Pin(5, Pin.IN)  # gp5 number pin is input

button1_pushed=0
button2_pushed=0
button3_pushed=0
button4_pushed=0

def monitorInput():
    global button1_pushed
    button1_pushed = 0
    global button2_pushed
    button2_pushed = 0
    global button3_pushed
    button3_pushed = 0
    global button4_pushed
    button4_pushed = 0
    logic_state1 = button1.value()
    logic_state2 = button2.value()
    logic_state3 = button3.value()
    logic_state4 = button4.value()
    if logic_state1 == 0 :
        button1_pushed=1
    if logic_state2 == 0 :
        button2_pushed=1
    if logic_state3 == 0 :
        button3_pushed=1
    if logic_state4 == 0 :
        button4_pushed=1

def monitorAlarm():
    global alarm_hour
    global alarm_min
    global alarm_second
    init_inturrupt()
    if (hour==alarm_hour and min==alarm_min and second==alarm_second and Alarm==1):
     while (True):
         resetOLED()
         monitorInput()
         display.text( "Pika Pika!!!",20, 0 )
         display.text( "2-Snooze 5min", 0,12)
         display.text( "3-Snooze 10min",0,24)
         display.text( "4-Stop",0, 36)
         display.show();
         button2.irq(trigger=Pin.IRQ_RISING, handler=snooze_alarm_5)
         button3.irq(trigger=Pin.IRQ_RISING, handler=snooze_alarm_10)
         button4.irq(trigger=Pin.IRQ_RISING, handler=stop_alarm)
         playsong(song)
         if(stop==1 ):
            sleep(0.5)
            break
    init_inturrupt()

def resetOLED():
    display.fill(0);
    display.text( "",0, 0)
    display.text( "",0, 12 )
    display.text( "",0, 24 )
    display.text( "",0, 36 )
    display.text( "",0, 48 )
    display.text( "",0, 60 )

def snooze_alarm_5(Pin):
    #5 min snooze
    init_inturrupt()
    global stop
    global alarm_min
    global alarm_hour
    stop=1
    alarm_min=alarm_min+5
    if(alarm_min>59):
     alarm_min=60-alarm_min
     alarm_hour=alarm_hour+1
     if(alarm_hour>23):
         alarm_hour=0
def snooze_alarm_10(Pin):
    #10 min snooze
    init_inturrupt()
    global stop
    global alarm_min
    global alarm_hour
    stop=1
    alarm_min=alarm_min+10
    if(alarm_min>59):
     alarm_min=60-alarm_min
     alarm_hour=alarm_hour+1
     if(alarm_hour>23):
         alarm_hour=0

def stop_alarm(Pin):
    #stops and turns off the alarm
    init_inturrupt()
    Alarm=0
    global stop
    stop=1

def init_inturrupt():
    button2.irq(handler=None)
    button3.irq(handler=None)
    button4.irq(handler=None)

status=0 #0 is the main menu
Volume=2# default value is 2
Mute = 1#muted by default
AM=1#assume AM
global TwentyFour
TwentyFour=1# true by default
Alarm=0# off by default
global alarm_hour
alarm_hour=0#hour for the alarm
global alarm_min
alarm_min=0# min for the alarm
global alarm_second
alarm_second=0
display_volume=3# volume will be shown from 1-16 to better represent the mute
hourtf=(utime.localtime()[3])# retains the hour in a 24 hr format
if ( fm_radio.SetMute( Mute ) == True ):
            fm_radio.ProgramRadio()
Frequency=101.9# default frequency
#default display
i2c = I2C(0,scl=Pin(1),sda=Pin(0),freq=400000)
result=I2C.scan(i2c)
rtc = DS1307(i2c)
while ( True ):
    init_inturrupt()
    stop=0
    (year,month,date,day,hour,min,second,p1)=rtc.datetime()
    hourtf=hour
    resetOLED()
    if(TwentyFour==0 and hourtf>=12):
                hour= hourtf-12
                display.text("PM",0,0,1)
    elif(TwentyFour==0 and hourtf<12):
                display.text("AM",0,0,1)
    display.text(str(hour)+':', 20, 0, 1)
    display.text(str(min)+': ', 45, 0, 1)
    display.text(str(second), 70, 0, 1)
    display.text( "Pika Clock Radio",0, 12 )
    display.text( "1-Radio",0, 24 )
    display.text( "2-Alarm",0, 36 )
    display.text( "3-Clock",0, 48 )
    monitorInput();
    monitorAlarm();
#
#Radio Menu
#
    if ( button1_pushed == 1 ):
        sleep(0.5)
        resetOLED()
        Mute = 0
        if ( fm_radio.SetMute( Mute ) == True ):
            fm_radio.ProgramRadio()
        while (True):
            resetOLED()
            display.text( str(Frequency),40, 0 )
            display.text( "1-Frequency",0, 12 )
            display.text( "2-Volume",0, 24 )
            display.text( "3-Current Info",0, 36 )
            display.text( "4-Back",0, 48 )
            display.show()
            monitorInput()
            monitorAlarm()
            if(button1_pushed==1):
                sleep(0.2)
                while (True):
                 monitorInput()
                 resetOLED()
                 display.text( str(Frequency),40, 0 )
                 display.text( "1-10",0, 24 )# increase by 10s
                 display.text( "2-1",40, 24 )#increase by 1s
                 display.text( "3-0.1",0, 36 )#increase by 0.1s
                 display.text( "4-Back",0, 48 )
                 display.show()

                 if (button1_pushed==1):
                     sleep(0.5)
                     while (True):
                         # changes by 10
                         monitorInput()
                         resetOLED()
                         display.text( str(Frequency),40, 0 )
                         display.text( "1-Up",0, 24 )
                         display.text( "2-Down",40, 24 )
                         display.text( "3-Set",0, 36 )
                         display.text( "4-Back",0, 48 )
                         display.show()
                         monitorAlarm()
                         if(button1_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency+10
                             if(Frequency<88.0):
                                 Frequency=88.0#lowest frequency allowed
                             elif(Frequency>108.0):
                                 Frequency=108.0#highest frequency allowed
                         elif(button2_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency-10
                             if(Frequency<88.0):
                                 Frequency=88.0
                             elif(Frequency>108.0):
                                 Frequency=108.0
                         elif (button3_pushed==1):
                                      #set Frequency
                             sleep(0.5)
                             if ( fm_radio.SetFrequency( Frequency ) == True ):
                                fm_radio.ProgramRadio()
                             break
                         elif (button4_pushed==1):
                            sleep(0.5)
                            break
                 elif (button2_pushed==1):
                     sleep(0.5)
                     while (True):
                         monitorInput()
                         resetOLED()
                         display.text( str(Frequency),40, 0 )
                         display.text( "1-Up",0, 24 )
                         display.text( "2-Down",40, 24 )
                         display.text( "3-Set",0, 36 )
                         display.text( "4-Back",0, 48 )
                         display.show()
                         monitorAlarm()
                         if(button1_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency+1

                             if(Frequency<88.0):
                                 Frequency=88.0
                             elif(Frequency>108.0):
                                 Frequency=108.0
                         elif(button2_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency-1

                             if(Frequency<88.0):
                                 Frequency=88.0
                             elif(Frequency>108.0):
                                 Frequency=108.0
                         elif (button3_pushed==1):
                             #set Frequency
                             sleep(0.5)
                             if ( fm_radio.SetFrequency( Frequency ) == True ):
                                fm_radio.ProgramRadio()
                             break
                         elif (button4_pushed==1):
                            sleep(0.5)
                            break
                 elif (button3_pushed==1):
                     sleep(0.5)
                     while (True):
                         #changes by 0.1
                         monitorInput()
                         resetOLED()
                         display.text( str(Frequency),40, 0 )
                         display.text( "1-Up",0, 24 )
                         display.text( "2-Down",40, 24 )
                         display.text( "3-Set",0, 36 )
                         display.text( "4-Back",0, 48 )
                         display.show()
                         monitorAlarm()
                         if(button1_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency+0.1
                             if(Frequency<88.0):
                                 Frequency=88.0
                             elif(Frequency>108.0):
                                 Frequency=108.0
                         elif(button2_pushed==1):
                             sleep(0.5)
                             Frequency= Frequency-0.1
                             if(Frequency<88.0):
                                 Frequency=88.0
                             elif(Frequency>108.0):
                                 Frequency=108.0
                         elif (button3_pushed==1):
                             #set Frequency
                             sleep(0.5)
                             if ( fm_radio.SetFrequency( Frequency ) == True ):
                                fm_radio.ProgramRadio()
                             break
                         elif (button4_pushed==1):
                            sleep(0.5)
                            break

                 elif (button4_pushed==1):
                     sleep(0.5)
                     break
#
#set radio Volume
#
            elif(button2_pushed==1):
                while (True):
                 resetOLED()
                 display_volume=Volume+1
                 monitorInput()
                 display.text( "Select Volume",0, 0 )
                 display.text( "%d" % display_volume,0, 12 )
                 display.text( "1-Up",0, 24 )
                 display.text( "2-Down",40, 24 )
                 display.text( "3-Set",0, 36 )
                 display.text( "4-Mute/Unmute",0,48)
                 monitorAlarm()
                 if (button1_pushed == 1):
                  Volume=Volume+1

                  sleep(0.3)
                 elif (button2_pushed == 1):
                  Volume=Volume-1
                  sleep(0.3)
                 if (Volume>15):
                  Volume=15
                 if (Volume<0):
                  Volume=0
                 display.show(); # somehow the volume doesnt change
                 if (button3_pushed == 1):
                  sleep(0.5)
                  button3_pushed=0
                  if ( fm_radio.SetVolume( Volume ) == True ):
                    fm_radio.ProgramRadio()
                    break
                 elif(button4_pushed==1):
                      sleep(0.5)
                      while (True):
                        monitorInput()
                        monitorAlarm()
                        resetOLED()
                        if(Mute==0):
                         display.text( "Unmute",40, 0 )
                        else:
                         display.text( "Mute",40,0)
                        display.text( "1-Toggle",0, 24 )
                        display.text( "3-Set",0, 36 )
                        display.show()
                        monitorInput()
                        if(button1_pushed==1):
                         sleep(0.3)
                         if(Mute==1):
                          Mute=0
                         elif (Mute==0):
                          Mute=1

                        if(button3_pushed==1):
                         sleep(0.3)
                         if ( fm_radio.SetMute( Mute ) == True ):
                          fm_radio.ProgramRadio()
                          break
#
#View Radio Information
#
            monitorInput()

            if(button3_pushed==1):
              sleep(0.5)
              while(True):
                 resetOLED()
                 display.text( "Radio Settings",0, 0 )
                 display.text( "Frequency:",0, 12 )
                 display.text( str(Frequency),80, 12 )
                 display.text( "Volume:%d" % display_volume,0, 24 )
                 monitorAlarm()

                 if(Mute==0):
                     display.text( "Unmuted",0, 36 )
                 else:
                     display.text( "Muted",0,36)

                 display.text( "Any Button-Back",0,48)
                 display.show()
                 monitorInput()
                 if(button1_pushed==1 or button2_pushed==1 or button3_pushed==1 or button4_pushed==1):
                     #exits loop with any button
                     sleep(0.5)
                     break

            monitorInput()
            if(button4_pushed==1):
               sleep(0.5)
               break
    elif ( button2_pushed == 1 ):
        #
        #Alarm interface
        #
        sleep(0.5)
        while (True):
            monitorInput();
            init_inturrupt()
            resetOLED()
            display.text(str(hour)+':', 20, 0, 1)
            display.text(str(min)+': ', 45, 0, 1)
            display.text(str(second), 70, 0, 1)
            if(Alarm==0):
                display.text("Alarm is OFF",0,12,1)
            elif(Alarm==1):
                display.text("Alarm is ON",0,12,1)
            display.text("1-Time",0,24)
            display.text("2-Toggle ON/OFF",0,36)
            display.text("4-Back", 0,48)
            display.show()
            monitorAlarm()
            if (button1_pushed==1):
                #
                #alarm adjustment interface
                #
                sleep(0.3)
                while (True):
                    #set alarm
                    monitorInput();
                    resetOLED()
                    (year,month,date,day,hour,min,second,p1)=rtc.datetime()
                    display.text(str(hour)+':', 20, 0, 1)
                    display.text(str(min)+': ', 45, 0, 1)
                    display.text(str(second), 70, 0, 1)
                    display.text("1-Hour",0,12)
                    display.text("2-Minute",0,24)
                    display.text("3-Second", 0,36)
                    display.text("4-Back",0, 48)
                    display.show()
                    monitorInput()
                    monitorAlarm()
                    if(button1_pushed==1):
                        #modify alarm by hour
                        sleep(0.5)
                        while(True):
                             resetOLED()
                             display.text(str(alarm_hour)+':', 20, 0, 1)
                             display.text(str(alarm_min)+': ', 45, 0, 1)
                             display.text(str(alarm_second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 alarm_hour= alarm_hour+1
                                 if(alarm_hour>23):
                                     alarm_hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 alarm_hour= alarm_hour-1

                                 if(alarm_hour<0):
                                     alarm_hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 break
                    monitorInput()
                    if(button2_pushed==1):
                        #modify alarm by minute
                        sleep(0.5)
                        while(True):
                             resetOLED()
                             display.text(str(alarm_hour)+':', 20, 0, 1)
                             display.text(str(alarm_min)+': ', 45, 0, 1)
                             display.text(str(alarm_second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 alarm_min= alarm_min+1
                                 if(alarm_min>59):
                                  alarm_hour=alarm_hour+1
                                  alarm_min=0
                                  if(alarm_hour>23):
                                     alarm_hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 alarm_min= alarm_min-1
                                 if(alarm_min<0):
                                  alarm_hour=alarm_hour-1
                                  alarm_min=59
                                  if(alarm_hour<0):
                                     alarm_hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 break
                    monitorInput()
                    if(button3_pushed==1):
                        #modify alarm by second
                        sleep(0.5)
                        while(True):
                             resetOLED()
                             display.text(str(alarm_hour)+':', 20, 0, 1)
                             display.text(str(alarm_min)+': ', 45, 0, 1)
                             display.text(str(alarm_second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 alarm_second= alarm_second+1
                                 if(alarm_second>59):
                                  alarm_second=0
                                  alarm_min=alarm_min+1
                                  if(alarm_min>59):
                                    alarm_min=0
                                    alarm_hour=alarm_hour+1
                                    if(alarm_hour>23):
                                        alarm_hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 alarm_second= alarm_second-1
                                 if(alarm_second<0):
                                  alarm_second=59
                                  alarm_min=alarm_min-1
                                  if(alarm_min<0):
                                    alarm_min=59
                                    alarm_hour=alarm_hour-1
                                    if(alarm_hour<0):
                                        alarm_hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 break
                    monitorInput()
                    if(button4_pushed==1):
                        sleep(0.5)
                        break
            monitorInput()
            if (button2_pushed==1):
                #toggles alarm status
                sleep(0.3)
                if(Alarm==0):
                    Alarm=1
                elif(Alarm==1):
                    Alarm=0
            monitorInput()
            if (button4_pushed==1):
                sleep(0.3)
                break
    elif ( button3_pushed == 1 ):
        #
        #Time Menu
        #
        while (True):
            resetOLED()
            (year,month,date,day,hour,min,second,p1)=rtc.datetime()
            hourtf=hour#keeps copy in 24 hr format
            if(TwentyFour==0 and hourtf>=12):
                hour= hourtf-12
                display.text("PM",0,0,1)
            elif(TwentyFour==0 and hourtf<12):
                display.text("AM",0,0,1)
            display.text(str(hour)+':', 20, 0, 1)
            display.text(str(min)+': ', 45, 0, 1)
            display.text(str(second), 70, 0, 1)
            display.text( "1-Toggle Hour Type",0, 12 )
            display.text( "2-Time Setting",0, 24 )
            display.text( "",0, 36 )
            display.text( "4-Back",0, 48 )
            monitorInput();
            display.show()
            monitorAlarm()
            if(button1_pushed==1):
                sleep(0.3)
                if(TwentyFour==0):
                 TwentyFour=1
                elif(TwentyFour==1):
                    TwentyFour=0
            if(button2_pushed==1):
                sleep(0.3)
                while (True):
                    #set alarm
                    monitorInput();
                    resetOLED()
                    (year,month,date,day,hour,min,second,p1)=rtc.datetime()
                    display.text(str(hour)+':', 20, 0, 1)
                    display.text(str(min)+': ', 45, 0, 1)
                    display.text(str(second), 70, 0, 1)
                    display.text("1-Hour",0,12)
                    display.text("2-Minute",0,24)
                    display.text("3-Second", 0,36)
                    display.text("4-Back",0, 48)
                    display.show()
                    monitorInput()
                    monitorAlarm()
                    if(button1_pushed==1):
                        #modify by hour
                        sleep(0.5)
                        while(True):
                             resetOLED()
                             display.text(str(hour)+':', 20, 0, 1)
                             display.text(str(min)+': ', 45, 0, 1)
                             display.text(str(second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 hour= hour+1
                                 if(hour>23):
                                     hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 hour= hour-1
                                 if(hour<0):
                                     hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 now=(year,month,date,day,hour,min,second,0)
                                 rtc.datetime(now)
                                 break
                    if(button2_pushed==1):
                        #modify by minute
                        sleep(0.5)
                        while(True):
                             resetOLED()
                             display.text(str(hour)+':', 20, 0, 1)
                             display.text(str(min)+': ', 45, 0, 1)
                             display.text(str(second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 min= min+1
                                 if(min>59):
                                  hour=hour+1
                                  min=0
                                  if(hour>23):
                                     hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 min= min-1

                                 if(min<0):
                                  hour=hour-1
                                  min=59
                                  if(hour<0):
                                     hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 now=(year,month,date,day,hour,min,second,0)
                                 rtc.datetime(now)
                                 break
                    monitorInput()
                    if(button3_pushed==1):
                        sleep(0.5)
                        #modify by second
                        while(True):
                             resetOLED()
                             display.text(str(hour)+':', 20, 0, 1)
                             display.text(str(min)+': ', 45, 0, 1)
                             display.text(str(second), 70, 0, 1)
                             display.text( "1-Up",0, 24 )
                             display.text( "2-Down",40, 24 )
                             display.text( "4-Back",0, 48 )
                             display.show()
                             monitorInput()
                             monitorAlarm()
                             if(button1_pushed==1):
                                 sleep(0.5)
                                 second= second+1
                                 if(second>59):
                                  second=0
                                  min=min+1
                                  if(min>59):
                                    min=0
                                    hour=hour+1
                                    if(hour>23):
                                        hour=0
                             if(button2_pushed==1):
                                 sleep(0.5)
                                 second= second-1
                                 if(second<0):
                                  second=59
                                  min=min-1
                                  if(min<0):
                                    min=59
                                    hour=hour-1
                                    if(hour<0):
                                        hour=23
                             if(button4_pushed==1):
                                 sleep(0.5)
                                 now=(year,month,date,day,hour,min,second,0)
                                 rtc.datetime(now)
                                 break
                    monitorInput()
                    if(button4_pushed==1):
                        sleep(0.5)
                        break
            monitorInput()
            if(button4_pushed==1):
                sleep(0.5)
                break
    display.show();
