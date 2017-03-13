import telebot
import config
from datetime import *
import pymysql
from telebot import types

# 1. Иниализация

# 1.1. Иниализация бота
bot = telebot.TeleBot(config.token)
quest_dict = {}
team_dict = {}
admin_quest = {}

# 1.2. Извлечение паролей из config.py
password = config.password
admin = config.admin

# 2. Смайлики и прочие константы

# 2.1. Юзерские константы
robosmile = 'Квесты ' + chr(0x1F916)
smilepodmig = 'Контакты ' + chr(0x1F609)
smiletrophy = 'Достижения ' + chr(0x1F3C6)
smileclock = 'Расписание ' + chr(0x1F557)
smilereg = 'Регистрация ' + chr(0x1F4DD)
smilemerop = 'Что сейчас? ' + chr(0x1F514)
smilephone = 'Телефоны ' + chr(0x1F4DE)
smilehome = 'Где я живу? ' + chr(0x1F3E0)

# 2.2. Админские константы
robosmileadmin = 'Создание Квеста ' + chr(0x1F916)
smileclockadmin = 'Задать Расписание ' + chr(0x1F557)
smilemeropadmin = 'Срочное Сообщение ' + chr(0x1F514)
smiletrophyadmin = 'Добавить Достижение ' + chr(0x1F3C6)
smileaddcontacts = 'Добавить Контакт ' + chr(0x1F609)
smileaddhome = 'Место проживания ' + chr(0x1F3E0)

# 3. Визуальные клавиатуры

hide = types.ReplyKeyboardHide()

# 3.1. Интерфейс меню регистрации
markup = types.ReplyKeyboardMarkup()
item = types.KeyboardButton(smilereg)
markup.row(item)

# 3.2. Юзерский интерфейс
markup2 = types.ReplyKeyboardMarkup()
item2 = types.KeyboardButton(smileclock)
item3 = types.KeyboardButton(smiletrophy)
item4 = types.KeyboardButton(robosmile)
item5 = types.KeyboardButton(smilepodmig)
item11 = types.KeyboardButton(smilemerop)
markup2.row(item2, item11)
markup2.row(item3, item4)
markup2.row(item5)

# 3.3. Интерфейс админки
markup3 = types.ReplyKeyboardMarkup()
item6 = types.KeyboardButton(smileclockadmin)
item9 = types.KeyboardButton(smilemeropadmin)
item7 = types.KeyboardButton(smiletrophyadmin)
item8 = types.KeyboardButton(robosmileadmin)
item10 = types.KeyboardButton(smileaddcontacts)
item12 = types.KeyboardButton(smileaddhome)
markup3.row(item6, item9)
markup3.row(item7, item8)
markup3.row(item10, item12)

# 3.4. Интерфейс кветса
markup4 = types.InlineKeyboardMarkup()
nextq = types.InlineKeyboardButton(text='Следующий вопрос!', callback_data='next')
ext = types.InlineKeyboardButton(text='Выход!', callback_data='ext')
markup4.add(nextq, ext)

# 3.5. Интерфейс контактов
markup5 = types.ReplyKeyboardMarkup()
phones = types.KeyboardButton(smilephone)
home = types.KeyboardButton(smilehome)
markup5.row(phones, home)


# 4. Основной код

# 4.1. Функция проверки на наличие регистрации для автоматического входа при перезагрузке\краше бота

# 4.1.1. Проверка пользователей
def ifreg(chatid):
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT Name FROM main WHERE ChatID=" + str(chatid) + ";")
    out = ""
    for row in cur:
        out += str(row)
    cur.close()
    conn.close()
    if out == '':
        return True
    else:
        return False


# 4.1.2. Проверка админов
def ifregadmin(chatid):
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT Status FROM admin WHERE ChatID=" + str(chatid) + ";")
    out = ""
    for row in cur:
        out += str(row)
    cur.close()
    conn.close()
    if out == '':
        return False
    else:
        return True


# 4.2. Основной код админской части

# 4.2.1. Рассылка
def rassilka(message):
    out = "Срочная рассылка: \n"
    out += message.text
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT ChatID FROM main;")
    for row in cur:
        chatid = str(row[0])
        bot.send_message(int(chatid), out)
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Сообщение успешно разосланно!', reply_markup=markup3)


# 4.2.2. Добавление мероприятия
def addevent(message):
    msg = message.text.split('\n')
    for data in msg:
        sthour = stminute = finhour = finminute = 0
        do = True
        data = data.split(" : ")
        if len(data) == 2:
            name = data[0]
            data = data[1]
            data = data.split(' ')
            if len(data) == 6:
                try:
                    year = datetime.now().year
                    month = int(data[0])
                    day = int(data[1])
                    sthour = int(data[2])
                    stminute = int(data[3])
                    finhour = int(data[4])
                    finminute = int(data[5])
                    d = date(year, month, day)
                except ValueError:
                    do = False
                    bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=markup3)
                if do:
                    t1 = time(sthour, stminute)
                    t2 = time(finhour, finminute)
                    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                           charset='utf8mb4')
                    cur = conn.cursor()
                    cur.execute("INSERT INTO timetable (Event, Date, Start, Finish) VALUES('" + name + "', '" + str(
                        d) + "', '" + str(t1) + "', '" + str(t2) + "');")
                    conn.commit()
                    cur.close()
                    bot.send_message(message.chat.id, 'Мероприятие успешно добавленно!', reply_markup=markup3)
            else:
                bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=markup3)
        else:
            bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=markup3)


# 4.2.3. Добавление достижений
def addtrophy(message):
    chatid = ''
    msg = message.text.split('\n')
    for data in msg:
        data = data.split(' : ')
        if len(data) == 2:
            name = data[0]
            trophy = data[1]
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("SELECT ChatID FROM main WHERE name='" + name + "';")
            for row in cur:
                chatid = row
            if chatid == '':
                bot.send_message(message.chat.id, 'Не удалось найти пользователя! Проверьте формат ввода.',
                                 reply_markup=markup3)
                cur.close()
                conn.close()
            else:
                chatid = int(chatid[0])
                cur.execute("INSERT INTO trophy (ChatID, Achiev) VALUES (" + str(chatid) + ", '" + trophy + "');")
                conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id, 'Достижение успешно добавлено!', reply_markup=markup3)
                bot.send_message(chatid, 'Вы получили достижение: ' + trophy)
        else:
            bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=markup3)


# 4.2.4. Создание Квеста

# 4.2.4.1. Создание ключей (паролей) команд
def addkey(message):
    msg = message.text.split('\n')
    for data in msg:
        if data == 'Готово!':
            bot.send_message(message.chat.id, 'Квест успешно создан!', reply_markup=markup3)
        elif len(data.split(' ')) < 2:
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("ALTER TABLE " + admin_quest[message.chat.id] + " ADD " + data + " TINYINT DEFAULT 2;")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Ключ добавлен!')
            bot.register_next_step_handler(message, addkey)
        else:
            bot.send_message(message.chat.id, 'Ключ не должен содержать пробелов! Попробуйте еще раз.')
            bot.register_next_step_handler(message, addkey)


# 4.2.4.2. Создание вопросов и ответов
def addquestions(message):
    if message.text == 'Готово!':
        bot.send_message(message.chat.id, 'Теперь добавьте ключи команд. Для каждый команды, участвующей в конкурсе '
                                          'придумайте собственный идентификатор, состоящий из одного слова. '
                                          'Вы можете отправить несколько идентификаторов в одном сообщении, '
                                          'начиная каждый последующий с новой строки. '
                                          'Когда закончите, отправьте "Готово!"')
        bot.register_next_step_handler(message, addkey)
    else:
        msg = message.text.split('\n')
        for data in msg:
            try:
                data = data.split(' : ')
                question = data[0]
                answer = data[1]
            except IndexError:
                bot.send_message(message.chat.id, 'Неверный формат вопроса. Введите вопрос еще раз.')
            else:
                conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                       charset='utf8mb4')
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO " + admin_quest[
                        message.chat.id] + " (Question, Answer) VALUES ('" + question + "', '" + answer + "');")
                conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id, 'Вопрос добавлен!')
            bot.register_next_step_handler(message, addquestions)


# 4.2.4.3. Иниализация нового квеста
def newquest(message):
    if len(message.text.split(' ')) > 1:
        bot.send_message(message.chat.id, 'Неправильный формат ввода! Не используйте пробелы.', reply_markup=markup3)
    else:
        questname = 'quest_' + message.text
        try:
            admin_quest.update({message.chat.id: questname})
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE " + questname + " (Question VARCHAR(255) NOT NULL, Answer VARCHAR(255) NOT NULL ) "
                                              "ENGINE=InnoDB;")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Далее введите вопросы и ответы квеста в формате: "Вопрос : Ответ". \n '
                                              'Пример: '
                                              '\n "Продолжите фразу - программисты не рождаются, программисты... : '
                                              'Наследуются"\n Вы можете отправить несколько вопросов в одном сообще'
                                              'нии, начиная каждую новую пару с новой строки. '
                                              'Когда закончите, отправьте "Готово!"')
            bot.register_next_step_handler(message, addquestions)
        except pymysql.err.InternalError:
            bot.send_message(message.chat.id, 'Такой квест уже существует.', reply_markup=markup3)


# 4.2.5. Добавление контактов
def addcontact(message):
    msg = message.text.split('\n')
    for data in msg:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO contacts (contact) VALUES ('" + data + "');")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Контакт добавлен!', reply_markup=markup3)


# 4.2.6 Добавление места жительства
def addhome(message):
    chatid = ''
    msg = message.text.split('\n')
    for data in msg:
        data = data.split(' : ')
        if len(data) == 2:
            name = data[0]
            home1 = data[1]
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("SELECT ChatID FROM main WHERE name='" + name + "';")
            for row in cur:
                chatid = row
            if chatid == '':
                bot.send_message(message.chat.id, 'Не удалось найти пользователя! Проверьте формат ввода.',
                                 reply_markup=markup3)
                cur.close()
                conn.close()
            else:
                chatid = int(chatid[0])
                cur.execute("UPDATE main SET Home='" + home1 + "' WHERE ChatID=" + str(chatid) + ";")
                conn.commit()
                cur.close()
                conn.close()
                bot.send_message(message.chat.id, 'Место проживания успешно обновлено.',
                                 reply_markup=markup3)
        else:
            bot.send_message(message.chat.id, 'Неправильный формат ввода!', reply_markup=markup3)


# 4.2.7. Интерфейс админской части
def adminlog(message):
    if message.text == smilemeropadmin:
        bot.send_message(message.chat.id, 'Введите сообщение для рассылки:', reply_markup=hide)
        bot.register_next_step_handler(message, rassilka)

    elif message.text == smiletrophyadmin:
        bot.send_message(message.chat.id, 'Введите получателя достижения, а затем наименование достижения в формате: \n'
                                          'Полное_Имя Фамилия : Название и описание достижения \n Пример: \n'
                                          '"Василий Пупкин : Костыли - наше Всё"\n'
                                          'Вы можете ввести несколько пар в одном сообщении, начиная каждую'
                                          ' с новой строки.', reply_markup=hide)
        bot.register_next_step_handler(message, addtrophy)

    elif message.text == smileclockadmin:
        bot.send_message(message.chat.id,
                         'Введите информацию о мероприятии в формате: \n "Название и описание : Месяц День'
                         ' Часы_Начала Минуты_Начала Часы_Конца Минуты_Конца" \n Пример: \n "Самый важный'
                         ' сбор : 3 8 12 15 12 30"\n'
                         'Вы можете ввести несколько меорпиятий в одном сообщении'
                         ', начиная ввод каждого с новой строки.', reply_markup=hide)
        bot.register_next_step_handler(message, addevent)

    elif message.text == robosmileadmin:
        bot.send_message(message.chat.id, 'Введите и запомните идентификатор квеста. Он должен состоять '
                                          'из одного слова.', reply_markup=hide)
        bot.register_next_step_handler(message, newquest)

    elif message.text == smileaddcontacts:
        bot.send_message(message.chat.id, 'Введите свои контакты в удобной для вас форме. Не более 255 символов.'
                                          ' \n Пример: \n'
                                          'Василий Пупкин - пионер 1 отряда, +7-999-999-99-99 \n'
                                          'Вы можете ввести несколько контактов в одном сообщении,'
                                          ' начиная каждый с новой строки.', reply_markup=hide)
        bot.register_next_step_handler(message, addcontact)

    elif message.text == smileaddhome:
        bot.send_message(message.chat.id, 'Введите место проживания пионера в формате: \n'
                                          'Полное_Имя Фамилия : Место жительства \n'
                                          'Пример: \n'
                                          'Василий Пупкин : Главный корпус, комната 209 \n'
                                          'Вы можете ввести несколько пар в одном сообщении, начиная каждую'
                                          'пару с новой строки.', reply_markup=hide)
        bot.register_next_step_handler(message, addhome)

    elif message.text == 'Я тут?':
        bot.send_message(message.chat.id, 'Вы в админке')


# 4.3. Основной код пользовательской части

# 4.3.1. Прохождение квеста
def playquest(message):
    if message.content_type == 'text' and not (
                                    message.text == robosmile or message.text == smilepodmig or message.text == smiletrophy or message.text == smileclock or message.text == smilereg or message.text == smilemerop):
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT " + team_dict[message.chat.id] + " FROM " + quest_dict[
            message.chat.id] + " WHERE Answer='" + message.text + "';")
        out = ''
        for row in cur:
            out += str(row[0])
            break
        cur.close()
        conn.close()
        if out == '':
            bot.send_message(message.chat.id, "Неправильный ответ на вопрос!", reply_markup=markup4)
            bot.register_next_step_handler(message, playquest)
        else:
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("UPDATE " + quest_dict[message.chat.id] + " SET " + team_dict[message.chat.id] + "=1 WHERE " +
                        team_dict[message.chat.id] + "=2 AND Answer='" + message.text + "';")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Ответ верный. Браво!", reply_markup=markup4)
            bot.register_next_step_handler(message, playquest)


def continuequest(message):
    teamid = message.text
    if message.text == '2':
        bot.send_message(message.chat.id, 'Неправильный ключ квеста\команды!', reply_markup=markup2)
    else:
        team_dict.update({message.chat.id: teamid})
        try:
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute(
                "SELECT Question FROM " + quest_dict[message.chat.id] + " WHERE " + team_dict[message.chat.id] + "=2;")
            out = ''
            for row in cur:
                out += str(row[0])
                break
            if out == '':
                bot.send_message(message.chat.id, 'Квест был пройден ранее!', reply_markup=markup2)
            else:
                bot.send_message(message.chat.id,
                                 'Для начала и для получения последующих вопросов, нажмите "Следующий вопрос!". '
                                 'Для выхода, нажмите "Выход!".',
                                 reply_markup=markup4)
            bot.register_next_step_handler(message, playquest)
        except pymysql.err.ProgrammingError:
            bot.send_message(message.chat.id, 'Неправильный ключ квеста\команды!', reply_markup=markup2)
        except pymysql.err.InternalError:
            bot.send_message(message.chat.id, 'Неправильный ключ квеста\команды!', reply_markup=markup2)


def startquest(message):
    questid = "quest_" + message.text
    quest_dict.update({message.chat.id: questid})
    bot.send_message(message.chat.id, 'Введите идентификатор команды.')
    bot.register_next_step_handler(message, continuequest)


# 4.3.6. Интерфейс пользовательской части
def userlog(message):
    if message.text == smiletrophy:
        out = "Список ваших достижений: \n"
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT Achiev FROM trophy WHERE ChatID=" + str(message.chat.id) + ";")
        for row in cur:
            out += row[0] + "\n"
        if out == "Список ваших достижений: \n":
            bot.send_message(message.chat.id, 'У вас пока нет достижений!')
        else:
            bot.send_message(message.chat.id, out)

    elif message.text == smilemerop:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT Event FROM timetable WHERE Active=1;")
        out = ''
        for row in cur:
            out += str(row[0])
            out += '\n'
        cur.close()
        conn.close()
        if out == '\n':
            bot.send_message(message.chat.id, 'На данный момент нет активных мероприятий.')
        else:
            bot.send_message(message.chat.id, 'Сейчас проходят мероприятия: \n'+out)

    elif message.text == smileclock:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT Start, Event FROM timetable WHERE Date=CURRENT_DATE() ORDER BY Start;")
        out = 'Мероприятия на сегодня: \n'
        for row in cur:
            out += str(row[0]) + ' - '+str(row[1]) + '\n'
        cur.close()
        conn.close()
        if out == 'Мероприятия на сегодня: \n':
            bot.send_message(message.chat.id, 'На сегодня мероприятий не залпанировано!')
        else:
            bot.send_message(message.chat.id, out)

    elif message.text == robosmile:
        bot.send_message(message.chat.id, 'Введите идентификатор квеста, который вы хотите пройти.', reply_markup=hide)
        bot.register_next_step_handler(message, startquest)

    elif message.text == smilepodmig:
        bot.send_message(message.chat.id, 'Выберите раздел!', reply_markup=markup5)

    elif message.text == smilephone:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT contact FROM contacts;")
        out = 'Контакты вожатых: \n'
        for row in cur:
            out += row[0] + '\n'
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, out, reply_markup=markup2)

    elif message.text == smilehome:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT Home FROM main WHERE ChatID=" + str(message.chat.id) + ";")
        out = ''
        for row in cur:
            out += str(row[0])
            break
        cur.close()
        conn.close()
        if out == 'None':
            bot.send_message(message.chat.id, 'Ваше место проживания пока не указанно! '
                                              'Попросите об этом вожатых.', reply_markup=markup2)
        else:
            bot.send_message(message.chat.id, out, reply_markup=markup2)

    elif message.text == 'Я тут?':
        bot.send_message(message.chat.id, 'Вы в юзере')


# 4.4. Регистрация

# 4.4.1. Добавление данных в БД
def adddata(message):
    if message.content_type == 'text':
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT ChatID FROM  main WHERE Name='" + message.text + "';")
        out = ''
        for row in cur:
            out += str(row[0])
            break
        if out == '':
            cur.execute(
                "INSERT INTO main (ChatID, Name) VALUES(" + str(message.chat.id) + ", '" + message.text + "');")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Спасибо за регистрацию! Добро Пожаловать в GoTo Hub!',
                             reply_markup=markup2)
        else:
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Такой пользователь уже существует!',
                             reply_markup=markup)


# 4.4.2. Проверка пароля
def passwordlog(message):
    global password
    global admin
    if message.text == password:
        bot.send_message(message.chat.id,
                         'Великолепно! Теперь введите ваше полное имя, а затем - фамилию. ВАЖНО: соблюдайте порядок,'
                         ' вводите сначала ПОЛНОЕ имя, а потом - фамилию. \n Пример: '
                         'Василий Пупкин')
        bot.register_next_step_handler(message, adddata)

    elif message.text == admin:
        bot.send_message(message.chat.id, 'Добро пожаловать в администрирование GoTo Hub!', reply_markup=markup3)
        # Добавление админа в бд
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO admin (ChatID, Status) VALUES(" + str(message.chat.id) + ", 1);")
        conn.commit()
        cur.close()

    else:  # Неправильный пароль
        bot.send_message(message.chat.id, 'Пароль неверный! Попробуйте еще раз.', reply_markup=markup)


# 4.5. Начало и регистрация (хендлеры)
@bot.message_handler(func=lambda message: (message.content_type == 'text'))
def start(message):
    if ifregadmin(message.chat.id):
        adminlog(message)
    elif ifreg(message.chat.id):
        if message.text == "/start":
            bot.send_message(message.chat.id, "Вас приветствует лагерь GoTo Camp! Чтобы продолжить, "
                                              "зарегестрируйтесь!", reply_markup=markup)
        if message.text == smilereg:
            bot.send_message(message.chat.id, "Введите пароль, сообщенный вам вожатыми!", reply_markup=hide)
            bot.register_next_step_handler(message, passwordlog)
    else:
        userlog(message)


# 4.6. Callback Query хендлер для Inline-клавиатур
@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'next':
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute(
            "SELECT Question FROM " + quest_dict[c.message.chat.id] + " WHERE " + team_dict[c.message.chat.id] + "=2;")
        out = ''
        for row in cur:
            out += row[0]
            break
        cur.close()
        conn.close()
        if out == '':
            bot.send_message(c.message.chat.id, "Поздравляем, вы прошли квест!", reply_markup=markup2)
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("SELECT ChatID FROM admin;")
            for row in cur:
                chatid = str(row)
                chatid = chatid[1:-2]
                bot.send_message(int(chatid), "Команда " + team_dict[c.message.chat.id] + " прошла квест "
                                 + (quest_dict[c.message.chat.id])[6:] + "!")
            cur.close()
            conn.close()

        else:
            bot.send_message(c.message.chat.id, out, reply_markup=markup4)
    elif c.data == 'ext':
        bot.send_message(c.message.chat.id, 'Вы вышли из квеста.', reply_markup=markup2)


# 4.7. Постоянный polling
if __name__ == '__main__':
    bot.polling(none_stop=True)

    # При успешном прохождении квеста - рассылка админам
    # Не создавать несколько квестов одновременно
