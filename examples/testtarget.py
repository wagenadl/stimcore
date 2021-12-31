#!/usr/bin/python3

import stimcore.stimulus as stimulus
import stimcore.display as display

import numpy as np

ar = np.zeros((18,32), np.uint8)
ar[8:11, 20:24] = 255

stim = stimulus.Stimulus()
stim.add_image(ar)
stim.set_refresh_rate(1)

disp = display.Display(full_screen=False)
disp.run(stim)

x0,y0 = disp.find_pixel((20, 8), (32, 18))
x1,y1 = disp.find_pixel((24, 11), (32, 18))

ar1 = np.random.rand(5*3,5*4,3)
stm1 = stimulus.Stimulus()
stm1.add_image(ar1)
stm1.set_refresh_rate(1)
disp.run(stm1, target=[x0, y0, x1-x0, y1-y0])
# disp.run(stm1, target=[20,8,4,3], rel_to=[32,18])

