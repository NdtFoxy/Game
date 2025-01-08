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

# Игровые данные, считываемые из файла
game_data = {
    "Player_Cards": "<empty>",
    "Bot1_Cards": "<empty>",
    "Bot2_Cards": "<empty>",
    "Bot3_Cards": "<empty>",
    "Bot4_Cards": "<empty>",
    "Player_Money": 1000,
    "Bot1_Money": 1000,
    "Bot2_Money": 1000,
    "Bot3_Money": 1000,
    "Bot4_Money": 1000,
    "Table_Cards": "<empty>",
    "Krupie_Cards": "<empty>",
    "Total_Bank": 0
}

def read_game_data():
    """Считывает игровые данные из файла."""
    try:
        with open("InfoForGameBots.txt", "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                line = line.split("//")[0]  # Игнорируем часть строки после "//"
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in game_data:
                        if key.endswith("_Money"):
                            game_data[key] = int(value)
                        else:
                            game_data[key] = value
    except FileNotFoundError:
        print("Файл не найден. Используются значения по умолчанию.")

def write_game_data():
    """Записывает игровые данные в файл."""
    with open("InfoForGameBots.txt", "w", encoding="utf-8") as file:
        for key, value in game_data.items():
            file.write(f"{key} = {value}\n")

# Получение размеров терминала
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

# Функция для отрисовки одной карты с использованием Panel, правильным цветом и центрированием
def draw_card(card_key, style="bold white", title=""):
    if card_key == "<empty>":
        card_art = cards["<empty>"]
    else:
        card_art = cards[card_key]

    if card_key == "<empty>":
        suit_color = "white"
        suit = ""
    else:
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
        if card_key != "<empty>" and suit in line and any(c.isalpha() for c in line):  # Проверяем, есть ли буквы в строке с мастью
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

        elif card_key != "<empty>" and suit in line:
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
    buttons = ["FOLD", "CHECK", "RAISE", "CONFIRM"]

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

def draw_poker_table(community_cards, player_cards, bot_cards, selected_card_index, game_data):
    # Верхняя линия: дилер
    top_row = Table.grid(expand=True)
    top_row.add_column("center", justify="center")
    top_row.add_row(
        Panel(f"👤 [bold yellow]Dealer[/]\n[blue]Chips: ∞[/]\n[magenta]Bank: {game_data['Total_Bank']}[/]", border_style="yellow", width=30)
    )
    top_row = Align.center(top_row)
    
    # Линия ботов над столом
    bots_row = Table.grid(expand=True)
    bots_row.add_column("left", justify="center")
    bots_row.add_column("center", justify="center")
    bots_row.add_column("right", justify="center")

    left_bot = Align.center(
        Panel(f"🤖 Bot 2\n[green]Chips: ${game_data['Bot2_Money']}[/]", border_style="green", width=30),
    )

    right_bot = Align.center(
        Panel(f"🤖 Bot 3\n[green]Chips: ${game_data['Bot3_Money']}[/]", border_style="green", width=30),
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
        Panel(f"👤 [bold cyan]Player 1[/]\n[green]Chips: ${game_data['Player_Money']}[/]", border_style="cyan", width=30)
    )
    player_row = Align.center(player_row)

    # Левая и правая боковые линии: боты 
    left_bot_top = Align.center(
        Panel(f"🤖 Bot 1\n[green]Chips: ${game_data['Bot1_Money']}[/]\n{draw_cards(bot_cards[0])}", border_style="green", width=30),
        vertical="middle",
    )
    right_bot_top = Align.center(
        Panel(f"🤖 Bot 4\n[green]Chips: ${game_data['Bot4_Money']}[/]\n{draw_cards(bot_cards[1])}", border_style="green", width=30),
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

def determine_winner(player_cards, bot1_cards, bot2_cards, bot3_cards, bot4_cards, community_cards):
    # Преобразуем строки карт в списки карт
    player_cards = player_cards.split(',') if player_cards != "<empty>" else []
    bot1_cards = bot1_cards.split(',') if bot1_cards != "<empty>" else []
    bot2_cards = bot2_cards.split(',') if bot2_cards != "<empty>" else []
    bot3_cards = bot3_cards.split(',') if bot3_cards != "<empty>" else []
    bot4_cards = bot4_cards.split(',') if bot4_cards != "<empty>" else []
    community_cards = community_cards.split(',') if community_cards != "<empty>" else []

    # Подсчет карт каждого достоинства
    def card_ranks(hand):
        ranks = []
        for card in hand:
            if card != "<empty>":
                rank = card[0]
                if rank == 'T':
                    ranks.append(10)
                elif rank == 'J':
                    ranks.append(11)
                elif rank == 'Q':
                    ranks.append(12)
                elif rank == 'K':
                    ranks.append(13)
                elif rank == 'A':
                    ranks.append(14)
                else:
                    ranks.append(int(rank))
        return ranks

    # Проверка наличия комбинаций
    def is_flush(hand):
        suits = [card[1] for card in hand if card != "<empty>"]
        return len(set(suits)) == 1

    def is_straight(ranks):
        if len(ranks) < 5:
            return False
        ranks.sort()
        for i in range(len(ranks) - 4):
            if ranks[i] + 1 == ranks[i+1] and ranks[i+1] + 1 == ranks[i+2] and ranks[i+2] + 1 == ranks[i+3] and ranks[i+3] + 1 == ranks[i+4]:
                return True
        # Проверка на туза как самую младшую карту
        if 14 in ranks:
            ranks = [1 if rank == 14 else rank for rank in ranks]
            ranks.sort()
            for i in range(len(ranks) - 4):
                if ranks[i] + 1 == ranks[i+1] and ranks[i+1] + 1 == ranks[i+2] and ranks[i+2] + 1 == ranks[i+3] and ranks[i+3] + 1 == ranks[i+4]:
                    return True
        return False

    def is_straight_flush(hand):
        if not is_flush(hand):
            return False
        ranks = card_ranks(hand)
        return is_straight(ranks)

    def is_four_of_a_kind(ranks):
        for rank in set(ranks):
            if ranks.count(rank) == 4:
                return True
        return False

    def is_full_house(ranks):
        has_three = False
        has_two = False
        for rank in set(ranks):
            if ranks.count(rank) == 3:
                has_three = True
            elif ranks.count(rank) == 2:
                has_two = True
        return has_three and has_two

    def is_three_of_a_kind(ranks):
        for rank in set(ranks):
            if ranks.count(rank) == 3:
                return True
        return False

    def is_two_pairs(ranks):
        pairs = 0
        for rank in set(ranks):
            if ranks.count(rank) == 2:
                pairs += 1
        return pairs == 2

    def is_one_pair(ranks):
        for rank in set(ranks):
            if ranks.count(rank) == 2:
                return True
        return False
    
    def highest_card(ranks):
        if not ranks:
            return 0
        return max(ranks)

    # Оценка силы комбинации
    def hand_strength(hand):
        ranks = card_ranks(hand)
        if is_straight_flush(hand):
            return (8, highest_card(ranks))
        elif is_four_of_a_kind(ranks):
            four_rank = [rank for rank in set(ranks) if ranks.count(rank) == 4][0]
            return (7, four_rank)
        elif is_full_house(ranks):
            three_rank = [rank for rank in set(ranks) if ranks.count(rank) == 3][0]
            two_rank = [rank for rank in set(ranks) if ranks.count(rank) == 2][0]
            return (6, three_rank, two_rank)
        elif is_flush(hand):
            return (5, highest_card(ranks))
        elif is_straight(ranks):
            return (4, highest_card(ranks))
        elif is_three_of_a_kind(ranks):
            three_rank = [rank for rank in set(ranks) if ranks.count(rank) == 3][0]
            return (3, three_rank)
        elif is_two_pairs(ranks):
            pair_ranks = [rank for rank in set(ranks) if ranks.count(rank) == 2]
            pair_ranks.sort(reverse=True)
            return (2, pair_ranks[0], pair_ranks[1])
        elif is_one_pair(ranks):
            pair_rank = [rank for rank in set(ranks) if ranks.count(rank) == 2][0]
            return (1, pair_rank)
        else:
            return (0, highest_card(ranks))

    # Сравнение комбинаций игроков
    player_strength = hand_strength(player_cards + community_cards)
    bot1_strength = hand_strength(bot1_cards + community_cards)
    bot2_strength = hand_strength(bot2_cards + community_cards)
    bot3_strength = hand_strength(bot3_cards + community_cards)
    bot4_strength = hand_strength(bot4_cards + community_cards)

    strengths = {
        "Player": player_strength,
        "Bot1": bot1_strength,
        "Bot2": bot2_strength,
        "Bot3": bot3_strength,
        "Bot4": bot4_strength
    }

    # Определение победителя
    max_strength = max(strengths.values())
    winners = [player for player, strength in strengths.items() if strength == max_strength]

    return winners

# Главная функция
def main():
    global game_data
    read_game_data()

    # Инициализируем колоду
    deck = list(cards.keys())
    deck.remove("<empty>")
    random.shuffle(deck)

    buttons = ["FOLD", "CHECK", "RAISE", "CONFIRM"]
    selected_index = 0  # Индекс выбранной кнопки
    bet_amount = 0  # Начальная ставка
    bet_increment = 10 # Шаг увеличения ставки
    last_up_pressed_time = 0
    last_down_pressed_time = 0
    
    # Преобразование строк карт в списки
    player_cards = game_data["Player_Cards"].split(',') if game_data["Player_Cards"] != "<empty>" else []
    bot1_cards = game_data["Bot1_Cards"].split(',') if game_data["Bot1_Cards"] != "<empty>" else []
    bot2_cards = game_data["Bot2_Cards"].split(',') if game_data["Bot2_Cards"] != "<empty>" else []
    bot3_cards = game_data["Bot3_Cards"].split(',') if game_data["Bot3_Cards"] != "<empty>" else []
    bot4_cards = game_data["Bot4_Cards"].split(',') if game_data["Bot4_Cards"] != "<empty>" else []
    community_cards = game_data["Table_Cards"].split(',') if game_data["Table_Cards"] != "<empty>" else []

    # Замена '<empty>' на реальные карты, если это необходимо
    if not player_cards:
        player_cards = [deck.pop(), deck.pop()]
    if not bot1_cards:
        bot1_cards = [deck.pop(), deck.pop()]
    if not bot2_cards:
        bot2_cards = [deck.pop(), deck.pop()]
    if not bot3_cards:
        bot3_cards = [deck.pop(), deck.pop()]
    if not bot4_cards:
        bot4_cards = [deck.pop(), deck.pop()]
    # community_cards обновляются в процессе игры
    
    # Запись обновленных данных обратно в словарь
    game_data["Player_Cards"] = ','.join(player_cards)
    game_data["Bot1_Cards"] = ','.join(bot1_cards)
    game_data["Bot2_Cards"] = ','.join(bot2_cards)
    game_data["Bot3_Cards"] = ','.join(bot3_cards)
    game_data["Bot4_Cards"] = ','.join(bot4_cards)
    game_data["Table_Cards"] = ','.join(community_cards)

    # Обновление данных в файле после раздачи карт
    write_game_data()

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
            bot_cards_display = [["<empty>", "<empty>"], ["<empty>", "<empty>"]]
            table_layout = draw_poker_table(community_cards, player_cards, bot_cards_display, selected_card_index, game_data)

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

                    bet_amount = min(bet_amount + bet_increment, game_data["Player_Money"])
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
                        game_data["Player_Money"] -= bet_amount
                        game_data["Total_Bank"] += bet_amount
                        bet_amount = 0
                        write_game_data()
                    elif buttons[selected_index] == "RAISE":
                        game_data["Player_Money"] -= bet_amount
                        game_data["Total_Bank"] += bet_amount
                        bet_amount = 0
                        write_game_data()
                    elif buttons[selected_index] == "CHECK":
                        # Раздача карт на стол (3 для флопа, по 1 для терна и ривера)
                        if len(community_cards) == 0:  # Флоп
                            community_cards.extend([deck.pop() for _ in range(3)])
                            game_data["Table_Cards"] = ','.join(community_cards)
                            write_game_data()
                        elif len(community_cards) == 3:  # Тёрн
                            community_cards.append(deck.pop())
                            game_data["Table_Cards"] = ','.join(community_cards)
                            write_game_data()
                        elif len(community_cards) == 4:  # Ривер
                            community_cards.append(deck.pop())
                            game_data["Table_Cards"] = ','.join(community_cards)
                            write_game_data()
                        
                        # Проверка, завершена ли раздача карт
                        if len(community_cards) == 5:
                            winners = determine_winner(
                                game_data["Player_Cards"],
                                game_data["Bot1_Cards"],
                                game_data["Bot2_Cards"],
                                game_data["Bot3_Cards"],
                                game_data["Bot4_Cards"],
                                game_data["Table_Cards"]
                            )

                            # Распределение банка между победителями
                            num_winners = len(winners)
                            if num_winners > 0:
                                winnings = game_data["Total_Bank"] // num_winners
                                for winner in winners:
                                    if winner == "Player":
                                        game_data["Player_Money"] += winnings
                                    elif winner == "Bot1":
                                        game_data["Bot1_Money"] += winnings
                                    elif winner == "Bot2":
                                        game_data["Bot2_Money"] += winnings
                                    elif winner == "Bot3":
                                        game_data["Bot3_Money"] += winnings
                                    elif winner == "Bot4":
                                        game_data["Bot4_Money"] += winnings

                                # Обнуление банка после распределения
                                game_data["Total_Bank"] = 0

                                # Обновление данных в файле после распределения банка
                                write_game_data()
                                
                                # Вывод победителей
                                winners_message = ", ".join(winners)
                                console.print(f"[bold magenta]Победители: {winners_message}[/bold magenta]", justify="center")
                                time.sleep(2)
                            
                            # Перезапуск игры
                            console.clear()
                            deck = list(cards.keys())
                            deck.remove("<empty>")
                            random.shuffle(deck)
                            player_cards = [deck.pop(), deck.pop()]
                            bot1_cards = [deck.pop(), deck.pop()]
                            bot2_cards = [deck.pop(), deck.pop()]
                            bot3_cards = [deck.pop(), deck.pop()]
                            bot4_cards = [deck.pop(), deck.pop()]
                            community_cards = []
                            game_data["Player_Cards"] = ','.join(player_cards)
                            game_data["Bot1_Cards"] = ','.join(bot1_cards)
                            game_data["Bot2_Cards"] = ','.join(bot2_cards)
                            game_data["Bot3_Cards"] = ','.join(bot3_cards)
                            game_data["Bot4_Cards"] = ','.join(bot4_cards)
                            game_data["Table_Cards"] = ','.join(community_cards)
                            write_game_data()

                    elif buttons[selected_index] == "FOLD":
                         # Сброс карт игрока и раздача новых
                        deck.extend(player_cards)  # Возвращаем карты игрока в колоду
                        player_cards = []
                        random.shuffle(deck)  # Перемешиваем колоду
                        player_cards = [deck.pop(), deck.pop()]  # Раздаем две новые карты
                        game_data["Player_Cards"] = ','.join(player_cards)
                        selected_card_index = -1

                        # Сброс общих карт
                        deck.extend(community_cards)
                        community_cards = []
                        game_data["Table_Cards"] = ','.join(community_cards)
                        random.shuffle(deck)
                        write_game_data()
                    selected_index = 0
                else:
                     # Действие при выборе карты
                    console.print(f"[bold green]Вы выбрали карту: {player_cards[selected_card_index]}[/bold green]", justify="center")
                time.sleep(0.2)

if __name__ == "__main__":
    main()