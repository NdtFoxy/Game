from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from keyboard import is_pressed
import shutil
import time

# Создаем консоль
console = Console()

# Получение размеров терминала
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

# Функция для создания кнопок с новым дизайном
def draw_buttons(selected):
    # Описание кнопок
    buttons = ["FOLD", "CHECK", "CONFIRM"]

    # Создаем строки панелей для каждой кнопки
    panels = []
    for i, button in enumerate(buttons):
        if button == selected:
            # Активная кнопка: яркая рамка, подсветка и подчёркнутый текст
            panel = Panel(
                f"[bold underline white]{button}[/bold underline white]",
                border_style="bright_white",
                padding=(1, 10),
                title="[bold bright_white]SELECTED[/bold bright_white]",
                title_align="center",
            )
        else:
            # Неактивная кнопка: стандартная рамка и текст
            panel = Panel(
                f"[bold]{button}[/bold]",
                border_style="dim",
                padding=(1, 10),
            )
        panels.append(panel)

    # Располагаем кнопки с большим отступом между ними
    table = Table.grid(padding=(0, 8))
    table.add_column(justify="center")
    table.add_column(justify="center")
    table.add_column(justify="center")

    table.add_row(*panels)  # Добавляем кнопки в строку
    return table

# Функция для отображения райзера ставки
def draw_bet_raiser(bet_amount):
    # Создаем таблицу для райзера
    raiser_table = Table.grid(padding=(1, 2))
    raiser_table.add_column(justify="center")
    raiser_table.add_column(justify="center")
    raiser_table.add_column(justify="center")

    # Добавляем элементы управления: стрелки и текущую ставку
    raiser_table.add_row(
        "[bold white]↑[/bold white]",
        f"[bold blue]{bet_amount}[/bold blue]",
        "[bold white]↓[/bold white]"
    )

    # Оборачиваем в панель для красоты
    panel = Panel(
        raiser_table,
        title="[bold blue]Bet Raiser[/bold blue]",
        border_style="blue"
    )
    return panel

# Главная функция
def main():
    buttons = ["FOLD", "CHECK", "CONFIRM"]
    selected_index = 0  # Индекс выбранной кнопки
    bet_amount = 0  # Начальная ставка
    bet_increment = 10 # Шаг увеличения ставки
    alt_pressed = False
    last_up_pressed_time = 0
    last_down_pressed_time = 0

    # Live для обновления интерфейса в реальном времени
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while True:
            # Получаем размеры терминала
            columns, rows = get_terminal_size()

            # Создаем таблицу для размещения элементов
            main_table = Table.grid(padding=(1, 2))
            main_table.add_column()

            # Добавляем райзер ставки
            main_table.add_row(draw_bet_raiser(bet_amount))

            # Добавляем кнопки
            main_table.add_row(draw_buttons(selected=buttons[selected_index]))

            # Центрируем таблицу
            centered_table = Align.center(main_table, vertical="middle")

            # Обновляем экран
            live.update(centered_table)

            # Обработка ввода клавиш для райзера
            if is_pressed("up"):
                current_time = time.time()
                if is_pressed("alt"):
                    if current_time - last_up_pressed_time < 0.1:
                       bet_increment = min(bet_increment + 10, 100)
                    else:
                       bet_increment = 10
                else:
                   bet_increment = 10

                bet_amount = min(bet_amount + bet_increment, 1000)
                last_up_pressed_time = current_time
                time.sleep(0.05) # Замедление для плавного увеличения

            elif is_pressed("down"):
                current_time = time.time()
                if is_pressed("alt"):
                    if current_time - last_down_pressed_time < 0.1:
                       bet_increment = min(bet_increment + 10, 100)
                    else:
                       bet_increment = 10
                else:
                   bet_increment = 10

                bet_amount = max(bet_amount - bet_increment, 0)
                last_down_pressed_time = current_time
                time.sleep(0.05) # Замедление для плавного уменьшения

            # Обработка ввода клавиш для кнопок
            if is_pressed("left"):  # Стрелка влево
                selected_index = (selected_index - 1) % len(buttons)
                time.sleep(0.2)  # Задержка для предотвращения скачков
            elif is_pressed("right"):  # Стрелка вправо
                selected_index = (selected_index + 1) % len(buttons)
                time.sleep(0.2)
            elif is_pressed("enter"):  # Enter
                console.clear()
                console.print(f"[bold green]Вы выбрали: {buttons[selected_index]}[/bold green]", justify="center")
                if buttons[selected_index] == "CONFIRM":
                    console.print(f"[bold green]Ваша ставка: {bet_amount}[/bold green]", justify="center")
                break

if __name__ == "__main__":
    main()