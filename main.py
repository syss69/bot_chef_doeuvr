import telebot
from telebot import types

import tokens

bot = telebot.TeleBot(tokens.TOKEN)
admChatId = (tokens.admChatId)

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
        user.user_id = user_id
        msg = bot.reply_to(message, 'Entrez votre numéro en commençant par zéro')
        bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
    except Exception :
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_phone_step(message, user, user_id):
    try:
        number = message.text
        if not number.isdigit() or len(number) != 10:
            msg = bot.reply_to(message, 'Le numéro doit être composé de dix chiffres')
            bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
            return
        user.number = number
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Pedeutour J.', 'Faraire S.')
        msg = bot.reply_to(message, 'Avec quel salarié souhaitez-vous vous inscrire ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_employee_step(message, user, user_id):
    try:
        employee = message.text.upper()
        if employee in ['FARAIRE S.', 'PEDEUTOUR J.']:
            user.employee = employee
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('08/01','09/01','10/01','11/01','12/01')
            msg = bot.send_message(message.chat.id, 'Sélectionner une date', reply_markup=markup)
            bot.register_next_step_handler(msg, process_date_step, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_date_step(message, user, user_id):
    try:
        date = message.text
        if date in ['08/01','09/01','10/01','11/01','12/01']:
            user.date = date
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('10-00','11-00','12-00','12-45','13-00','14-00','15-00','16-00')
            msg = bot.send_message(message.chat.id, "Préciser l'heure", reply_markup=markup)
            bot.register_next_step_handler(msg, process_time_step, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_date_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')


def process_time_step(message, user, user_id):
    try:
        time = message.text
        if time in ['10-00','11-00','12-00','12-45','13-00','14-00','15-00','16-00']:
            user.time = time
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            markup.add('Oui', 'Non')
            msg = bot.send_message(message.chat.id,'Les données sont-elles correctes ? ' + f'\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}\nDate: {user.date}\nTemps: {user.time} ', reply_markup=markup)
            bot.register_next_step_handler(msg, process_check_data, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_time_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /start pour recommencer')

def process_check_data(message, user, user_id):
    try:
        answer = message.text.lower()
        if answer == 'oui':
            bot.reply_to(message, 'Merci!')
            user.answer = answer
            bot.send_message(admChatId, f'{user.employee}, Nouvelle candidature reçue:\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}\nDate: {user.date}\nTemps: {user.time} ')
            markup = types.InlineKeyboardMarkup(row_width=2)
            btn_confirm = types.InlineKeyboardButton('Confirmer', callback_data=f'confirm_{user.name}_{user.number}_{user.employee}_{user.date}_{user.time}_{user_id}')
            btn_reject = types.InlineKeyboardButton('Rejeter', callback_data=f'reject_{user.name}_{user.number}_{user.employee}_{user.date}_{user.time}_{user_id}')
            markup.add(btn_confirm, btn_reject)
            askAdmMsg = ('Confirmer ou rejeter la candidature ?')
            bot.send_message(admChatId, askAdmMsg, reply_markup=markup)
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
    _, name, number, employee, date, time, _ = call.data.split('_')
    if call.data.startswith('confirm'):
        bot.send_message(user_id, f'Votre demande est confirmée!\nEmployé: {employee}\nDate: {date}\nTemps: {time}')
        confirmation_message = (f'Candidat confirmé:\nNom: {name}\nNuméro de téléphone: {number}\nEmployé: {employee}\nDate: {date}\nTemps: {time}')
        bot.send_message(admChatId, confirmation_message)
        bot.delete_message(admChatId, call.message.message_id)
        print('button confirm pressed')
    elif call.data.startswith('reject'):
        bot.send_message(user_id, f'Votre demande:\nEmployé: {employee}\nDate: {date}\nTemps: {time}\nest rejetée.')
        bot.send_message(admChatId, f'Candidat {name} rejeté')
        bot.delete_message(admChatId, call.message.message_id)
        print('button reject pressed')





bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()