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

ar1 = np.random.rand(5*3,5*4,3)
stm1 = stimulus.Stimulus()
stm1.add_image(ar1)
stm1.set_refresh_rate(1)
disp.run(stm1, target=[20,8,4,3], rel_to=[32,18])

