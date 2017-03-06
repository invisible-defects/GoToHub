import telebot
import config
from datetime import *
import pymysql
from telebot import types

# 1. Иниализация

# 1.1. Иниализация бота
bot = telebot.TeleBot(config.token)
questname = ''
questbusy = False

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

# 2.2. Админские константы
robosmileadmin = 'Создание Квеста ' + chr(0x1F916)
smileclockadmin = 'Задать Расписание ' + chr(0x1F557)
smilemeropadmin = 'Срочное Сообщение ' + chr(0x1F514)
smiletrophyadmin = 'Добавить Достижение ' + chr(0x1F3C6)

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
markup3.row(item6, item9)
markup3.row(item7, item8)


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
        booli = True
    else:
        booli = False
    return booli


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
        booli = False
    else:
        booli = True
    return booli


# 4.2. Основной код админской части

# 4.2.1. Рассылка
def rassilka(message):
    out = "Срочная рассылка: \n \n"
    out += message.text
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT ChatID FROM main;")
    for row in cur:
        chatid = str(row)
        chatid = chatid[1:-2]
        bot.send_message(int(chatid), out)
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Сообщение успешно разосланно!', reply_markup=markup3)


# 4.2.2. Добавление мероприятия
def addevent(message):
    sthour = stminute = finhour = finminute = 0
    do = True
    data = message.text
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
    data = message.text
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
    global questbusy
    data = message.text
    if data == 'Готово!':
        questbusy = False
        bot.send_message(message.chat.id, 'Квест успешно создан!', reply_markup=markup3)
    else:
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("ALTER TABLE " + questname + " ADD " + data + " TINYINT NULL;")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Ключ добавлен!')
        bot.register_next_step_handler(message, addkey)


# 4.2.4.2. Создание вопросов и ответов
def addquestions(message):
    if message.text == 'Готово!':
        bot.send_message(message.chat.id, 'Теперь добавьте ключи команд. Для каждый команды, участвующей в конкурсе '
                                          'придумайте собственный идентификатор (латиница, одно слово) и '
                                          'отправьте его в отдельном сообщении. '
                                          'Когда закончите, отправьте "Готово!"')
        bot.register_next_step_handler(message, addkey)
    else:
        go = True
        data = message.text
        try:
            data = data.split(' : ')
            question = data[0]
            answer = data[1]
        except ValueError:
            go = False
            bot.send_message(message.chat.id, 'Неверный формат вопроса. Введите вопрос еще раз.')
            bot.register_next_step_handler(message, addquestions)
        if go:
            conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO " + questname + " (Question, Answer) VALUES ('" + question + "', '" + answer + "');")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, 'Вопрос добавлен!')
            bot.register_next_step_handler(message, addquestions)


# 4.2.4.3. Иниализация нового квесиа
def newquest(message):
    global questname
    questname = 'quest_' + message.text
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                           charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("CREATE TABLE " + questname + " (Question VARCHAR(255) NOT NULL, Answer VARCHAR(255) NOT NULL ) "
                                              "ENGINE=InnoDB;")
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Далее введите вопросы и ответы квеста в формате: "Вопрос : Ответ". \n '
                                      'Пример: '
                                      '\n "Продолжите фразу - программисты не рождаются, программисты... : '
                                      'Наследуются"\nКаждую следующую пару вопрос-ответ отправляйте в новом '
                                      'сообщении. '
                                      'Когда закончите, отправьте "Готово!"')
    bot.register_next_step_handler(message, addquestions)


# 4.2.5. Интерфейс
def adminlog(message):
    global questbusy
    if message.text == smilemeropadmin:
        bot.send_message(message.chat.id, 'Введите сообщение для рассылки:', reply_markup=hide)
        bot.register_next_step_handler(message, rassilka)

    elif message.text == smiletrophyadmin:
        bot.send_message(message.chat.id, 'Введите получателя достижения, а затем наименование достижения в формате: \n'
                                          'Полное_Имя Фамилия : Название и описание достижения \n Пример: \n'
                                          '"Василий Пупкин : Костыли - наше Всё"', reply_markup=hide)
        bot.register_next_step_handler(message, addtrophy)

    elif message.text == smileclockadmin:
        bot.send_message(message.chat.id,
                         'Введите информацию о мероприятии в формате: \n "Название и описание : Месяц День'
                         ' Часы_Начала Минуты_Начала Часы_Конца Минуты_Конца" \n Пример: \n "Самый важный'
                         ' сбор : 3 8 12 15 12 30"', reply_markup=hide)
        bot.register_next_step_handler(message, addevent)

    elif message.text == robosmileadmin:
        if not questbusy:
            questbusy = True
            bot.send_message(message.chat.id, 'Введите и запомните идентификатор квеста. Он должен быть на латинице, '
                                              'состоять из одного слова и не '
                                              'должен содержать слов "main", "admin", "timetable".', reply_markup=hide)
            bot.register_next_step_handler(message, newquest)
        else:
            bot.send_message(message.chat.id, 'В данный момент Конструктор Квестов занят кем-то еще :c \n '
                                              'Попробуйте позже.', reply_markup=markup3)

    elif message.text == 'Я тут?':
        bot.send_message(message.chat.id, 'Вы в админке')


# 4.3. Основной код пользовательской части

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

    elif message.text == 'Я тут?':
        bot.send_message(message.chat.id, 'Вы в юзере')


# 4.4. Регистрация

# 4.4.1. Добавление данных в БД
def adddata(message):
    if message.content_type == 'text':
        conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='password', db='goto',
                               charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO main (ChatID, Name) VALUES(" + str(message.chat.id) + ", '" + message.text + "');")
        conn.commit()
        cur.close()

        bot.send_message(message.chat.id, 'Спасибо за регистрацию! Добро Пожаловать в GoTo Hub!', reply_markup=markup2)
        bot.register_next_step_handler(message, userlog)


# 4.4.2. Проверка пароля
def passwordlog(message):
    global password
    global admin
    if message.text == password:
        bot.send_message(message.chat.id, 'Великолепно! Теперь введите ваше полное имя, а затем - фамилию. \n Пример: '
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
        bot.register_next_step_handler(message, adminlog)

    else:  # Неправильный пароль
        bot.send_message(message.chat.id, 'Пароль неверный! Попробуйте еще раз.')
        bot.register_next_step_handler(message, passwordlog)


# 4.5. Начало и регистрация (хендлеры)
@bot.message_handler(func=lambda message: (message.content_type == 'text'))
def start(message):
    if ifregadmin(message.chat.id):
        adminlog(message)
    elif ifreg(message.chat.id):
        if message.text == "/start":
            bot.send_message(message.chat.id, "Вас приветствуют лагерь GoTo Hub! Чтобы продолжить, "
                                              "зарегестрируйтесь!", reply_markup=markup)
        if message.text == smilereg:
            bot.send_message(message.chat.id, "Введите пароль, сообщенный вам вожатыми!", reply_markup=hide)
            bot.register_next_step_handler(message, passwordlog)
    else:
        userlog(message)


# 4.6. Постоянный polling
if __name__ == '__main__':
    bot.polling(none_stop=True)
