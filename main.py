import telebot
from telebot import types

import tokens

bot = telebot.TeleBot(tokens.TOKEN)

user_dict = {}

class User:
    def __init__(self, name):
        self.name = name
        self.number = None
        self.employee = None
        self.date = None
        self.time = None

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Bonjour, je suis un robot. 
Quel est Votre nom et prenom?
""")
    bot.clear_step_handler(message)
    bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
    try:
        user_id = message.from_user.id
        user = User(message.text)
        msg = bot.reply_to(message, 'Quel est votre numéro de téléphone?')
        bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
    except Exception :
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_phone_step(message, user, user_id):
    try:
        number = message.text
        if not number.isdigit():
            msg = bot.reply_to(message, 'l numéro de téléphone doit être un nombre')
            bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
            return
        user.number = number
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Pedetour J.', 'Faraire S.')
        msg = bot.reply_to(message, 'Avec quel salarié souhaitez-vous vous inscrire ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_employee_step(message, user, user_id):
    try:
        employee = message.text.upper()
        if employee in ['FARAIRE S.', 'PEDETOUR J.']:
            user.employee = employee
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Oui', 'Non')
            msg = bot.send_message(message.chat.id, 'Les données sont-elles correctes ? ' + f'\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}', reply_markup=markup)
            bot.register_next_step_handler(msg, process_check_data, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_check_data(message, user, user_id):
    try:
        answer = message.text.lower()
        if answer == 'oui':
            bot.reply_to(message, 'Merci!')
            user.answer = answer
            bot.send_message(tokens.admChatId, f'{user.employee}, Nouvelle candidature reçue:\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}')
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_confirm = types.InlineKeyboardButton('Confirmer',callback_data=f'confirm_{user.name}_{user.number}_{user.employee}_{user_id}')
            btn_reject = types.InlineKeyboardButton('Rejeter', callback_data='reject')
            markup.add(btn_confirm, btn_reject)
            bot.send_message(tokens.admChatId, 'Confirmer ou rejeter la candidature ?', reply_markup=markup)
        elif answer == 'non':
            bot.reply_to(message, "Recommençons")
            send_welcome(message)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_check_data, user=user)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')
        print('error in check data')

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    user_id = call.from_user.id
    if call.data.startswith('confirm'):
        # callbackdata for parts
        _, name, age, employee, _ = call.data.split('_', 4)
        bot.send_message(user_id, 'Votre demande est confirmée!')
        confirmation_message = f'Candidat confirmé:\nNom: {name}\nNuméro de téléphone: {age}\nEmployé: {employee}'
        bot.send_message(tokens.admChatId, confirmation_message)
        print('button confirm pressed')
    elif call.data == 'reject':
        print('button reject pressed')
        bot.send_message(user_id, 'Votre demande est rejetée.')
        bot.send_message(tokens.admChatId, 'Candidat rejeté')





bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()