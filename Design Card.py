# cards.py

cards = {
    "A♠": """
+-------+
|A      |
|       |
|   ♠   |
|       |
|      A|
+-------+
""",
    "2♠": """
+-------+
|2      |
|       |
|   ♠   |
|       |
|      2|
+-------+
""",
    "3♠": """
+-------+
|3      |
|       |
|   ♠   |
|       |
|      3|
+-------+
""",
    # ... остальные карты ...
    "K♣": """
+-------+
|K      |
|       |
|   ♣   |
|       |
|      K|
+-------+
"""
}

# Все масти и значения карт хранятся в словаре для удобного доступа.
# Для каждой карты используется ключ в формате "значение+масть", например: "A♠", "10♦", "Q♥", "K♣".

#

# main.py

from cards import cards

# Получить ASCII-арт карты, например "A♠"
card = "A♠"
print(cards[card])

# Вывести еще одну карту
card = "K♣"
print(cards[card])


#


# generate_cards.py
suits = {"♠": "Spades", "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs"}
values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

cards = {}

for suit in suits.keys():
    for value in values:
        key = f"{value}{suit}"
        cards[key] = f"""
+-------+
|{value:<2}     |
|       |
|   {suit}   |
|       |
|     {value:>2}|
+-------+
"""

# Сохранение в файл
with open("cards.py", "w") as file:
    file.write("# cards.py\n\n")
    file.write("cards = {\n")
    for card, art in cards.items():
        file.write(f'    "{card}": """{art.strip()}""",\n')
    file.write("}\n")
