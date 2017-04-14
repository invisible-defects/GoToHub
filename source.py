# -*- coding: utf-8 -*-

# Импорт библиотек, необходимых для работы бота

import hashlib
from bs4 import BeautifulSoup
import requests
import config
import telebot
import datetime
import feedparser
from openpyxl import load_workbook
import pymysql
from telebot import types
import sys
from threading import Timer
import random

# Иниализация бота и импорт учительского пароля

bot = telebot.TeleBot(config.token)
teacher_pass = config.teacher_pass

# Загрузка расписания

wb = load_workbook(filename='1.xlsx')
sheet_ranges = wb['1']

# Время начала уроков, классы, дни и словарь для рассылки

ll1 = datetime.time(2, 0, 0, 0, )
ll2 = datetime.time(8, 45, 0, 0)
ll3 = datetime.time(9, 45, 0, 0)
ll4 = datetime.time(10, 45, 0, 0)
ll5 = datetime.time(11, 45, 0, 0)
ll6 = datetime.time(12, 50, 0, 0)
ll7 = datetime.time(13, 55, 0, 0)
ll8 = datetime.time(14, 50, 0, 0)
ll9 = datetime.time(15, 35, 0, 0)

classes = {'5а': 'C', '5б': 'D', '5в': 'E', '5г': 'F', '5д': 'G', '6а': 'H', '6б': 'I',
           '6в': 'J', '6г': 'K', '7а': 'L', '7б': 'M', '7в': 'N', '7г': 'O', '7д': 'P',
           '8а': 'Q', '8б': 'R', '8в': 'S', '8г': 'T', '9а': 'U', '9б': 'V', '9в': 'W',
           '10.1': 'X', '10.2': 'Y', '10.3': 'Z', '10.4': 'AA', '10.5': 'AB', '11.1': 'AC',
           '11.2': 'AD', '11.3': 'AE', '11.4': 'AF'}

days = {0: 'Понедельник: \n', 1: 'Вторник: \n', 2: 'Среда: \n', 3: 'Четверг: \n', 4: 'Пятница: \n'}

dist = {}

ent = '\n'


#Словарь пользователей
users = {}

# Список пожеланий хорошего дня
nice_day = ['Хорошего Вам дня!', 'Хорошо провести день!', 'Удачного дня!', 'Хорошего настроения!',
            'Удачи во всех начинаниях!', 'Великих свершений!', 'Позитивных эмоций!', 'Позитивного настроя!']


# Кнопки меню (b = button, ch = char)

b_tt = types.KeyboardButton('Следующий Урок ' + chr(0x1F552))
b_news = types.KeyboardButton('Новости ' + chr(0x1F4C5))
b_links = types.KeyboardButton('Полезные Ссылки ' + chr(0x1F47E))
b_ads = types.KeyboardButton('Объявления ' + chr(0x1F4DD))
b_help = types.KeyboardButton('Помощь ' + chr(0x1F609))
b_cont = types.KeyboardButton('Поддержка ' + chr(0x2764))
b_lost = types.KeyboardButton('Потерянные Вещи' + chr(0x1F50E))
b_event = types.KeyboardButton('Мероприятия' + chr(0x23F0))
b_dist = types.KeyboardButton('Рассылка' + chr(0x2709))
b_parent = types.KeyboardButton('Родитель ' + chr(0x1F46A))
b_kid = types.KeyboardButton('Гимназист ' + chr(0x270D))
b_teacher = types.KeyboardButton('Учитель ' + chr(0x1F3EB))
b_more = types.KeyboardButton('Подробнее ' + chr(0x1F50E))
b_menu = types.KeyboardButton('Меню ' + chr(0x1F4CB))
b_register = types.KeyboardButton('Дневник ' + chr(0x1F4D6))
b_bells = types.KeyboardButton('Расписание Звонков ' + chr(0x1F552))
b_add = types.KeyboardButton('Добавить ' + chr(0x1F527))
b_watch = types.KeyboardButton('Посмотреть ' + chr(0x1F62F))

# Пользовательские клавиатуры (m = markup)

# Меню ученика
m_kid = types.ReplyKeyboardMarkup()
m_kid.row(b_tt, b_news)
m_kid.row(b_links, b_ads)
m_kid.row(b_register, b_cont)

# Меню учителя
m_teacher = types.ReplyKeyboardMarkup()
m_teacher.row(b_dist, b_news)
m_teacher.row(b_links, b_ads)
m_teacher.row(b_bells, b_cont)

# Меню родителя
m_parent = types.ReplyKeyboardMarkup()
m_parent.row(b_news)
m_parent.row(b_ads)
m_parent.row(b_bells)
m_parent.row(b_cont)

# Меню "Подробнее"
m_more = types.ReplyKeyboardMarkup()
m_more.row(b_more, b_menu)

# Меню "Объявления"
m_ads = types.ReplyKeyboardMarkup()
m_ads.row(b_event)
m_ads.row(b_lost)

# Меню регистрации
m_reg = types.ReplyKeyboardMarkup()
m_reg.row(b_kid)
m_reg.row(b_teacher)
m_reg.row(b_parent)

# Дополнительное меню потерянных вещей
m_choose = types.ReplyKeyboardMarkup()
m_choose.row(b_add, b_watch)

# Выбор источника новостей
m_news = types.ReplyKeyboardMarkup()
m_news.row('Новости Гимназии')
m_news.row('Новости Департамента Образования')
m_news.row('Популярная Механика')
m_news.row('Хабрахабр')
m_news.row('Яндекс.Наука')

# Очистка клавиатуры
m_hide = types.ReplyKeyboardRemove()


# Регистрация

# Учителя
def teacher_reg(message):
    if message.text == teacher_pass:
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO main(chatid, status) VALUES (" + str(message.chat.id) + ", 2);")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, "Добро пожаловать в режим учителя!", reply_markup=m_teacher)
    else:
        bot.send_message(message.chat.id, "Пароль неверен!", reply_markup=m_reg)
        bot.register_next_step_handler(message, registration)


# Ученика
def kid_reg(message):
    clas = message.text.lower()
    if len(clas) <= 4:
        if len(clas) == 3:
            clas = clas[0] + clas[2]
        if clas in classes:
            conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main',
                                   charset='utf8mb4')
            cur = conn.cursor()
            cur.execute("INSERT INTO main(chatid, status, class) VALUES (" + str(message.chat.id) + ", 1, '" +
                        clas + "');")
            conn.commit()
            cur.close()
            conn.close()
            bot.send_message(message.chat.id, "Спасибо за регистрацию! Добро пожаловать!", reply_markup=m_kid)
        else:
            bot.send_message(message.chat.id, "Неправильный формат ввода! Попробуйте еще раз. \n Пример: \n 9б, 10.1")
            bot.register_next_step_handler(message, kid_reg)
    else:
        bot.send_message(message.chat.id, "Неправильный формат ввода! Попробуйте еще раз. \n Пример: \n 9б, 10.1")
        bot.register_next_step_handler(message, kid_reg)


# Приветствие и выбор категории

def hello(message):
    bot.send_message(message.chat.id, "Добро Пожаловать! Чтобы продолжить, зарегистрируйтесь.", reply_markup=m_reg)
    bot.register_next_step_handler(message, registration)


def registration(message):
    if 'Родитель' in message.text:
        bot.send_message(message.chat.id, "Приветствуем Вас в режиме родителя!", reply_markup=m_parent)
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO main(chatid, status) VALUES (" + str(message.chat.id) + ", 3);")
        conn.commit()
        cur.close()
        conn.close()

    elif 'Учитель' in message.text:
        bot.send_message(message.chat.id, "Введите пароль учителя!", reply_markup=m_hide)
        bot.register_next_step_handler(message, teacher_reg)

    elif 'Гимназист' in message.text:
        bot.send_message(message.chat.id, "Введите Ваш класс!", reply_markup=m_hide)
        bot.register_next_step_handler(message, kid_reg)

    else:
        bot.send_message(message.chat.id, "Выберите одну из категорий, предложенных в меню!", reply_markup=m_reg)
        bot.register_next_step_handler(message, registration)


# Проверка авторизации

def check_reg(chatid):
    conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT status FROM main WHERE chatid=" + str(chatid) + ";")
    out = 0
    for row in cur:
        out += row[0]
    cur.close()
    conn.close()
    users[chatid] = out
    return out


# Основной код (c = code)

# Парсинг дневника
def c_parse(login, password):
    pas = password.encode('utf-8')
    pas = str(hashlib.md5(pas).hexdigest())
    session = requests.Session()
    headers = {'Referer': 'https://www.mos.ru/pgu/ru/application/dogm/journal/'}
    auth_url = "https://mrko.mos.ru/dnevnik/services/index.php"
    auth_req = session.get(auth_url, headers=headers, params={"login": login,
                                                              "password": pas},
                           allow_redirects=False)
    d1 = datetime.datetime.now()
    d1 = datetime.datetime.date(d1)
    d = datetime.datetime.weekday(d1)
    if d == 5 or d == 6 or d == 4:
        try:
            d = datetime.date(d1.year, d1.month, d1.day + 7 - d)
        except Exception:
            d1 = datetime.date(d1.year, d1.month + 1, 1)
            d = datetime.date(d1.year, d1.month + 1, 1 + 7 - datetime.datetime.weekday(d1))
        main_req = session.get("https://mrko.mos.ru/dnevnik/services/dnevnik.php?r=1&first=1&next=" + str(d))
    else:
        main_req = session.get("https://mrko.mos.ru/dnevnik/services/dnevnik.php?r=1&first=1")
    parsed_html = BeautifulSoup(main_req.content, "lxml")
    columns = parsed_html.body.find_all('div', 'b-diary-week__column')
    final_ans = []
    d = datetime.datetime.weekday(d)
    d2 = d + 1
    d = (days[d])[:-3]
    d = d.upper()
    d2 = days[d2][:-3]
    d2 = d2.upper()
    for column in columns:
        date_number = column.find("span", "b-diary-date").text
        date_word = column.find("div", "b-diary-week-head__title").find_all("span")[0].text
        if date_word == d or date_word == d2:
            final_ans.append("<b>" + date_word + "</b> \n" + date_number + "\n \n")
            lessons_table = column.find("div", "b-diary-lessons_table")
            all_lists = lessons_table.find_all("div", "b-dl-table__list")
            for lesson in all_lists:
                lesson_columns = lesson.find_all("div", "b-dl-td_column")
                lesson_number = lesson_columns[0].span.text
                lesson_name = lesson_columns[1].span.text
                if lesson_name == "":
                    pass
                else:
                    lesson_dz = lesson_columns[2].find("div", "b-dl-td-hw-section").span.text
                    lesson_mark = lesson_columns[3].span.text[0:1]
                    final_ans.append(
                        "<b>{0}. {1}</b>. Домашнее задание:\n"
                        "<i>{2}</i>\n"
                        "Оценка за урок: <i>{3}</i>\n\n".format(lesson_number,
                                                                lesson_name,
                                                                lesson_dz,
                                                                lesson_mark))

    return final_ans


# Дневник, ч.2
def c_register2(message):
    try:
        login = message.text.split(' ')[0]
        password = message.text.split(' ')[1]
        out = ''
        data = c_parse(login, password)
        for lesson in data:
            out += lesson + '\n'
        if out == '':
            bot.send_message(message.chat.id, 'Возможно, дневник сейчас не работает.'
                                              ' Попробуйте позже.', reply_markup=m_kid)
        else:
            bot.send_message(message.chat.id, out, reply_markup=m_kid, parse_mode='HTML')
    except Exception:
        bot.send_message(message.chat.id, 'Неправильный пароль и логин! \n'
                                          '*Возможно, это неполадка Электронного Дневника.* '
                                          'Попробуйте еще раз.', reply_markup=m_kid,
                         parse_mode='Markdown')


# Дневник
def c_register(message):
    bot.send_message(message.chat.id, 'Введите пароль и логин от Электронного дневника, разделив их пробелом. \n'
                                      '*Внимание!* \n Логин является *последовательностью цифр*, а не'
                                      ' адресом электронной почты. Узнать свой логин можно по'
                                      ' адресу: \n https://my.mos.ru/my/#profile \n Выбрав вкладку'
                                      ' Электронный дневник и нажав "Редактировать".', reply_markup=m_hide,
                     parse_mode='Markdown')
    bot.register_next_step_handler(message, c_register2)


# Расписание звонков
def c_bells(message):
    bot.send_message(message.chat.id, '*1 Урок* \n'
                                      '8:30 - 9:15 \n'
                                      '*2 урок* \n'
                                      '9:30 - 10:15 \n'
                                      '*3 урок* \n'
                                      '10:30 - 11:15 \n'
                                      '*4 урок* \n'
                                      '11:30 - 12:15 \n'
                                      '*5 урок* \n'
                                      '12:35 - 13:20 \n'
                                      '*6 урок* \n'
                                      '13:40 - 14:25 \n'
                                      '*7 урок* \n'
                                      '14:35 - 15:20 \n'
                                      '*8 урок* \n'
                                      '15:30 - 16:15', parse_mode='Markdown')


# Выбор новостей
def c_select(message):
    if 'Гимназии' in message.text:
        c_news_parse(message, 'http://gsg.mskobr.ru/data/rss/77/')
    elif 'Департамента' in message.text:
        c_news_parse(message, 'http://dogm.mos.ru/rssexport/')
    elif 'Хабр' in message.text:
        c_news_parse(message, 'https://habrahabr.ru/rss/hubs/all/')
    elif 'Популярная' in message.text:
        c_news_parse(message, 'http://www.popmech.ru/out/public-all.xml')
    elif '.Наука' in message.text:
        c_news_parse(message, 'https://news.yandex.ru/science.rss')


# Выбор Новостного канала
def c_news(message):
    bot.send_message(message.chat.id, 'Выберите новостной канал!', reply_markup=m_news)
    bot.register_next_step_handler(message, c_select)


# Парсинг Новостей
def c_news_parse(message, link):
    out = ''
    d = feedparser.parse(link)
    for a in range(3):
        title = (d['entries'][a]['title'])
        link = (d['entries'][a]['link'])
        out += str(a + 1) + '. ' + title + ent + link + ent
    if users[message.chat.id] == 1:
        mkup = m_kid
    elif users[message.chat.id] == 2:
        mkup = m_teacher
    if users[message.chat.id] == 3:
        mkup = m_parent
    bot.send_message(message.chat.id, out, reply_markup=mkup)


# "Подробнее" в расписании
def c_more(message):
    if 'Подробнее' in message.text:
        out = ''
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT class FROM main WHERE ChatID=" + str(message.chat.id) + ";")
        for row in cur:
            out += row[0]
        cur.close()
        conn.close()
        charty = classes[out]
        out = ''
        for day in range(5):
            out += '*' + days[day] + '*' + '\n'
            for lesson in range(7):
                chartx = 1 + day * 8 + lesson + 1
                chartx = str(chartx)
                tabl = charty + chartx
                if sheet_ranges[tabl].value == '':
                    out += '- \n'
                else:
                    out += sheet_ranges[tabl].value + '\n'
            out += '\n'
        bot.send_message(message.chat.id, out, reply_markup=m_kid, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Выберите категорию!', reply_markup=m_kid)


# Расписание
def c_tt(message):
    conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT class FROM main WHERE ChatID=" + str(message.chat.id) + ";")
    out = ""
    for row in cur:
        out += row[0]
    cur.close()
    conn.close()
    charty = classes[out]

    ddd = datetime.datetime.now()
    nowt = datetime.datetime.time(ddd)
    nowd = datetime.datetime.date(ddd)
    dday = datetime.datetime.weekday(nowd)

    if ll1 < nowt < ll2:
        les = 1
    elif ll2 < nowt < ll3:
        les = 2
    elif ll3 < nowt < ll4:
        les = 3
    elif ll4 < nowt < ll5:
        les = 4
    elif ll5 < nowt < ll6:
        les = 5
    elif ll6 < nowt < ll7:
        les = 6
    elif ll7 < nowt < ll8:
        les = 7
    elif ll8 < nowt < ll9:
        les = 8
    else:
        les = 0
    chartx = 1 + dday * 8 + les
    chartx = str(chartx)
    tabl = charty + chartx
    out = sheet_ranges[tabl].value
    if not (dday == 6 or dday == 5 or les == 0):
        bot.send_message(message.chat.id, 'Ваш следующий урок: \n' + out, reply_markup=m_more)
        bot.register_next_step_handler(message, c_more)
    else:
        bot.send_message(message.chat.id, "У вас больше нет сегодня уроков!", reply_markup=m_more)
        bot.register_next_step_handler(message, c_more)


# Полезные ссылки
def c_links(message):
    out = '*Образовательные интернет-ресурсы* \n https://www.udacity.com/ \n' \
          ' https://www.coursera.org/ \n https://www.edx.org/ \n welcome.stepik.org/ru \n ' \
          'https://foxford.ru/ \n \n *Олимпиады для школьников* \n https://reg.olimpiada.ru/ \n' \
          ' https://abitu.net/ \n https://it-edu.mipt.ru/ \n \n *Официальный сайт Гимназии* \n gsg.mskobr.ru/'
    bot.send_message(message.chat.id, out, parse_mode="Markdown")


# Добавление потерянной вещи
def c_lost(message):
    if message.text.lower() == 'выход':
        bot.send_message(message.chat.id, 'Выберите категорию!', reply_markup=m_teacher)
    else:
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO lost(item) VALUES ('" + message.text + "');")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Объявление успешно добавлено!', reply_markup=m_teacher)


# Потерянные вещи, окно выбора
def c_lost0(message):
    if 'Посмотреть' in message.text:
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT item FROM lost;")
        out = ""
        cnt = 1
        for row in cur:
            out += str(cnt) + '. ' + row[0] + '\n'
            cnt += 1
        cur.close()
        conn.close()
        if out == '':
            bot.send_message(message.chat.id, 'Информации о потерянных вещах пока нет!', reply_markup=m_teacher)
        else:
            bot.send_message(message.chat.id, out, reply_markup=m_teacher)
    else:
        bot.send_message(message.chat.id,
                         'Введите информацию о потерянной вещи: описание вещи, дату нахождения и'
                         ' местонахождение вещи в данный момент.',
                         reply_markup=m_hide)
        bot.register_next_step_handler(message, c_lost)


# Мероприятия, ввод
def c_event1(message):
    try:
        text = message.text.split('\n')
        name = text[0]
        date = text[1]
        descr = text[2]
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("INSERT INTO events(name, date, descr) VALUES ('" + name + "', '" + date + "', '" + descr + "');")
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(message.chat.id, 'Мероприятие успешно добавлено!', reply_markup=m_teacher)
    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])
        if len(message.text.split('\n')) > 3:
            bot.send_message(message.chat.id, 'Неправильный формат ввода, не используйте'
                                              ' начатие с новой строки.', reply_markup=m_teacher)
        else:
            bot.send_message(message.chat.id, 'Неправильный формат ввода! Попробуйте еще раз.', reply_markup=m_teacher)


# Мероприятия, окно выбора
def c_event0(message):
    if 'Посмотреть' in message.text:
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT date, name, descr FROM events;")
        out = ""
        cnt = 1
        for row in cur:
            out += str(cnt) + '. ' + row[1] + ' - ' + str(row[0]) + '\n' + row[2] + '\n'
            cnt += 1
        cur.close()
        conn.close()
        if out == '':
            bot.send_message(message.chat.id, 'Пока мероприятий не запланировано!', reply_markup=m_teacher)
        else:
            bot.send_message(message.chat.id, out, reply_markup=m_teacher)
    else:
        bot.send_message(message.chat.id, 'Введите информацию о мероприятии в формате: \n'
                                          '_Название \n'
                                          'гггг-мм-дд \n'
                                          'Описание_', reply_markup=m_hide, parse_mode='Markdown')
        bot.register_next_step_handler(message, c_event1)


# Объявления, ч.2 (версия для учителей)
def c_ads2_t(message):
    if 'Мероприятия' in message.text:
        bot.send_message(message.chat.id,
                         'Выберите действие!',
                         reply_markup=m_choose)
        bot.register_next_step_handler(message, c_event0)
    else:
        bot.send_message(message.chat.id,
                         'Выберите действие!',
                         reply_markup=m_choose)
        bot.register_next_step_handler(message, c_lost0)


# Объявления, ч.2
def c_ads2(message):
    if message.text == 'Мероприятия' + chr(0x23F0):
        sheet_ranges = wb['2']
        k = 1
        out = ''
        while k <= 3:
            out += str(k) + '. '
            meropkor = 'A' + str(k + 2)
            merop = sheet_ranges[meropkor].value
            merop = str(merop)
            out += merop + ', '
            meropkor = 'B' + str(k + 2)
            merop = sheet_ranges[meropkor].value
            merop = str(merop)
            out += merop + ' ' + ent
            meropkor = 'C' + str(k + 2)
            merop = sheet_ranges[meropkor].value
            merop = str(merop)
            out += merop + ent + ent
            k += 1
        sheet_ranges = wb['1']
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT status FROM main WHERE ChatID=" + str(message.chat.id) + ";")
        clas = 0
        for row in cur:
            clas += row[0]
        cur.close()
        conn.close()
        if clas == 1:
            bot.send_message(message.chat.id, out, reply_markup=m_kid)
        else:
            bot.send_message(message.chat.id, out, reply_markup=m_parent)
    else:
        conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
        cur = conn.cursor()
        cur.execute("SELECT item FROM lost;")
        out = ""
        cnt = 1
        for row in cur:
            out += str(cnt) + '. ' + row[0] + '\n'
            cnt += 1
        cur.execute("SELECT status FROM main WHERE ChatID=" + str(message.chat.id) + ";")
        clas = 0
        for row in cur:
            clas += row[0]
        cur.close()
        conn.close()

        if clas == 1:
            if out == '':
                bot.send_message(message.chat.id, 'Информации о потерянных вещах пока нет!', reply_markup=m_kid)
            else:
                bot.send_message(message.chat.id, out, reply_markup=m_kid)
        else:
            if out == '':
                bot.send_message(message.chat.id, 'Информации о потерянных вещах пока нет!', reply_markup=m_parent)
            else:
                bot.send_message(message.chat.id, out, reply_markup=m_parent)


# Объявления
def c_ads(message):
    bot.send_message(message.chat.id, "Выберите категорию!", reply_markup=m_ads)
    bot.register_next_step_handler(message, c_ads2)


# Объявления (версия для учителей)
def c_ads_t(message):
    bot.send_message(message.chat.id, "Выберите категорию!", reply_markup=m_ads)
    bot.register_next_step_handler(message, c_ads2_t)


# Контакты
def c_cont(message):
    out = 'Если вам есть, что сказать автору, Вы можете связаться со мной по этому никнейму в Telegram: \n ' \
          '@diveintodarkness \n Спасибо, что пользуетесь Помощником Гимназиста! ' + chr(0x2764)
    bot.send_message(message.chat.id, out)


# Рассылки ч. 3
def c_dist3(message):
    conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main', charset='utf8mb4')
    cur = conn.cursor()
    for adress in dist[message.chat.id]:
        if len(adress) == 1:
            cur.execute("SELECT chatid FROM main WHERE status=" + adress + " ;")
            for row in cur:
                if not row[0] == message.chat.id:
                    bot.send_message(row[0], message.text)
        else:
            cur.execute("SELECT chatid FROM main WHERE class='" + adress + "' ;")
            for row in cur:
                bot.send_message(row[0], message.text)
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, 'Сообщение успешно разослано!', reply_markup=m_teacher)


# Рассылки ч.2
def c_dist2(message):
    go = True
    text = message.text.lower()
    text = text.split(',')
    adresses = set()
    for adress in text:
        adress = adress.strip()
        if adress == 'учителя':
            adresses.add('2')
        elif adress == 'ученики':
            adresses.add('1')
        elif adress == 'родители':
            adresses.add('3')
        elif adress in classes and not (1 in adresses):
            adresses.add(adress)
        else:
            bot.send_message(message.chat.id,
                             'Адресат ' + adress + ' не найден! \n Попробуйте ввести адресатов еще раз.')
            bot.register_next_step_handler(message, c_dist2)
            go = False
            break
    if go:
        dist[message.chat.id] = adresses
        bot.send_message(message.chat.id, 'Теперь введите рассылаемое сообщение.')
        bot.register_next_step_handler(message, c_dist3)


# Рассылки
def c_dist(message):
    bot.send_message(message.chat.id,
                     'Через запятую введите получателей сообщения. \n Возможные получатели:'
                     ' \n Учителя, родители, ученики, конкретный класс (10.1, 9б, 7в и т.д.)',
                     reply_markup=m_hide)
    bot.register_next_step_handler(message, c_dist2)


# Пользователские интерфейсы

# Интерфейс ученика
def c_kid(message):
    if 'Следующий Урок' in message.text:
        c_tt(message)
    elif 'Новости ' + chr(0x1F4C5) in message.text:
        c_news(message)
    elif 'Полезные Ссылки' in message.text:
        c_links(message)
    elif 'Объявления' in message.text:
        c_ads(message)
    elif 'Поддержка' in message.text:
        c_cont(message)
    elif 'Дневник' in message.text:
        c_register(message)


# Интерфейс учителя
def c_teacher(message):
    if 'Рассылка' in message.text:
        c_dist(message)
    elif 'Новости ' + chr(0x1F4C5) in message.text:
        c_news(message)
    elif 'Полезные Ссылки' in message.text:
        c_links(message)
    elif 'Объявления' in message.text:
        c_ads_t(message)
    elif 'Поддержка' in message.text:
        c_cont(message)
    elif 'Расписание' in message.text:
        c_bells(message)
    elif 'ADMIN_EVENTS' in message.text:
        checker()


# Интерфейс родителя
def c_parent(message):
    if 'Новости ' + chr(0x1F4C5) in message.text:
        c_news(message)
    elif 'Объявления' in message.text:
        c_ads(message)
    elif 'Поддержка' in message.text:
        c_cont(message)
    elif 'Расписание' in message.text:
        c_bells(message)


# Рассылка событий на сегодня
def checker():
    conn = pymysql.connect(host='localhost', port=3306, user='bot', passwd='password', db='main',
                           charset='utf8mb4')
    cur = conn.cursor()
    cur.execute("SELECT name FROM events WHERE date = CURRENT_DATE;")
    out = '*Напоминаем, что сегодня проходят мероприятия:* \n'
    for row in cur:
        out += row[0] + '\n'
    random.seed()
    out += '\n' + random.choice(nice_day) + '\n _- Администрация Помощника Гимназиста_'
    cur.execute("SELECT chatid FROM main;")
    for row in cur:
        bot.send_message(row[0], out, parse_mode='Markdown')
    cur.close()
    conn.close()


# Хендлер сообщений
@bot.message_handler(func=lambda message: (message.content_type == 'text'))
def all_messages(message):
    if message.text == '/start' and check_reg(message.chat.id) == 0:
        hello(message)
    elif check_reg(message.chat.id) == 1:
        c_kid(message)
    elif check_reg(message.chat.id) == 2:
        c_teacher(message)
    elif check_reg(message.chat.id) == 3:
        c_parent(message)


# Постоянный polling

if __name__ == '__main__':
    bot.polling(none_stop=True)
