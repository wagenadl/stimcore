#!/usr/bin/python3

import numpy as np
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication

class Stimulus:
    app = QApplication.instance()
    def __init__(self):
        self.fns = []
        self.order = None
        self.pixmaps = []
        self.f_Hz = 10
        self.initial_delay_s = 0
        self.final_delay_s = 0
        self.background = [0,0,0]
        
    def add_image_from_file(self, fn):
        '''ADD_IMAGE_FROM_FILE - Add an image to the list
        id = ADD_IMAGE_FROM_FILE(fn) adds an image to our collection
        based on its filename. The returned ID is an integer that can 
        be used in SET_ORDER. IDs count up from zero, so you can also 
        keep count yourself.'''
        Stimulus.app = QApplication.instance()
        if Stimulus.app is None:
            Stimulus.app = QApplication(['stimcore'])

        self.fns.append(fn)
        self.pixmaps.append(QPixmap(fn))
        return len(self.fns) - 1

    def add_image_from_array(self, ar, label=None):
        '''ADD_IMAGE_FROM_ARRAY - Add an image to the list
        id = ADD_IMAGE_FROM_ARRAY(ar) adds an image to our collection
        based on a numpy array.
        AR must be either HxW for a grayscale image or HxWx3 for RGB.
        If the type of AR is integer (e.g., uint8), we assume pixel
        values range from 0 (black) to 255 (white); otherwise, pixel
        values must be between 0.0 (black) and 1.0 (white).
        Optional argument LABEL specifies a name for the image in lieu
        of a filename. By default, its numeric ID is used as a name.'''
        Stimulus.app = QApplication.instance()
        if Stimulus.app is None:
            Stimulus.app = QApplication(['stimcore'])
        
        isint = np.issubdtype(ar.dtype, np.integer)
        if isint:
            ar = ar.astype(np.uint8)
        else:
            ar = (255.99999*ar).astype(np.uint8)
        shp = ar.shape
        if len(shp)==3 and shp[2]==3:
            # RGB
            h, w, _ = shp
            img = QImage(ar.data, w, h, 3*w, QImage.Format_RGB888)
        elif len(shp)==2:
            h, w = shp
            img = QImage(ar.data, w, h, w, QImage.Format_Grayscale8)
        else:
            raise ValueError('Unacceptable shape of array')
        if label is None:
            label = f'{len(self.fns)}'
        self.fns.append(label)
        self.pixmaps.append(QPixmap(img))
            
    
    def set_order(self, order):
        '''SET_ORDER - Specify the order of image presentation
        SET_ORDER(order), where ORDER is a list of image IDs (as returned
        by ADD_IMAGE) specifies the order of presentation. If no order
        is specified in this way, the default is to present each image
        once in the order they were added.'''
        self.order = order
        
    def reset_order(self):
        '''RESET_ORDER - Reset order of image presentation
        RESET_ORDER() resets the order of image presentation to a single
        pass through the list in order of image addition.'''
        self.order = None
        
    def set_refresh_rate(self, f_Hz):
        '''SET_REFRESH_RATE - Set rate of image presentation
        SET_REFRESH_RATE(f_Hz) sets the rate of image presentation to
        the given frame rate, expressed in Hertz.'''
        self.f_Hz = f_Hz

    def presentation_order(self):
        '''PRESENTATION_ORDER - Return presentation order
        PRESENTATION_ORDER() returns the order of presentation as a list
        of image IDs.'''
        if self.order is None:
            return list(range(len(self.fns)))
        else:
            return self.order

    def get_image(self, k):
        '''GET_IMAGE - Retrieve an image from the list
        GET_IMAGE(id), where ID is an ID as returned by ADD_IMAGE,
        returns the corresponding image as a QPixmap.'''
        return self.pixmaps[k]
    
    def set_initial_delay(self, dt_s):
        '''SET_INITIAL_DELAY - Specify delay before first image
        SET_INITIAL_DELAY(t) specifies the delay before the first image
        should be shown, in seconds. Default is zero.'''
        self.initial_delay_s = dt_s
        
    def set_final_delay(self, dt_s):
        '''SET_FINAL_DELAY - Specify delay after final image
        SET_FINAL_DELAY(t) specifies the delay after the final image
        is shown, in seconds. Default is zero.'''
        self.final_delay_s = dt_s

    def set_background(self, rgb):
        '''SET_BACKGROUND - Specify background color
        SET_BACKGROUND(rgb) specifies the background color as an RGB
        triplet. Default is black.'''
        self.background = rgb
