
dev = True

retries = 20
timeout_at_too_many_requests = 0.5
normal_timeout = 0.15
#could try to set this to 3 if checkout errors because of too fast checkouts occur
checkout_delay = 0

class Product:
    def __init__(self, type, keywords, amount):
        self.type = type.lower()
        self.keywords = keywords
        self.amount = amount

    def __repr__(self):
        return self.type + " " + str(self.keywords) + " " + str(self.amount)

products = [
    Product("jacket", [ " " ], 1 ),
    Product("bag", [ " " ], 1 ),
    Product("sweatshirt", [ " " ], 1 ),
]

keys = {
    "name": "John Fisher",
    "email": "email@gmail.com",
    "phone": "6789998212",
    "address": "Forest Hills Dr.",
    "city": "Timbuktu",
    "zip": "91601",
    "country": 14,   # is Germany

    "card_cvv": "666",
    "card_number": "5168441223630339 ",
    "exp_month": 12,
    "exp_year": 1,   # 1 is 2020, 10 2030 -> select accoardingly
    "card_type": 3,  # 1: Visa, 2: American Express, 3: Mastercard, 4: Solo, 5: PayPal
}