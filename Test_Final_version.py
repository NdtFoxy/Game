from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.text import Text
from keyboard import is_pressed
import shutil
import time
import random
from rich.ansi import AnsiDecoder

# Импортируем карты из card_art.py
from card_art import cards

console = Console()
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
            card_panels.append(draw_card(key, style="bold bright_yellow", title="[bold bright_yellow]SELECTED[/]"))
        else:
            card_panels.append(draw_card(key, style=style))

    table.add_row(*card_panels)
    return table

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

def draw_poker_table(community_cards, player_cards, selected_card_index):
    # Верхняя линия: дилер
    top_row = Table.grid(expand=True)
    top_row.add_column("center", justify="center")
    top_row.add_row(
        Panel("👤 [bold yellow]Dealer[/]\n[blue]Chips: ∞[/]", border_style="yellow", width=30)
    )
    top_row = Align.center(top_row)
    
    # Линия ботов над столом
    bots_row = Table.grid(expand=True)
    bots_row.add_column("left", justify="center")
    bots_row.add_column("center", justify="center")
    bots_row.add_column("right", justify="center")

    left_bot = Align.center(
        Panel("🤖 Bot 2\n[green]Chips: $1800[/]", border_style="green", width=30),
    )

    right_bot = Align.center(
        Panel("🤖 Bot 3\n[green]Chips: $1700[/]", border_style="green", width=30),
    )
    
    bots_row.add_row(left_bot, "", right_bot)
    bots_row = Align.center(bots_row)

    # Центральная зона для карт
    selected_card_key = player_cards[selected_card_index] if selected_card_index >= 0 and selected_card_index < len(player_cards) else None
    
    community_cards_table = draw_cards(community_cards, style="bold blue")
    player_cards_table = draw_cards(player_cards, style="bold green", selected_card_key=selected_card_key)

    table_center_content = Table.grid(expand=True)
    table_center_content.add_column(justify="center")
    table_center_content.add_row(Align.center(community_cards_table))
    table_center_content.add_row(Align.center(player_cards_table))

    table_center = Align.center(
        Panel(
            Align.center(
                table_center_content,
                vertical="middle",
            ),
            title="Table Center",
            title_align="center",
            border_style="bold magenta",
            width=50,
            height=20,
        )
    )

    # Нижняя линия: игрок
    player_row = Table.grid(expand=True)
    player_row.add_column("center", justify="center")
    player_row.add_row(
        Panel("👤 [bold cyan]Player 1[/]\n[blue]Chips: $1500[/]", border_style="cyan", width=30)
    )
    player_row = Align.center(player_row)

    # Левая и правая боковые линии: боты 
    left_bot_top = Align.center(
        Panel("🤖 Bot 1\n[green]Chips: $1800[/]", border_style="green", width=30),
        vertical="middle",
    )
    right_bot_top = Align.center(
        Panel("🤖 Bot 4\n[green]Chips: $1700[/]", border_style="green", width=30),
        vertical="middle",
    )

 # Объединение всех элементов
    middle_row = Table.grid(expand=True)
    middle_row.add_column("left", width=20, justify="center")
    middle_row.add_column("center", justify="center")
    middle_row.add_column("right", width=20, justify="center")
    middle_row.add_row(left_bot_top, table_center, right_bot_top)
    middle_row = Align.center(middle_row)

    # Вывод стола с отступами
    full_table = Table.grid(expand=True)
    full_table.add_row(top_row)
    full_table.add_row("")
    full_table.add_row(bots_row)
    full_table.add_row("")
    full_table.add_row(middle_row)
    full_table.add_row("")
    full_table.add_row(player_row)
    full_table.add_row("")

    return full_table

# Главная функция
def main():
    # Инициализируем колоду
    deck = list(cards.keys())
    random.shuffle(deck)

    buttons = ["FOLD", "CHECK", "CONFIRM"]
    selected_index = 0  # Индекс выбранной кнопки
    bet_amount = 0  # Начальная ставка
    bet_increment = 10 # Шаг увеличения ставки
    last_up_pressed_time = 0
    last_down_pressed_time = 0

    # Игровые данные
    community_cards = []
    player_cards = [deck.pop(), deck.pop()]
    selected_card_index = -1  # Индекс выбранной карты, -1 означает, что карта не выбрана
    
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
            table_layout = draw_poker_table(community_cards, player_cards, selected_card_index)

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

             # Обработка ввода клавиш
            if is_pressed("left"):
                if selected_card_index == -1:
                    selected_index = (selected_index - 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index - 1) % len(player_cards)
                time.sleep(0.2)
            elif is_pressed("right"):
                if selected_card_index == -1:
                    selected_index = (selected_index + 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index + 1) % len(player_cards)
                time.sleep(0.2)
            elif is_pressed("up"):
                if selected_card_index == -1:
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
                    time.sleep(0.05)
                else:
                   selected_card_index = -1
                   time.sleep(0.2) # Замедление для плавного увеличения
            elif is_pressed("down"):
                if selected_card_index == -1:
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
                else:
                    if selected_card_index == -1:
                        selected_card_index = 0
                    time.sleep(0.2)

            elif is_pressed("enter"):  # Enter
                if selected_card_index == -1:
                    console.clear()
                    console.print(f"[bold green]Вы выбрали: {buttons[selected_index]}[/bold green]", justify="center")
                    if buttons[selected_index] == "CONFIRM":
                        console.print(f"[bold green]Ваша ставка: {bet_amount}[/bold green]", justify="center")
                    elif buttons[selected_index] == "CHECK":
                        # Раздача карт на стол (3 для флопа, по 1 для терна и ривера)
                        if len(community_cards) == 0:  # Флоп
                            community_cards.extend([deck.pop() for _ in range(3)])
                        elif len(community_cards) == 3:  # Тёрн
                            community_cards.append(deck.pop())
                        elif len(community_cards) == 4:  # Ривер
                            community_cards.append(deck.pop())
                    elif buttons[selected_index] == "FOLD":
                         # Сброс карт игрока и раздача новых
                        deck.extend(player_cards)  # Возвращаем карты игрока в колоду
                        player_cards = []
                        random.shuffle(deck)  # Перемешиваем колоду
                        player_cards = [deck.pop(), deck.pop()]  # Раздаем две новые карты
                        selected_card_index = -1

                        # Сброс общих карт
                        deck.extend(community_cards)
                        community_cards = []
                        random.shuffle(deck)
                    selected_index = 0
                else:
                     # Действие при выборе карты
                    console.print(f"[bold green]Вы выбрали карту: {player_cards[selected_card_index]}[/bold green]", justify="center")
                time.sleep(0.2)

if __name__ == "__main__":
    main()