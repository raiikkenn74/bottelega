import telebot
from telebot import types
import requests
import json
import API
import random
import datetime

bot = telebot.TeleBot('6080363454:AAFL_BIpfut-dZS7W9FqXhGSdPNXcIR-9es')
points = 0
count = 0
current_test_id = None
Username = ""
TestId = ""
DateOfPassage = ""

@bot.message_handler(commands=['start'])
def start(message):
    global count
    global points
    count = 0
    points = 0
    global current_test_id
    response = requests.get('http://127.0.0.1:5000/api/tests')
    try:
        response.raise_for_status()  # Check if the request was successful
        tests = json.loads(response.text)['tests']
        if tests:
            current_test_id = None
            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for test in tests:
                keyboard.add(types.InlineKeyboardButton(test['name'], callback_data=f'test_{test["id"]}'))
            bot.send_message(message.chat.id, 'Выберите тест:', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id, 'Нет доступных тестов.')
    except requests.exceptions.RequestException as e:
        bot.send_message(message.chat.id, f'Ошибка при получении списка тестов: {e}')

@bot.callback_query_handler(func=lambda call: call.data.startswith('test_'))
def handle_test_selection(call):
    global current_test_id
    global TestId
    test_id = int(call.data.split('_')[1])
    current_test_id = test_id
    TestId = current_test_id
    response = requests.get(f'http://127.0.0.1:5000/api/questions?test_id={test_id}')
    try:
        response.raise_for_status()
        questions = json.loads(response.text)['questions']
        if questions:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add('Готов')  # Добавляем кнопку "Готов"
            question_text = questions[0]['question']
            bot.send_message(call.message.chat.id, 'Вы готовы?',
                             reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, 'Выбранный тест не содержит вопросов.')
    except requests.exceptions.RequestException as e:
        bot.send_message(call.message.chat.id, f'Ошибка при получении вопросов: {e}')

@bot.message_handler(func=lambda message: True)
def lalala(message):
    global points
    global count
    global current_test_id
    global Username
    global TestId
    global DateOfPassage

    if current_test_id is None:
        response = requests.get(f'http://127.0.0.1:5000/api/tests?username={Username}')
        try:
            response.raise_for_status()  # Check if the request was successful
            tests = json.loads(response.text)['tests']
            if tests:
                current_test_id = None
                keyboard = types.InlineKeyboardMarkup(row_width=1)
                for test in tests:
                    keyboard.add(types.InlineKeyboardButton(test['name'], callback_data=f'test_{test["id"]}'))
                bot.send_message(message.chat.id, 'Выберите тест:', reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, 'Нет доступных тестов.')
        except requests.exceptions.RequestException as e:
            bot.send_message(message.chat.id, f'Ошибка при получении списка тестов: {e}')
        return

    if message.chat.type == 'private' and count == 0:
        if message.text.lower() == 'готов':
            response = requests.get(f'http://127.0.0.1:5000/api/questions?test_id={current_test_id}')
            questions = json.loads(response.text)['questions']
            options = [questions[count]['answer']]
            incorrect_questions = questions[count + 1:]  # Получаем вопросы после текущего вопроса
            incorrect_answers = random.sample(incorrect_questions, min(2, len(incorrect_questions)))
            options.extend([answer['answer'] for answer in incorrect_answers])
            random.shuffle(options)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*options)
            question_text = questions[count]['question']
            bot.send_message(message.chat.id, f"{question_text}\n\nВарианты ответов:\n- " + "\n- ".join(options),
                             reply_markup=markup)
            count += 1
        else:
            bot.send_message(message.chat.id, 'Пожалуйста, отправьте "Готов", чтобы начать тестирование.')
        return

    if message.chat.type == 'private' and count >= 1:
        response = requests.get(f'http://127.0.0.1:5000/api/questions?test_id={TestId}')
        questions = json.loads(response.text)['questions']
        current_question = questions[count - 1]['question']
        if message.text.lower() == questions[count - 1]['answer'].lower():
            bot.send_message(message.chat.id, 'Правильно!')
            points += 1
        else:
            bot.send_message(message.chat.id, 'Близко, но нет')
        if count == len(questions):
            bot.send_message(message.chat.id, 'Ты ответил на все вопросы. Твой результат: ' + str(points) + ' из ' + str(count),
                             reply_markup=types.ReplyKeyboardRemove())
            DateOfPassage = datetime.datetime.now()
            Username = message.from_user.username
            API.write_to_database(count, points, Username, TestId, DateOfPassage)
            count = 0
            points = 0
        else:
            options = [questions[count]['answer']]
            incorrect_questions = questions[count + 1:]  # Получаем вопросы после текущего вопроса
            incorrect_answers = random.sample(incorrect_questions, min(2, len(incorrect_questions)))
            options.extend([answer['answer'] for answer in incorrect_answers])
            random.shuffle(options)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*options)
            question_text = questions[count]['question']
            bot.send_message(message.chat.id, f"{question_text}\n\nВарианты ответов:\n- " + "\n- ".join(options),
                             reply_markup=markup)
            count += 1

bot.polling(none_stop=True)
