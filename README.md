# stimcore
Very basic visual stimulus display

StimCore is a very basic Python library for displaying visual stimuli on an LCD monitor. 
StimCore is particularly suited for running on a Raspberry Pi. 
While StimCore lacks the flexibility of sophisticated systems like PsychoPy, for simple stimulation paradigms it may be easier to use.

# Dependencies

StimCore depends on Qt5 and its Python3 bindings. On Ubuntu, the easiest way to satisfy this requirement is:

    sudo apt install python3-pyqt5
  
On other operating systems, pip or conda may be convenient.

# Installation

On Linux, the most convenient thing to do is to create a soft link to the "stimcore" subfolder in $HOME/.local/lib/python3.9/site-packages. 
(Replace "3.9" with your own version of python.) If you use PyCharm on Windows, you can add stimcore as a root to your project.

# Usage

See "test.py" and "teartest.py" for examples of usage. These examples depend on numpy, which you probably already have. If not:

    sudo apt install python3-numpy

The essential routine is to first import the library:

    from stimcore import stimulus, display

After that, you can immediately start constructing a stimulus sequence:

    stim = stimulus.Stimulus()

to which you can add images one by one. Images can be loaded from a file, as in:

    stim.add_image("/path/to/a/file.png")

or from a numpy array, as in:

    stim.add_image(img)

where `img` is a HxW grayscale image or an HxWx3 RGB image.

Beyond the images that make up the stimulus sequence, you must also set the refresh rate, and how long to wait at the beginning and end of the sequence:

   stim.set_refresh_rate(10) # In units of frames per second
   stim.set_initial_delay(0.5) # In units of seconds
   stim.set_final_delay(0.5) # In units of seconds

The next step is connecting to the display:

    disp = display.Display()

at which point the stimulus sequence can be run simply by:

    disp.run(stim)

This displays each image once, in order of `add_image` calls. 

If a different display sequence is desired, you can call:

    id1 = stim.add_image(xxx)
    id2 = stim.add_image(yyy)
 
(etc.), and then call

    stim.set_order([id2, id1, id1, id2]) 

to create an arbitrary sequence.

Very often, it is useful to display a little blinking square in the corner of the screen to enable synchronization of external equipment. This is achieved by calling

    disp.add_photodiode((0, 0, 20, 20))

before calling `run`. (This creates a 20x20 pixel square in the top-left corner that is white and black every other frame. 
See the built-in documentation for more details.)

If stimuli are to be defined in terms of real units (millimeters or degrees of visual angle) rather than pixels, the 
methods `width_cm`, `height_cm`, `width_pixels`, and `height_pixels` in the Display class are useful.

Images are scaled to fit the screen (with preservation of aspect ratio) and centered on the screen if their aspect ratio does not match the screen. 
The color of any remaining space on the screen may be specified using the `set_background` method in the Stimulus class. To calculate where on the screen 
a specific pixel in a source image ends up, the `find_pixel` method in the Display class may be used.

To display an image sequence in a smaller target area (e.g., over the previously determined receptive field of a neuron of interest), you can call the `run` method
of the Display class as

    disp.run(stim, target=[x, y, w, h])

StimCore works well in multi-monitor setups:

    disp = display.Display(screen_number=n)

displays the stimuli on the n-th monitor (counting from zero).

Lastly, for debugging it is sometimes useful to display stimulus sequences in a window rather than full screen. This is easy:

    disp = display.Display(full_screen=False)
    
# Notes on performance

StimCore has been tested on Windows and on Linux, including on Raspberry Pi. On a Pi 4, it is capable of reliably displaying 1920x1080 images at 30 Hz. 
We recommend splurging on a Pi with 8 GB of RAM, as StimCore needs to hold all the images in a sequence in memory at once. On Linux, faster frame rates are possible. 
On Windows, this is also true, but we have seen occasional glitches where the system "hangs" for several hundred milliseconds, apparently while engaged 
in some background housekeeping task.  For best results, careful tests are recommended before running StimCore on a computer that is simultaneously used for
demanding data acquisition.

# Essential caveat on X11

On Linux screen "tearing" is a significant problem under X11. (It actually seems to be a design flaw in X11 itself. You can read about 
double buffering techniques on the internet until you are blue in the face, but the problem does not go away even with the X11 DOUBLE-BUFFER 
extension.) Fortunately, Wayland solves this problem entirely. Wayland is available in more and more distributions, including Ubuntu 20.04.

On the Raspberry Pi, Wayland is available starting from Ubuntu 21.04. After installation, you will need to run

    sudo apt update
    sudo apt upgrade

to actually get it to work. On the login screen, after clicking on your username, there should be a little "settings gear" icon in the bottom right.
Click that and select "Gnome" rather than "Gnome on X11" to enable Wayland. Once logged in, you can verify in "Settings → About" whether you are actually
running Wayland or X11. Visually, the two are indistinguishable.

(In case it is not obvious: tearing is problematic for at least two reasons: First, tears in the display can make for rather salient stimuli. Second, especially when using stimcore simultaneously with high-time-resolution recording techniques, tearing can mean that the synchronization between the stimulus and the "photodiode" signal is off by 16.7 ms, or however fast your monitor refreshes. This can easily lead to misinterpretation of resulting data.)
