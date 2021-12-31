#!/usr/bin/python3

import stimcore.stimulus as stimulus
import stimcore.display as display

from PyQt5.QtWidgets import QApplication
import sys
import numpy as np

disp = display.Display()
times = []
def foo(k, t):
    times.append(t)
disp.add_callback(foo)
disp.add_photodiode((0, 0, 50, 50))

R = 128
C = 128
xx = np.arange(C).reshape((1,C))
yy = np.arange(R).reshape((R,1))
K = 16

stim = stimulus.Stimulus()
for k in range(K*10):
    ar = np.cos(xx*20/C + k/K*2*np.pi) + 0*yy
    ar *= np.exp(-.5*((xx-C/2)**2 + (yy-R/2)**2)/(C/6)**2)
    stim.add_image_from_array((128+100*ar).astype(np.uint8))

stim.set_refresh_rate(20)
stim.set_initial_delay(.5)
stim.set_final_delay(.5)
stim.set_background((128,128,128))
R = 18
C = 32

x0,y0 = disp.find_pixel((22-2.5,13.5-2.5), (C,R))
x1,y1 = disp.find_pixel((22+2.5,13.5+2.5), (C,R))
times.clear()
disp.run(stim, target=(x0,y0,x1-x0,y1-y0))
print(f'{1e3*np.mean(np.diff(times)):.2f} ms',
      '±',
      f'{1000*np.std(np.diff(times)):.2f} ms')

