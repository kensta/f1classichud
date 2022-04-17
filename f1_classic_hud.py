######################################################################
# F1 CLASSIC HUD by Kenji Kumakura <kenji.kumakura@gmail.com>
#
# Version 1.0.1
######################################################################
# 1.0.1
# - Added inner shadow to RPM and GAS bars
# - Replaced the remaining texts from background image to native text
#   -> The only image kept is the green circle around gear numbers
######################################################################
import ac
import acsys
import os
import sys
import platform

if platform.architecture()[0] == "64bit":
    libdir = 'third_party/lib64'
else:
    libdir = 'third_party/lib'

sys.path.insert(0, os.path.join(os.path.dirname(__file__), libdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from third_party.sim_info import info
from third_party.util import *

APP_WIDTH = 940
APP_HEIGHT = 280
SCALE = 1
RPM_BAR_CURRENT_VALUE = 0
GAS_BAR_CURRENT_VALUE = 20
APP_PATH = "apps/python/f1_classic_hud/"

class AppHud:
    def __init__(self, window):
        self.window = window

        # Initialize car values
        if info.static.maxRpm:
            self.rpm_max = info.static.maxRpm
        else:
            self.rpm_max = 0
        
        ac.setTitle(self.window, "")
        ac.drawBorder(self.window, 0)
        ac.setIconPosition(self.window, 0, -10000)
        ac.setSize(self.window, round(APP_WIDTH * SCALE), round(APP_HEIGHT * SCALE))
        
        ac.addRenderCallback(self.window , onFormRender)

        self.gear_circle = ac.addLabel(self.window, "")
        ac.setSize(self.gear_circle, 150, 150)
        ac.setPosition(self.gear_circle, 598, 99)
        ac.setBackgroundTexture(self.gear_circle, APP_PATH + "textures/gear_circle.png")        

        # Initialize labels
        self.pilot_label_shadow = ac.addLabel(self.window, info.static.playerName) 
        ac.setPosition(self.pilot_label_shadow, 3, 2)
        ac.setFontSize(self.pilot_label_shadow, 45)
        ac.setCustomFont(self.pilot_label_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.pilot_label_shadow, 0.2, 0.2, 0.2, 1)
        
        self.pilot_label = ac.addLabel(self.window, info.static.playerName)
        ac.setPosition(self.pilot_label, 1, 0)
        ac.setFontSize(self.pilot_label, 45)
        ac.setCustomFont(self.pilot_label, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.pilot_label, 0.89, 0.89, 0.89, 1)

        self.gear_label_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.gear_label_shadow, 656, 139)
        ac.setFontSize(self.gear_label_shadow, 55)
        ac.setCustomFont(self.gear_label_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.gear_label_shadow, 0.2, 0.2, 0.2, 1)
        
        self.gear_label = ac.addLabel(self.window, "")
        ac.setPosition(self.gear_label, 654, 137)
        ac.setFontSize(self.gear_label, 55)
        ac.setCustomFont(self.gear_label, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.gear_label, 0.89, 0.89, 0.89, 1)

        self.speed_label_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.speed_label_shadow, 851, 167)
        ac.setFontSize(self.speed_label_shadow, 55)
        ac.setCustomFont(self.speed_label_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.speed_label_shadow, 0.2, 0.2, 0.2, 1)
        ac.setFontAlignment(self.speed_label_shadow, "center")
        
        self.speed_label = ac.addLabel(self.window, "")
        ac.setPosition(self.speed_label, 849, 165)
        ac.setFontSize(self.speed_label, 55)
        ac.setCustomFont(self.speed_label, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.speed_label, "center")
        ac.setFontColor(self.speed_label, 0.89, 0.89, 0.89, 1)

        self.rpm_max_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm_max_shadow, 568, 67)
        ac.setFontSize(self.rpm_max_shadow, 30)
        ac.setCustomFont(self.rpm_max_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontColor(self.rpm_max_shadow, 0.2, 0.2, 0.2, 1)
        ac.setFontAlignment(self.rpm_max_shadow, "right")
        ac.setText(self.rpm_max_shadow, str(info.static.maxRpm))
        
        self.rpm_max = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm_max, 566, 65)
        ac.setFontSize(self.rpm_max, 30)
        ac.setCustomFont(self.rpm_max, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.rpm_max, "right")
        ac.setText(self.rpm_max, str(info.static.maxRpm))
        ac.setFontColor(self.rpm_max, 0.89, 0.89, 0.89, 1)

        self.rpm_zero_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm_zero_shadow, 162, 67)
        ac.setFontSize(self.rpm_zero_shadow, 30)
        ac.setCustomFont(self.rpm_zero_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.rpm_zero_shadow, "right")
        ac.setText(self.rpm_zero_shadow, "0")
        ac.setFontColor(self.rpm_zero_shadow, 0.2, 0.2, 0.2, 1)
        
        self.rpm_zero = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm_zero, 160, 65)
        ac.setFontSize(self.rpm_zero, 30)
        ac.setCustomFont(self.rpm_zero, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.rpm_zero, "right")
        ac.setText(self.rpm_zero, "0")
        ac.setFontColor(self.rpm_zero, 0.89, 0.89, 0.89, 1)

        self.gas_hundred_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_hundred_shadow, 569, 242)
        ac.setFontSize(self.gas_hundred_shadow, 30)
        ac.setCustomFont(self.gas_hundred_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_hundred_shadow, "right")
        ac.setText(self.gas_hundred_shadow, str(100))
        ac.setFontColor(self.gas_hundred_shadow, 0.2, 0.2, 0.2, 1)
        
        self.gas_hundred = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_hundred, 567, 240)
        ac.setFontSize(self.gas_hundred, 30)
        ac.setCustomFont(self.gas_hundred, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_hundred, "right")
        ac.setText(self.gas_hundred, "100")
        ac.setFontColor(self.gas_hundred, 0.89, 0.89, 0.89, 1)

        self.gas_percent_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_percent_shadow, 364, 242)
        ac.setFontSize(self.gas_percent_shadow, 30)
        ac.setCustomFont(self.gas_percent_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_percent_shadow, "right")
        ac.setText(self.gas_percent_shadow, "%")
        ac.setFontColor(self.gas_percent_shadow, 0.2, 0.2, 0.2, 1)
        
        self.gas_percent = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_percent, 362, 240)
        ac.setFontSize(self.gas_percent, 30)
        ac.setCustomFont(self.gas_percent, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_percent, "right")
        ac.setText(self.gas_percent, "%")
        ac.setFontColor(self.gas_percent, 0.89, 0.89, 0.89, 1)

        self.gas_zero_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_zero_shadow, 162, 242)
        ac.setFontSize(self.gas_zero_shadow, 30)
        ac.setCustomFont(self.gas_zero_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_zero_shadow, "right")
        ac.setText(self.gas_zero_shadow, "0")
        ac.setFontColor(self.gas_zero_shadow, 0.2, 0.2, 0.2, 1)
        
        self.gas_zero = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_zero, 160, 240)
        ac.setFontSize(self.gas_zero, 30)
        ac.setCustomFont(self.gas_zero, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_zero, "right")
        ac.setText(self.gas_zero, "0")
        ac.setFontColor(self.gas_zero, 0.89, 0.89, 0.89, 1)

        self.rpm_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm_shadow, 3, 108)
        ac.setFontSize(self.rpm_shadow, 45)
        ac.setCustomFont(self.rpm_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.rpm_shadow, "left")
        ac.setText(self.rpm_shadow, "RPM")
        ac.setFontColor(self.rpm_shadow, 0.2, 0.2, 0.2, 1)

        self.rpm = ac.addLabel(self.window, "")
        ac.setPosition(self.rpm, 1, 106)
        ac.setFontSize(self.rpm, 45)
        ac.setCustomFont(self.rpm, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.rpm, "left")
        ac.setText(self.rpm, "RPM")
        ac.setFontColor(self.rpm, 0.7, 0.77, 0, 1)

        self.gas_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.gas_shadow, 3, 186)
        ac.setFontSize(self.gas_shadow, 45)
        ac.setCustomFont(self.gas_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas_shadow, "left")
        ac.setText(self.gas_shadow, "GAS")
        ac.setFontColor(self.gas_shadow, 0.2, 0.2, 0.2, 1)
        
        self.gas = ac.addLabel(self.window, "")
        ac.setPosition(self.gas, 1, 184)
        ac.setFontSize(self.gas, 45)
        ac.setCustomFont(self.gas, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.gas, "left")
        ac.setText(self.gas, "GAS")
        ac.setFontColor(self.gas, 0.7, 0.77, 0, 1)

        self.kmh_shadow = ac.addLabel(self.window, "")
        ac.setPosition(self.kmh_shadow, 794, 110)
        ac.setFontSize(self.kmh_shadow, 45)
        ac.setCustomFont(self.kmh_shadow, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.kmh_shadow, "left")
        ac.setText(self.kmh_shadow, "Km/h")
        ac.setFontColor(self.kmh_shadow, 0.2, 0.2, 0.2, 1)
        
        self.kmh = ac.addLabel(self.window, "")
        ac.setPosition(self.kmh, 792, 108)
        ac.setFontSize(self.kmh, 45)
        ac.setCustomFont(self.kmh, "MonospaceTypewriter", 0, 1)
        ac.setFontAlignment(self.kmh, "left")
        ac.setText(self.kmh, "Km/h")
        ac.setFontColor(self.kmh, 0.7, 0.77, 0, 1)

    def update_gears(self):
        current_gear = ac.getCarState(0, acsys.CS.Gear)
        current_gear_s = "N"
        if current_gear == 0:
            current_gear_s = "R"
        elif current_gear == 1:
            current_gear_s = "N"
        else:
            current_gear_s = str(current_gear - 1)
        ac.setText(self.gear_label, current_gear_s)
        ac.setText(self.gear_label_shadow, current_gear_s)

    def update_speed(self):
        current_speed = round(ac.getCarState(0, acsys.CS.SpeedKMH))
        ac.setText(self.speed_label, str(current_speed))
        ac.setText(self.speed_label_shadow, str(current_speed))

    def update_pedals(self):
        global GAS_BAR_CURRENT_VALUE

        throttle_value = round(ac.getCarState(0, acsys.CS.Gas) * 100)
        GAS_BAR_CURRENT_VALUE = throttle_value

    def update_rpm(self):
        global RPM_BAR_CURRENT_VALUE

        current_rpm = round(ac.getCarState(0, acsys.CS.RPM) / 1)
        percent_part = info.static.maxRpm / 100
        percent_calc = current_rpm / percent_part
        RPM_BAR_CURRENT_VALUE = percent_calc
    
    def on_update(self, deltaT):
        ac.setBackgroundOpacity(self.window, 0)
        self.update_pedals()
        self.update_rpm() 
        self.update_gears()
        self.update_speed()

    def on_shutdown(self):
        self.rpm_max = 0

def drawRpmBar(w):
    # width max = 414
    bar_percent_part = 414 / 100
    bar_percent_value = w * bar_percent_part

    ac.glColor4f(0, 0.6, 0.9, 1)
    ac.glQuad(147, 113, bar_percent_value, 50)    

def drawGasBar(w):
    # width max = 414
    bar_percent_part = 414 / 100
    bar_percent_value = w * bar_percent_part

    ac.glColor4f(0, 0.8, 0.1, 1)
    ac.glQuad(147, 189, bar_percent_value, 50)

def drawRpmBarBorder():
    # border shadow layer 1
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(144, 106, 424, 5) # top
    ac.glQuad(563, 110, 5, 55)  # right
    ac.glQuad(144, 165, 424, 5) # bottom

    # border shadow layer 2
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(144, 105, 424, 5) # top
    ac.glQuad(563, 110, 5, 55)  # right
    ac.glQuad(144, 165, 424, 5) # bottom

    # horizontal top inner shadow
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(147, 113, 414, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(147, 114, 414, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(147, 115, 414, 1)

    # horizontal bottom inner shadow
    ac.glColor4f(0, 0, 0, 0.8)
    ac.glQuad(147, 162, 414, 1)
    ac.glColor4f(0, 0, 0, 0.6)
    ac.glQuad(147, 161, 414, 1)
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(147, 160, 414, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(147, 159, 414, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(147, 158, 414, 1)

    # vertical inner shadows
    ac.glColor4f(0, 0, 0, 0.8)
    ac.glQuad(147, 113, 1, 50)
    ac.glColor4f(0, 0, 0, 0.6)
    ac.glQuad(148, 113, 1, 50)
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(149, 113, 1, 50)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(150, 113, 1, 50)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(151, 113, 1, 50)
    
    # border
    ac.glColor4f(0.89, 0.89, 0.89, 1)
    ac.glQuad(142, 108, 5, 55)  # left
    ac.glQuad(142, 108, 423, 5) # top
    ac.glQuad(560, 108, 5, 55)  # right
    ac.glQuad(142, 163, 423, 5) # bottom

def drawGasBarBorder():
    # border shadow layer 1
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(144, 182, 424, 5) # top
    ac.glQuad(563, 187, 5, 55)  # right
    ac.glQuad(144, 240, 424, 5) # bottom

    # border shadow layer 2
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(144, 181, 424, 5) # top
    ac.glQuad(563, 181, 5, 55)  # right
    ac.glQuad(144, 241, 424, 5) # bottom

    # horizontal top inner shadow
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(147, 189, 414, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(147, 190, 414, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(147, 191, 414, 1)

    # horizontal bottom inner shadow
    ac.glColor4f(0, 0, 0, 0.8)
    ac.glQuad(147, 238, 413, 1)
    ac.glColor4f(0, 0, 0, 0.6)
    ac.glQuad(147, 237, 413, 1)
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(147, 236, 413, 1)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(147, 235, 413, 1)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(147, 234, 413, 1)

    # vertical inner shadows
    ac.glColor4f(0, 0, 0, 0.8)
    ac.glQuad(147, 188, 1, 50)
    ac.glColor4f(0, 0, 0, 0.6)
    ac.glQuad(148, 189, 1, 50)
    ac.glColor4f(0, 0, 0, 0.4)
    ac.glQuad(149, 190, 1, 50)
    ac.glColor4f(0, 0, 0, 0.2)
    ac.glQuad(150, 191, 1, 50)
    ac.glColor4f(0, 0, 0, 0.1)
    ac.glQuad(151, 192, 1, 50)

    # border
    ac.glColor4f(0.89, 0.89, 0.89, 1)
    ac.glQuad(142, 184, 5, 55)  # left
    ac.glQuad(142, 184, 423, 5) # top
    ac.glQuad(560, 184, 5, 55)  # right
    ac.glQuad(142, 239, 423, 5) # bottom

def onFormRender(deltaT):
    drawRpmBar(RPM_BAR_CURRENT_VALUE)
    drawGasBar(GAS_BAR_CURRENT_VALUE)
    drawRpmBarBorder()
    drawGasBarBorder()

def acMain(ac_version):
    global app_window, app_hud
    try:
        app_window = ac.newApp("F1 Classic HUD")
        app_hud = AppHud(app_window)
    except Exception as e:
        ac.console("f1_classic_hud: acMain() failure: {}".format(e))
        ac.log("f1_classic_hud: acMain() failure: {}".format(e))

def acUpdate(deltaT):
    try:
        app_hud.on_update(deltaT)
    except Exception as e:
        ac.console("f1_classic_hud: acUpdate() failure: {}".format(e))
        ac.log("f1_classic_hud: acUpdate() failure: {}".format(e))
    
def acShutdown():
    app_hud.on_shutdown()

