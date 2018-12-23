# -*- coding: utf-8 -*-
# made by: Медведев Иван
from flask import Flask, render_template, json, request, jsonify
from flask_mysqldb import MySQL
import re

app = Flask(__name__)

#Тут вводят логин, пароль, имя БД
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'site'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#Выводим страницы по переходам с кнопки
@app.route('/')
def index():
    return render_template('form.html')
	
@app.route('/form1')
def form1():
    return render_template('form1.html')

@app.route('/form2')
def form2():
    return render_template('form2.html')
	
@app.route('/form')
def form():
    return render_template('form.html')

#Из AJAX запроса мы получаем категорию товара и подставляем в SQL запрос
@app.route('/process2', methods=['POST'])
def process2():
    category = request.form["category"]
    cur = mysql.connection.cursor()
    data = {'category': category}
    query="SELECT `times`.`time` \
               FROM( \
               (SELECT count(*) as `count`, 'ночью (00:00 - 06:00)' as `time` \
               FROM `action` \
               WHERE time(`datetime`) BETWEEN '00:00:00' AND '05:59:59' \
               AND `product_category`=(SELECT `id` FROM `product_category` WHERE `name`='{category}') \
               )UNION( \
               SELECT count(*) as `count`, 'утром (06:00 - 12:00)' as `time` \
               FROM `action` \
               WHERE time(`datetime`) BETWEEN '06:00:00' AND '11:59:59' \
               AND `product_category`=(SELECT `id` FROM `product_category` WHERE `name`='{category}') \
               )UNION( \
               SELECT count(*) as `count`, 'днём (12:00 - 18:00)' as `time` \
               FROM `action` \
               WHERE time(`datetime`) BETWEEN '12:00:00' AND '17:59:59' \
               AND `product_category`=(SELECT `id` FROM `product_category` WHERE `name`='{category}') \
               )UNION( \
               SELECT count(*) as `count`, 'вечером (18:00 - 0:00)' as `time` \
               FROM `action` \
               WHERE time(`datetime`) BETWEEN '18:00:00' AND '23:59:59' \
               AND `product_category`=(SELECT `id` FROM `product_category` WHERE `name`='{category}') \
               )) as `times` \
               ORDER BY `times`.`count` DESC"
    cur.execute(query.format(**data))
    rv = cur.fetchall()
    if category:
	
          return jsonify({'category' : 'Интересно, но чаще всего этот товар просматривают  '+ str(rv[0]['time'])+ '. И с чем это связано?'})
    
    return jsonify({'error' : 'Потеряно!'})
	
@app.route('/process1', methods=['POST'])
def process1():
    category = request.form["category"]
    cur = mysql.connection.cursor()
    data = {'category': category}
    query="SELECT user.country , count(*) as count_actions FROM user, action \
               WHERE user.id=action.user \
               AND user.country IN ('China', 'Germany', 'United States', 'Japan', 'United Kingdom') \
               AND action.product_category=(SELECT id FROM product_category WHERE name='{category}') \
               GROUP BY user.country \
               ORDER BY count_actions DESC"
    cur.execute(query.format(**data))
    rv = cur.fetchall()
    if category:
	
         return jsonify({'category' : 'Этим товаром чаще всего интересуются в '+ str(rv[0]['country'])+ ', целых - ' + str(rv[0]['count_actions']) + ' раз!'})
    
    return jsonify({'error' : 'Ну и где Ваши данные?!'})


@app.route('/process', methods=['POST'])
def process():
    inputDate = request.form["inputDate"]
    outputDate = request.form["outputDate"]
    cur = mysql.connection.cursor()
    data = {'inputDate': inputDate, 'outputDate': outputDate}
    query="SELECT count(*) as count \
                 FROM \
                 ( \
                         SELECT new.user, count(*) as 'count' \
                         FROM (select user from action where action_type=5 and date(datetime) between '{inputDate}' and '{outputDate}') as new\
                         GROUP BY new.user \
                         ORDER BY count  DESC \
                 ) as neew \
                 WHERE neew.count>1"
    cur.execute(query.format(**data))
    rv = cur.fetchall()
    return jsonify({'inputDate' : 'За данный период пользователи приобрели что-то повторно ' + str(rv[0]['count'])+ ' раз. Видимо у Вас не так всё плохо ;)'})

if __name__ == '__main__':
	app.run(debug=True)