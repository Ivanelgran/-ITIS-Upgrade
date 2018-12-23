#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
import urllib.request
import pymysql.cursors

#Вставляем ip и возвращаем Страну
def ipToCountry(ip):
	url = 'http://api.ipstack.com/' + ip + '?access_key=dfe38edcd4541577119d91e7053a584a'
	data = urllib.request.urlopen(url).read().decode("utf-8")
	json_data = json.loads(data)
	if not json_data['country_name'] is None:
		return json_data['country_name']
	return 'none'
print('Добро пожаловать в парсер логов :)')
print('Пожалуйста введите путь к файлу')
a=input()
f = open(a, 'r')
#f = open('logs_lite.txt', 'r')

#Создаем словари и массивы
users = {}
product_categories = []
carts = {}
types_action = []
actions = []
users_cart_pay = []

users_products = {}

print('Изучаем строки:')
i = 1
for line in f:
    #Изучаем логи и разбиваем на составляющие
	date = re.search(r'\d{4}-\d{2}-\d{2}', line).group(0)
	time = re.search(r'\d{2}:\d{2}:\d{2}', line).group(0)
	action_name = re.search(r'\[\w{8}\]', line).group(0)[1:-1]
	ip = re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line).group(0)
	buf = re.search(r'(ttom.com).+', line).group(0)
	user_action = re.sub(r'(ttom.com/)', '', buf)
	type_action = 'none'
	action = {}
	action['category'] = 'none'
    #Фиксируем страну по IP
	if not ip in users:
		users[ip] = ipToCountry(ip)
		users_products[ip] = []
    #Фиксируем оплату
	if not user_action or re.match(r'pay\?', user_action):
		type_action = "other"
    #Фиксируем формирование корзины и её ID
	elif re.match(r'cart\?', user_action):
		type_action = "cart"
		buf = re.search(r'(cart_id=).+', user_action).group(0)
		cart_id = re.sub(r'(cart_id=)', '', buf)
		if not cart_id in carts:
			carts[cart_id] = 0
		user_cart_pay = {}
		user_cart_pay['user_cart'] = users_products.pop(ip)
		user_cart_pay['cart_id'] = cart_id
		user_cart_pay['ip'] = ip
		users_cart_pay.append(user_cart_pay)
    #Извлекаем ID корзины в случае успешной покупки
	elif re.match(r'success_pay_', user_action):
		type_action = "success_pay"
		buf = re.search(r'(success_pay_).+', user_action).group(0)
		cart_id = re.sub(r'(success_pay_)', '', buf)[:-1]
		carts[cart_id] = 1
    #Если один слэш в адресе - пользователь выбирает категорию
	elif user_action.count('/') is 1:
		type_action = "category"
		category = user_action[:-1]
		if not category in product_categories:
			product_categories.append(category)
		action['category'] = category
    #Если 2 слеша, то выбирает продукт
	elif user_action.count('/') is 2:
		type_action = "product"
		category = re.split(r'/', user_action)[0]
		if not category in product_categories:
			product_categories.append(category)
		if not ip in users_products:
			users_products[ip] = []
		if not category in users_products[ip]:
			users_products[ip].append(action_name)
		action['category'] = category

	if not type_action in types_action:
		types_action.append(type_action)

	action['date'] = date
	action['time'] = time
	action['ip'] = ip
	action['type_action'] = type_action
	action['name'] = action_name
	actions.append(action)

        
	print('Читаем строку №: ' + format(i))
	i = i + 1

f.close()


#Вводим данные от нашей БД
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='site',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

try:

    print("Таблица 'user': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for key, value in users.items() :
            try:
                sql = "INSERT INTO `user` (`ip`, `country`) VALUES (%s, %s)"
                cursor.execute(sql, (key, value))
                connection.commit()
                print("Таблица 'user': Загружаем строку #: " + format(i))
                i = i + 1
            except pymysql.err.IntegrityError as err:
                if 'Duplicate entry' in format(err) :
                    print("Внимание: Duplicate: {}".format(err))
                else :
                    raise pymysql.err.IntegrityError(err)
    print("Таблица 'user': Успешная загрузка данных!")

    print("Таблица 'product_category': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for value in product_categories :
            try:
                sql = "INSERT INTO `product_category` (`name`) VALUES (%s)"
                cursor.execute(sql, (value))
                connection.commit()
                print("Таблица 'product_category': Загружаем строку #: " + format(i))
                i = i + 1
            except pymysql.err.IntegrityError as err:
                if 'Duplicate entry' in format(err) :
                    print("Внимание: Duplicate: {}".format(err))
                else :
                    raise pymysql.err.IntegrityError(err)
    print("Таблица 'product_category': Успешная загрузка данных!")

    print("Таблица 'action_type': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for value in types_action :
            try:
                sql = "INSERT INTO `action_type` (`name`) VALUES (%s)"
                cursor.execute(sql, (value))
                connection.commit()
                print("Таблица 'action_type': Загружаем строку #: " + format(i))
                i = i + 1
            except pymysql.err.IntegrityError as err:
                if 'Duplicate entry' in format(err) :
                    print("Внимание: Duplicate: {}".format(err))
                else :
                    raise pymysql.err.IntegrityError(err)
    print("Таблица 'action_type': Успешная загрузка данных!")

    print("Таблица 'cart': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for key, value in carts.items() :
            try:
                sql = "INSERT INTO `cart` (`id_cart`, `success_pay_flag`) VALUES (%s, %s)"
                if value is 1:
                    cursor.execute(sql, (key, '1'))
                else :
                    cursor.execute(sql, (key, '0'))
                connection.commit()
                print("Таблица 'cart': Загружаем строку #: " + format(i))
                i = i + 1
            except pymysql.err.IntegrityError as err:
                if 'Duplicate entry' in format(err) :
                    print("Внимание: Duplicate: {}".format(err))
                else :
                    raise pymysql.err.IntegrityError(err)
 
    print("Таблица 'cart': Успех!")

    print("Таблица 'action': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for action in actions :
            sql = "SELECT `id` FROM `user` WHERE `ip`=%s"
            cursor.execute(sql, (action['ip']))
            _user = cursor.fetchone()['id']

            sql = "SELECT `id` FROM `action_type` WHERE `name`=%s"
            cursor.execute(sql, (action['type_action']))
            _action_type = cursor.fetchone()['id']

            _product_category = 'none'
            if not action['category'] is 'none' :
                sql = "SELECT `id` FROM `product_category` WHERE `name`=%s"
                cursor.execute(sql, (action['category']))
                _product_category = cursor.fetchone()['id']

            try:
                if not _product_category is 'none' :
                    sql = "INSERT INTO `action` (`datetime`, `user` , `action_type` , `product_category` , `name`) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (action['date'] + ' ' + action['time'], _user, _action_type, _product_category, action['name']))
                else :
                    sql = "INSERT INTO `action` (`datetime`, `user` , `action_type` , `name`) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (action['date'] + ' ' + action['time'], _user, _action_type, action['name']))
                connection.commit()
                print("Таблица 'action': Вставляем строку #: " + format(i))
                i = i + 1
            except pymysql.err.IntegrityError as err:
                if 'Duplicate entry' in format(err) :
                    print("Внимание: Duplicate: {}".format(err))
                else :
                    raise pymysql.err.IntegrityError(err)
    print("Таблица 'action': Успешная загрузка данных!")

    print("Таблица 'cart_to_user': Загружаем данные...")
    i = 1
    with connection.cursor() as cursor:
        for value in users_cart_pay :
            sql = "SELECT `id` FROM `user` WHERE `ip`=%s"
            cursor.execute(sql, (value['ip']))
            _user = cursor.fetchone()['id']

            sql = "SELECT `id` FROM `cart` WHERE `id_cart`=%s"
            cursor.execute(sql, (value['cart_id']))
            _cart = cursor.fetchone()['id']

            for action_name in value['user_cart'] :
                sql = "SELECT `id` FROM `action` WHERE `name`=%s"
                cursor.execute(sql, (action_name))
                _action = cursor.fetchone()['id']

                try:
                    sql = "INSERT INTO `cart_to_user` (`user`, `cart`, `action`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (_user, _cart, _action))
                    connection.commit()
                    print("Таблица 'cart_to_user': Загружаем строку #: " + format(i))
                    i = i + 1
                except pymysql.err.IntegrityError as err:
                    if 'Duplicate entry' in format(err) :
                        print("Внимание: Duplicate: {}".format(err))
                    else :
                        raise pymysql.err.IntegrityError(err)
    print("Таблица 'cart_to_user': Успешная загрузка данных!")


finally:
    connection.close()