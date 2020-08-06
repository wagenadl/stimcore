#!/usr/bin/python3

import stimcore.stimulus as stimulus
import stimcore.display as display

from PyQt5.QtWidgets import QApplication
import sys
import numpy as np

#app = QApplication(sys.argv)

ar = np.zeros((18,32), np.uint8)
for phi in np.arange(0, 6.3, .05):
    x = 16 + 12 * np.cos(phi)
    y = 9 + 8 * np.sin(phi)
    ar[int(y), int(x)] = 128
ar[8, 20] = 255
ar[8, 12] = 255
ar[13, 14:19] = 255
ar[12, 13] = 255
ar[12, 19] = 255

stim = stimulus.Stimulus()
stim.add_image_from_file('test/one.png')
stim.add_image_from_file('test/two.png')
stim.add_image_from_file('test/three.png')
stim.add_image_from_file('test/four.png')
stim.add_image_from_file('test/five.png')
stim.add_image_from_array(ar)
stim.set_refresh_rate(5)
stim.set_initial_delay(.5)
stim.set_final_delay(.5)

#disp = display.Display(full_screen=False)
disp = display.Display()

def foo(k, t):
    print(f'Foo {k} at {t}')

disp.add_callback(foo)

stim.set_order([0,1,2,3,4, 5, 4,3,2,1,0])

disp.run(stim)
disp.add_photodiode((10, 10, 20, 20), delay=1, period=3)
disp.add_gpio(25)
disp.add_gpio(22, delay=1, period=3)
disp.run(stim, [100, 100, 400, 300])
