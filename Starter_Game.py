import os
import random
import time
from colorama import Fore, Style, init

# Инициализация colorama
init(autoreset=True)

DEFAULT_CONSOLE_SIZE = (100, 25)
UPDATE_INTERVAL = 0.5
SEA_HEIGHT_RATIO = 0.125
DEFAULT_STAR_HEIGHT_OFFSET = 10
DEFAULT_TEXT_OFFSET = 0
DEFAULT_SEA_HEIGHT = 5
TEXT_PADDING = 1

SHIP_SPAWN_OFFSET = 5  # Константа для изменения высоты спавна корабля

FIREWORK_SYMBOLS = ['*', '.', 'o', '+', 'x',]

SHIP = [
    "                __/___            ",
    "          _____/______|           ",
    "  _______/_____\_______\_____     ",
    "  \\              < < <       |    ",
    "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
]

# Функция для определения размеров консоли
def get_console_size():
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return DEFAULT_CONSOLE_SIZE

# Генерация города с кораблем и фейерверками
def generate_city(width, height, sea_height, stars_height_limit, fireworks, ship_x, show_ship):
    city = [[" " for _ in range(width)] for _ in range(height)]

    # Здания
    num_buildings = width // 12
    for i in range(num_buildings):
        x_start = i * (width // num_buildings) + random.randint(0, 2)
        building_width = random.randint(4, 8)
        building_height = random.randint(4, 12)

        for y in range(height - sea_height - 1, height - sea_height - 1 - building_height, -1):
            for x in range(x_start, x_start + building_width):
                if 0 <= x < width:
                    city[y][x] = Fore.WHITE + "█"
                    if (
                        x > x_start and x < x_start + building_width - 1
                        and y < height - sea_height - 1
                        and y > height - sea_height - 1 - building_height + 1
                        and x % 2 == 0 and y % 2 == 0
                    ):
                        city[y][x] = Fore.YELLOW + (" " if (x + y) % 3 else "▒")

    # Море
    for y in range(height - sea_height, height):
        for x in range(width):
            city[y][x] = Fore.LIGHTCYAN_EX + "~" if (x + y) % 2 else Fore.BLUE + "≈"

    # Добавление корабля в море, если разрешено
    if show_ship:
        ship_y = height - sea_height - len(SHIP) + SHIP_SPAWN_OFFSET
        for i, line in enumerate(SHIP):
            for j, char in enumerate(line):
                if 0 <= ship_y + i < height and 0 <= ship_x + j < width:
                    if char.strip():  # Только видимые символы корабля
                        city[ship_y + i][ship_x + j] = Fore.LIGHTBLACK_EX + char

    # Звезды
    num_stars = max(10, width // 5)
    for _ in range(num_stars):
        while True:
            star_x = random.randint(0, width - 1)
            star_y = random.randint(0, stars_height_limit)
            if city[star_y][star_x] == " ":
                city[star_y][star_x] = Fore.YELLOW + ("*" if random.random() > 0.5 else "•")
                break

    # Фейерверки
    for fw in fireworks:
        x, y, symbol = fw
        if 0 <= y < height:
            city[y][x] = Fore.RED + symbol

    return city

# Генерация фейерверков
def generate_fireworks(width, height):
    fireworks = []
    for _ in range(random.randint(3, 6)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height // 3)
        symbol = random.choice(FIREWORK_SYMBOLS)
        fireworks.append((x, y, symbol))
    return fireworks

# Отображение города
def display_city(city, big_text, game_name, width, height, sea_height):
    os.system('cls' if os.name == 'nt' else 'clear')

    # Печать заголовка
    text_start_y = max(0, height // 2 - len(big_text) // 2)
    text_start_x = (width - len(big_text[0])) // 2
    for i, line in enumerate(big_text):
        print(" " * text_start_x + line)

    # Печать названия игры
    sub_text_start_x = (width - len(game_name)) // 2
    print(" " * sub_text_start_x + Fore.RED + game_name)

    # Печать города
    for row in city:
        print("".join(row))

# Основной цикл программы
def main():
    big_text = [
        Fore.BLUE + "██████╗  ██████╗ ██╗  ██╗███████╗██████╗ ",
        Fore.BLUE + "██╔══██╗██╔═══██╗██║ ██║ ██╔════╝██╔══██╗",
        Fore.BLUE + "██████╔╝██║   ██║███████║█████╗  ██████╔╝",
        Fore.BLUE + "██╔═══╝ ██║   ██║██╔═██║ ██╔══╝  ██╔═██╗ ",
        Fore.BLUE + "██║     ╚██████╔╝██║  ██║███████╗██║  ██╗",
        Fore.BLUE + "╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝",
    ]
    game_name = "Your Game Name Here"

    while True:
        width, height = get_console_size()
        sea_height = max(3, int(height * SEA_HEIGHT_RATIO))
        stars_height_limit = max(0, height - sea_height - DEFAULT_STAR_HEIGHT_OFFSET)

        # Если экран слишком маленький, скрываем корабль
        show_ship = height > 12 and width > 30  # Условие для показа корабля

        # Если корабль можно показывать, устанавливаем начальную позицию
        if show_ship:
            ship_x = width - len(SHIP[0]) - 1  # Начальная позиция корабля
        else:
            ship_x = -len(SHIP[0])  # Скрыть корабль

        fireworks = generate_fireworks(width, stars_height_limit)
        city = generate_city(width, height, sea_height, stars_height_limit, fireworks, ship_x, show_ship)

        display_city(city, big_text, game_name, width, height, sea_height)

        # Движение корабля влево
        if show_ship:
            ship_x -= 1
            if ship_x < -len(SHIP[0]):  # Если корабль полностью ушел за левый край
                ship_x = width  # Появляется справа

        time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    main()
