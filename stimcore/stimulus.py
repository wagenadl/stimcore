#!/usr/bin/python3

import numpy as np
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication

class Stimulus:
    '''Class STIMULUS: A sequence of images with extra information
    The most important methods are:
      - ADD_IMAGE - Add an image to the sequence from file or numpy array
      - SET_ORDER - Specify the order of image presentation
      - SET_REFRESH_RATE - Set rate of image presentation    
      - SET_INITIAL_DELAY - Specify delay before first image
      - SET_FINAL_DELAY - Specify delay after final image
      - SET_BACKGROUND - Specify background color

    Less frequently used methods are:
      - ADD_IMAGE_FROM_FILE - Add an image to the list from a file
      - ADD_IMAGE_FROM_ARRAY - Add an image to the list from an array
      - RESET_ORDER - Reset order of image presentation
      - PRESENTATION_ORDER - Return presentation order
      - GET_IMAGE - Retrieve an image from the list
      - IMAGE_NAME - Retrieve the filename or alternative label for an image
      - FIND_IMAGE_BY_NAME - Find the ID of an image given its name

    This class is completely passive (it merely stores the images). The
    actual presentation of a stimulus sequence is the responsibility of
    the DISPLAY class.'''
    app = QApplication.instance()
    def __init__(self):
        self.fns = []
        self.order = None
        self.pixmaps = []
        self.f_Hz = 10
        self.initial_delay_s = 0
        self.final_delay_s = 0
        self.background = [0,0,0]

    def add_image(self, img, label=None):
        '''ADD_IMAGE - Add an image to the list
        id = ADD_IMAGE(img) adds an image to our collection.
        IMG may either be a filename or a numpy array.
        This is just a convenience function over ADD_IMAGE_FROM_FILE
        and ADD_IMAGE_FROM_ARRAY.
        Optional argument LABEL may be used to give the image an alternative
        name.'''
        if type(img)==str:
            return add_image_from_file(img, label)
        elif type(img)==np.ndarray:
            return add_image_from_array(img, label)
        else:
            raise ValueError('Must have a filename or a numpy array')
        
    def add_image_from_file(self, fn, label=None):
        '''ADD_IMAGE_FROM_FILE - Add an image to the list
        id = ADD_IMAGE_FROM_FILE(fn) adds an image to our collection
        based on its filename. The returned ID is an integer that can 
        be used in SET_ORDER. IDs count up from zero, so you can also 
        keep count yourself.
        Optional argument LABEL uses something other than the filename
        as the name for the image.'''
        Stimulus.app = QApplication.instance()
        if Stimulus.app is None:
            Stimulus.app = QApplication(['stimcore'])

        if label is None:
            label = fn
        self.fns.append(label)
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
        if ar.dtype==np.uint8:
            ar = ar.copy() # Needed if loaded straight from scipy.io
        elif isint:
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

    def image_name(self, k):
        '''IMAGE_NAME - Retrieve the filename or alternative label for an image
        IMAGE_NAME(id) returns the filename or alternative label for the
        image with the given ID.'''
        return self.fns[k]

    def find_image_by_name(self, name):
        '''FIND_IMAGE_BY_NAME - Find the ID of an image given its name
        FIND_IMAGE_BY_NAME(name) returns the ID of the image that matches
        the given name exactly. Raises an exception if the image does 
        not exist.'''
        return self.fns.index(name)
    
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
