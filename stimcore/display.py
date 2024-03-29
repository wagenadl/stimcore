#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QTimer, QRect, QTime
from PyQt5.QtGui import QPainter, QColor, QCursor, QBitmap
import time
import os
import numpy as np
from collections import namedtuple
from . import gpio

class _Display(QWidget):
    if 'DISPLAY' not in os.environ or os.environ['DISPLAY'] == '':
        os.environ['DISPLAY'] = ':0'
    app = QApplication.instance()

    def __init__(self, screen_number=0, full_screen=True):
        '''DISPLAY - Canvas for displaying images
        DISPLAY() creates a full-screen display window.
        Optional argument SCREEN_NUMBER specifies the number of the monitor
        on which to display (counting from zero).
        DISPLAY(full_screen=False) creates a smaller window for testing.'''

        _Display.app = QApplication.instance()
        if _Display.app is None:
            _Display.app = QApplication(['stimcore'])

        super(_Display, self).__init__()

        self.target = None
        self.k = None
        self.stim = None
        self.callbacks = []
        self.photodiodes = []
        self.gpios = []

        # The paintEvent causes the app to then exit immediately if k is None.
        # Oddly, just running processEvents doesn't cause repaint

        # If we don't show() first, we don't have a window handle, so
        # we cannot send ourselves to requested screen.
        scrs = _Display.app.screens()
        if screen_number >= len(scrs):
            raise ValueError('Nonexistent screen')

        if screen_number>0:
            self.show()
            self.hide()
            self.windowHandle().setScreen(scrs[screen_number])

        siz = scrs[screen_number].size()
        self.screensize = (siz.width(), siz.height())

        if full_screen:
            print(self.screensize)
            self.resize(siz)
            self.showFullScreen()
        else:
            self.resize(self.screensize[0]*480//self.screensize[1], 480)
            self.show()
        self.windowHandle().setScreen(scrs[screen_number])
        _Display.app.exec() # This forces window to be painted black
        self.setCursor(QCursor(QBitmap(1,1), QBitmap(1,1)))

    def add_gpio(self, pin, period=2, delay=0):
        '''ADD_GPIO - Add a GPIO signal
        ADD_GPIO(pin) causes the given GPIO pin to be toggled up and down
        periodically for synchronization.
        By default, the signal goes up and down every other frame. 
        Optional argument PERIOD makes it go up every n-th frame instead
        of every second frame.
        Optional argument DELAY makes the first appearance of the signal
        be in the given frame (counted from zero) rather than in frame 0.'''
        gpio.make_output(pin)
        T = namedtuple('GP', ['pin', 'period', 'delay'])
        self.gpios.append(T._make((pin, period, delay)))
        
    def add_photodiode(self, rect, period=2, delay=0):
        '''ADD_PHOTODIODE - Add a photodiode signal
        ADD_PHOTODIODE([x,y,w,h]) causes a rectangle to flash on and off
        periodically as a signal for a photodiode.
        The location of the rectangle is given in pixels.
        By default, the PD flashes on and off every other frame. 
        Optional argument PERIOD makes it appear every n-th frame instead
        of every second frame.
        Optional argument DELAY makes the first appearance of the signal
        be in the given frame (counted from zero) rather than in frame 0.'''
        T = namedtuple('PD', ['rect', 'period', 'delay'])
        self.photodiodes.append(T._make((rect, period, delay)))
        
    def add_callback(self, cb):
        '''ADD_CALLBACK - Add a function to be called at start of frame
        ADD_CALLBACK(func) causes the given function to be called at
        the start of every frame, with the frame number and the current
        time (in seconds) as arguments.'''
        self.callbacks.append(cb)

    def width_pixels(self):
        '''WIDTH_PIXELS - Width of the window in pixels
        WIDTH_PIXELS() returns the width of the window in pixels.'''
        return self.width()

    def height_pixels(self):
        '''HEIGHT_PIXELS - Height of the window in pixels
        HEIGHT_PIXELS() returns the height of the window in pixels.'''
        return self.height()

    def windowwidth_cm(self):
        '''WIDTH_CM - Width of the window in centimeters
        WIDTH_CM() returns the width of the window in centimeters.'''
        scr = self.windowHandle().screen()
        sizpix = scr.size()
        sizmm = scr.physicalSize()
        wpix = sizpix.width()
        wmm = sizmm.width()
        return (wmm/10) * self.width_pixels() / wpix

    def windowheight_cm(self):
        '''HEIGHT_CM - Height of the window in centimeters
        HEIGHT_CM() returns the height of the window in centimeters.'''
        scr = self.windowHandle().screen()
        sizpix = scr.size()
        sizmm = scr.physicalSize()
        hpix = sizpix.height()
        hmm = sizmm.height()
        return (hmm/10) * self.height_pixels() / hpix


    def width_cm(self):
        '''WIDTH_CM - Width of the screen in centimeters
        WIDTH_CM() returns the width of the screen in centimeters.'''
        scr = self.windowHandle().screen()
        sizmm = scr.physicalSize()
        wmm = sizmm.width()
        return wmm/10

    def height_cm(self):
        '''HEIGHT_CM - Height of the screen in centimeters
        HEIGHT_CM() returns the height of the screen in centimeters.'''
        scr = self.windowHandle().screen()
        sizmm = scr.physicalSize()
        hmm = sizmm.height()
        return hmm/10

    def timeout(self):
        if self.k is None:
            return
        if self.k<0:
            # First image
            self.timer.setInterval(1000 / self.stim.f_Hz)
            
        self.k += 1
        if self.k < self.N:
            self.pixmap = self.stim.get_image(self.order[self.k])
            self.update()
        elif self.k == self.N:
            for gp in self.gpios:
                gpio.write(gp.pin, 0)
            if self.stim.final_delay_s>0:
                print('prefinal')
                self.update()
                self.timer.setInterval(1000 * self.stim.final_delay_s)
            else:
                print('final')
                self.k = None
                _Display.app.quit()
        else:
            self.k = None
            _Display.app.quit()

    def resizeEvent(self, evt):
        self.target = [0, 0, self.width(), self.height()]
            
    def run(self, stim, target=None):
        '''RUN - Show a sequence of stimuli
        RUN(stim), where STIM is of type STIMULUS, runs through the
        given stimulus sequence.
        RUN(stim, target), where TARGET is an (x,y,w,h)-quad, limits
        the stimulus to the given rectangle, specified in pixels.'''
        if target is None:
            self.target = [0, 0, self.width(), self.height()]
        else:
            self.target = target
        self.show()
        self.timer = QTimer(self)
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.timeout.connect(self.timeout)
        self.time = QTime()
        self.time.start()
        self.last_t = 0
        self.last_k = -1
        self.stim = stim
        self.pixmap = None
        self.order = stim.presentation_order()
        self.N = len(self.order)
        self.k = -1
        self.pdphases = []
        for pd in self.photodiodes:
            self.pdphases.append(pd.period - pd.delay)
        self.gpphases = []
        for gp in self.gpios:
            self.gpphases.append(gp.period - gp.delay)
            
        if self.stim.initial_delay_s>0:
            self.timer.setInterval(self.stim.initial_delay_s * 1000)
        else:
            self.timeout()
        self.timer.start()


        if True:
            _Display.app.exec()
            
        self.timer.stop()
        del self.timer

    def paintEvent(self, evt):
        ww = self.target[2]
        wh = self.target[3]
        p = QPainter(self)
        if self.stim is None:
            rgb = [0,0,0]
        else:
            rgb = self.stim.background
        p.fillRect(QRect(0,0,self.width(),self.height()),
                   QColor(rgb[0], rgb[1], rgb[2]))
        if self.k is None or self.k<0 or self.k>=self.N:
            if self.k is None:
                _Display.app.quit()
            return
        iw = self.pixmap.width() # image size (pix)
        ih = self.pixmap.height()
        if iw>0 and ih>0:
            rx = ww/iw # ratio
            ry = wh/ih
            rat = min(rx, ry)
            sw = iw*rat # actual size of image on screen
            sh = ih*rat
            x0 = self.target[0] + (ww-sw)//2 # margin
            y0 = self.target[1] + (wh-sh)//2
            p.drawPixmap(QRect(x0, y0, sw, sh), self.pixmap)
        self.showphotodiodes(p)
        self.showgpios()
                
        if self.k != self.last_k:
            self.notify()

    def showgpios(self):
        if len(self.gpios)==0:
            return
        for n in range(len(self.gpios)):
            gp = self.gpios[n]
            pin = gp.pin
            if self.gpphases[n]>=gp.period:
                val = 1
                self.gpphases[n] = 1
            else:
                val = 0
                self.gpphases[n] += 1
            gpio.write(pin, val)

    def showphotodiodes(self, p):
        for n in range(len(self.photodiodes)):
            pd = self.photodiodes[n]
            x,y,w,h = pd.rect
            if self.pdphases[n]>=pd.period:
                col = QColor(255,255,255)
                self.pdphases[n] = 1
            else:
                col = QColor(0,0,0)
                self.pdphases[n] += 1
            p.fillRect(QRect(x,y,w,h), col)
        

    def notify(self):
        t = self.time.elapsed()/1000
        dt = t - self.last_t
        fn = self.stim.fns[self.order[self.k]]
        #print(f'Showing image {self.k} ({fn}) at {t:.3f} (delta={dt:.3f})')
        self.last_t = t
        self.last_k = self.k
        for cb in self.callbacks:
            cb(self.k, t)

class Display:
    def __init__(self, screen_number=0, full_screen=True):
        '''DISPLAY - Canvas for displaying images
        DISPLAY() creates a full-screen display window.
        Optional argument SCREEN_NUMBER specifies the number of the monitor
        on which to display (counting from zero).
        DISPLAY(full_screen=False) creates a smaller window for testing.'''
        self._disp = _Display(screen_number, full_screen)

    def add_gpio(self, pin, period=2, delay=0):
        '''ADD_GPIO - Add a GPIO signal
        ADD_GPIO(pin) causes the given GPIO pin to be toggled up and down
        periodically for synchronization.
        By default, the signal goes up and down every other frame. 
        Optional argument PERIOD makes it go up every n-th frame instead
        of every second frame.
        Optional argument DELAY makes the first appearance of the signal
        be in the given frame (counted from zero) rather than in frame 0.'''
        self._disp.add_gpio(pin, period, delay)

    def add_photodiode(self, rect, period=2, delay=0):
        '''ADD_PHOTODIODE - Add a photodiode signal
        ADD_PHOTODIODE([x,y,w,h]) causes a rectangle to flash on and off
        periodically as a signal for a photodiode.
        The location of the rectangle is given in pixels.
        By default, the PD flashes on and off every other frame. 
        Optional argument PERIOD makes it appear every n-th frame instead
        of every second frame.
        Optional argument DELAY makes the first appearance of the signal
        be in the given frame (counted from zero) rather than in frame 0.'''
        self._disp.add_photodiode(rect, period, delay)

    def add_callback(self, cb):
        '''ADD_CALLBACK - Add a function to be called at start of frame
        ADD_CALLBACK(func) causes the given function to be called at
        the start of every frame, with the frame number and the current
        time (in seconds) as arguments.'''
        self._disp.add_callback(cb)

    def width_pixels(self):
        '''WIDTH_PIXELS - Width of the window in pixels
        WIDTH_PIXELS() returns the width of the window in pixels.'''
        return self._disp.width_pixels()

    def height_pixels(self):
        '''HEIGHT_PIXELS - Height of the window in pixels
        HEIGHT_PIXELS() returns the height of the window in pixels.'''
        return self._disp.height_pixels()
    
    def windowwidth_cm(self):
        '''WINDOWWIDTH_CM - Width of the window in centimeters
        WINDOWWIDTH_CM() returns the width of the window in centimeters.'''
        return self._disp.windowwidth_cm()

    def windowheight_cm(self):
        '''WINDOWHEIGHT_CM - Height of the window in centimeters
        WINDOWHEIGHT_CM() returns the height of the window in centimeters.'''
        return self._disp.windowheight_cm()

    def width_cm(self):
        '''WIDTH_CM - Width of the window in centimeters
        WIDTH_CM() returns the width of the window in centimeters.'''
        return self._disp.width_cm()

    def height_cm(self):
        '''HEIGHT_CM - Height of the window in centimeters
        HEIGHT_CM() returns the height of the window in centimeters.'''
        return self._disp.height_cm()

    def find_pixel_static(xy, wh, WH):
        iw, ih = wh  # image width, height

        ix, iy = xy  # point of interest in image coords
        ww, hh = WH
        rx = ww / iw
        ry = hh / ih
        rat = min(rx, ry)  # effective scale of image on screen
        sw = iw * rat  # screen width of image
        sh = ih * rat
        x0 = ww / 2 - sw / 2  # screen position of top left of image
        y0 = hh / 2 - sh / 2
        x = x0 + ix * rat
        y = y0 + iy * rat
        return x, y

    def find_pixel(self, xy, wh):
        '''FIND_PIXEL - Find location of image pixel on screen
        p = FIND_PIXEL((x,y), (w,h)) returns the screen location of the
        (topleft) corner of the pixel (X, Y) in an image of size WxH.
        This is, of course, almost trivial, but the aspect ratio of the
        image may not be the same as the aspect ratio of the display window,
        so this method trivializes the calculation.
        The result is a 2-ple.'''
        ww = self.width_pixels()  # window width
        hh = self.height_pixels()
        return Display.find_pixel_static(xy, wh, (ww,hh))

    def angle_to_pixel(self, theta, screendist_cm):
        '''ANGLE_TO_PIXEL - Convert a visual angle to a pixel count
        npix = ANGLE_TO_PIXEL(theta, screendist_cm) calculates the number of
        pixels on the screen corresponding to a given visual half angle theta.
        This only uses width and not height of screen.
        The calculation is correct fo full-screen mode. For non-fullscreen
        mode, the calculation is as if the output is going to be scaled to the
        full screen in post.'''

        sw_pix = self.width_pixels()
        #sh_pix = self.height_pixels()
        sw_cm = self.width_cm()
        #sh_cm = self.height_cm()
        iw_cm = np.tan(theta * np.pi / 180) * screendist_cm
        iw_pix = int(sw_pix * iw_cm / sw_cm)
        return iw_pix

    def pixel_to_angle(self, npix, screendist_cm):
        '''PIXEL_TO_ANGLE - Inverse of ANGLE_TO_PIXEL'''
        sw_pix = self.width_pixels()
        # sh_pix = self.height_pixels()
        sw_cm = self.width_cm()
        # sh_cm = self.height_cm()
        iw_pix = npix
        iw_cm = iw_pix * sw_cm / sw_pix
        theta = (180 / np.pi) * np.atan(iw_cm/screendist_cm)
        return theta

    def run(self, stim, target=None):
        '''RUN - Show a sequence of stimuli
        RUN(stim), where STIM is of type STIMULUS, runs through the
        given stimulus sequence.
        RUN(stim, target), where TARGET is an (x,y,w,h)-quad, limits
        the stimulus to the given rectangle, specified in pixels.
        Images from the stimulus sequence are always scaled (up or down)
        to optimally fit in the target rectangle, possibly leaving
        bands of background color along top and bottom, or along left and
        right edges.
        '''
        self._disp.run(stim, target)
        
    def close(self):
        '''CLOSE - Close the display window
        CLOSE() closes the display window. This is not what you normally
        want to do: normally you just want the black background to stay
        on forever, but on MS Windows, this is the only way to hide the
        window without crashing the software.'''
        self._disp.hide()
        
