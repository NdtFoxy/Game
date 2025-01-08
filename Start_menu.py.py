import keyboard  # Для обработки событий клавиатуры
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.live import Live
from rich.text import Text
from rich.align import Align
from time import sleep

console = Console()


def create_menu(title, options, selected_option):
    """Создает меню с красивым заголовком и списком опций."""
    # Создаем строки панелей для каждой опции
    panels = []
    for index, label in enumerate(options):
        if index == selected_option:
            # Активная опция: подсветка, выделение и рамка
            panel = Panel(
                f"[bold underline white]{label}[/bold underline white]",
                border_style="bright_white",
                padding=(1, 10),
                title="[bold bright_white]SELECTED[/bold bright_white]",
                title_align="center",
            )
        else:
            # Неактивная опция: стандартная рамка и текст
            panel = Panel(
                f"[bold]{label}[/bold]",
                border_style="dim",
                padding=(1, 10),
            )
        panels.append(panel)

    # Располагаем опции вертикально в таблице
    table = Table.grid(padding=(1, 0))
    for panel in panels:
        table.add_row(panel)

    # Центрируем таблицу
    centered_table = Align.center(table, vertical="middle")

    # Компоновка меню
    layout = Layout()
    layout.split_column(
        Layout(
            Align.center(
                Panel(f"[bold magenta]{title}[/]", border_style="cyan", padding=(1, 2)),
                vertical="middle",
            ),
            name="header",
            size=5,
        ),
        Layout(Align.center(centered_table, vertical="middle"), name="menu"),
        Layout(
            Align.center(
                Panel(
                    Text(
                        "Use [bold yellow]↑[/] and [bold yellow]↓[/] to navigate, [bold yellow]Enter[/] to select, or [bold yellow]Q[/] to quit.",
                        justify="center",
                    ),
                    border_style="green",
                ),
                vertical="middle",
            ),
            size=3,
        ),
    )
    return layout


def navigate(state, option):
    """Навигация по меню."""
    current_menu = state["current_menu"]
    if current_menu == "main":
        if option == 0:
            console.print("[bold green]🎮 Starting a game with a human![/]")
        elif option == 1:
            console.print("[bold green]🤖 Starting a game with a bot![/]")
        elif option == 2:
            state["current_menu"] = "settings"
        elif option == 3:
            state["current_menu"] = "language"
        elif option == 4:
            console.clear()
            console.print(Panel("[bold red]Goodbye![/]", border_style="red", title="Exit", title_align="center"))
            return False
    elif current_menu == "settings" and option == len(state["menus"][current_menu]["options"]) - 1:
        state["current_menu"] = "main"
    elif current_menu == "language" and option == len(state["menus"][current_menu]["options"]) - 1:
        state["current_menu"] = "main"
    return True


def get_current_menu(state):
    """Возвращает текущий экран меню."""
    menu_data = state["menus"][state["current_menu"]]
    return create_menu(menu_data["title"], menu_data["options"], state["selected_option"])


def run_menu():
    """Основной цикл меню."""
    state = {
        "selected_option": 0,
        "current_menu": "main",
        "menus": {
            "main": {
                "title": "✨ Welcome to the Game ✨",
                "options": ["🎮 Play with a Human", "🤖 Play with a Bot", "⚙️ Settings", "🌐 Change Language", "❌ Exit"],
            },
            "settings": {
                "title": "🃏 Select Poker Type",
                "options": ["♠ Texas Hold'em", "♣ Omaha", "♥ Seven Card Stud", "♦ Five Card Draw", "🔙 Back"],
            },
            "language": {
                "title": "🌐 Change Language",
                "options": ["🇬🇧 English", "🇵🇱 Polish", "🔙 Back"],
            },
        },
    }

    with Live(console=console, screen=True, refresh_per_second=10) as live:
        running = True
        while running:
            # Обновление интерфейса
            live.update(get_current_menu(state))

            # Обработка нажатий клавиш
            if keyboard.is_pressed("up") or keyboard.is_pressed("w"):
                state["selected_option"] = (state["selected_option"] - 1) % len(state["menus"][state["current_menu"]]["options"])
                sleep(0.2)
            elif keyboard.is_pressed("down") or keyboard.is_pressed("s"):
                state["selected_option"] = (state["selected_option"] + 1) % len(state["menus"][state["current_menu"]]["options"])
                sleep(0.2)
            elif keyboard.is_pressed("enter"):
                running = navigate(state, state["selected_option"])
                sleep(0.2)
            elif keyboard.is_pressed("q"):
                running = False
                console.print(Panel("[bold red]Exiting the application...[/]", border_style="bright_red"))
                sleep(0.5)


# Запуск
run_menu()
