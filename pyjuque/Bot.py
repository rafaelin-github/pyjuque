import time
from os import getenv
from yaspin import yaspin
from pyjuque.Engine.Models.BotModels import TABotModel, GridBotModel, getSession
from pyjuque.Engine.Database import InitializeDatabaseTaBot, InitializeDatabaseGridBot
from pyjuque.Engine.BotController import BotController
from pyjuque.Engine.GridBotController import GridBotController
from pyjuque.Exchanges.CcxtExchange import CcxtExchange 
from pprint import pprint 
import functools
# bot_config = {
#     'db_url' : 'sqlite:///my_first_strategy.db',
#     'name' : 'bot1',
#     'type' : 'ta', # 'grid' or 'ta'
#     'exchange' : {
#         'name' : 'binance',
#         'params' : {
#             'api_key': '...',
#             'secret' : '...'
#         },
#     },
#     'symbols' : [],
#     'starting_balance' : 0.0005,
#     'quote_asset': 'BTC',
#     'entry_strategy': {
#         'name': 'BBRSIStrategy',
#         'function' : None,
#         'params': {
#             'rsi_len' : 8,
#             'bb_len' : 100,
#             'rsi_ob' : 50,
#             'rsi_os' : 50
#         }
#     },
#     'entry_settings' : {
#         'initial_entry_allocation': 20,
#         'signal_distance': 0.3
#     },
#     'exit_strategy' : None,
#     'exit_settings' : {
#         'take_profit' : 3,
#         'stop_loss_value': 10
#     },
#     'use_logger' : True,
#     'display_status' : True
# }

def defineBot(bot_config):
    for key in ['db_url', 'name', 'symbols', 'exchange', 'type']:
        assert key in bot_config.keys(), '{} should be inside the config object'.format(key)
    for key in ['name', 'params']:
        assert key in bot_config['exchange'].keys(), '{} should be inside the exchange config object'.format(key)
    
    bot_type = bot_config['type']
    
    assert bot_type == 'ta', 'can only have \'ta\' as the bot\'s type for now' 

    bot_controller = _defineTaBot(bot_config)
    
    return bot_controller

def _defineTaBot(bot_config):
    session = getSession(bot_config['db_url'])
    bot_name = bot_config['name']
    exchange_name = bot_config['exchange']['name']
    exchange_params = bot_config['exchange']['params']
    exchange = CcxtExchange(exchange_name, exchange_params)
    symbols = bot_config['symbols']
    bot_model = session.query(TABotModel).filter_by(name=bot_name).first()
    
    if bot_model is None:
        print('No bot found by name: {}. Creating...'.format(bot_name))
        InitializeDatabaseTaBot(session, bot_config)
        return _defineTaBot(bot_config)

    print('Bot model before init bot_controller', bot_model)
    bot_controller = BotController(session, bot_model, exchange, None)
    if bot_config.__contains__('display_status'):
        if bot_config['display_status']:
            status_printer = yaspin()
            bot_controller.status_printer = status_printer
    
    if bot_config.__contains__('strategy'):
        found = False
        if bot_config['strategy'].__contains__('custom'):
            if bot_config['strategy']['custom'] == True:
                found = True
                def nothing(self, symbol): return False, None
                entry_function = nothing
                exit_function = nothing
                if bot_config['strategy'].__contains__('entry_function'):
                    if bot_config['strategy']['entry_function'] not in [None, False]:
                        entry_function = bot_config['strategy']['entry_function']
                if bot_config['strategy'].__contains__('exit_function'):
                    if bot_config['strategy']['exit_function'] not in [None, False]:
                        exit_function = bot_config['strategy']['exit_function']

            bot_controller.checkEntryStrategy = functools.partial(entry_function, bot_controller)
            bot_controller.checkExitStrategy = functools.partial(exit_function, bot_controller)

        if not found and bot_config['strategy'].__contains__('function'):
            bot_controller.strategy = bot_config['strategy']['function'](**bot_config['strategy']['params'])
    
    return bot_controller

# def Main():

#     for key in ['db_url', 'name', 'symbols', 'exchange', 'type']:
#         assert key in bot_config.keys(), '{} should be inside the config object'.format(key)
#     for key in ['name', 'params']:
#         assert key in bot_config['exchange'].keys(), '{} should be inside the exchange config object'.format(key)
    
#     session = getSession(bot_config['db_url'])
#     bot_name = bot_config['name']
#     exchange_name = bot_config['exchange']['name']
#     exchange_params = bot_config['exchange']['params']
#     exchange = CcxtExchange(exchange_name, exchange_params)
#     symbols = bot_config['symbols']
#     bot_type = bot_config['type']

#     bot_model = session.query(Bot).filter_by(name=bot_name).first()
#     if bot_model is None:
#         print('No bot found by name: {}. Creating...'.format(bot_name))
#         if bot_type == 'ta':
#             InitializeDatabaseTaBot(session, bot_config)
#         elif bot_ta == 'grid':
#             InitializeDatabaseGridBot(session, bot_config)
#         Main()

#     strategy = None
#     if bot_config.__contains__('entry_strategy'):
#         if bot_config.__contains__('function'):
#             strategy = bot_config['entry_strategy']['function'](**bot_config['entry_strategy']['params'])

#     bot_controller = None
#     if bot_type == 'ta':
#         bot_controller = BotController(session, bot_model, exchange, strategy)
#     elif bot_type == 'grid':
#         bot_controller = GridBotController(name)
#         bot.create(exchange, symbols[0], total_amount, trade_amount, trade_step, total_trades)

#     if bot_config.__contains__('display_status'):
#         if bot_config['display_status']:
#             status_printer = yaspin()
#             bot_controller.status_printer = status_printer

#     while True:
#         try:
#             bot_controller.executeBot()
#         except KeyboardInterrupt:
#             return
#         bot_controller.status_printer.start()
#         left_to_sleep = bot_config['sleep']
#         while left_to_sleep > 0:
#             if bot_controller.status_printer != None:
#                 open_orders = bot_controller.bot_model.getOpenOrders(bot_controller.session)
#                 bot_controller.status_printer.text = 'Open Orders: {} | Checking signals in {} |'.format(
#                     len(open_orders), 
#                     left_to_sleep)
#             time.sleep(1)
#             left_to_sleep -= 1

# if __name__ == '__main__':
#     Main()