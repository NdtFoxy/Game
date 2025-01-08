import curses
import time
import random

def generate_mountains(width):
    """Динамическая генерация гор."""
    mountain = ""
    for i in range(width):
        if i % 3 == 0 and random.choice([True, False]):
            mountain += "/\\"
        else:
            mountain += "  "
    return mountain

def animate_clouds(clouds, width):
    """Обновление положения облаков."""
    new_clouds = []
    for cloud in clouds:
        new_cloud = " " + cloud[:-1]  # Смещение облака влево
        if len(new_cloud.strip()) == 0:  # Если облако "ушло", перегенерировать
            new_cloud = " " * random.randint(5, 20) + random.choice([" ☁", " ☁☁"])
        new_clouds.append(new_cloud)
    return new_clouds

def render_scene(stdscr, width, height):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    # Облака
    clouds = [
        " ☁         ☁ ",
        "      ☁☁      ☁",
        "   ☁    ☁   ☁☁",
    ]

    # Постоянные части сцены
    building1 = [
        "                           o                    ",
        "                       _---|         _ _ _ _ _ ",
        "                    o   ---|     o   ]-I-I-I-[ ",
        "   _ _ _ _ _ _  _---|      | _---|    \\ ` ' / ",
        "   ]-I-I-I-I-[   ---|      |  ---|    |.   | ",
        "    \\ `   '_/       |     / \\    |    | /^\\| ",
        "     [*]  __|       ^    / ^ \\   ^    | |*|| ",
        "     |__   ,|      / \\  /    `\\ / \\   | ===| ",
        "  ___| ___ ,|__   /    /=_=_=_=\\   \\  |,  _|",
        "  I_I__I_I__I_I  (====(_________)___|_|____|____",
        "  \\-\\--|-|--/-/  |     I  [ ]__I I_I__|____I_I_| ",
        "   |[]      '|   | []  |`__  . [  \\-\\--|-|--/-/  ",
        "   |.   | |' |___|_____I___|___I___|---------| ",
        "  / \\| []   .|_|-|_|-|-|_|-|_|-|_|-| []   [] | ",
        " <===>  |   .|-=-=-=-=-=-=-=-=-=-=-|   |    / \\  ",
    ]

    building2 = building1  # Второе здание идентично первому

    poker_text = [
        "██████╗  ██████╗ ██╗  ██╗███████╗██████╗ ",
        "██╔══██╗██╔═══██╗██║ ██║ ██╔════╝██╔══██╗",
        "██████╔╝██║   ██║███████║█████╗  █████╔╝",
        "██╔═══╝ ██║   ██║██╔═██║ ██╔══╝  ██╔═██╗ ",
        "██║     ╚██████╔╝██║  ██║███████╗██║  ██╗",
        "╚═╝      ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝",
    ]

    while True:
        # Очистка экрана
        stdscr.clear()

        # Генерация гор
        mountains = generate_mountains(width)

        # Отрисовка облаков
        for i, cloud in enumerate(clouds):
            stdscr.addstr(1 + i, 2, cloud)

        # Отрисовка зданий
        for i, line in enumerate(building1):
            stdscr.addstr(6 + i, 2, line)
        for i, line in enumerate(building2):
            stdscr.addstr(6 + i, width - 40, line)

        # Отрисовка текста "ПОКЕР"
        for i, line in enumerate(poker_text):
            x = (width // 2) - (len(line) // 2)
            stdscr.addstr(20 + i, x, line)

        # Отрисовка гор
        stdscr.addstr(height - 3, 0, mountains)

        # Обновление облаков
        clouds = animate_clouds(clouds, width)

        # Обновление экрана
        stdscr.refresh()

        # Завершение при нажатии "q"
        key = stdscr.getch()
        if key == ord("q"):
            break

# Запуск
if __name__ == "__main__":
    curses.wrapper(render_scene)
