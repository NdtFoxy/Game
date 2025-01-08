import curses
import time

def render_scene(stdscr):
    # Настройки curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    while True:
        # Получение размеров окна
        height, width = stdscr.getmaxyx()

        # Минимальные размеры экрана для корректной работы
        if height < 25 or width < 80:
            stdscr.clear()
            stdscr.addstr(0, 0, "Увеличьте размер окна терминала (минимум 80x25).")
            stdscr.refresh()
            time.sleep(0.5)
            continue

        # Облака
        clouds = [
            " ☁         ☁ ",
            "      ☁☁      ☁",
            "   ☁    ☁   ☁☁",
        ]

        # Фиксированные горы
        mountains = [
            "          /\\",
            "         /**\\",
            "        /****\   /\\",
            "       /      \ /**\\",
            "      /  /\    /    \        /\    /\  /\      /\            /\/\/\  /\\",
            "     /  /  \  /      \      /  \/\/  \/  \  /\/  \/\  /\  /\/ / /  \/  \\",
            "    /  /    \/ /\     \    /    \ \  /    \/ /   /  \/  \/  \  /    \   \\",
            "   /  /      \/  \/\   \  /      \    /   /    \\",
            "__/__/_______/___/__\___\__________________________________________________"
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

        # Очистка экрана
        stdscr.clear()

        # Отрисовка облаков
        for i, cloud in enumerate(clouds):
            if i + 1 < height:
                stdscr.addstr(1 + i, 2, cloud[:width])

        # Отрисовка фиксированных гор
        for i, mountain_line in enumerate(mountains):
            if 4 + i < height:
                stdscr.addstr(4 + i, max(0, (width // 2) - (len(mountain_line) // 2)), mountain_line[:width])

        # Отрисовка зданий
        for i, line in enumerate(building1):
            if 12 + i < height:
                stdscr.addstr(12 + i, 2, line[:width])
        for i, line in enumerate(building2):
            if 12 + i < height:
                stdscr.addstr(12 + i, width - len(line) - 2, line[:width])

        # Отрисовка текста "ПОКЕР"
        for i, line in enumerate(poker_text):
            x = max(0, (width // 2) - (len(line) // 2))
            if 20 + i < height:
                stdscr.addstr(20 + i, x, line[:width])

        # Отрисовка ландшафта (земля под зданиями)
        if height - 3 >= 0:
            stdscr.addstr(height - 4, 0, "_" * width)

        # Обновление экрана
        stdscr.refresh()

        # Завершение при нажатии "q"
        key = stdscr.getch()
        if key == ord("q"):
            break

# Запуск
if __name__ == "__main__":
    curses.wrapper(render_scene)
