import stimulus
import display
from PyQt5.QtWidgets import QApplication
import sys

#app = QApplication(sys.argv)

stim = stimulus.Stimulus()
stim.add_image('test/one.png')
stim.add_image('test/two.png')
stim.add_image('test/three.png')
stim.add_image('test/four.png')
stim.add_image('test/five.png')
stim.set_refresh_rate(1.0)
stim.set_initial_delay(.5)
stim.set_final_delay(.5)

disp = display.Display(False)

def foo(k, t):
    print(f'Foo {k} at {t}')

disp.add_callback(foo)

stim.set_order([0,1,2,3,4, 3,2,1,0])

disp.run(stim)
disp.add_photodiode((10, 10, 20, 20), delay=1, period=3)
disp.run(stim, [100, 100, 400, 300])
