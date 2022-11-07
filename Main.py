import telebot
import re
from config import token

# Создаём объект на основе токена
mybot = telebot.TeleBot(token)


# Запуск бота
@mybot.message_handler(commands=['start'])
def start_mes(message):
    mybot.send_message(message.chat.id, 'Начнём общение! Напишите мне')


@mybot.message_handler(content_types=['text'])
def dialog(message):
    global memory
    smiles = {'😀', '😑', '☹', '😡'}
    logic = {'👍', '👎'}
    # Получаем сообщение от пользователя
    story = message.text
    # Пытаемся узнать пользователя или записываем нового
    index_id = read_id(message.chat.id)
    # Вспоминаем реплики собеседника. Если нет, то создаём ячейку памяти
    words_id = read_words_id(index_id)
    # Вспоминаем ответы бота. Если нет, то создаём ячейку памяти
    answers_id = read_answers_id(index_id)

    # При  условии, что написанное, не является одним из смайлов
    if story not in smiles and story not in logic:
        # Обрабатываем текст
        story = story.replace('.', '')
        story = story.replace(',', '')
        story = story.replace('!', '')
        story = story.replace('?', '')
        story = story.lower()
        spisok_story = story.split()

        # Сравниваем написанный текст, с диалогом из памяти
        # И составляем список совпадений
        list_overlap = []
        for i in words_id:
            overlap = 0
            for j in spisok_story:
                find_word = re.search(j, i)
                if find_word != None:
                    overlap += 1
            list_overlap.append(overlap)
        # Находим большее число совпадений
        index_list_overlap = list_overlap.index(max(list_overlap))
        # Выводим ответ согласно наибольшего количества совпадений в диалоге
        if max(list_overlap) > 0:
            answer = answers_id[index_list_overlap]
            mybot.send_message(message.chat.id, answer, reply_markup=keyboard_go())
            memory = message.text
        else:
            mybot.send_message(message.chat.id, "...", reply_markup=keyboard_go())
            memory = message.text
    elif story == '👎':
        mybot.send_message(message.chat.id, "А что Вы ожидали услышать?")
        mybot.register_next_step_handler(message, save_word_answer)
    elif story == '👍':
        pass

    if story == '😀':
        emotion(index_id, story)
    elif story == '😑':
        emotion(index_id, story)
    elif story == '☹':
        emotion(index_id, story)
    elif story == '😡':
        emotion(index_id, story)


# Распознование и добавление нового собеседника
def read_id(user_id):
    with open("all_id.txt", 'r', encoding='utf-8') as f:
        spisok_id = str(f.read())
        spisok_id = spisok_id.split()

    # Пытаемся узнать человека
    # Ищем его в списке раннее писавших
    if str(user_id) in spisok_id:
        return str(spisok_id.index(str(user_id)))
    else:
        with open("all_id.txt", 'a', encoding='utf-8') as f:
            print(f' {user_id}', end='', file=f)
        emotion_index = f'emotion_{str(len(spisok_id))}.txt'
        with open(emotion_index, 'w', encoding='utf-8') as f:
            f.close()
        return str(len(spisok_id))


# Реплики собеседника
def read_words_id(index):
    global words
    words = f'words_{index}.txt'
    try:
        with open(words, 'r', encoding='utf-8') as f:
            list_words = str(f.read())
            list_words = list_words.lower()
            list_words = list_words.replace(' ', '')
            list_words = list_words.split('<p>')
        return list_words
    except:
        f = open(words, 'w', encoding='utf-8')
        f.close()


# Ответы бота
def read_answers_id(index):
    global answers
    answers = f'answers_{index}.txt'
    try:
        with open(answers, 'r', encoding='utf-8') as f:
            list_answers = str(f.read())
            list_answers = list_answers.split('<p>')
        return list_answers
    except:
        f = open(answers, 'w', encoding='utf-8')
        f.close()


# Запись реплики и ответа
def save_word_answer(message):
    with open(words, 'a', encoding='utf-8') as f:
        print(f'<p>{memory}', end='', file=f)
    with open(answers, 'a', encoding='utf-8') as f:
        print(f'<p>{message.text}', end='', file=f)
    mybot.send_message(message.chat.id, 'ага')


# Запись эмоций
def emotion(index, story):
    pass


# Клавиатура для передачи эмоций и истинности ответа
def keyboard_go():
    keyb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_smile = telebot.types.KeyboardButton('😀')
    button_middle = telebot.types.KeyboardButton('😑')
    button_sad = telebot.types.KeyboardButton('☹')
    button_angry = telebot.types.KeyboardButton('😡')
    button_ok = telebot.types.KeyboardButton('👍')
    button_notok = telebot.types.KeyboardButton('👎')
    keyb.row(button_ok, button_notok)
    keyb.row(button_smile, button_middle, button_sad, button_angry)
    return keyb


# Запуск бота в телегу(цикл постоянного обновления)
mybot.infinity_polling()
