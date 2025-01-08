from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.panel import Panel
from rich.live import Live
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

# Главная функция
def main():
    buttons = ["FOLD", "CHECK", "CONFIRM"]
    selected_index = 0  # Индекс выбранной кнопки

    # Live для обновления интерфейса в реальном времени
    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            # Получаем размеры терминала
            columns, rows = get_terminal_size()

            # Центрируем кнопки
            centered_table = Align.center(
                draw_buttons(selected=buttons[selected_index]),
                vertical="middle",
            )

            # Обновляем экран
            live.update(centered_table)

            # Обработка ввода клавиш
            if is_pressed("left"):  # Стрелка влево
                selected_index = (selected_index - 1) % len(buttons)
                time.sleep(0.2)  # Задержка для предотвращения скачков
            elif is_pressed("right"):  # Стрелка вправо
                selected_index = (selected_index + 1) % len(buttons)
                time.sleep(0.2)
            elif is_pressed("enter"):  # Enter
                console.clear()
                console.print(f"[bold green]Вы выбрали: {buttons[selected_index]}[/bold green]", justify="center")
                break

if __name__ == "__main__":
    main()
