from rich.console import Console
from rich.table import Table
from rich.align import Align
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from keyboard import is_pressed
import shutil
import time
import random
from rich.ansi import AnsiDecoder

# Импортируем карты из card_art.py
from card_art import cards

# Создаем консоль
console = Console()
# Создаем декодер ANSI
decoder = AnsiDecoder()

# Получение размеров терминала
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

# Функция для отрисовки одной карты с использованием Panel, правильным цветом и центрированием
def draw_card(card_key, style="bold white", title=""):
    card_art = cards[card_key]
    suit = card_key[-1]

    if suit in ('H', 'D'):
        suit_color = "red"
    elif suit in ('S', 'C'):
        suit_color = "black"
    else:
        suit_color = "white"

    lines = card_art.split('\n')
    # Находим максимальную длину среди ВСЕХ строк
    max_line_len = max(len(line) for line in lines)

    centered_lines = []
    for i, line in enumerate(lines):
        if suit in line and any(c.isalpha() for c in line):  # Проверяем, есть ли буквы в строке с мастью
            # Центрируем строку с символом масти и буквой
            colored_suit = f"[{suit_color}]{suit}[/{suit_color}]"
            text_colored_suit = next(decoder.decode(colored_suit))

            # Ищем позицию буквы в строке
            letter_index = next((i for i, c in enumerate(line) if c.isalpha()), None)
            letter = line[letter_index]

            # Разделяем строку на части до и после буквы
            before_letter = line[:letter_index]
            after_letter = line[letter_index+1:]

            # Считаем отступ для каждой части
            padding_before = (max_line_len - len(text_colored_suit) - 1) // 2  # -1 для учёта буквы
            padding_after = max_line_len - padding_before - len(text_colored_suit) - 1

            # Центрируем каждую часть и объединяем
            centered_line = " " * padding_before + before_letter + letter + after_letter + " " * padding_after

        elif suit in line:
            # Центрируем строку с символом масти (без буквы)
            colored_suit = f"[{suit_color}]{suit}[/{suit_color}]"
            text_colored_suit = next(decoder.decode(colored_suit))
            padding = (max_line_len - len(text_colored_suit)) // 2
            centered_line = " " * padding + colored_suit + " " * (max_line_len - padding - len(text_colored_suit))
        else:
            # Центрируем остальные строки
            padding = (max_line_len - len(line)) // 2
            centered_line = " " * padding + line + " " * (max_line_len - padding - len(line))

        centered_lines.append(centered_line)

    centered_card_art = "\n".join(centered_lines)

    panel = Panel(
        centered_card_art,
        style=style,
        padding=(0, 1),
        title=title,
        title_align="left"
    )
    return panel

# Функция для отрисовки нескольких карт в ряд
def draw_cards(card_keys, style="bold white", selected_card_key=None):
    table = Table.grid(padding=(1, 2))
    table.add_column(justify="center")

    card_panels = []
    for key in card_keys:
        if key == selected_card_key:
            panel = Panel(
                Align.center(draw_card(key, style="bold bright_yellow", title="[bold bright_yellow]SELECTED[/]")),
                style=style
            )
        else:
            panel = Panel(
                Align.center(draw_card(key, style=style)),
                style=style
            )
        card_panels.append(panel)

    table.add_row(*card_panels)
    return table

# Функция для создания кнопок с новым дизайном
def draw_buttons(selected):
    buttons = ["FLOP", "TURN", "RIVER", "DEAL"]

    panels = []
    for i, button in enumerate(buttons):
        if button == selected:
            panel = Panel(
                f"[bold underline white]{button}[/bold underline white]",
                border_style="bright_white",
                padding=(1, 2),
                title="[bold bright_white]SELECTED[/bold bright_white]",
                title_align="center",
            )
        else:
            panel = Panel(
                f"[bold]{button}[/bold]",
                border_style="dim",
                padding=(1, 2),
            )
        panels.append(panel)

    table = Table.grid(padding=(0, 4))
    for _ in buttons:
        table.add_column(justify="center")

    table.add_row(*panels)
    return table

# Главная функция
def main():
    # Инициализируем колоду
    deck = list(cards.keys())
    random.shuffle(deck)

    # Игровые данные
    community_cards = []
    player_cards = [deck.pop(), deck.pop()]

    buttons = ["FLOP", "TURN", "RIVER", "DEAL"]
    selected_button_index = 0
    selected_card_index = -1  # Индекс выбранной карты, -1 означает, что карта не выбрана

    # Live для обновления интерфейса в реальном времени
    with Live(console=console, refresh_per_second=10, screen=True) as live:
        while True:
            columns, rows = get_terminal_size()

            # Отрисовываем общие карты
            community_cards_table = draw_cards(community_cards, style="bold blue")

            # Отрисовываем карты игрока
            selected_card_key = player_cards[selected_card_index] if selected_card_index >= 0 and selected_card_index < len(player_cards) else None
            player_cards_table = draw_cards(player_cards, style="bold green", selected_card_key=selected_card_key)

            # Отрисовываем кнопки
            buttons_table = draw_buttons(selected=buttons[selected_button_index])

            # Компонуем интерфейс
            main_table = Table.grid(padding=(1, 2))
            main_table.add_column(justify="center")
            main_table.add_row(Align.center(community_cards_table, vertical="middle"))
            main_table.add_row(Align.center(player_cards_table, vertical="middle"))
            main_table.add_row(Align.center(buttons_table, vertical="middle"))

            # Центрируем и обновляем
            centered_table = Align.center(main_table, vertical="middle")
            live.update(centered_table)

            # Обработка ввода клавиш
            if is_pressed("left"):
                if selected_card_index == -1:
                    selected_button_index = (selected_button_index - 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index - 1) % len(player_cards)
                time.sleep(0.2)
            elif is_pressed("right"):
                if selected_card_index == -1:
                    selected_button_index = (selected_button_index + 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index + 1) % len(player_cards)
                time.sleep(0.2)
            elif is_pressed("up"):
                if selected_card_index != -1:
                    selected_card_index = -1
                time.sleep(0.2)
            elif is_pressed("down"):
                if selected_card_index == -1:
                    selected_card_index = 0
                time.sleep(0.2)
            elif is_pressed("enter"):
                if selected_card_index == -1:
                    action = buttons[selected_button_index]
                    if action == "FLOP" and len(community_cards) == 0:
                        community_cards.extend([deck.pop() for _ in range(3)])
                    elif action == "TURN" and len(community_cards) == 3:
                        community_cards.append(deck.pop())
                    elif action == "RIVER" and len(community_cards) == 4:
                        community_cards.append(deck.pop())
                    elif action == "DEAL":
                        # Сбрасываем игру
                        deck = list(cards.keys())
                        random.shuffle(deck)
                        community_cards = []
                        player_cards = [deck.pop(), deck.pop()]
                    selected_button_index = 0  # Сбрасываем выбор кнопки
                else:
                    # Действие при выборе карты
                    console.print(f"[bold green]Вы выбрали карту: {player_cards[selected_card_index]}[/bold green]", justify="center")
                time.sleep(0.2)

if __name__ == "__main__":
    main()