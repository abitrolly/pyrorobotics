# Draw an array-based image in a gtk window
# D.S. Blank, with help from the pygtk mailing list

import Numeric
import array3d
from gtk import *

def appendbox(list, x, y, z, width):
    list.append([canvas3D.LINE, x, y, z,  x, y + width, z])
    list.append([canvas3D.LINE, x, y, z,  x + width, y, z])
    list.append([canvas3D.LINE, x + width, y + width, z,  x, y + width, z])
    list.append([canvas3D.LINE, x + width, y + width, z,  x + width, y, z])
    list.append([canvas3D.LINE, x, y, z + width,  x, y + width, z + width])
    list.append([canvas3D.LINE, x, y, z + width,  x + width, y, z + width])
    list.append([canvas3D.LINE, x + width, y + width, z + width,  x, y + width, z + width])
    list.append([canvas3D.LINE, x + width, y + width, z + width, x + width, y, z + width])
    list.append([canvas3D.LINE, x, y, z,  x, y, z + width])
    list.append([canvas3D.LINE, x, y + width, z,  x, y + width, z + width])
    list.append([canvas3D.LINE, x + width, y + width, z, x + width, y + width, z + width])
    list.append([canvas3D.LINE, x + width, y, z,  x + width, y, z + width])
    return list

class canvas3D:
    POINT = 0
    LINE = 1
    COLOR = 2
    LINE_WIDTH = 3
    FILL = 4
    def __init__(self, width = 200, height = 200):
        self.width = width
        self.height = height
    def origin(self, x, y):
        self.originx = x
        self.originy = y
    def camera(self, x, y):
        self.camerax = x
        self.cameray = y
    def process(self, array, list=[]):
        array3d.process(array, list)        

class DrawPixmap(GtkWindow):
    def __init__(self, width = 200, height = 200):
        # ---------------- initialize window instance:
        GtkWindow.__init__(self)
        self.width = width  # my own var
        self.height = height # my own var
        self.set_default_size(self.width, self.height)
        # ---------------- Now create a drawing area:
        self.pic = GtkDrawingArea()
        self.pic.show()
        self.add(self.pic)
        # ---------------- Set Callbacks, and event handlers:
        self.pic.connect("expose_event", self.on_exposure)
        self.connect("destroy", mainquit)
        self.pic.set_events(GDK.EXPOSURE_MASK | GDK.DESTROY)
        # ---------------- Create a 3D canvas
        self.canvas = canvas3D(self.width, self.height)

    def on_exposure(self, widget, event):
        # create a pixmap, just once:
        if not hasattr(self, 'pixmap'):
            self.pixmap = create_pixmap(self, self.width, self.height)
            self.gc = self.pixmap.new_gc()
            # create a numeric array filled with zeros of type 8 bit int:
            self.buff = Numeric.zeros((self.height, self.width, 3), 'b')
            self.buff[...] = 255
            # draw a design:
            # a type 'b' 3D numeric array
            list = []
            list.append([canvas3D.COLOR, 255, 0, 0])
            appendbox(list, 0, 0, 0, 2)
            list.append([canvas3D.LINE_WIDTH, 1])
            list.append([canvas3D.COLOR, 0, 0, 255])
            appendbox(list, 1, 1, 1, 1)
            self.canvas.process(self.buff, list)
            # put the array on the pixmap:
            draw_array(self.pixmap, self.gc, 0, 0, GDK.RGB_DITHER_NONE, \
                       self.buff)
        # draw it:
        self.pic.draw_pixmap(self.gc, self.pixmap, 0, 0, 0, 0, \
                             self.width, self.height)

if __name__ == '__main__':
    push_rgb_visual()
    example = DrawPixmap(400, 400)
    pop_visual()
    example.show()
    mainloop()



