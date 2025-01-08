from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from keyboard import is_pressed
import shutil
import time

console = Console()

def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

def draw_poker_table():
    # Верхняя линия: крупье
    top_row = Table.grid(expand=True)
    top_row.add_column("center", justify="center")
    top_row.add_row(
        Panel("👤 [bold yellow]Dealer[/]\n[blue]Chips: ∞[/]", border_style="yellow", width=30)
    )
    top_row = Align.center(top_row)

    # Линия под крупье: два бота
    bot_row_top = Table.grid(expand=True)
    bot_row_top.add_column("left", justify="center")
    bot_row_top.add_column("right", justify="center")
    bot_row_top.add_row(
        Panel("🤖 Bot 2\n[green]Chips: $2000[/]", border_style="green", width=30),
        Panel("🤖 Bot 3\n[green]Chips: $1900[/]", border_style="green", width=30),
    )
    bot_row_top = Align.center(bot_row_top)

    # Центральная зона для карт
    table_center = Align.center(
        Panel(
            Align.center(
                """
[bold white]♠♠ [red]♥♥ [blue]♣♣ [yellow]♦♦[/]
[bold green]Community Cards[/]
[dim]-- Empty --[/dim]
""",
                vertical="middle",
            ),
            title="Table Center",
            title_align="center",
            border_style="bold magenta",
            width=50,
            height=10,
        )
    )

    # Нижняя линия: игрок
    player_row = Table.grid(expand=True)
    player_row.add_column("center", justify="center")
    player_row.add_row(
        Panel("👤 [bold cyan]Player 1[/]\n[blue]Chips: $1500[/]", border_style="cyan", width=30)
    )
    player_row = Align.center(player_row)

    # Левая и правая боковые линии: боты с увеличенным отступом
    left_bot = Align.center(
        Panel("🤖 Bot 1\n[green]Chips: $1800[/]", border_style="green", width=30),
        vertical="middle",
    )
    right_bot = Align.center(
        Panel("🤖 Bot 4\n[green]Chips: $1700[/]", border_style="green", width=30),
        vertical="middle",
    )

    # Объединение боковых ботов с центральной зоной
    middle_row = Table.grid(expand=True)
    middle_row.add_column("left", width=20, justify="center")
    middle_row.add_column("center", justify="center")
    middle_row.add_column("right", width=20, justify="center")
    middle_row.add_row(left_bot, table_center, right_bot)
    middle_row = Align.center(middle_row)

    # Создание главной таблицы для компоновки всех элементов
    main_table = Table.grid(expand=True)
    main_table.add_column("center", justify="center")
    main_table.add_row(top_row)
    main_table.add_row(bot_row_top)
    main_table.add_row(middle_row)
    main_table.add_row(player_row)

    return main_table

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

            # Рисуем стол
            table = draw_poker_table()

            # Центрируем кнопки
            buttons_table = draw_buttons(selected=buttons[selected_index])
            centered_buttons = Align.center(buttons_table, vertical="bottom", height=7)

            # Создаем главную таблицу и добавляем в нее стол и кнопки
            main_layout = Table.grid(expand=True)
            main_layout.add_column("center", justify="center")
            main_layout.add_row(table)
            main_layout.add_row(centered_buttons)
            
            # Обновляем экран
            live.update(main_layout)

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