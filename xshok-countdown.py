#! /usr/bin/env python3
# -*- encoding: utf8 -*-

################################################################################
# This is property of eXtremeSHOK.com
# You are free to use, modify and distribute, however you may not remove this notice.
# Copyright (c) Adrian Jon Kriel :: admin@extremeshok.com
################################################################################
#
# Script updates can be found at: https://bitbucket.org/extremeshok/xshok-countdown
#
# License: BSD (Berkeley Software Distribution)
#
################################################################################
#
# A graphical countdown timer which can be used for a conference, accepts keyboard input to control the countdown timer for a speaker.
#
# Keys
# start/pause = spacebar/right
# increase 1minute = plus/equal/up
# decrease 1minute = minus/underscore/down
# reset = enter/return/left
# exit/terminate = esc
# label/branding = tab/t
#
# Features
# Prevent negative times, allow add/remove minutes whilst counting down
# Reset the timer without needing to relaunch
# Set a branding message

################################################################################
#
#    THERE ARE NO USER CONFIGURABLE OPTIONS IN THIS SCRIPT
#   ALL CONFIGURATION OPTIONS WOULD BE LOCATED BELOW THIS MESSAGE
#
################################################################################

# ################################################################################

# ######  #######    #     # ####### #######    ####### ######  ### #######
# #     # #     #    ##    # #     #    #       #       #     #  #     #
# #     # #     #    # #   # #     #    #       #       #     #  #     #
# #     # #     #    #  #  # #     #    #       #####   #     #  #     #
# #     # #     #    #   # # #     #    #       #       #     #  #     #
# #     # #     #    #    ## #     #    #       #       #     #  #     #
# ######  #######    #     # #######    #       ####### ######  ###    #
#
# ################################################################################

normal_style = """
 QLabel {
   color: white;
   background-color: black;
   font-size: 180pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

warning_style = """
 QLabel {
   color: red;
   background-color: black;
   font-size: 180pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

negative_style = """
 QLabel {
   color: black;
   background-color: red;
   font-size: 180pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

STYLE_BLINK_ON = """
 QLabel {
   color: black;
   background-color: red;
   font-size: 180pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

STYLE_BLINK_OFF = """
 QLabel {
   color: black;
   background-color: black;
   font-size: 180pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

reset_style = """
 QLabel {
   color: blue;
   background-color: black;
   font-size: 100pt;
   font-family: "DejaVu Sans Mono";
   font-weight: bold;
}"""

import sys
from PyQt4 import QtCore, QtGui
import logging
import time


class ActiveLabel(QtGui.QLabel):
    clicked = QtCore.pyqtSignal(QtGui.QMouseEvent)
    keypress = QtCore.pyqtSignal(QtGui.QKeyEvent)

    def __init__(self, *args):
        super(ActiveLabel, self).__init__(*args)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit(ev)

    def keyReleaseEvent(self, ev):
        self.keypress.emit(ev)


class FSM(object):
    def __init__(self, label, totalTime):
        self.label = label
        self.totalTime = totalTime
        self.remainingTime = totalTime
        self.current_state = self.reset
        self.current_state()
        self.timer = QtCore.QTimer(interval=1000)  # miliseconds
        self.timer.timeout.connect(self.on_every_second)
        self.timerBlink = QtCore.QTimer()
        self.last_blinked = None
        self.blink = False
        self.labelText = "www.eXtremeSHOK.com"

    # Event methods:
    def on_every_second(self):
        if self.current_state not in [self.reset]:
            if self.remainingTime <= 0:
                self.remainingTime = 0
                self.current_state()
            else:
                self.remainingTime -= 1
                self.current_state()
        else:
            self.remainingTime = 900

    # Methods:
    def start(self):
        self.current_state = self.countdown
        self.current_state()
        self.timer.start()

    def reset(self):
        self.timerBlink.stop()
        self.timer.stop()
        self.current_state = self.reset
        self.current_state()

    def timeisup(self):
        self.current_state = self.timesup
        self.timerBlink.timeout.connect(self.timesup)
        self.timerBlink.start(1000)
        if self.current_state not in [self.reset]:
            self.current_state()

    def inctime(self):
        self.remainingTime += 60
        if self.current_state not in [self.reset]:
            self.current_state()
        self.countdown()

    def dectime(self):
        self.remainingTime -= 60
        if self.remainingTime < 60:  # prevent negative times
            self.remainingTime = 60
        if self.current_state not in [self.reset]:
            self.current_state()
        self.countdown()

    def pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.current_state = self.paused
            self.current_state()

    def resume(self):
        if not self.timer.isActive():
            self.timer.start(self.remainingTime)
            self.current_state = self.countdown
            self.current_state()

    def gettext(self):
        dlg = QtGui.QInputDialog()
        dlg.setInputMode(QtGui.QInputDialog.TextInput)
        dlg.setLabelText("Label Text: ")
        dlg.resize(500, 100)
        ok = dlg.exec_()
        dlg.textValue()
        # print(dlg.textValue())
        self.label.setStyleSheet(reset_style)
        self.label.setText(dlg.textValue())
        self.current_state = self.gottext
        self.current_state()

    # States:
    def gottext(self):
        self.label.setStyleSheet(reset_style)

    def reset(self):
        self.label.setStyleSheet(reset_style)
        self.label.setText("www.soundtrek.co.za")
        self.remainingTime = 900
        self.totalTime = 900

    def paused(self):
        logging.info('paused')

    def resumed(self):
        logging.info('resume')

    def timesup(self):
        if self.remainingTime <= 0:
            if self.blink:
                self.label.setStyleSheet(STYLE_BLINK_ON)
            else:
                self.label.setStyleSheet(STYLE_BLINK_OFF)
            self.blink = not self.blink
            self.label.setText("TIMES UP")

    def countdown(self):
        # print(self.remainingTime)
        if self.remainingTime <= 0:
            self.timeisup()
            return
        if self.remainingTime < 60 and self.remainingTime >= 0:
            self.label.setStyleSheet(warning_style)
            self.label.setText("%02d:%02d" % divmod(self.remainingTime, 60))
        else:
            self.label.setStyleSheet(normal_style)
            self.label.setText("%02d:%02d" % divmod(self.remainingTime, 60))


def main(argv):
    try:
        totalTime = int(argv[1]) * 60
    except IndexError:
        totalTime = 900
    app = QtGui.QApplication(argv)
    mw = QtGui.QMainWindow()
    mw.setWindowTitle('SoundTrek Timer')
    l = ActiveLabel()
    l.setAlignment(QtCore.Qt.AlignCenter)

    fsm = FSM(l, totalTime)

    def on_key(ev):
        if ev.key() == QtCore.Qt.Key_Up or ev.key() == QtCore.Qt.Key_Plus or ev.key() == QtCore.Qt.Key_Equal:
            # print("increase")
            fsm.inctime()
        elif ev.key() == QtCore.Qt.Key_Tab or ev.key() == QtCore.Qt.Key_T:
            # print("text")
            fsm.gettext()
        elif ev.key() == QtCore.Qt.Key_Down or ev.key() == QtCore.Qt.Key_Minus or ev.key() == QtCore.Qt.Key_Underscore:
            # print("decrease")
            fsm.dectime()
        elif ev.key() == QtCore.Qt.Key_Left or ev.key() == QtCore.Qt.Key_Enter or ev.key() == QtCore.Qt.Key_Return:
            if fsm.current_state in [fsm.countdown]:
                fsm.pause()
            if fsm.current_state in [fsm.gottext]:
                fsm.current_state = fsm.reset
            else:
                fsm.reset()
        elif ev.key() == QtCore.Qt.Key_Right or ev.key() == QtCore.Qt.Key_Space:
            # print("play/pause")
            if fsm.current_state in [fsm.reset]:
                # print("reset")
                fsm.start()
            elif fsm.current_state in [fsm.countdown]:
                # print("countdown")
                fsm.pause()
            elif fsm.current_state in [fsm.paused]:
                # print("paused")
                fsm.resume()
        elif ev.key() == QtCore.Qt.Key_Escape:
            sys.exit()

    l.keypress.connect(on_key)
    mw.setCentralWidget(l)
    mw.showFullScreen()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
