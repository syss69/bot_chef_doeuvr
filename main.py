import telebot
from telebot import types
import sqlite3


import tokens

bot = telebot.TeleBot(tokens.TOKEN)
admChatId = tokens.admChatId
database = 'pybot.db'

user_dict = {}
aDates = []
superpassword = "supermdp"
password = "mdp2024"
employers = []
atime = ['10-00', '11-00', '12-00', '12-45', '13-00', '14-00', '15-00', '16-00']

connection = sqlite3.connect("pybot.db", check_same_thread=False)
cursor = connection.cursor()
cursor.execute('SELECT date FROM Dates')
dates = cursor.fetchall()
for date in dates:
    aDates.append(date)
cursor.execute('SELECT Name FROM Users WHERE IsAdmin = 1')
noms = cursor.fetchall()
for nom in noms:
    employers.append(nom)
connection.close()
aDates = [date[0] for date in aDates]
employers = [nom[0] for nom in employers]


class User:  # Informations nécessaires pour faire une demande//Information needed to make a request
    def __init__(self, name):
        self.name = name
        self.number = None
        self.employee = None
        self.date = None
        self.time = None


@bot.message_handler(commands=['help', 'start'])
def ask_group(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Utilisateur', 'Administrateur')
    msg = bot.reply_to(message, "Pour obtenir une liste de commandes sélectionnez un groupe d'utilisateurs",
                       reply_markup=markup)
    bot.clear_step_handler(message)
    bot.register_next_step_handler(msg, send_help)


def send_help(message):
    answer = message.text
    if answer == 'Utilisateur':
        bot.reply_to(message, 'Сréer une demande /new')
    elif answer == 'Administrateur':
        msg = bot.reply_to(message, "Entrez le mot de passe administrateur")
        bot.register_next_step_handler(msg, send_admin)
    else:
        bot.send_message(message.chat.id, 'Je ne vous ai pas compris')
        bot.register_next_step_handler(message, send_help)


def send_admin(message):
    if message.text != password:
        bot.reply_to(message, "Le mot de passe est incorrect, opération annulée")
    else:
        bot.reply_to(message, """\
    Changer la date /date
Liste des rendez-vous /get
""")

@bot.message_handler(commands=['create'])
def open_superadmin(message):
    msg = bot.reply_to(message, "Entrez le mot de passe super administrateur")
    bot.clear_step_handler(message)
    bot.register_next_step_handler(msg, check_superpassword)


def check_superpassword(message):
    if message.text != password:
        bot.reply_to(message, "Le mot de passe est incorrect, opération annulée")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Oui', 'Non')
        msg = bot.reply_to(message, "Le mot de passe est correct, voulez-vous continuer?", reply_markup=markup)
        bot.register_next_step_handler(msg, create_employee)


def create_employee(message):
    answer = message.text.lower()
    if answer == "oui":
        msg = bot.reply_to(message, "Entrez le nom de nouveau salarie")
        bot.register_next_step_handler(msg, confirmation)


def confirmation(message):
    answer = message.text.upper()
    bot.reply_to(message,f"Le salarié {answer} était inscrit")
    con = sqlite3.connect(database, check_same_thread=False)
    cur = con.cursor()
    cur.execute(f"INSERT INTO Employe (Nom) VALUES ('{answer}')")
    con.commit()
    cur.close()
    con.close()
    employers.append(answer)



@bot.message_handler(commands=['date'])
def open_admin(message):
    msg = bot.reply_to(message, "Entrez le mot de passe super administrateur")
    bot.clear_step_handler(message)
    bot.register_next_step_handler(msg, check_password)


def check_password(message):
    if message.text != superpassword:
        bot.reply_to(message, "Le mot de passe est incorrect, opération annulée")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Oui', 'Non')
        msg = bot.reply_to(message, "Le mot de passe est correct, voulez-vous continuer?", reply_markup=markup)
        bot.register_next_step_handler(msg, change_date)


def change_date(message):
    chat_id = message.chat.id
    answer = message.text.lower()
    if answer == 'oui':
        aDates.clear()
        bot.send_message(chat_id, "Saisissez la date 1 (au format 'jour-mois', par exemple '12-02') :")
        bot.register_next_step_handler(message, enter_date)
    elif answer == 'non':
        bot.send_message(chat_id, "Opération annulée")
    else:
        bot.send_message(chat_id, 'Je ne vous ai pas compris')
        bot.register_next_step_handler(message, change_date)


def enter_date(message):
    chat_id = message.chat.id
    date = message.text.strip()
    aDates.append(date)
    if len(aDates) < 5:
        bot.send_message(chat_id, f"La date '{date}' a été enregistrée avec succès. Entrez la date {len(aDates) + 1}")
        bot.register_next_step_handler(message, enter_date)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        markup.add('Oui', 'Non')
        bot.send_message(chat_id, "Sauvegarder?", reply_markup=markup)
        bot.register_next_step_handler(message, save_date, aDates)


def save_date(message, aDates):
    chat_id = message.chat.id
    answer = message.text.lower()
    if answer == 'oui':
        con = sqlite3.connect(database, check_same_thread=False)
        cur = con.cursor()
        cur.execute(f"DELETE FROM Dates")
        cur.execute("DELETE FROM Сonfirmed")
        cur.execute("DELETE FROM Unsorted")
        i = 1
        for date in aDates:
            cur.execute(f"INSERT INTO Dates (id, date) VALUES('{i}', '{date}')")
            i += 1
        con.commit()
        bot.send_message(chat_id, "Succes")
        cur.close()
        con.close()
    else:
        bot.reply_to(message, 'Recommençons')
        change_date(message)


@bot.message_handler(commands=['get'])
def choose_employee(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(employers[0], employers[1])
    msg = bot.send_message(message.chat.id, "Sélectionnez un employé", reply_markup=markup)
    bot.register_next_step_handler(msg, choose_date)


def choose_date(message):
    employee = message.text
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add(aDates[0], aDates[1], aDates[2], aDates[3], aDates[4])
    msg = bot.send_message(message.chat.id, "Sélectionner une date", reply_markup=markup)
    bot.register_next_step_handler(msg, get_meets, employee)


def get_meets(message, employee):
    date = message.text
    con = sqlite3.connect(database, check_same_thread=False)
    cur = con.cursor()
    cur.execute(f"SELECT * FROM CONFIRMED WHERE Date = '{date}' AND Employee = '{employee}")
    meets = cur.fetchall()
    if meets:
        bot.send_message(message.chat.id, "Rendez-vous pour la date sélectionnée :")
        for meet in meets:
            time = meet[4]
            name = meet[1]
            number = meet[2]
            bot.send_message(message.chat.id, f"Temps: {time}, Nom: {name}\n Numero: {number}")
    else:
        bot.send_message(message.chat.id, "Il n'y a aucun rendez-vous pour la date sélectionnée.")
    cur.close()
    con.close()


@bot.message_handler(commands=['new'])
def send_welcome(message):
    msg = bot.reply_to(message, """\
Bonjour, je suis un robot. 
Quel est Votre nom et prenom?
""")
    bot.clear_step_handler(message)
    bot.register_next_step_handler(msg, process_name_step)


def process_name_step(message):  # Toutes les fonctions fonctionnent de la même manière : gérer la réponse de l'utilisateur et envoyer la question suivante//All functions works at same way: handle user responce and send next question
    try:
        user_id = message.from_user.id
        user = User(message.text)
        user.user_id = user_id
        msg = bot.reply_to(message, 'Entrez votre numéro en commençant par zéro')
        bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /new pour recommencer')


def process_phone_step(message, user, user_id):
    try:
        number = message.text
        if not number.isdigit() or len(
                number) != 10:  # vérifiez si le numéro est réel et non une chaîne comme 'asfjz5423'//check if numer is real and not a string like 'asfjz5423'
            msg = bot.reply_to(message, 'Le numéro doit être composé de dix chiffres')
            bot.register_next_step_handler(msg, process_phone_step, user=user, user_id=user_id)
            return
        user.number = number
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        for employer in employers:
            markup.add(employer)
        msg = bot.reply_to(message, 'Avec quel salarié souhaitez-vous vous inscrire ?', reply_markup=markup)
        bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /new pour recommencer')


def process_employee_step(message, user, user_id):
    try:
        employee = message.text
        if employee in employers:
            user.employee = employee
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(aDates[0], aDates[1], aDates[2], aDates[3], aDates[4])
            msg = bot.send_message(message.chat.id, 'Sélectionner une date', reply_markup=markup)
            bot.register_next_step_handler(msg, process_date_step, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'Cette personne n existe pas')
            bot.register_next_step_handler(msg, process_employee_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /new pour recommencer')


def process_date_step(message, user, user_id):
    try:
        date = message.text
        if date in aDates:  # pareil, il sera retravaillé//same, it will be reworked
            user.date = date
            types.ReplyKeyboardRemove(selective=False)
            markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
            markup.add(*atime)
            msg = bot.send_message(message.chat.id, "Préciser l'heure", reply_markup=markup)
            bot.register_next_step_handler(msg, process_time_step, user=user, user_id=user_id)
        else:
            msg = bot.reply_to(message, 'la date choisie n est pas disponible')
            bot.register_next_step_handler(msg, process_date_step, user=user, user_id=user_id)
    except Exception:
        bot.reply_to(message, 'Erreur! Utilisez /new pour recommencer')


def process_time_step(message, user, user_id):
        time = message.text
        if time in atime:
            con = sqlite3.connect(database)
            cur = con.cursor()
            cur.execute(f"SELECT * FROM Сonfirmed WHERE Date = '{user.date}' AND Temps = '{time}' AND Employee = '{user.employee}'")
            user.time = time
            if cur.fetchone():
                msg = bot.reply_to(message, "Malheureusement, cette heure est déjà prise, veuillez en sélectionner une autre.")
                bot.register_next_step_handler(msg, process_time_step, user=user, user_id=user_id)
            elif cur.fetchall() == 8:
                msg = bot.reply_to(message,"Malheureusement, tous les créneaux horaires pour cette journée sont déjà pris. Veuillez choisir une autre date.")
                bot.register_next_step_handler(msg, process_date_step, user=user, user_id=user_id)
            else:
                types.ReplyKeyboardRemove(selective=False)
                markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
                markup.add('Oui', 'Non')
                msg = bot.send_message(message.chat.id,
                                       'Les données sont-elles correctes ? ' + f'\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}\nDate: {user.date}\nTemps: {user.time} ',
                                       reply_markup=markup)
                bot.register_next_step_handler(msg, process_check_data, user=user, user_id=user_id)
            cur.close()
            con.close()
        else:
            msg = bot.reply_to(message, 'Date incorrecte, réessayez')
            bot.register_next_step_handler(msg, process_time_step, user=user, user_id=user_id)


def process_check_data(message, user, user_id):
        answer = message.text.lower()
        if answer == 'oui':
            try:
                con = sqlite3.connect(database)
                cur = con.cursor()
                cur.execute(f"INSERT INTO Unsorted (Nom, Numero, Salarie, Date, Temps, user_id) VALUES (?,?,?,?,?,?);", (user.name, user.number, user.employee, user.date, user.time, user_id))
                con.commit()
                cur.close()
                con.close()
                bot.reply_to(message, 'Merci, vous recevrez une réponse sous peu')
                bot.send_message(admChatId,
                                 f'{user.employee}, Nouvelle candidature reçue:\nNom: {user.name}\nNuméro de téléphone: {user.number}\nEmployé: {user.employee}\nDate: {user.date}\nTemps: {user.time} ')
                markup = types.InlineKeyboardMarkup(row_width=2)
                btn_confirm = types.InlineKeyboardButton('Confirmer',
                                                         callback_data=f'confirm_{user.name}_{user.number}_{user.employee}_{user.date}_{user.time}_{user_id}')
                btn_reject = types.InlineKeyboardButton('Rejeter',
                                                        callback_data=f'reject_{user.name}_{user.number}_{user.employee}_{user.date}_{user.time}_{user_id}')
                markup.add(btn_confirm, btn_reject)
                askAdmMsg = ('Confirmer ou rejeter la candidature ?')
                bot.send_message(admChatId, askAdmMsg, reply_markup=markup)
            except Exception:
                bot.reply_to(message, "Erreur evec API. Merci de réitérer votre demande")
        elif answer == 'non':
            bot.reply_to(message, "Recommençons")
            send_welcome(message)
        else:
            msg = bot.reply_to(message, 'Je ne vous ai pas compris, merci de réitérer votre demande')
            bot.register_next_step_handler(msg, process_check_data, user=user)



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    _, name, number, employee, date, time, user_id = call.data.split('_')
    user_id = int(user_id)
    if call.data.startswith('confirm'):
        bot.send_message(user_id, f'Votre demande est confirmée!\nEmployé: {employee}\nDate: {date}\nTemps: {time}')
        confirmation_message = (
            f'Candidat confirmé:\nNom: {name}\nNuméro de téléphone: {number}\nEmployé: {employee}\nDate: {date}\nTemps: {time}')
        bot.send_message(admChatId, confirmation_message)
        bot.delete_message(admChatId, call.message.message_id)
        con = sqlite3.connect(database, check_same_thread=False)
        cur = con.cursor()
        cur.execute(f"INSERT INTO Сonfirmed (Employee, Nom, Numero, Date, Temps, user_id) VALUES (?,?,?,?,?,?)", (employee, name, number, date, time, user_id))
        con.commit()
        cur.close()
        con.close()
    elif call.data.startswith('reject'):
        bot.send_message(user_id, f'Votre demande:\nEmployé: {employee}\nDate: {date}\nTemps: {time}\nest rejetée.')
        bot.send_message(admChatId, f'Candidat {name} rejeté')
        bot.delete_message(admChatId, call.message.message_id)
    con = sqlite3.connect(database, check_same_thread=False)
    cur = con.cursor()
    cur.execute(f"DELETE FROM Unsorted WHERE (Salarie, Nom, Numero, Date, Temps) = ('{employee}', '{name}', '{number}', '{date}', '{time}')")
    con.commit()
    cur.close()
    con.close()


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()