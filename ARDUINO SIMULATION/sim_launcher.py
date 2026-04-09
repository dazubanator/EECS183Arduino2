import sys
import os
import types
import time

# Add the parent directory to sys.path so we can import space_invaders
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import hardware_mock

# --- Mocking CircuitPython Modules ---

# board
board = hardware_mock.MockBoard()
sys.modules['board'] = board

# digitalio
digitalio = types.ModuleType('digitalio')
digitalio.DigitalInOut = hardware_mock.MockDigitalInOut
digitalio.Direction = types.SimpleNamespace(INPUT=0, OUTPUT=1)
digitalio.Pull = types.SimpleNamespace(UP=0, DOWN=1)
sys.modules['digitalio'] = digitalio

# analogio
analogio = types.ModuleType('analogio')
analogio.AnalogIn = hardware_mock.MockAnalogIn
sys.modules['analogio'] = analogio

# displayio
displayio = types.ModuleType('displayio')
displayio.release_displays = lambda: None
displayio.Bitmap = hardware_mock.MockBitmap
displayio.Palette = hardware_mock.MockPalette
displayio.TileGrid = lambda bitmap, pixel_shader: None
displayio.Group = lambda **kwargs: types.SimpleNamespace(append=lambda x: None, scale=1)
sys.modules['displayio'] = displayio

# terminalio
terminalio = types.ModuleType('terminalio')
terminalio.FONT = "FONT"
sys.modules['terminalio'] = terminalio

# framebufferio
framebufferio = types.ModuleType('framebufferio')
class MockFramebufferDisplay:
    def __init__(self, panel, auto_refresh=False):
        self.width = 32
        self.height = 16
        self.root_group = None
    def refresh(self):
        # This is where we update the Tkinter window
        sim = hardware_mock.get_sim()
        # We need the bitmap and palette from the global space_invaders scope later
        # For now, we'll try to find them in the game object
        import space_invaders
        sim.update_display(space_invaders.matrix, space_invaders.pixelColor)

framebufferio.FramebufferDisplay = MockFramebufferDisplay
sys.modules['framebufferio'] = framebufferio

# rgbmatrix
rgbmatrix = types.ModuleType('rgbmatrix')
rgbmatrix.RGBMatrix = lambda **kwargs: types.SimpleNamespace()
sys.modules['rgbmatrix'] = rgbmatrix

# adafruit_display_text.label
import types
display_text_mod = types.ModuleType('adafruit_display_text')
sys.modules['adafruit_display_text'] = display_text_mod
label_mod = types.ModuleType('adafruit_display_text.label')
class MockLabel:
    def __init__(self, font, color, text):
        self.text = text
        print(f"[SCREEN TEXT]: {text}")
    def x(self, val): pass
    def y(self, val): pass
label_mod.Label = MockLabel
sys.modules['adafruit_display_text.label'] = label_mod
display_text_mod.label = label_mod

# --- Dynamic Loading of space_invaders.py ---

# We read the file and strip the 'setup()' call at the end so it doesn't block
path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'space_invaders.py')
with open(path, 'r') as f:
    lines = f.readlines()

# Filter out the setup() call at the end (could be one of the last few lines)
clean_lines = []
for line in lines:
    if line.strip() == "setup()":
        continue
    clean_lines.append(line)

code = "".join(clean_lines)

# Create a module-like object to hold the game state
space_invaders = types.ModuleType('space_invaders')
sys.modules['space_invaders'] = space_invaders
# Inject the globals into the module
exec(code, space_invaders.__dict__)

print("Starting Simulator...")
print("Controls: Left/Right Arrow Keys to move, Space to fire.")

# Initialize simulator instance
sim = hardware_mock.get_sim()

def run_sim_loop():
    # Update mock inputs from simulator state
    space_invaders.pot._value = sim.pot_val
    space_invaders.button.value = sim.btn_val
    
    # Run the game update
    space_invaders.game.update(space_invaders.pot.value, space_invaders.button.value)
    
    # Schedule next update
    sim.root.after(16, run_sim_loop) # ~60 FPS

# Call setup_game and run the mainloop
space_invaders.game.setup_game()
run_sim_loop()
sim.root.mainloop()
