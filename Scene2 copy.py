import os
import time
import random

def get_terminal_size():
    """Gets the current size of the terminal."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        # Handle cases where terminal size cannot be determined
        return 80, 24  # Default size

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def center_text(text, width):
    """Centers a list of strings within a given width."""
    centered_text = []
    for line in text:
        padding = (width - len(line)) // 2
        centered_text.append(" " * padding + line)
    return centered_text

def draw_castle(width, castle_width, side):
    """Draws a castle on either the left or right side."""
    castle = [
        "                                                  !_",
        "                                                  |*~=-.,",
        "                                                  |_,-'`",
        "                                                  |",
        "                                                  |",
        "                                                 /^\ ",
        "                   !_                           /   \ ",
        "                   |*`~-.,                     /,    \ ",
        "                   |.-~^`                     /#\"     \ ",
        "                   |                        _/##_   _  \_",
        "              _   _|  _   _   _            [ ]_[ ]_[ ]_[ ]",
        "             [ ]_[ ]_[ ]_[ ]_[ ]            |_=_-=_ - =_|",
        "           !_ |_=_ =-_-_  = =_|           !_ |=_= -    |",
        "           |*`--,_- _        |            |*`~-.,= []  |",
        "           |.-'|=     []     |   !_       |_.-'`_-     |",
        "           |   |_=- -        |   |*`~-.,  |  |=_-      |",
        "          /^\  |=_= -        |   |_,-~`  /^\ |_ - =[]  |",
        "      _  /   \_|_=- _   _   _|  _|  _   /   \|=_-      |",
        "     [ ]/,    \[ ]_[ ]_[ ]_[ ]_[ ]_[ ]_/,    \[ ]=-    |",
        "      |/#\"     \_=-___=__=__- =-_ -=_ /#\"     \| _ []  |",
        "     _/##_   _  \_-_ =  _____       _/##_   _  \_ -    |\\",
        "    [ ]_[ ]_[ ]_[ ]=_0~{_ _ _}~0   [ ]_[ ]_[ ]_[ ]=-   | \ ",
        "    |_=__-_=-_  =_|-=_ |  ,  |     |_=-___-_ =-__|_    |  \ ",
        "     | _- =-     |-_   | ((* |      |= _=       | -    |___\\",
        "     |= -_=      |=  _ |  `  |      |_-=_       |=_    |/+\\|",
        "     | =_  -     |_ = _ `-.-`       | =_ = =    |=_-   ||+||",
        "     |-_=- _     |=_   =            |=_= -_     |  =   ||+||",
        "     |=_- /+\    | -=               |_=- /+\    |=_    |^^^|",
        "     |=_ |+|+|   |= -  -_,--,_      |_= |+|+|   |  -_  |=  |",
        "     |  -|+|+|   |-_=  / |  | \     |=_ |+|+|   |-=_   |_-/",
        "     |=_=|+|+|   | =_= | |  | |     |_- |+|+|   |_ =   |=/",
        "     | _ ^^^^^   |= -  | |  <&>     |=_=^^^^^   |_=-   |/",
        "     |=_ =       | =_-_| |  | |     |   =_      | -_   |",
        "     |_=-_       |=_=  | |  | |     |=_=        |=-    |",
        "^^^^^^^^^^`^`^^`^`^`^^^\"\"\"\"\"\"\"\"^`^^``^^`^^`^^`^`^``^`^``^``^^"
    ]
    
    castle_height = len(castle)
    start_row = 5 # Adjust if needed

    if side == "left":
        start_col = 2
    else:  # side == "right"
        start_col = width - castle_width - 2

    for i in range(castle_height):
        if start_row + i < len(scene):
             # Ensure we don't go beyond the scene's height
            if len(scene[start_row + i]) < width :
                # Pad with spaces if the line is shorter than the width
                scene[start_row + i] += " " * (width - len(scene[start_row + i]))
            scene[start_row + i] = scene[start_row + i][:start_col] + castle[i] + scene[start_row + i][start_col + castle_width:]

def draw_mountains(width):
    """Draws the mountains, scaling to the terminal width."""
    mountains = [
        r"          /\ ",
        r"         /**\ ",
        r"        /****\   /\ ",
        r"       /      \ /**\ ",
        r"      /  /\    /    \        /\    /\  /\      /\            /\/\/\  /\ ",
        r"     /  /  \  /      \      /  \/\/  \/  \  /\/  \/\  /\  /\/ / /  \/  \ ",
        r"    /  /    \/ /\     \    /    \ \  /    \/ /   /  \/  \/  \  /    \   \ ",
        r"   /  /      \/  \/\   \  /      \    /   /    \ ",
        r"__/__/_______/___/ __\___\__________________________________________________"
    ]
    
    
    scale = width / len(mountains[-1])
    scaled_mountains = []
    for line in mountains:
        scaled_line = ""
        for char in line:
            scaled_line += char * int(scale)
        
        if len(scaled_line) < width:
            scaled_line += scaled_line[-(width - len(scaled_line)):]
        elif len(scaled_line) > width:
            scaled_line = scaled_line[:width]
            
        
        scaled_mountains.append(scaled_line)
    
    
    return scaled_mountains

def draw_clouds(width, num_clouds=5):
    """Draws clouds randomly across the top of the scene."""
    cloud_shapes = [
        "   _===_ ",
        " _======_ ",
        "   .--. ",
        "  (    ) ",
        " (      ) ",
        "  `----' ",
    ]
    cloud_width = max(len(line) for line in cloud_shapes)
    cloud_height = len(cloud_shapes)

    for _ in range(num_clouds):
        cloud_row = random.randint(0, 3)  # Clouds in the top 4 rows
        cloud_col = random.randint(0, width - cloud_width)

        for i in range(cloud_height):
             if cloud_row + i < len(scene) and cloud_col + cloud_width < len(scene[cloud_row + i]):  # Check bounds
                scene[cloud_row + i] = scene[cloud_row + i][:cloud_col] + cloud_shapes[i] + scene[cloud_row + i][cloud_col + cloud_width:]



# Initialize scene
width, height = get_terminal_size()
scene = [" " * width for _ in range(height)]

# Draw elements
poker_text = [
    "██████╗  ██████╗ ██╗  ██╗███████╗██████╗ ",
    "██╔══██╗██╔═══██╗██║ ██║ ██╔════╝██╔══██╗",
    "██████╔╝██║   ██║███████║█████╗  █████╔╝",
    "██╔═══╝ ██║   ██║██╔═██║ ██╔══╝  ██╔═██╗ ",
    "██║     ╚██████╔╝██║  ██║███████╗██║  ██╗",
    "╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝",
]
centered_poker = center_text(poker_text, width)
for i, line in enumerate(centered_poker):
    row = height // 2 - len(poker_text) // 2 + i - 5
    if 0 <= row < height:
        scene[row] = line

mountains = draw_mountains(width)
for i, line in enumerate(mountains):
    row = height - len(mountains) + i -2
    if 0 <= row < height:
        scene[row] = line

draw_clouds(width)

castle_width = 51  # Width of the castle ASCII art
draw_castle(width, castle_width, "left")
draw_castle(width, castle_width, "right")

# Display the scene
clear_screen()
for line in scene:
    print(line)

time.sleep(5) # Display for 5 seconds