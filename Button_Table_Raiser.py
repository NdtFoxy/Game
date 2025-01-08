from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.text import Text
from keyboard import is_pressed
import shutil
import time

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
                Text(button, style="bold underline white"),
                border_style="bright_white",
                padding=(1, 10),
                title="[bold bright_white]SELECTED[/bold bright_white]",
                title_align="center",
            )
        else:
            # Неактивная кнопка: стандартная рамка и текст
            panel = Panel(
                Text(button, style="bold"),
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

    # Вывод стола с отступами
    full_table = Table.grid(expand=True)
    full_table.add_row(top_row)
    full_table.add_row("")
    full_table.add_row(bot_row_top)
    full_table.add_row("")
    full_table.add_row("")
    full_table.add_row("")
    full_table.add_row(middle_row)
    full_table.add_row("")
    full_table.add_row(player_row)

    return full_table

# Главная функция
def main():
    buttons = ["FOLD", "CHECK", "CONFIRM"]
    selected_index = 0  # Индекс выбранной кнопки
    bet_amount = 0  # Начальная ставка
    bet_increment = 10 # Шаг увеличения ставки
    last_up_pressed_time = 0
    last_down_pressed_time = 0
    
    # Live для обновления интерфейса в реальном времени
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while True:
            # Получаем размеры терминала
            columns, rows = get_terminal_size()

            # Создаем таблицу для размещения элементов
            main_table = Table.grid(expand=True)
            main_table.add_column(justify="center") # Одна колонка для всего контента
            main_table.add_column(width=10, justify="center") # Добавляем пустую колонку справа для отступа

            # Рисуем покерный стол
            table_layout = draw_poker_table()

            # Добавляем райзер ставки и кнопки внизу
            controls_table = Table.grid(padding=(1, 2), expand=False)
            controls_table.add_column(justify="center")
            controls_table.add_row(Align.center(draw_bet_raiser(bet_amount)))
            controls_table.add_row(Align.center(draw_buttons(selected=buttons[selected_index])))

            # Создаем таблицу для нижней части с контролами и выравниваем по низу
            bottom_table = Align(controls_table, vertical="bottom", height=rows//4)

            # Создаем контейнер для стола и контролов и центрируем его
            content_table = Table.grid(expand=True)
            content_table.add_column(justify="center")
            content_table.add_row(table_layout)
            content_table.add_row(bottom_table)
            content_table = Align.center(content_table)

            # Добавляем все элементы на главную таблицу
            main_table.add_row(content_table, "")

            # Обновляем экран
            live.update(main_table)

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