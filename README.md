# Taco Bell Menu Discord Bot

## Requirements
- Install dependencies:
    pip install -r requirements.txt

## Setup and run
1. Initialize DB and seed sample data:
    python db_init.py

2. Run the API:
    python api.py

3. Open a new terminal and Run the bot:
    python bot.py

## TODO LIST
- Replace the sample menu items and specials with those from an actual taco bell API of some sort.

## Slash commands provided
- /menu [category]
- /item <item_name>
- /deals
- /order_add <item_name> [quantity]
- /order_view
- /order_checkout
- /feedback <message>

## Notes
- This is a fake bot prototype and does not process real payments or orders. Play around with it!
