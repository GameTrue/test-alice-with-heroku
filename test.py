from flask import Flask, request
import logging
import json
import random
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

cities = {
    'москва': ['1540737/25d27626471923609fee', '1540737/f4f4af7f82af68b0fe4c'],
    'нью-йорк': ['213044/92fa25d10e048df60b14', '937455/31224b7d2ddaad88214c'],
    'париж': ["1540737/5eaa49a4b6e4e4cff726", '997614/b8a4c8217a8e9d1cd7d8'],
    'берлин': ["965417/b69fe66f22feb657bf92", '1652229/b45e0d121ae8a70e7f6c'],
    'санкт-петербург': ["1540737/388971f2b205771b2a24", '1652229/cbfffd480e710314ed61'],
    'россия': "москва санкт-петербург",
    'америка': "нью-йорк",
    'франция': "париж",
    'германия': "берлин"
}


cars = {
    'lada': ['1652229/9db6a190c3712e449cde', '1030494/6bbd2a1c21c7321dcabe'],
    'ford': ['1540737/851a0c518a4cdc56a6b4', '213044/76ae0e3da3aeb940567c'],
    'renault': ["1533899/2e4bcdc7616971165314", '965417/e6d0c08d22ddb00cde80'],
    'audi': ["997614/d6fdf0ad5710b0aefeb0", '1652229/d11234830d9c5f71836c'],
    'kia': ["1540737/2db0c369726ab9476756", '1652229/502f3428210494f27251'],
    'россия': "lada",
    'америка': "ford",
    'франция': "renault",
    'германия': "audi",
    'корея': 'kia'
}

food = {
    'гамбургер': ['965417/3ab793ecfa11217f7958', '1540737/84b0cd530a646af6ad7b'],
    'картошка': ['965417/d60f4b886d740f38215a', '1533899/049f3e6cd8ac757b59e6'],
    'нагетсы': ["1030494/705e56d5a988f21340c6", '1540737/e12fbf590b56d6ad218a'],
    'хлеб': ["1030494/ee1fef0e562ba003f48d", '1540737/be07d6c5523394f6a81a'],
    'пельмени': ["1652229/4011543b22d7fc32c3fa", '1521359/b75586d602f333911254']
}

countries = ['россия', 'нью-йорк', 'франция']
ch_countries = {'москва': 'россия', 'нью-йорк': 'америка', 'париж': 'франция', 'санкт-петербург': 'россия', 'берлин': 'германия'}
ch_cars = {'lada': 'россия', 'ford': 'америка', 'renault': 'франция'}

sessionStorage = {'tip': '', 'balls': 0, 'diff': 'easy'}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']
    if req['session']['new']:
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'game_started': False,
            # здесь информация о том, что пользователь начал игру. По умолчанию False
            'city_fol': '',
            'balls': 0,
            'tip': '',
            'diff': 'easy'
        }
        return

    if sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)
        txtt = req['request']['original_utterance'].lower()
        if txtt == 'помощь':
            res['response']['text'] = 'Проект выполнен учеником Яндекс Лицея. А теперь назови имя!'
        elif 'что ты умеешь' in txtt:
            res['response']['text'] = 'Это игра с угадыванием картинок. Ты можешь выбрать темы для отгадывания: Города, Машины или Еда, а такдже в некоторых темах есть возможность выбрать сложность, функционал обновляется. Теперь назови имя!'
        elif first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
        else:
            sessionStorage[user_id]['first_name'] = first_name
            # создаём пустой массив, в который будем записывать города, которые пользователь уже отгадал
            sessionStorage[user_id]['guessed_cities'] = []
            # как видно из предыдущего навыка, сюда мы попали, потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response'][
                'text'] = f'Приятно познакомиться, {first_name.title()}. Я Алиса. Ты можешь поиграть в игру с угадыванием картинок. Ты можешь выбрать темы для отгадывания: Города, Машины или Еда?'

            res['response']['buttons'] = [
                {
                    'title': 'Города',
                    'hide': False
                },
                {
                    'title': 'Машины',
                    'hide': False
                },
                {
                    'tittle': 'Еда',
                    'hide': False
                },
                {
                    'tittle': 'Никакую',
                    'hide': False
                }
            ]
    else:
        # У нас уже есть имя, и теперь мы ожидаем ответ на предложение сыграть.
        # В sessionStorage[user_id]['game_started'] хранится True или False в зависимости от того,
        # начал пользователь игру или нет.
        if not sessionStorage[user_id]['game_started']:
            # игра не начата, значит мы ожидаем ответ на предложение сыграть.
            if sessionStorage[user_id]['tip'] == '':
                txtt = req['request']['original_utterance'].lower()
                if txtt == 'помощь':
                    res['response']['text'] = 'Проект выполнен учеником Яндекс Лицея. Так какую тему вы хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]
                elif 'что ты умеешь' in txtt:
                    res['response'][
                        'text'] = 'Это игра с угадыванием картинок. Ты можешь выбрать темы для отгадывания: Города, Машины или Еда, а такдже в некоторых темах есть возможность выбрать сложность, функционал обновляется. Так какую тему вы хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]
                elif 'города' in req['request']['nlu']['tokens']:
                    # если пользователь согласен, то проверяем не отгадал ли он уже все города.
                    # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                    # если есть неотгаданные города, то продолжаем игру
                    sessionStorage[user_id]['game_started'] = True
                    # номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    sessionStorage['tip'] = 'city'
                    # функция, которая выбирает город для игры и показывает фото
                    play_game(res, req)
                elif 'машины' in req['request']['nlu']['tokens']:
                    # если пользователь согласен, то проверяем не отгадал ли он уже все города.
                    # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                    # если есть неотгаданные города, то продолжаем игру
                    res['response']['text'] = 'Выберите сложность: легкая или сложная'
                    res['response']['buttons'] = [
                        {
                            'title': 'Легкая',
                            'hide': False
                        },
                        {
                            'title': 'Сложная',
                            'hide': False
                        }
                    ]
                    sessionStorage[user_id]['tip'] = 'cars'
                elif 'вывести' in req['request']['nlu']['tokens']:
                    # если пользователь согласен, то проверяем не отгадал ли он уже все города.
                    # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                    # если есть неотгаданные города, то продолжаем игру
                    res['response']['text'] = 'Вы молодец, ваш рейтинг: {}! Теперь выбери тему для отгадывания: Города, Машины или Еда'.format(str(sessionStorage['balls']))
                    sessionStorage['tip'] = ''
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]

                    # функция, которая выбирает город для игры и показывает фото
                elif 'еда' in req['request']['nlu']['tokens']:
                    # если пользователь согласен, то проверяем не отгадал ли он уже все города.
                    # По схеме можно увидеть, что здесь окажутся и пользователи, которые уже отгадывали города
                    sessionStorage[user_id]['game_started'] = True
                    # номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    sessionStorage['tip'] = 'food'
                    # функция, которая выбирает город для игры и показывает фото
                    play_game(res, req)
                elif 'никакую' in req['request']['nlu']['tokens']:
                    res['response']['text'] = 'Ну и ладно!'
                    res['end_session'] = True

                else:
                    res['response']['text'] = 'Не поняла ответа! Так какую тему вы хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]
            elif sessionStorage[user_id]['tip'] == 'cars':
                txtt = req['request']['original_utterance'].lower()
                if txtt == 'помощь':
                    res['response'][
                        'text'] = 'Проект выполнен учеником Яндекс Лицея. Так какую тему вы хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Легкая',
                            'hide': False
                        },
                        {
                            'title': 'Сложная',
                            'hide': False
                        }
                    ]
                elif 'что ты умеешь' in txtt:
                    res['response'][
                        'text'] = 'Это игра с угадыванием картинок. Ты можешь выбрать темы для отгадывания: Города, Машины или Еда, а такдже в некоторых темах есть возможность выбрать сложность, функционал обновляется. Так какую сложность выбирешь?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Легкая',
                            'hide': False
                        },
                        {
                            'title': 'Сложная',
                            'hide': False
                        }
                    ]
                elif 'легкая' in req['request']['nlu']['tokens']:
                    sessionStorage[user_id]['diff'] = 'easy'
                    sessionStorage[user_id]['game_started'] = True
                    # номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    sessionStorage['tip'] = 'cars'
                    # функция, которая выбирает город для игры и показывает фото
                    play_game(res, req)
                elif 'сложная' in req['request']['nlu']['tokens']:
                    sessionStorage[user_id]['diff'] = 'hard'
                    sessionStorage[user_id]['game_started'] = True
                    # номер попытки, чтобы показывать фото по порядку
                    sessionStorage[user_id]['attempt'] = 1
                    sessionStorage['tip'] = 'cars'
                    # функция, которая выбирает город для игры и показывает фото
                    play_game(res, req)
                else:
                    res['response']['text'] = 'Не поняла ответа! Так какую сложность вы хотите выбрать: легкая или сложная?'
                    res['response']['buttons'] = [
                        {
                            'title': 'Легкая',
                            'hide': False
                        },
                        {
                            'title': 'Сложная',
                            'hide': False
                        }
                    ]

        else:
            play_game(res, req)


def play_game(res, req):
    user_id = req['session']['user_id']
    attempt = sessionStorage[user_id]['attempt']
    res['response']['buttons'] = [
        {
            'title': 'Помощь',
            'hide': True
        }
    ]
    if sessionStorage['tip'] == 'city':
        if attempt == 1:
            # если попытка первая, то случайным образом выбираем город для гадания
            city = random.choice(list(cities)[:5])
            # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
            while city in sessionStorage[user_id]['guessed_cities']:
                city = random.choice(list(cities)[:5])
            # записываем город в информацию о пользователе
            sessionStorage[user_id]['city'] = city
            res['response']['buttons'].append(
                {
                    'title': 'Показать город на карте',
                    "url": "https://yandex.ru/maps/?mode=search&text={}".format(
                        sessionStorage[user_id]['city']),
                    'hide': True
                }
            )
            # добавляем в ответ картинку
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Что это за город?'
            res['response']['card']['image_id'] = cities[city][attempt - 1]
            res['response']['text'] = 'Тогда сыграем!'
            sessionStorage[user_id]['attempt'] += 1
        else:
            # сюда попадаем, если попытка отгадать не первая
            city = sessionStorage[user_id]['city']
            # проверяем есть ли правильный ответ в сообщение
            if req['request']['original_utterance'].lower() != 'показать город на карте':

                if sessionStorage[user_id]['city_fol']:
                    if req['request']['original_utterance'].lower() == ch_countries[sessionStorage[user_id]['city_fol']]:
                        res['response']['text'] = 'Правильно! Ты все сделал! Какую тему хотите выбрать теперь: Города, Машины, Еда или Вывести баллы??'
                        sessionStorage['balls'] += 2
                        sessionStorage[user_id]['game_started'] = False
                        res['response']['buttons'] = [
                            {
                                'title': 'Города',
                                'hide': False
                            },
                            {
                                'title': 'Машины',
                                'hide': False
                            },
                            {
                                'tittle': 'Еда',
                                'hide': False
                            },
                            {
                                'tittle': 'Никакую',
                                'hide': False
                            }
                        ]
                        sessionStorage[user_id]['city_fol'] = ''
                        return
                    else:
                        res['response']['text'] = 'Вы пытались. Это {}. Какую тему хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'.format(
                            ch_countries[sessionStorage[user_id]['city_fol']])
                        sessionStorage['balls'] -= 1
                        if sessionStorage['balls'] < 0:
                            sessionStorage['balls'] = 0
                        sessionStorage[user_id]['game_started'] = False
                        sessionStorage[user_id]['city_fol'] = ''
                        return

                else:
                    if req['request']['nlu']['tokens'][0] == 'помощь':
                        # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                        # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                        res['response']['text'] = 'Игра была сделана учеником Яндекс.Лицея!'
                    elif get_city(req) == city:
                        # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                        # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                        res['response']['text'] = 'Правильно! Теперь укажите страну!'
                        sessionStorage['balls'] += 1
                        sessionStorage[user_id]['guessed_cities'].append(city)
                        sessionStorage[user_id]['city_fol'] = city
                        return
                    else:
                        # если нет
                        if attempt == 3:
                            # если попытка третья, то значит, что все картинки мы показали.
                            # В этом случае говорим ответ пользователю,
                            # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                            # Обратите внимание на этот шаг на схеме.
                            res['response']['text'] = f'Вы пытались. Это {city.title()}. Какую тему хотите выбрать теперь: Города, Машины, Еда или Вывести баллы??'
                            sessionStorage['balls'] -= 1
                            if sessionStorage['balls'] < 0:
                                sessionStorage['balls'] = 0
                            sessionStorage[user_id]['game_started'] = False
                            sessionStorage[user_id]['guessed_cities'].append(city)
                            sessionStorage[user_id]['attempt']
                            return
                        else:
                            # иначе показываем следующую картинку
                            res['response']['card'] = {}
                            res['response']['card']['type'] = 'BigImage'
                            res['response']['card'][
                                'title'] = 'Неправильно. Вот тебе дополнительное фото'
                            res['response']['card']['image_id'] = cities[city][attempt - 1]
                            res['response']['text'] = 'А вот и не угадал!'
                            sessionStorage['balls'] -= 1
                            if sessionStorage['balls'] < 0:
                                sessionStorage['balls'] = 0
                    # увеличиваем номер попытки доля следующего шага
                    sessionStorage[user_id]['attempt'] += 1
            else:
                res['response']['text'] = 'Можете посмотреть месторасположение на Яндекс Картах'
    elif sessionStorage['tip'] == 'cars':
        if sessionStorage[user_id]['diff'] == 'hard':
            if attempt == 1:
                # если попытка первая, то случайным образом выбираем город для гадания
                city = random.choice(list(cars)[:5])
                # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
                while city in sessionStorage[user_id]['guessed_cities']:
                    city = random.choice(list(cars)[:5])
                # записываем город в информацию о пользователе
                sessionStorage[user_id]['city'] = city
                res['response']['buttons'].append(
                    {
                        'title': 'Показать город на карте',
                        "url": "https://yandex.ru/maps/?mode=search&text={}".format(
                            sessionStorage[user_id]['city']),
                        'hide': True
                    }
                )
                # добавляем в ответ картинку
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Что это за машина?'
                res['response']['card']['image_id'] = cars[city][attempt - 1]
                res['response']['text'] = 'Тогда сыграем!'
                sessionStorage[user_id]['attempt'] += 1
            else:
                # сюда попадаем, если попытка отгадать не первая
                city = sessionStorage[user_id]['city']
                # проверяем есть ли правильный ответ в сообщение
                if sessionStorage[user_id]['city_fol']:
                    if cars[req['request']['original_utterance'].lower()] == sessionStorage[user_id]['city_fol'].lower():
                        res['response']['text'] = 'Правильно! Ты все сделал! Какую тему хотите выбрать теперь: Города, Машины, Еда или Вывести баллы?'
                        sessionStorage['balls'] += 2
                        sessionStorage[user_id]['game_started'] = False
                        res['response']['buttons'] = [
                            {
                                'title': 'Города',
                                'hide': False
                            },
                            {
                                'title': 'Машины',
                                'hide': False
                            },
                            {
                                'tittle': 'Еда',
                                'hide': False
                            },
                            {
                                'tittle': 'Никакую',
                                'hide': False
                            }
                        ]
                        sessionStorage[user_id]['city_fol'] = ''
                        sessionStorage[user_id]['tip'] = ''
                        return
                    else:
                        sessionStorage['balls'] -= 1
                        if sessionStorage['balls'] < 0:
                            sessionStorage['balls'] = 0
                        res['response']['text'] = 'Вы пытались. Это {}. Сыграем ещё?'.format(
                            ch_cars[sessionStorage[user_id]['city_fol']])
                        sessionStorage[user_id]['game_started'] = False
                        sessionStorage[user_id]['city_fol'] = ''
                        return

                else:
                    if req['request']['original_utterance'].lower() == 'помощь':
                        # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                        # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                        res['response']['text'] = 'Игра была сделана учеником Яндекс.Лицея!'
                    elif req['request']['original_utterance'].lower() == city.lower():
                        # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                        # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                        res['response']['text'] = 'Правильно! Теперь укажи страну производителя!'
                        sessionStorage['balls'] += 1
                        sessionStorage[user_id]['guessed_cities'].append(city)
                        sessionStorage[user_id]['city_fol'] = city
                        return
                    else:
                        # если нет
                        if attempt == 3:
                            # если попытка третья, то значит, что все картинки мы показали.
                            # В этом случае говорим ответ пользователю,
                            # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                            # Обратите внимание на этот шаг на схеме.
                            res['response']['text'] = f'Вы пытались. Это {city.title()}. Сыграем ещё?'
                            sessionStorage['balls'] -= 1
                            if sessionStorage['balls'] < 0:
                                sessionStorage['balls'] = 0
                            sessionStorage[user_id]['game_started'] = False
                            sessionStorage[user_id]['guessed_cities'].append(city)
                            sessionStorage[user_id]['attempt'] = 1
                            return
                        else:
                            # иначе показываем следующую картинку
                            res['response']['card'] = {}
                            res['response']['card']['type'] = 'BigImage'
                            res['response']['card'][
                                'title'] = 'Неправильно. Вот тебе дополнительное фото'
                            res['response']['card']['image_id'] = cars[city][attempt - 1]
                            res['response']['text'] = 'А вот и не угадал!'
                            sessionStorage['balls'] -= 1
                            if sessionStorage['balls'] < 0:
                                sessionStorage['balls'] = 0
                    # увеличиваем номер попытки доля следующего шага
                    sessionStorage[user_id]['attempt'] += 1
        elif sessionStorage[user_id]['diff'] == 'easy':
            if attempt == 1:
                # если попытка первая, то случайным образом выбираем город для гадания
                city = random.choice(list(cars)[:5])
                # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
                while city in sessionStorage[user_id]['guessed_cities']:
                    city = random.choice(list(cars)[:5])
                # записываем город в информацию о пользователе
                sessionStorage[user_id]['city'] = city
                # добавляем в ответ картинку
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['title'] = 'Что это за машина?'
                res['response']['card']['image_id'] = cars[city][attempt - 1]
                res['response']['text'] = 'Тогда сыграем!'
                sessionStorage[user_id]['attempt'] += 1
            else:
                # сюда попадаем, если попытка отгадать не первая
                city = sessionStorage[user_id]['city']
                # проверяем есть ли правильный ответ в сообщение
                if req['request']['original_utterance'].lower() == 'помощь':
                    # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                    # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                    res['response']['text'] = 'Игра была сделана учеником Яндекс.Лицея!'
                elif req['request']['original_utterance'].lower() == city.lower():
                    # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                    # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.

                    # если попытка третья, то значит, что все картинки мы показали.
                    # В этом случае говорим ответ пользователю,
                    # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                    # Обратите внимание на этот шаг на схеме.
                    res['response'][
                        'text'] = f'Правильно. Что теперь: Машины, Города, Еда или вывести баллы?'
                    sessionStorage['balls'] += 1
                    if sessionStorage['balls'] < 0:
                        sessionStorage['balls'] = 0
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]
                    sessionStorage[user_id]['tip'] = ''
                    sessionStorage[user_id]['game_started'] = False
                    sessionStorage[user_id]['guessed_cities'].append(city)
                    sessionStorage[user_id]['attempt'] = 1
                    return
                else:
                    # если нет
                    if attempt == 3:
                        # если попытка третья, то значит, что все картинки мы показали.
                        # В этом случае говорим ответ пользователю,
                        # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                        # Обратите внимание на этот шаг на схеме.
                        res['response']['text'] = f'Вы пытались. Это {city.title()}. Что теперь: Машины, Города, Еда или вывести баллы?'
                        sessionStorage['balls'] -= 1
                        if sessionStorage['balls'] < 0:
                            sessionStorage['balls'] = 0
                        res['response']['buttons'] = [
                            {
                                'title': 'Города',
                                'hide': False
                            },
                            {
                                'title': 'Машины',
                                'hide': False
                            },
                            {
                                'tittle': 'Еда',
                                'hide': False
                            },
                            {
                                'tittle': 'Никакую',
                                'hide': False
                            }
                        ]
                        sessionStorage[user_id]['tip'] = ''
                        sessionStorage[user_id]['game_started'] = False
                        sessionStorage[user_id]['guessed_cities'].append(city)
                        sessionStorage[user_id]['attempt'] = 1
                        return
                    else:
                        # иначе показываем следующую картинку
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card'][
                            'title'] = 'Неправильно. Вот тебе дополнительное фото'
                        res['response']['card']['image_id'] = cars[city][attempt - 1]
                        res['response']['text'] = 'А вот и не угадал!'
                        sessionStorage['balls'] -= 1
                        if sessionStorage['balls'] < 0:
                            sessionStorage['balls'] = 0
                # увеличиваем номер попытки доля следующего шага
                sessionStorage[user_id]['attempt'] += 1
    elif sessionStorage['tip'] == 'food':
        if attempt == 1:
            # если попытка первая, то случайным образом выбираем город для гадания
            city = random.choice(list(food)[:5])
            # выбираем его до тех пор пока не выбираем город, которого нет в sessionStorage[user_id]['guessed_cities']
            while city in sessionStorage[user_id]['guessed_cities']:
                city = random.choice(list(food)[:5])
            # записываем город в информацию о пользователе
            sessionStorage[user_id]['city'] = city
            # добавляем в ответ картинку
            res['response']['card'] = {}
            res['response']['card']['type'] = 'BigImage'
            res['response']['card']['title'] = 'Как называется эта еда?'
            res['response']['card']['image_id'] = food[city][attempt - 1]
            res['response']['text'] = 'Тогда сыграем!'
            sessionStorage[user_id]['attempt'] += 1
        else:
            # сюда попадаем, если попытка отгадать не первая
            city = sessionStorage[user_id]['city']
            # проверяем есть ли правильный ответ в сообщение
            if req['request']['original_utterance'].lower() == 'помощь':
                # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.
                res['response']['text'] = 'Игра была сделана учеником Яндекс.Лицея!'
            elif req['request']['original_utterance'].lower() == city.lower():
                # если да, то добавляем город к sessionStorage[user_id]['guessed_cities'] и
                # отправляем пользователя на второй круг. Обратите внимание на этот шаг на схеме.

                # если попытка третья, то значит, что все картинки мы показали.
                # В этом случае говорим ответ пользователю,
                # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                # Обратите внимание на этот шаг на схеме.
                res['response'][
                    'text'] = f'Правильно. Что теперь: Машины, Города, Еда или вывести баллы?'
                sessionStorage['balls'] += 1
                if sessionStorage['balls'] < 0:
                    sessionStorage['balls'] = 0
                res['response']['buttons'] = [
                    {
                        'title': 'Города',
                        'hide': False
                    },
                    {
                        'title': 'Машины',
                        'hide': False
                    },
                    {
                        'tittle': 'Еда',
                        'hide': False
                    },
                    {
                        'tittle': 'Никакую',
                        'hide': False
                    }
                ]
                sessionStorage[user_id]['tip'] = ''
                sessionStorage[user_id]['game_started'] = False
                sessionStorage[user_id]['guessed_cities'].append(city)
                sessionStorage[user_id]['attempt'] = 1
                return
            else:
                # если нет
                if attempt == 3:
                    # если попытка третья, то значит, что все картинки мы показали.
                    # В этом случае говорим ответ пользователю,
                    # добавляем город к sessionStorage[user_id]['guessed_cities'] и отправляем его на второй круг.
                    # Обратите внимание на этот шаг на схеме.
                    res['response']['text'] = f'Вы пытались. Это {city.title()}. Что теперь: Машины, Города, Еда или вывести баллы?'
                    sessionStorage['balls'] -= 1
                    if sessionStorage['balls'] < 0:
                        sessionStorage['balls'] = 0
                    res['response']['buttons'] = [
                        {
                            'title': 'Города',
                            'hide': False
                        },
                        {
                            'title': 'Машины',
                            'hide': False
                        },
                        {
                            'tittle': 'Еда',
                            'hide': False
                        },
                        {
                            'tittle': 'Никакую',
                            'hide': False
                        }
                    ]
                    sessionStorage[user_id]['tip'] = ''
                    sessionStorage[user_id]['game_started'] = False
                    sessionStorage[user_id]['guessed_cities'].append(city)
                    sessionStorage[user_id]['attempt'] = 1
                    return
                else:
                    # иначе показываем следующую картинку
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card'][
                        'title'] = 'Неправильно. Вот тебе дополнительное фото'
                    res['response']['card']['image_id'] = food[city][attempt - 1]
                    res['response']['text'] = 'А вот и не угадал!'
                    sessionStorage['balls'] -= 1
                    if sessionStorage['balls'] < 0:
                        sessionStorage['balls'] = 0
            # увеличиваем номер попытки доля следующего шага
            sessionStorage[user_id]['attempt'] += 1



def get_city(req):
    # перебираем именованные сущности
    for entity in req['request']['nlu']['entities']:
        # если тип YANDEX.GEO, то пытаемся получить город(city), если нет, то возвращаем None
        if entity['type'] == 'YANDEX.GEO':
            # возвращаем None, если не нашли сущности с типом YANDEX.GEO
            return entity['value'].get('city', None)


def check_country(city, country):
    return cities[country] == city.lower()


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
