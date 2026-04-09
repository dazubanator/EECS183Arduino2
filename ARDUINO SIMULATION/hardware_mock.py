import tkinter as tk
import time

class MockBoard:
    def __init__(self):
        self.D7 = "D7"
        self.A5 = "A5"
        self.D8 = self.D9 = self.D10 = self.D11 = self.D12 = self.D13 = "RGB"
        self.D4 = self.D5 = self.D6 = "ADDR"
        self.D1 = "CLK"
        self.D3 = "LAT"
        self.D2 = "OE"

class MockAnalogIn:
    def __init__(self, pin):
        self._value = 32768 # Middle
    @property
    def value(self):
        return self._value

class MockDigitalInOut:
    def __init__(self, pin):
        self.value = True # Pull.UP default
        self.direction = None
        self.pull = None

class MockBitmap:
    def __init__(self, width, height, colors):
        self.width = width
        self.height = height
        self._data = [0] * (width * height)
    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            x, y = key
            self._data[y * self.width + x] = value
        else:
            self._data[key] = value
    def __getitem__(self, key):
        if isinstance(key, tuple):
            x, y = key
            return self._data[y * self.width + x]
        return self._data[key]

class MockPalette:
    def __init__(self, count):
        self.colors = [0] * count
    def __setitem__(self, key, value):
        self.colors[key] = value

class Simulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Arduino Matrix Simulator")
        self.canvas = tk.Canvas(self.root, width=640, height=320, bg='black')
        self.canvas.pack()
        
        self.width = 32
        self.height = 16
        self.pixel_size = 20
        self.pixels = []
        for y in range(self.height):
            row = []
            for x in range(self.width):
                p = self.canvas.create_rectangle(
                    x * self.pixel_size, y * self.pixel_size,
                    (x+1) * self.pixel_size, (y+1) * self.pixel_size,
                    fill='black', outline='#111'
                )
                row.append(p)
            self.pixels.append(row)
            
        self.pot_val = 32768
        self.btn_val = True
        
        self.root.bind('<Left>', self.on_left)
        self.root.bind('<Right>', self.on_right)
        self.root.bind('<KeyPress-space>', self.on_space_press)
        self.root.bind('<KeyRelease-space>', self.on_space_release)
        
    def on_left(self, event):
        self.pot_val = max(0, self.pot_val - 2048)
    def on_right(self, event):
        self.pot_val = min(65535, self.pot_val + 2048)
    def on_space_press(self, event):
        self.btn_val = False # Pressed
    def on_space_release(self, event):
        self.btn_val = True # Released

    def update_display(self, bitmap, palette):
        for y in range(self.height):
            for x in range(self.width):
                color_idx = bitmap[x, y]
                hex_color = "#{:06x}".format(palette.colors[color_idx])
                self.canvas.itemconfig(self.pixels[y][x], fill=hex_color)
        self.root.update()

sim_inst = None
def get_sim():
    global sim_inst
    if sim_inst is None:
        sim_inst = Simulator()
    return sim_inst
