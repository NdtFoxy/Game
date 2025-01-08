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

# Цвета для мастей
SUIT_COLORS = {
    'H': 'red',
    'D': 'red',
    'S': 'black',
    'C': 'black',
}

# Текстовые представления мастей
SUIT_SYMBOLS = {
    'H': '♥',
    'D': '♦',
    'S': '♠',
    'C': '♣',
}

class Player:
    def __init__(self, name, chips, is_human=False):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.is_human = is_human
        self.is_all_in = False
        self.folded = False
        self.is_active = False # Добавлено для отображения активности

    def reset_hand(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.is_all_in = False
        self.is_active = False

    def bet(self, amount):
        if amount >= self.chips:
            amount = self.chips
            self.is_all_in = True

        self.chips -= amount
        self.current_bet += amount
        return amount
    
    def call(self, amount_to_call):
        bet_amount = min(amount_to_call, self.chips)
        self.chips -= bet_amount
        self.current_bet += bet_amount
        if self.chips == 0:
            self.is_all_in = True
        return bet_amount
    
    def check(self):
        return 0

    def fold(self):
        self.folded = True

    def __str__(self):
        return f"{self.name} (Chips: {self.chips})"

class Deck:
    def __init__(self):
        self.cards = list(cards.keys())
        random.shuffle(self.cards)

    def deal(self):
        if not self.cards:
            return None
        return self.cards.pop()
    
    def shuffle(self):
        random.shuffle(self.cards)

    def reset(self, used_cards):
        self.cards = list(cards.keys())
        self.cards.extend(used_cards)
        random.shuffle(self.cards)

class PokerGame:
    def __init__(self, num_players=5, starting_chips=1000, small_blind=5, big_blind=10):
        self.players = [Player(f"Bot {i+1}", starting_chips) for i in range(num_players - 1)]
        self.players.append(Player("Player 1", starting_chips, is_human=True))  # Добавляем игрока-человека
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.current_bet = 0
        self.dealer_index = 0
        self.active_player_index = 0
        self.betting_round = 0
        self.game_started = False
        self.used_cards = []

    def read_game_state(self, filename="InfoForGameBots.txt"):
        """Считывает состояние игры из файла."""
        try:
            with open(filename, "r") as f:
                lines = f.readlines()

            data = {}
            for line in lines:
                key, value = line.strip().split(" = ")
                data[key] = value

            self.players[4].hand = self.parse_cards(data["Player_Cards"])
            for i in range(4):
                self.players[i].hand = self.parse_cards(data[f"Bot{i+1}_Cards"])
            
            self.players[4].chips = int(data["Player_Money"])
            for i in range(4):
                self.players[i].chips = int(data[f"Bot{i+1}_Money"])

            self.community_cards = self.parse_cards(data["Table_Cards"])
            self.deck.reset(self.parse_cards(data["Krupie_Cards"]))

        except FileNotFoundError:
            console.print(f"[bold red]File '{filename}' not found. Starting a new game.[/]")
            self.start_game()
        except Exception as e:
            console.print(f"[bold red]Error reading game state from '{filename}': {e}[/]")
            self.start_game()
        

    def parse_cards(self, card_str):
        """Преобразует строку с картами в список карт."""
        if card_str == "<empty>":
            return []
        else:
            return card_str.split(", ")

    def write_game_state(self, filename="InfoForGameBots.txt"):
        """Записывает состояние игры в файл."""
        with open(filename, "w") as f:
            f.write(f"Player_Cards = {', '.join(self.players[4].hand) if self.players[4].hand else '<empty>'}\n")
            for i in range(4):
                f.write(f"Bot{i+1}_Cards = {', '.join(self.players[i].hand) if self.players[i].hand else '<empty>'}\n")

            f.write(f"Player_Money = {self.players[4].chips}\n")
            for i in range(4):
                f.write(f"Bot{i+1}_Money = {self.players[i].chips}\n")
            
            f.write(f"Table_Cards = {', '.join(self.community_cards) if self.community_cards else '<empty>'}\n")
            f.write(f"Krupie_Cards = {', '.join(self.deck.cards) if self.deck.cards else '<empty>'}\n")

    def reset_round(self):
        """Сбрасывает состояние для нового раунда."""
        
        self.used_cards.extend(self.community_cards)
        for p in self.players:
            self.used_cards.extend(p.hand)
        self.deck.reset(self.used_cards)
        self.used_cards = []

        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.dealer_index = (self.dealer_index + 1) % len(self.players)
        self.betting_round = 0

        for player in self.players:
            player.reset_hand()

    def deal_hands(self):
        for player in self.players:
            if not player.folded:
                player.hand = [self.deck.deal(), self.deck.deal()]

    def deal_community_cards(self):
        if self.betting_round == 1:  # Флоп
            self.community_cards.extend([self.deck.deal() for _ in range(3)])
        elif self.betting_round in [2, 3]:  # Тёрн и Ривер
            self.community_cards.append(self.deck.deal())

    def start_game(self):
        self.game_started = True
        self.reset_round()
        self.deal_hands()
        self.start_betting_round()

    def start_betting_round(self):
        # Начинаем раунд торговли
        self.current_bet = 0

        # Малый и большой блайнд
        sb_index = (self.dealer_index + 1) % len(self.players)
        bb_index = (self.dealer_index + 2) % len(self.players)
        
        small_blind_amount = self.players[sb_index].bet(self.small_blind)
        big_blind_amount = self.players[bb_index].bet(self.big_blind)
        self.pot += small_blind_amount + big_blind_amount
        self.current_bet = self.big_blind

        # Устанавливаем активного игрока после большого блайнда
        self.active_player_index = (self.dealer_index) % len(self.players)

    def next_betting_round(self):
        # Сбрасываем ставки игроков
        for player in self.players:
            player.current_bet = 0

        self.betting_round += 1
        if self.betting_round == 4:
            self.showdown()
            return
        
        self.deal_community_cards()
        self.active_player_index = (self.dealer_index + 1) % len(self.players) # Начинаем с игрока после дилера
        self.current_bet = 0
        self.start_betting_round()
        
    def next_player(self):
        """Переход к следующему активному игроку."""
        while True:
            self.active_player_index = (self.active_player_index + 1) % len(self.players)
            active_player = self.players[self.active_player_index]
            
            # Пропускаем сложенных игроков и игроков, у которых все фишки в ставках
            if not active_player.folded and not active_player.is_all_in:
                break

    def showdown(self):
        """Определение победителя и распределение банка."""
        
        # Фильтруем игроков, которые не сбросили карты и не ушли в олл-ин
        eligible_players = [p for p in self.players if not p.folded]

        if len(eligible_players) == 1:
            winner = eligible_players[0]
            console.print(f"[bold green]{winner.name} wins the pot of ${self.pot}![/]")
            winner.chips += self.pot
            self.pot = 0

        elif len(eligible_players) > 1:
            # Здесь должен быть код для сравнения комбинаций карт
            # Временно выбираем победителя случайным образом
            winner = random.choice(eligible_players)
            console.print(f"[bold green]{winner.name} wins the pot of ${self.pot} with a random hand![/]")
            winner.chips += self.pot
            self.pot = 0

        # Подготовка к новому раунду
        self.reset_round()
        self.deal_hands()
        self.start_betting_round()
        self.write_game_state()

    def handle_player_action(self, action, bet_amount=0):
        player = self.players[self.active_player_index]
        amount_to_call = self.current_bet - player.current_bet

        if action == "FOLD":
            player.fold()
        elif action == "CHECK":
            if player.current_bet == self.current_bet:
                player.check()
            else:
                console.print("[bold red]Cannot check. Must call or fold.[/]")
                return
        elif action == "CALL":
            bet_amount = player.call(amount_to_call)
            self.pot += bet_amount
        elif action == "RAISE":
            if bet_amount > amount_to_call:
                self.current_bet = player.current_bet + bet_amount
                bet_amount = player.bet(bet_amount)
                self.pot += bet_amount
            else:
                console.print(f"[bold red]Bet must be at least {amount_to_call + self.big_blind}.[/]")
                return

        console.print(f"[bold green]{player.name} {action}s.[/]")

        # Проверка, все ли игроки сделали ход
        all_bets_equal = all((p.current_bet == self.current_bet or p.folded or p.is_all_in) for p in self.players if not p.folded)
        
        if all_bets_equal:
            self.next_betting_round()
        else:
            self.next_player()

# Получение размеров терминала
def get_terminal_size():
    columns, rows = shutil.get_terminal_size()
    return columns, rows

# Функция для отрисовки одной карты с использованием Panel, правильным цветом и центрированием
def draw_card(card_key, style="bold white", title=""):
    card_art = cards.get(card_key, '')
    suit = card_key[-1]

    suit_color = SUIT_COLORS.get(suit, "white")

    lines = card_art.split('\n')
    # Находим максимальную длину среди ВСЕХ строк
    max_line_len = max(len(line) for line in lines)

    centered_lines = []
    for i, line in enumerate(lines):
        if suit in line and any(c.isalpha() for c in line):  # Проверяем, есть ли буквы в строке с мастью
            # Центрируем строку с символом масти и буквой
            colored_suit = f"[{suit_color}]{SUIT_SYMBOLS.get(suit, suit)}[/{suit_color}]"
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
            colored_suit = f"[{suit_color}]{SUIT_SYMBOLS.get(suit, suit)}[/{suit_color}]"
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
    buttons = ["FOLD", "CHECK", "CALL", "RAISE"]

    # Создаем строки панелей для каждой кнопки
    panels = []
    for i, button in enumerate(buttons):
        if button == selected:
            # Активная кнопка: яркая рамка, подсветка и подчёркнутый текст
            panel = Panel(
                Text(button, style="bold underline white"),
                border_style="bright_white",
                padding=(1, 4),
                
            )
        else:
            # Неактивная кнопка: стандартная рамка и текст
            panel = Panel(
                Text(button, style="bold"),
                border_style="dim",
                padding=(1, 4),
            )
        panels.append(panel)

    # Располагаем кнопки с большим отступом между ними
    table = Table.grid(padding=(0, 2))
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

def draw_poker_table(game, selected_card_index, bet_amount, columns):
    # Верхняя линия: дилер
    dealer_info = f"👤 [bold yellow]Dealer[/]\n[blue]Chips: ∞[/]\n[green]Pot: ${game.pot}[/]"
    
    top_row = Table.grid(expand=True)
    top_row.add_column("center", justify="center")
    top_row.add_row(
        Panel(dealer_info, border_style="yellow", width=columns//4)
    )
    top_row = Align.center(top_row)
    
    # Линия ботов над столом
    bots_row = Table.grid(expand=True)
    bots_row.add_column("left", justify="center")
    bots_row.add_column("center", justify="center")
    bots_row.add_column("right", justify="center")

    # Получаем ботов, исключая игрока
    bot_players = [p for p in game.players if not p.is_human]

    
    # Добавляем информацию о ботах и их картах
    bot_info = []
    for i, bot in enumerate(bot_players):
        info = f"🤖 {bot.name}\n[green]Chips: ${bot.chips}[/]\n"
        if bot.folded:
            info += "[bold red]FOLDED[/]\n"
        elif bot.is_all_in:
            info += "[bold magenta]ALL IN[/]\n"
        else:
            info += f"[yellow]Bet: ${bot.current_bet}[/]\n"
        
        border_style = "green"
        if bot.is_active:
            border_style = "bold bright_white"  # Выделяем активного бота
        bot_info.append(Panel(info, border_style=border_style, width=columns//4))

    left_bot = Align.center(
        bot_info[0]
    )

    right_bot = Align.center(
        bot_info[1]
    )
    
    bots_row.add_row(left_bot, "", right_bot)
    bots_row = Align.center(bots_row)

    # Центральная зона для карт
    player = game.players[-1]  # Предполагаем, что игрок последний в списке
    player_cards = player.hand
    selected_card_key = player_cards[selected_card_index] if selected_card_index >= 0 and selected_card_index < len(player_cards) else None
    
    community_cards_table = draw_cards(game.community_cards, style="bold blue")
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
            title=f"Table Center (Bet: ${game.current_bet}, Round: {game.betting_round + 1})",
            title_align="center",
            border_style="bold magenta",
            width=columns//2,
            height=20,
        )
    )

    # Нижняя линия: игрок
    player_info = f"👤 [bold cyan]{player.name}[/]\n[blue]Chips: ${player.chips}[/]\n"
    if player.folded:
        player_info += "[bold red]FOLDED[/]\n"
    elif player.is_all_in:
        player_info += "[bold magenta]ALL IN[/]\n"
    else:
        player_info += f"[yellow]Bet: ${player.current_bet}[/]\n"
        
    border_style = "cyan"
    if player.is_active:
        border_style = "bold bright_white"  # Выделяем активного игрока

    player_row = Table.grid(expand=True)
    player_row.add_column("center", justify="center")
    player_row.add_row(
        Panel(player_info, border_style=border_style, width=columns//4)
    )
    player_row = Align.center(player_row)

    # Левая и правая боковые линии: боты
    left_bot_top = Align.center(
        bot_info[2],
        vertical="middle",
    )
    right_bot_top = Align.center(
        bot_info[3],
        vertical="middle",
    )

 # Объединение всех элементов
    middle_row = Table.grid(expand=True)
    middle_row.add_column("left", width=columns//4, justify="center")
    middle_row.add_column("center", justify="center")
    middle_row.add_column("right", width=columns//4, justify="center")
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
    game = PokerGame()
    game.read_game_state()

    buttons = ["FOLD", "CHECK", "CALL", "RAISE"]
    selected_index = 0  # Индекс выбранной кнопки
    bet_amount = 0  # Начальная ставка
    bet_increment = 10 # Шаг увеличения ставки
    last_up_pressed_time = 0
    last_down_pressed_time = 0

    # Игровые данные
    player = game.players[-1]
    selected_card_index = -1  # Индекс выбранной карты, -1 означает, что карта не выбрана

    
    # Live для обновления интерфейса в реальном времени
    with Live(console=console, refresh_per_second=20, screen=True) as live:
        while True:
            if not game.game_started:
                # Начало игры
                game.start_game()

            # Получаем размеры терминала
            columns, rows = get_terminal_size()

            # Создаем таблицу для размещения элементов
            main_table = Table.grid(expand=True)
            main_table.add_column(justify="center") # Одна колонка для всего контента
            main_table.add_column(width=10, justify="center") # Добавляем пустую колонку справа для отступа

            # Рисуем покерный стол
            table_layout = draw_poker_table(game, selected_card_index, bet_amount, columns)

            # Добавляем райзер ставки и кнопки внизу
            controls_table = Table.grid(padding=(1, 2), expand=False)
            controls_table.add_column(justify="center")
            controls_table.add_row(Align.center(draw_bet_raiser(bet_amount)))
            controls_table.add_row(Align.center(draw_buttons(selected=buttons[selected_index])))

            # Создаем таблицу для нижней части с контролами и выравниваем по низу
            bottom_table = Align(controls_table, vertical="bottom", height=rows//4)
            #bottom_table = Align.center(controls_table)

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

            # Определяем чей ход и подсвечиваем игрока
            for i, p in enumerate(game.players):
                p.is_active = (i == game.active_player_index)

            # Ход бота
            if not player.is_active:
                time.sleep(5)  # Задержка для имитации размышления бота
                # Тут должна быть логика принятия решения для бота
                # Временно бот случайно выбирает действие
                bot_action = random.choice(["CHECK", "CALL", "RAISE", "FOLD"])
                if bot_action == "RAISE":
                    max_raise = game.players[game.active_player_index].chips
                    bet_amount = random.randint(game.current_bet + game.big_blind, max_raise)
                    
                if bot_action == "FOLD" and game.players[game.active_player_index].current_bet < game.current_bet:
                    game.handle_player_action(bot_action)
                elif bot_action == "CHECK" and game.players[game.active_player_index].current_bet == game.current_bet:
                    game.handle_player_action(bot_action)
                elif bot_action == "CALL" and game.players[game.active_player_index].current_bet < game.current_bet:
                    game.handle_player_action(bot_action)
                elif bot_action == "RAISE":
                    game.handle_player_action(bot_action, bet_amount)
                else:
                    game.handle_player_action(bot_action)

                game.write_game_state()  # Записываем состояние после хода бота
                continue

             # Обработка ввода клавиш для игрока
            if is_pressed("left"):
                if selected_card_index == -1:
                    selected_index = (selected_index - 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index - 1) % len(player.hand)
                time.sleep(0.2)
            elif is_pressed("right"):
                if selected_card_index == -1:
                    selected_index = (selected_index + 1) % len(buttons)
                else:
                    selected_card_index = (selected_card_index + 1) % len(player.hand)
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

                    bet_amount = min(bet_amount + bet_increment, player.chips)
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
                    
                    if buttons[selected_index] == "RAISE":
                        console.print(f"[bold green]Ваша ставка: {bet_amount}[/bold green]", justify="center")
                        game.handle_player_action(buttons[selected_index], bet_amount)
                        bet_amount = 0
                    else:
                        game.handle_player_action(buttons[selected_index])
                    
                    selected_index = 0
                    game.write_game_state()
                else:
                     # Действие при выборе карты
                    console.print(f"[bold green]Вы выбрали карту: {player.hand[selected_card_index]}[/bold green]", justify="center")
                time.sleep(0.2)

if __name__ == "__main__":
    main()