import random
import time
import board
import displayio
import terminalio
import framebufferio
import rgbmatrix
from digitalio import DigitalInOut, Direction, Pull
from analogio import AnalogIn
import adafruit_display_text.label

displayio.release_displays()

# set up the button input
button = DigitalInOut(board.D7)
button.direction = Direction.INPUT
button.pull = Pull.UP

# set up the potentiometer
pot = AnalogIn(board.A5)

#set up the LED display
panel = rgbmatrix.RGBMatrix(
    width=32, bit_depth=4,
    rgb_pins=[board.D8, board.D9, board.D10, board.D11, board.D12, board.D13],
    addr_pins=[board.D4, board.D5, board.D6],
    clock_pin=board.D1, latch_pin=board.D3, output_enable_pin=board.D2)
display = framebufferio.FramebufferDisplay(panel, auto_refresh=False)
SCALE = 1
matrix = displayio.Bitmap(display.width//SCALE, display.height//SCALE, 10)
pixelColor = displayio.Palette(10)
tg1 = displayio.TileGrid(matrix, pixel_shader=pixelColor)
g1 = displayio.Group(scale=SCALE)
g1.append(tg1)
display.root_group = g1

# pallette color index numbers
BLACK, RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE, WHITE, LIME, AQUA = range(10)

# set pallette colors
pixelColor[BLACK] = 0x000000
pixelColor[RED] = 0xff0000
pixelColor[ORANGE] = 0xffa500
pixelColor[YELLOW] = 0xffff00
pixelColor[GREEN] = 0x008000
pixelColor[BLUE] = 0x0000ff
pixelColor[PURPLE] = 0xa020f0
pixelColor[WHITE] = 0xffffff
pixelColor[LIME] = 0x00ff00
pixelColor[AQUA] = 0x00ffff

# ---------------- Utility display functions ----------------

def print_text(inputText: str, value: str | int | None = None) -> None:
    '''
    # call this function with one or two arguments
    # the first argument will print on the top half of the display
    # the second argument (if provided) will print on the bottom half
    '''
    # first line
    topline = adafruit_display_text.label.Label(
        terminalio.FONT,
        color=0xffffff,
        text=inputText
    )
    topline.x = 0
    topline.y = 4

    textGroup = displayio.Group()
    textGroup.append(topline)

    # optional second line
    if value is not None:
        bottomline = adafruit_display_text.label.Label(
            terminalio.FONT,
            color=0xffffff,
            text=str(value)
        )
        bottomline.x = 0
        bottomline.y = 12
        textGroup.append(bottomline)

    display.root_group = textGroup

    display.refresh()

    display.root_group = g1

def fill_screen(color) -> None:
    # sets each pixel on the display to color
    for i in range(matrix.height * matrix.width):
        matrix[i] = color
    display.refresh()  

NUM_ENEMIES = 16

# ---------------- Invader ----------------
class Invader:
    def __init__(self, x_arg: int = 0, y_arg: int = 0, strength_arg: int = 0) -> None:
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg

    def initialize(self, x_arg: int, y_arg: int, strength_arg: int) -> None:
        # initialize instance variables
        self.x = x_arg
        self.y = y_arg
        self.strength = strength_arg
    
    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_strength(self) -> int:
        return self.strength

    # Moves the Invader down the screen by one row
    # Modifies: y
    def move(self) -> None:
        self.y += 1

    def get_body_color(self):
        if self.strength == 1:
            return RED
        elif self.strength == 2:
            return ORANGE
        elif self.strength == 3:
            return YELLOW
        elif self.strength == 4:
            return GREEN
        elif self.strength == 5:
            return BLUE
        elif self.strength == 6:
            return PURPLE
        elif self.strength == 7:
            return WHITE
        else:
            return BLACK
        
    # draws the Invader if its strength is greater than 0
    # use self.draw_with_rgb
    def draw(self) -> None:
        if self.strength > 0:
            body_color = self.get_body_color()
            self.draw_with_rgb(body_color, BLUE)

    # draws black where the Invader used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        if self.strength > 0:
            body_color = self.get_body_color()
            self.draw_with_rgb(BLACK, BLACK)

    # Invader is hit by a Cannonball.
    # Modifies: strength
    # calls: draw, erase
    def hit(self) -> None:
        self.erase()
        self.strength -= 1
        if self.strength > 0:
            self.draw()

    # draws the Invader
    def draw_with_rgb(self, body_color: int, eye_color: int) -> None:
        left = self.x
        top = self.y
        matrix[left + 1, top] = body_color
        matrix[left + 2, top] = body_color
        matrix[left, top + 1] = body_color
        matrix[left + 1, top + 1] = eye_color
        matrix[left + 2, top + 1] = eye_color
        matrix[left + 3, top + 1] = body_color
        matrix[left, top + 2] = body_color
        matrix[left + 1, top + 2] = body_color
        matrix[left + 2, top + 2] = body_color
        matrix[left + 3, top + 2] = body_color
        matrix[left, top + 3] = body_color
        matrix[left + 3, top + 3] = body_color


# ---------------- Cannonball ----------------
class Cannonball:
    def __init__(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # resets private data members to initial values
    def reset(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def has_been_fired(self) -> bool:
        return self.fired

    # sets private data members
    def fire(self, x_arg: int, y_arg: int) -> None:
        if not self.fired:
            self.x = x_arg
            self.y = y_arg
            self.fired = True

    # moves the Cannonball and detects if it goes off the screen
    # Modifies: y, fired
    def move(self) -> None:
        if self.fired:
            self.y -= 1
            if self.y < 0:
                self.reset()
        

    # resets private data members to initial values
    '''why do we have this as a separate function to reset()--------------------------------''' 
    def hit(self) -> None:
        self.x = 0
        self.y = 0
        self.fired = False

    # draws the Cannonball, if it is fired
    def draw(self) -> None:
        if self.fired:
            left = self.x
            top = self.y
            if 0 <= left < matrix.width:
                if 0 <= top < matrix.height:
                    matrix[left, top] = ORANGE
                if 0 <= top + 1 < matrix.height:
                    matrix[left, top + 1] = ORANGE

    # draws black where the Cannonball used to be
    def erase(self) -> None:
        if self.fired:
            left = self.x
            top = self.y
            if 0 <= left < matrix.width:
                if 0 <= top < matrix.height:
                    matrix[left, top] = BLACK
                if 0 <= top + 1 < matrix.height:
                    matrix[left, top + 1] = BLACK


# ---------------- Player ----------------
class Player:
    def __init__(self) -> None:
        self.x = 0
        self.y = 14
        self.lives = 3

    # getters
    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def get_lives(self) -> int:
        return self.lives

    # setter
    def set_x(self, x_arg: int) -> None:
        self.x = x_arg

    # Modifies: lives
    def die(self) -> None:
        self.lives -= 1

    # draws the Player
    # use self.draw_with_rgb
    def draw(self) -> None:
        self.draw_with_rgb(AQUA)

    # draws black where the Player used to be
    # use self.draw_with_rgb
    def erase(self) -> None:
        self.draw_with_rgb(BLACK)

    # resets private data members x and y to initial values
    def reset(self, x_arg: int, y_arg: int, lives_arg: int) -> None:
        self.x = x_arg
        self.y = y_arg
        ''' are we resetting the lives? ---------------------------------------- '''
        self.lives = lives_arg

    # draws the player
    def draw_with_rgb(self, color: int) -> None:
        left = self.x
        top = self.y
        # 4 LEDs: 3 on bottom, 1 on top middle
        # top middle: (left+1, top)
        # bottom: (left, top+1), (left+1, top+1), (left+2, top+1)
        coords = [(left + 1, top), (left, top + 1), (left + 1, top + 1), (left + 2, top + 1)]
        for x, y in coords:
            if 0 <= x < matrix.width and 0 <= y < matrix.height:
                matrix[x, y] = color

# ---------------- Game ----------------
class Game:
    def __init__(self) -> None:
        self.level: int = 1
        self.time: float = time.monotonic()
        self.move_time = time.monotonic()
        # suggested: you will want to add more attributes here
        # suggested - float for time for cannonball and invaders to move
        self.ball_last_move = time.monotonic()
        self.player: Player = Player()
        self.ball: Cannonball = Cannonball()
        self.enemies: list[Invader] = [Invader() for _ in range(NUM_ENEMIES)]

    # sets up a new game of Space Invaders
    def setup_game(self) -> None:
        fill_screen(BLACK)
        self.reset_level()

    # main loop (called repeatedly)
    def update(self, potentiometer_value: int, button_pressed: bool) -> None:
        # TODO
        self.time = time.monotonic()

        # suggested steps (check the Game Dynamics section of the specification for more)
        # 1. get the current time - this is a float in seconds
        # since the unit was powered on
        
        # 1. Update the player position
        # suggested: update the player if potentiometer moved significantly
        # normalize
        # potentiometer_value is likely 0-65535
        # Range of x: -1 to 30. Total 32 steps.
        # pot.value // 2048 gives 0 to 31. Subtract 1 to get -1 to 30.
        new_x = (potentiometer_value // 2048) - 1
        if new_x != self.player.get_x():
            self.player.erase()
            self.player.set_x(new_x)
            self.player.draw()

        # 2. Fire cannonball
        # suggested: detect if should fire
        # button.value is False when pressed (Pull.UP)
        if not button_pressed:
            self.ball.fire(self.player.get_x() + 1, self.player.get_y() - 1)

        # 3. Move cannonball
        # suggested: move cannonball if fired
        if self.time - self.ball_last_move > 0.05: # Adjusted speed
            self.ball.erase()
            self.ball.move()
            self.ball.draw()
            self.ball_last_move = self.time
            self.check_ball_collision()

        # 4. Move invaders
        # suggested: move invaders
        if self.time - self.move_time > 1.0: # 1 second interval
            # Move bottom row first
            bottom_cleared = True
            for i in range(8, 16):
                if self.enemies[i].get_strength() > 0:
                    bottom_cleared = False
                    break
            
            # Identify which invaders to move
            can_move_down = False
            if bottom_cleared:
                # Top row moves
                for i in range(0, 8):
                    if self.enemies[i].get_strength() > 0:
                        can_move_down = True
                        break
                if can_move_down:
                    for i in range(0, 8):
                        self.enemies[i].erase()
                        self.enemies[i].move()
                        self.enemies[i].draw()
            else:
                # Bottom row moves
                for i in range(8, 16):
                    if self.enemies[i].get_strength() > 0:
                        can_move_down = True
                        break
                if can_move_down:
                    for i in range(8, 16):
                        self.enemies[i].erase()
                        self.enemies[i].move()
                        self.enemies[i].draw()
            
            self.move_time = self.time
            
        # 5. Check for failures (collisions or reaching bottom)
        # suggested: check for collision with player
        if self.check_invader_collision():
            self.player.die()
            if self.player.get_lives() > 0:
                self.reset_level()
            else:
                print_text("Game Over")
                time.sleep(3)
                self.level = 1
                self.player.reset(0, 14, 3)
                self.setup_game()

        # 6. Check for level clear
        # suggested: check for cleared level
        if self.level_cleared():
            self.level += 1
            self.reset_level()

        display.refresh()

    # this function might be useful in loop: check if Player defeated all Invaders
    def level_cleared(self) -> bool:
        # TODO
        for enemy in self.enemies:
            if enemy.get_strength() > 0:
                return False
        return True
    
    # set up/reset a level
    def reset_level(self) -> None:
        # TODO
        # suggested steps:
        # 1. print level and lives

        # 2. reset the cannonball

        # 3. check for game over

        # 4. initialize invaders based on level
        
        # 5. draw enemies

        # 6. draw player

        # 7. reset time so invaders do not move immediately
        fill_screen(BLACK)
        print_text("Level: " + str(self.level), "Lives: " + str(self.player.get_lives()))
        time.sleep(1.5)
        fill_screen(BLACK)
        
        self.ball.reset()
        self.ball_last_move = time.monotonic()
        self.move_time = time.monotonic()
        
        # Reset player position (roughly middle)
        self.player.set_x(14)
        self.player.draw()

        # Initialize invaders based on level
        s1 = [1] * 8 + [0] * 8
        s2 = [1, 2, 1, 2, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 2, 1]
        s3 = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1]
        s4 = [5, 4, 5, 4, 5, 4, 5, 4, 2, 3, 2, 3, 2, 3, 2, 3]
        
        strengths = []
        if self.level == 1: strengths = s1
        elif self.level == 2: strengths = s2
        elif self.level == 3: strengths = s3
        elif self.level == 4: strengths = s4
        else:
            # Level 5 and up: Random
            strengths = [random.randint(1, 7) for _ in range(16)]

        for i in range(16):
            # Row 0: 0-7, Row 1: 8-15
            row = i // 8
            col = i % 8
            x = col * 4
            y = row * 4
            self.enemies[i].initialize(x, y, strengths[i])
            self.enemies[i].draw()
        
        display.refresh()

    # check if cannonball hits an invader
    def check_ball_collision(self) -> None:
        # TODO
        if not self.ball.has_been_fired():
            return
        
        bx = self.ball.get_x()
        by = self.ball.get_y()
        
        # Cannonball is 1x2 (vertically)
        # Check bx, by and bx, by+1
        for enemy in self.enemies:
            if enemy.get_strength() > 0:
                ex = enemy.get_x()
                ey = enemy.get_y()
                # Invader is 4x4.
                # Per-pixel hitbox check:
                # Body: (x+1,y),(x+2,y),(x,y+1),(x+3,y+1),(x,y+2),(x+1,y+2),(x+2,y+2),(x+3,y+2),(x,y+3),(x+3,y+3)
                # Eyes: (x+1,y+1),(x+2,y+1)
                # Basically x range [ex, ex+3] and y range [ey, ey+3]
                # Check ball pixels (bx, by) and (bx, by+1)
                for by_pixel in [by, by+1]:
                    if ex <= bx <= ex + 3 and ey <= by_pixel <= ey + 3:
                        # Pixel hit check
                        rel_x = bx - ex
                        rel_y = by_pixel - ey
                        
                        # Define hitbox pixels (anything not blank)
                        # ## 
                        # #**#
                        # ####
                        # #  #
                        hit_pixels = [
                            (1,0),(2,0),
                            (0,1),(1,1),(2,1),(3,1),
                            (0,2),(1,2),(2,2),(3,2),
                            (0,3),(3,3)
                        ]
                        if (rel_x, rel_y) in hit_pixels:
                            enemy.hit()
                            self.ball.reset()
                            return

    # check if invaders hit the player or bottom
    def check_invader_collision(self) -> bool:
        # TODO
        px = self.player.get_x()
        py = self.player.get_y()
        # Player size coords: (px+1, py), (px, py+1), (px+1, py+1), (px+2, py+1)
        player_pixels = [(px+1, py), (px, py+1), (px+1, py+1), (px+2, py+1)]
        
        for enemy in self.enemies:
            if enemy.get_strength() > 0:
                ex = enemy.get_x()
                ey = enemy.get_y()
                
                # Check if it reached the bottom (py+1 is the base line)
                if ey + 3 >= 15:
                    return True
                
                # Check collision with player
                # Invader pixels
                inv_pixels = [
                    (ex+1,ey),(ex+2,ey),
                    (ex,ey+1),(ex+1,ey+1),(ex+2,ey+1),(ex+3,ey+1),
                    (ex,ey+2),(ex+1,ey+2),(ex+2,ey+2),(ex+3,ey+2),
                    (ex,ey+3),(ex+3,ey+3)
                ]
                for ix, iy in inv_pixels:
                    if (ix, iy) in player_pixels:
                        return True
        return False

# ---------------- Global game instance ----------------
game = Game()


# ---------------- Arduino-style setup and loop ----------------
def setup() -> None:
    game.setup_game()
    loop()

def loop() -> None:
    while True:
        game.update(pot.value, button.value)


