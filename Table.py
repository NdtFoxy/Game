from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from time import sleep

console = Console()

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
    console.clear()
    console.print(top_row)
    console.print("\n")  # Пробел между линиями
    console.print(bot_row_top)
    console.print("\n")  # Пробел между линиями
    console.print("\n" * 3)  # Увеличенный отступ перед боковыми ботами
    console.print(middle_row)
    console.print("\n")  # Пробел между линиями
    console.print(player_row)

# Запуск отрисовки
draw_poker_table()

# Пауза перед выходом
sleep(5)
