from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import pyrostep
import sqlite3
import requests
from datetime import datetime, date, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import time
import asyncio
import sys
from PIL import Image
import urllib.request
import json
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

app = Client("Bot_account", api_id="YOUR API ID", api_hash="YOUR API HASH", bot_token="BOT TOKEN")

pyrostep.listen(app)

requests_dict = {}
reports_dict = {}

@app.on_message(filters.command(commands=["start", "accounts"]))
async def start_bot(client, message):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("Привязанные аккаунты", callback_data=f"my_accs")]])
    await app.send_message(chat_id=message.chat.id, text="Бот BerryStats приветствует вас!\U0001F44B\n\nДля продолжения воспользуйтесь кнопками ниже\U00002B07", reply_markup=markup)

@app.on_message(filters.command(commands=["work_send"]))
async def work_sender(client, message):
    await sender()
    await app.send_message(chat_id=message.chat.id, text="Готово!")

@app.on_message(filters.command(commands=["reports"]))
async def report(client, message):
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отчёт по операциям", callback_data=f"report_operations")], [InlineKeyboardButton("Отчёт по остаткам", callback_data=f"report_overs")], [InlineKeyboardButton(text="Привязанные токены\U0001F519", callback_data="my_accs")]])
    await app.send_message(chat_id=message.chat.id, text="\U0001F4C3Какой отчёт вам интересен?", reply_markup=markup)


@app.on_callback_query()
async def answer(client, function_call):
    if function_call.data == "my_accs":
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute('SELECT name, api, num FROM Sellers WHERE id = ?', (function_call.message.chat.id,))
        sells = cursor.fetchall()
        connection.close()
        if sells == []:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("\U0001F195Привязать аккаунт продавца", callback_data="new_sell")]])
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F193Вы не привязали ни одного аккаунта продавца\n\nВоспользуйтесь кнопкой ниже\U00002B07", reply_markup=markup, message_id=function_call.message.id)
        else:
            markup_array = []
            for sell in sells:
                markup_array.append([InlineKeyboardButton(f"{sell[0]}", callback_data=f"api_sell{sell[2]}")])
            markup_array.append([InlineKeyboardButton("\U0001F195Привязать аккаунт продавца", callback_data="new_sell")])
            markup = InlineKeyboardMarkup(markup_array)
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="Для управления привязанными аккаунтами воспользуйтесь кнопками\U00002B07", reply_markup=markup, message_id=function_call.message.id)
    elif function_call.data == "new_sell":
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Temp WHERE id = ?", (function_call.message.chat.id,))
        reg = cursor.fetchall()
        if reg != []:
            cursor.execute('DELETE FROM Temp WHERE id = ?', (function_call.message.chat.id,))
            connection.commit()
        connection.close()
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="Придумайте название аккаунта\U0001F520", message_id=function_call.message.id)
        await pyrostep.register_next_step(function_call.message.chat.id, add_name)
    elif "api_sell" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute('SELECT name, notific, api, is_supp FROM Sellers WHERE num = ?', ((function_call.data)[8:],))
        token = cursor.fetchall()
        if token[0][1] == True:
            notific = "Включены\U0001F50A"
            notific_do = "\U0001F515Отключить уведомления"
        else:
            notific = "Отключены\U0001F508"
            notific_do = "\U0001F50AВключить уведомления"
        if token[0][3] == True:
            fast = "Включен\U0001F680"
            fast_do = "\U0001F4F4Выкл. Fast Mode"
        else:
            fast = "Выключен\U0001F4F4"
            fast_do = "\U0001F680Вкл. Fast Mode"

        markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=notific_do, callback_data=f"notific{(function_call.data)[8:]}"), InlineKeyboardButton(text=fast_do, callback_data=f"fast{(function_call.data)[8:]}")], [InlineKeyboardButton(text="\U0000274CОтвязать токен", callback_data=f"del_token{(function_call.data)[8:]}")], [InlineKeyboardButton(text="Назад\U000025C0", callback_data="my_accs")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U0001F4CDВы выбрали токен **{token[0][0]}**\n\U0001F4CDТокен:\n`{token[0][2]}`\n\U0001F4CDУведомления: {notific}\n\U0001F4CDFast Mode: {fast}", reply_markup=markup, message_id=function_call.message.id)
        connection.close()
    elif "notific" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute('SELECT name, notific FROM Sellers WHERE num = ?', (function_call.data)[7:],)
        name = cursor.fetchall()
        if name[0][1] == 1:
            notific = False
            txt_not = "отключены"
        else:
            notific = True
            txt_not = "включены"
        cursor.execute('UPDATE Sellers SET notific = ?, last = ?, last_canc = ?, last_sell = ? WHERE num = ?', (notific, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), (function_call.data)[7:]))
        connection.commit()
        connection.close()
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U00002705Уведомления для токена **{name[0][0]}** успешно {txt_not}", message_id=function_call.message.id)
    elif "fast" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute('SELECT name, is_supp FROM Sellers WHERE num = ?', ((function_call.data)[4:],))
        name = cursor.fetchall()
        if name[0][1] == 1:
            notific = False
            await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U00002705Fast Mode для токена **{name[0][0]}** успешно отключен! Его можно включить в любой момент", message_id=function_call.message.id)
        else:
            notific = True
            await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U00002705Fast Mode для токена **{name[0][0]}** успешно включен!\U0001F389\n\nТеперь уведомления о новых заказах будут приходить в несколько раз быстрее!\U0001F51C Но регион получателя показываться не будет, потому что в данном режиме бот проверяет остатки товаров на складах\U0001F7E3", message_id=function_call.message.id)
        cursor.execute('UPDATE Sellers SET is_supp = ? WHERE num = ?', (notific, (function_call.data)[4:]))
        connection.commit()
        connection.close()
    elif "del_token" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute('SELECT name FROM Sellers WHERE num = ?', ((function_call.data)[9:],))
        name = cursor.fetchall()
        cursor.execute('DELETE FROM Sellers WHERE num = ?', ((function_call.data)[9:],))
        connection.commit()
        connection.close()
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U00002705Токен **{name[0][0]}** успешно отвязан", message_id=function_call.message.id)
    elif "report_operations" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name, num FROM Sellers WHERE id = ?", (function_call.message.chat.id,))
        accounts = cursor.fetchall()
        if function_call.data == "report_operations":
            if len(accounts) != 1 and len(accounts) != 0:
                markup_array = []
                for account in accounts:
                    markup_array.append([InlineKeyboardButton(f"{account[0]}", callback_data=f"report_operations{account[1]}")])
                markup_array.append([InlineKeyboardButton(text="Привязанные токены\U0001F519", callback_data="my_accs")])
                markup = InlineKeyboardMarkup(markup_array)
                await app.edit_message_text(chat_id=function_call.message.chat.id, text="Выберите токен, для которого хотите посмотреть **отчёт по операциям**\U00002B07", reply_markup=markup, message_id=function_call.message.id)
            elif len(accounts) == 1:
                await report_operations(accounts[0][1], function_call.message)
            else:
                await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CОшибка! Вы не привязали ни одного аккаунта продавца. Для привязки аккаунта воспользуйтесь командой /accounts",  message_id=function_call.message.id)
        else:
            await report_operations((function_call.data)[17:], function_call.message)
        connection.close()
    elif "report_oper_today" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Смотрю заказы...", message_id=function_call.message.id)
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int((function_call.data)[18:]),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[(function_call.data)[18:]][0]
        sales_many = requests_dict[(function_call.data)[18:]][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        back_comission = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=function_call.message.id)
            return
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=function_call.message.id)
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Считаю продажи...", message_id=function_call.message.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Подвожу итог...", message_id=function_call.message.id)
        text = f"**Отчёт по операциям** за {datetime.now().strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{(function_call.data)[18:]}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{(function_call.data)[18:]}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{(function_call.data)[18:]}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{(function_call.data)[18:]}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{(function_call.data)[18:]}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{(function_call.data)[18:]}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{(function_call.data)[18:]}")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=text, message_id=function_call.message.id, reply_markup=markup)
    elif "report_oper_yesterday" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Смотрю заказы... Подождите", message_id=function_call.message.id)
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int((function_call.data)[21:]),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[(function_call.data)[21:]][0]
        sales_many = requests_dict[(function_call.data)[21:]][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=function_call.message.id)
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Считаю продажи...", message_id=function_call.message.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Подвожу итог...", message_id=function_call.message.id)
        text = f"**Отчёт по операциям** за {(datetime.now() - timedelta(days=1)).strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{(function_call.data)[21:]}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{(function_call.data)[21:]}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{(function_call.data)[21:]}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{(function_call.data)[21:]}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{(function_call.data)[21:]}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{(function_call.data)[21:]}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{(function_call.data)[21:]}")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=text, message_id=function_call.message.id, reply_markup=markup)
    elif "report_oper_week_now" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Смотрю заказы... Подождите.", message_id=function_call.message.id)
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int((function_call.data)[20:]),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[(function_call.data)[20:]][0]
        sales_many = requests_dict[(function_call.data)[20:]][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=function_call.message.id)
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Считаю продажи...", message_id=function_call.message.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Подвожу итог...", message_id=function_call.message.id)
        text = f"**Отчёт по операциям** за {(datetime.now() - timedelta(days=datetime.now().weekday())).strftime(format='%d.%m.%Y')} - {(datetime.now()).strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{(function_call.data)[20:]}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{(function_call.data)[20:]}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{(function_call.data)[20:]}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{(function_call.data)[20:]}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{(function_call.data)[20:]}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{(function_call.data)[20:]}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{(function_call.data)[20:]}")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=text, message_id=function_call.message.id, reply_markup=markup)
    elif "report_oper_week_pred" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Смотрю заказы... Подождите.", message_id=function_call.message.id)
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int((function_call.data)[21:]),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[(function_call.data)[21:]][0]
        sales_many = requests_dict[(function_call.data)[21:]][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=function_call.message.id)
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=(datetime.now().weekday() + 7))).strftime("%Y-%m-%d"), "%Y-%m-%d") and datetime.strptime(order['date'][:10], "%Y-%m-%d") < datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=(datetime.now().weekday() + 7))).strftime("%Y-%m-%d"), "%Y-%m-%d") and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") < datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Считаю продажи...", message_id=function_call.message.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=(datetime.now().weekday() + 7))).strftime("%Y-%m-%d"), "%Y-%m-%d") and datetime.strptime(sale['date'][:10], "%Y-%m-%d") < datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= datetime.strptime((date.today() - timedelta(days=(datetime.now().weekday() + 7))).strftime("%Y-%m-%d"), "%Y-%m-%d") and datetime.strptime(sale['date'][:10], "%Y-%m-%d") < datetime.strptime((date.today() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d"), "%Y-%m-%d") and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F551Подвожу итог...", message_id=function_call.message.id)
        text = f"**Отчёт по операциям** за {(datetime.now() - timedelta(days=(datetime.now().weekday() + 7))).strftime(format='%d.%m.%Y')} - {(datetime.now() - timedelta(days=(datetime.now().weekday() + 1))).strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{(function_call.data)[21:]}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{(function_call.data)[21:]}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{(function_call.data)[21:]}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{(function_call.data)[21:]}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{(function_call.data)[21:]}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{(function_call.data)[21:]}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{(function_call.data)[21:]}")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=text, message_id=function_call.message.id, reply_markup=markup)
    elif "report_oper_data" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U0001F4C6Введите произвольную дату в формате {(datetime.now()).strftime(format='%d.%m.%Y')}\n\nДоступны данные не ранее {(datetime.now() - timedelta(days=90)).strftime(format='%d.%m.%Y')}", message_id=function_call.message.id)
        await pyrostep.register_next_step(function_call.message.chat.id, one_data, kwargs={"num": (function_call.data)[16:]})
    elif "report_oper_diap" in function_call.data:
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=f"\U0001F4C6Введите диапазон дат в формате {(datetime.now() - timedelta(days=7)).strftime(format='%d.%m.%Y')} - {(datetime.now()).strftime(format='%d.%m.%Y')}\n\nДоступны данные не ранее {(datetime.now() - timedelta(days=90)).strftime(format='%d.%m.%Y')}", message_id=function_call.message.id)
        await pyrostep.register_next_step(function_call.message.chat.id, many_data, kwargs={"num": (function_call.data)[16:]})
    elif "back_to_rep" in function_call.data:
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{(function_call.data)[11:]}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{(function_call.data)[11:]}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{(function_call.data)[11:]}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{(function_call.data)[11:]}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{(function_call.data)[11:]}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{(function_call.data)[11:]}")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text=reports_dict[int((function_call.data)[11:])], reply_markup=markup, message_id=function_call.message.id)
    elif "report_overs" in function_call.data:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name, num FROM Sellers WHERE id = ?", (function_call.message.chat.id,))
        accounts = cursor.fetchall()
        if function_call.data == "report_overs":
            if len(accounts) != 1 and len(accounts) != 0:
                markup_array = []
                for account in accounts:
                    markup_array.append([InlineKeyboardButton(f"{account[0]}", callback_data=f"report_overs{account[1]}")])
                markup_array.append([InlineKeyboardButton(text="Привязанные токены\U0001F519", callback_data="my_accs")])
                markup = InlineKeyboardMarkup(markup_array)
                await app.edit_message_text(chat_id=function_call.message.chat.id, text="Выберите токен, для которого хотите посмотреть **отчёт по операциям**\U00002B07", reply_markup=markup, message_id=function_call.message.id)
            elif len(accounts) == 1:
                await report_overs(accounts[0][1], function_call.message)
            else:
                await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0000274CОшибка! Вы не привязали ни одного аккаунта продавца. Для привязки аккаунта воспользуйтесь командой /accounts",  message_id=function_call.message.id)
        else:
            await report_overs((function_call.data)[12:], function_call.message)
        connection.close()
    elif function_call.data == "rep_back_now":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Отчёт по операциям", callback_data=f"report_operations")], [InlineKeyboardButton("Отчёт по остаткам", callback_data=f"report_overs")], [InlineKeyboardButton(text="Привязанные токены\U0001F519", callback_data="my_accs")]])
        await app.edit_message_text(chat_id=function_call.message.chat.id, text="\U0001F4C3Какой отчёт вам интересен?", reply_markup=markup, message_id=function_call.message.id)

async def one_data(client, message, num: str = True):
    try:
        need_date = datetime.strptime(message.text, "%d.%m.%Y") 
        mess = await app.send_message(chat_id=message.chat.id, text="\U0001F551Смотрю заказы... Подождите")
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int(num),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[num][0]
        sales_many = requests_dict[num][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        back_comission = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
            return
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.send_message(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут")
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") == need_date and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") == need_date and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Считаю комиссии...", message_id=mess.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == need_date and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == need_date and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Подвожу итог...", message_id=mess.id)
        text = f"**Отчёт по операциям** за {need_date.strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{num}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{num}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{num}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{num}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{num}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{num}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{num}")]])
        await app.edit_message_text(chat_id=message.chat.id, text=text, message_id=mess.id, reply_markup=markup)
    except:
        if message.text == "/start" or message.text == "/accounts" or message.text == "/reports":
            return
        await app.send_message(chat_id=message.chat.id, text=f"\U0000274CНеверный формат даты!\n\nВведите произвольную дату в формате {(datetime.now()).strftime(format='%d.%m.%Y')}\n\nДоступны данные не ранее {(datetime.now() - timedelta(days=90)).strftime(format='%d.%m.%Y')}")
        await pyrostep.register_next_step(message.chat.id, one_data, kwargs={"num": num})

async def many_data(client, message, num: str = True):
    try:
        try:
            need_date1 = datetime.strptime(message.text[:10], "%d.%m.%Y")
            need_date2 = datetime.strptime(message.text[13:], "%d.%m.%Y")
        except:
            need_date1 = datetime.strptime(message.text[:10], "%d.%m.%Y")
            need_date2 = datetime.strptime(message.text[11:], "%d.%m.%Y")
        mess = await app.send_message(chat_id=message.chat.id, text="\U0001F551Смотрю заказы... Подождите")
        def count_comission(api_key, order, warehouses):
            api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {
                "settings": {
                    "sort": {
                        "ascending": False
                    },
                    "filter": {
                        "textSearch": f"{order['nmId']}",
                        "withPhoto": -1
                    },
                    "cursor": {
                        "limit": 1
                    }
                }
            }
            response = requests.post(api_url, headers=headers, json=params, timeout=10)
            data2 = response.json()
            for warehouse in warehouses["response"]['data']["warehouseList"]:
                if warehouse["warehouseName"] == order['warehouseName']:
                    need_warehouse = warehouse
                    break
            width = data2['cards'][0]['dimensions']['width']
            height = data2['cards'][0]['dimensions']['height']
            length = data2['cards'][0]['dimensions']['length']
            first_liter = need_warehouse["boxDeliveryBase"]
            next_liter = need_warehouse["boxDeliveryLiter"]
            first_liter = float(f"{first_liter}".replace(',','.'))
            next_liter = float(f"{next_liter}".replace(',','.'))
            v = round((width * height * length / 1000), 1)
            cost = round((first_liter + (v-1.0)*next_liter), 1)
            return cost
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT api FROM Sellers WHERE num = ?", (int(num),))
        api = cursor.fetchall()
        api_key = api[0][0]
        connection.close()
        order_many = requests_dict[num][0]
        sales_many = requests_dict[num][1]
        today_orders = 0
        today_orders_count = 0
        today_cansel = 0
        today_cansel_count = 0
        today_sales = 0
        today_sales_count = 0
        today_backs = 0
        today_backs_count = 0
        today_orders_dict = {}
        today_cansel_dict = {}
        today_sales_dict = {}
        today_backs_dict = {}
        itcomsum = 0
        back_comission = 0
        try:
            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"date": date.today()}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            warehouses = response.json()
        except:
            await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
            return
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") >= need_date1 and datetime.strptime(order['date'][:10], "%Y-%m-%d") <= need_date2 and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_orders_dict:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_orders_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") >= need_date1 and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") <= need_date2 and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
                if f"{order['supplierArticle']} ({order['techSize']})" not in today_cansel_dict:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] = 1
                else:
                    today_cansel_dict[f"{order['supplierArticle']} ({order['techSize']})"] += 1
        await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Считаю комиссии...", message_id=mess.id)
        back_comission = 0
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= need_date1 and datetime.strptime(sale['date'][:10], "%Y-%m-%d") <= need_date2 and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_sales_dict:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_sales_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") >= need_date1 and datetime.strptime(sale['date'][:10], "%Y-%m-%d") <= need_date2 and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
                back_comission += (sale['priceWithDisc'] - sale['finishedPrice'])
                if f"{sale['supplierArticle']} ({sale['techSize']})" not in today_backs_dict:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] = 1
                else:
                    today_backs_dict[f"{sale['supplierArticle']} ({sale['techSize']})"] += 1
        today_orders_dict = dict(sorted(today_orders_dict.items()))
        today_cansel_dict = dict(sorted(today_cansel_dict.items()))
        today_sales_dict = dict(sorted(today_sales_dict.items()))
        today_backs_dict = dict(sorted(today_backs_dict.items()))
        await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Подвожу итог...", message_id=mess.id)
        text = f"**Отчёт по операциям** за {need_date1.strftime(format='%d.%m.%Y')} - {need_date2.strftime(format='%d.%m.%Y')}. Актуален на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        text += f"\U0001F4CD**Заказано** {today_orders} шт. на сумму {round(today_orders_count)}₽\n"
        i = 0
        for el in today_orders_dict:
            i += 1
            text += f"{i}) {el} - {today_orders_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Отказов** {today_cansel} шт. на сумму {round(today_cansel_count)}₽\n"
        i = 0
        for el in today_cansel_dict:
            i += 1
            text += f"{i}) {el} - {today_cansel_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Продано** {today_sales} шт. на сумму {round(today_sales_count)}₽\n"
        i = 0
        for el in today_sales_dict:
            i += 1
            text += f"{i}) {el} - {today_sales_dict[f'{el}']} шт.\n"
        text += f"\n\U0001F4CD**Возвращено на склад** {today_backs} шт. на сумму {round(today_backs_count)}₽\n"
        i = 0
        for el in today_backs_dict:
            i += 1
            text += f"{i}) {el} - {today_backs_dict[f'{el}']} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{num}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{num}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{num}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{num}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{num}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{num}")], [InlineKeyboardButton("Назад\U000025C0", callback_data=f"back_to_rep{num}")]])
        await app.edit_message_text(chat_id=message.chat.id, text=text, message_id=mess.id, reply_markup=markup)
    except:
        if message.text == "/start" or message.text == "/accounts" or message.text == "/reports":
            return
        await app.send_message(chat_id=message.chat.id, text=f"\U0000274CНеверный формат даты!\n\nВведите диапазон дат в формате {(datetime.now() - timedelta(days=7)).strftime(format='%d.%m.%Y')} - {(datetime.now()).strftime(format='%d.%m.%Y')}\n\nДоступны данные не ранее {(datetime.now() - timedelta(days=90)).strftime(format='%d.%m.%Y')}")
        await pyrostep.register_next_step(message.chat.id, many_data, kwargs={"num": num})



async def add_name(client, message):
    connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Temp (id, name) VALUES (?, ?)", (message.chat.id, message.text))
    connection.commit()
    connection.close()
    await app.send_message(chat_id=message.chat.id, text='\U0001F4CEТеперь вам нужно отправить ключ из раздела "Доступ к API". Для этого:\n\n**1.** Зайдите в личный кабинет в Wildberries -> Настройки -> Доступ к новому API.\n**2.** Нажмите "Создать новый токен".\n**3.** Введите имя "BerryStatsBot". Так потом вы сможете понять, для какого сервиса выпущен ключ.\n\U0000203CВажно!! Для каждого сервиса выпускайте новый ключ во избежание задержек и ошибок в получении данных.\n**4.** Выберите тип ключа "Контент", "Поставки", "Статистика", "Аналитика", "Вопросы и отзывы".\n**5.** Скопируйте токен и отправьте в этот чат.\n\n\U0000203CЕсли бот не сможет проверить ключ, повторите отправку через пару часов. Иногда Wildberries не сразу обновлет информацию о новом ключе')
    await pyrostep.register_next_step(message.chat.id, add_api)

async def add_api(client, message):
    await app.send_message(chat_id=message.chat.id, text="\U0001F55DСекунду. Проверяю токен")
    test_url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
    test_headers = {'Authorization': message.text, 'Content-Type': 'application/json'}
    test_params = {"dateFrom": (date.today() - timedelta(days=90)), "flag": 0}
    test_response = requests.get(test_url, headers=test_headers, params=test_params)
    if test_response.status_code != 200:
        await app.send_message(chat_id=message.chat.id, text="\U0000274CНе удалось подключиться к кабинету продавца по указанному токену.\n\U0001F50EПроверьте корректность токена и правильность выбранных категорий и повторите попытку с помощью команды /accounts")
        print(test_response.status_code)
        return
    test_response = test_response.json()
    test_url2 = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
    test_headers2 = {'Authorization': message.text, 'Content-Type': 'application/json'}
    test_params2 = {
        "settings": {
            "sort": {
            "ascending": False
            },
            "filter": {
                "withPhoto": -1
            },
            "cursor": {
                "limit": 100
            }
        }
    }
    test_response2 = requests.post(test_url2, headers=test_headers2, json=test_params2)
    test_url3 = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
    test_headers3 = {'Authorization': message.text, 'Content-Type': 'application/json'}
    test_response3 = requests.get(test_url3, headers=test_headers3)
    test_url4 = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
    test_headers4 = {'Authorization': message.text, 'Content-Type': 'application/json'}
    test_params4 = {"nmId": test_response[0]['nmId']}
    test_response4 = requests.get(test_url4, headers=test_headers4, params=test_params4)
    time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
    time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    test_url5 = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
    test_headers5 = {'Authorization': message.text, 'Content-Type': 'application/json'}
    test_params5 = {"nmIDs": [test_response[0]['nmId']], "period": {"begin": time_7, "end": time_now}, "page": 1}
    test_response5 = requests.post(test_url5, headers=test_headers5, json=test_params5)
    warehouses_url = 'https://supplies-api.wildberries.ru/api/v1/warehouses'
    warehouses_headers = {'Authorization': message.text, 'Content-Type': 'application/json'}
    warehouses_response = requests.get(warehouses_url, headers=warehouses_headers)
    if test_response2.status_code ==200 and test_response3.status_code == 200 and test_response4.status_code == 200 and test_response5.status_code == 200 and warehouses_response.status_code == 200:
        connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM Temp name WHERE id = ?", (message.chat.id,))
        name = cursor.fetchall()
        cursor.execute("SELECT id, name FROM Sellers WHERE api = ?", (message.text,))
        api = cursor.fetchall()
        if api == []:
            cursor.execute("INSERT INTO Sellers (id, api, name, notific, last, last_canc, last_sell, is_supp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (message.chat.id, message.text, name[0][0], True, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0))
            connection.commit()
            cursor.execute("SELECT num FROM Sellers WHERE api = ?", (message.text,))
            num = cursor.fetchall()
            try:
                requests_dict[f'{num[0][0]}'] = [test_response.json(), 0, 0]
            except:
                pass
            cards = test_response2.json()
            for card in cards['cards']:
                url = "https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm=" + str(card["nmID"])
                warehouses_response = requests.get(url = url, timeout=10)
                warehouses = warehouses_response.json()
                for size in warehouses['data']['products'][0]['sizes']:
                    for stock in size['stocks']:
                        cursor.execute('INSERT INTO Supplies (api_key, id, nmId, size, whouse, osts) VALUES (?, ?, ?, ?, ?, ?)', (message.text, message.chat.id, card["nmID"], size["origName"], stock['wh'], stock['qty']))
                connection.commit()
            await app.send_message(chat_id=message.chat.id, text=f"\U00002705Аккаунт продавца **{name[0][0]}** успешно привязан\n\n\U00002699Для управления аккаунтами введите /accounts")
        elif api != [] and api[0][0] == message.chat.id:
            await app.send_message(chat_id=message.chat.id, text=f"\U0000274CДанный токен уже был привязан вами. \U0001F50EВы найдёте его с помощью команды /accounts под именем **{api[0][1]}**")
        else:
            await app.send_message(chat_id=message.chat.id, text="\U0000274CДругой пользователь уже привязал данный токен. Чтобы подключить этот кабинет продавца, создайте другой токен и повторите попытку с помощью команды\n/accounts")
            try:
                await app.send_message(chat_id=api[0][0], text=f"\U0000203CВнимание! Другой пользователь попытался привязать принадлежащий вам токен **{api[0][1]}**.\n\U00002049Если вы не знаете, кто это сделал, в целях безопасности удалите токен **{api[0][1]}** с помощью команды /accounts и создайте новый в личном кабинете продавца, после чего привяжите его с помощью команды /accounts")
            except:
                pass
        
        connection.close()
    else:
        print(test_response2.status_code, test_response3.status_code, test_response4.status_code, test_response5.status_code, warehouses_response.status_code)
        await app.send_message(chat_id=message.chat.id, text="\U0000274CНе удалось подключиться к кабинету продавца по указанному токену.\n\U0001F50EПроверьте корректность токена и правильность выбранных категорий и повторите попытку с помощью команды /accounts")

async def report_operations(num, message):
    await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Смотрю заказы...", message_id=message.id)
    connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
    cursor = connection.cursor()
    cursor.execute("SELECT api FROM Sellers WHERE num = ?", (num,))
    api = cursor.fetchall()
    api_key = api[0][0]
    connection.close()
    api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
    headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
    params = {"dateFrom": (date.today() - timedelta(days=90))}
    response = requests.get(api_url, headers=headers, params=params, timeout=10)
    api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"
    headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
    params = {"dateFrom": (date.today() - timedelta(days=90))}
    response2 = requests.get(api_url, headers=headers, params=params, timeout=10)
    if response.status_code == 400 or response.status_code == 401 or response.status_code == 404 or response2.status_code == 400 or response2.status_code == 401 or response2.status_code == 404:
        print(response.status_code)
        print(response2.status_code)
        await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
    else:
        try:
            text = f"**Отчёт по операциям** на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
            if response.status_code == 429 and response2.status_code == 200:
                order_many = requests_dict[f'{num}'][0]
                sales_many = response2.json()
                requests_dict[num][1] = sales_many
            elif response2.status_code == 429 and response.status_code == 200:
                sales_many = requests_dict[f'{num}'][1]
                order_many = response.json()
                requests_dict[num][0] = order_many
            elif response.status_code == 429 and response2.status_code == 429:
                order_many = requests_dict[f'{num}'][0]
                sales_many = requests_dict[f'{num}'][1]
            else:
                order_many = response.json()
                sales_many = response2.json()
                requests_dict[f'{num}'] = [order_many, sales_many]
        except:
            await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
            return
        today_orders = 0
        today_cansel = 0
        today_sales = 0
        today_backs = 0
        yesterday_orders = 0
        yesterday_cansel = 0
        yesterday_sales = 0
        yesterday_backs = 0
        week_orders = 0
        week_cansel = 0
        week_sales = 0
        week_backs = 0
        month_orders = 0
        month_cansel = 0
        month_sales = 0
        month_backs = 0
        today_orders_count = 0
        today_cansel_count = 0
        today_sales_count = 0
        today_backs_count = 0
        yesterday_orders_count = 0
        yesterday_cansel_count = 0
        yesterday_sales_count = 0
        yesterday_backs_count = 0
        week_orders_count = 0
        week_cansel_count = 0
        week_sales_count = 0
        week_backs_count = 0
        month_orders_count = 0
        month_cansel_count = 0
        month_sales_count = 0
        month_backs_count = 0
        await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Считаю продажи...", message_id=message.id)
        for order in order_many:
            if order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                today_orders += 1
                today_orders_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                yesterday_orders += 1
                yesterday_orders_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=7)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                week_orders += 1
                week_orders_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=30)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == False:
                month_orders += 1
                month_orders_count += order['priceWithDisc']
            if order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                today_cansel += 1
                today_cansel_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                yesterday_cansel += 1
                yesterday_cansel_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=7)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                week_cansel += 1
                week_cansel_count += order['priceWithDisc']
            elif order['orderType'] == "Клиентский" and datetime.strptime(order['cancelDate'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=30)).strftime("%Y-%m-%d"), "%Y-%m-%d") and order['isCancel'] == True:
                month_cansel += 1
                month_cansel_count += order['priceWithDisc']
        for sale in sales_many:
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                today_sales += 1
                today_sales_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                yesterday_sales += 1
                yesterday_sales_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=7)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                week_sales += 1
                week_sales_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=30)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "S":
                month_sales += 1
                month_sales_count += sale['priceWithDisc']
            if sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today()).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                today_backs += 1
                today_backs_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                yesterday_backs += 1
                yesterday_backs_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=7)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                week_backs += 1
                week_backs_count += sale['priceWithDisc']
            elif sale['orderType'] == "Клиентский" and datetime.strptime(sale['date'][:10], "%Y-%m-%d") > datetime.strptime((date.today() - timedelta(days=30)).strftime("%Y-%m-%d"), "%Y-%m-%d")and sale['saleID'][0] == "R":
                month_backs += 1
                month_backs_count += sale['priceWithDisc']
        today_orders_count = round(today_orders_count)
        today_cansel_count = round(today_cansel_count)
        today_sales_count = round(today_sales_count)
        today_backs_count = round(today_backs_count)
        yesterday_orders_count = round(yesterday_orders_count)
        yesterday_cansel_count = round(yesterday_cansel_count)
        yesterday_sales_count = round(yesterday_sales_count)
        yesterday_backs_count = round(yesterday_backs_count)
        week_orders_count = round(week_orders_count)
        week_cansel_count = round(week_cansel_count)
        week_sales_count = round(week_sales_count)
        week_backs_count = round(week_backs_count)
        month_orders_count = round(month_orders_count)
        month_cansel_count = round(month_cansel_count)
        month_sales_count = round(month_sales_count)
        month_backs_count = round(month_backs_count)
        text += f"**Сегодня** {datetime.now().strftime(format='%d.%m.%Y')}\n\U0001F6D2Заказы: {today_orders} на {today_orders_count}₽\n\U0000274CОтмены: {today_cansel} на {today_cansel_count}₽\n\U0001F4B0Продажи: {today_sales} на {today_sales_count}₽\n\U0001F501Возвраты на склад WB: {today_backs} на {today_backs_count}₽\n\n"
        text += f"**Вчера** {(datetime.now() - timedelta(days=1)).strftime(format='%d.%m.%Y')}\n\U0001F6D2Заказы: {yesterday_orders} на {yesterday_orders_count}₽\n\U0000274CОтмены: {yesterday_cansel} на {yesterday_cansel_count}₽\n\U0001F4B0Продажи: {yesterday_sales} на {yesterday_sales_count}₽\n\U0001F501Возвраты на склад WB: {yesterday_backs} на {yesterday_backs_count}₽\n\n"
        text += f"**За неделю** {(datetime.now() - timedelta(days=6)).strftime(format='%d.%m.%Y')} - {datetime.now().strftime(format='%d.%m.%Y')}\n\U0001F6D2Заказы: {week_orders} на {week_orders_count}₽\n\U0000274CОтмены: {week_cansel} на {week_cansel_count}₽\n\U0001F4B0Продажи: {week_sales} на {week_sales_count}₽\n\U0001F501Возвраты на склад WB: {week_backs} на {week_backs_count}₽\n\n"
        text += f"**За месяц** {(datetime.now() - timedelta(days=29)).strftime(format='%d.%m.%Y')} - {datetime.now().strftime(format='%d.%m.%Y')}\n\U0001F6D2Заказы: {month_orders} на {month_orders_count}₽\n\U0000274CОтмены: {month_cansel} на {month_cansel_count}₽\n\U0001F4B0Продажи: {month_sales} на {month_sales_count}₽\n\U0001F501Возвраты на склад WB: {month_backs} на {month_backs_count}₽"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Сегодня", callback_data=f"report_oper_today_{num}"), InlineKeyboardButton("Вчера", callback_data=f"report_oper_yesterday{num}")], [InlineKeyboardButton("Текущая неделя", callback_data=f"report_oper_week_now{num}"), InlineKeyboardButton("Предыдущая неделя", callback_data=f"report_oper_week_pred{num}")], [InlineKeyboardButton("Выбрать дату", callback_data=f"report_oper_data{num}"), InlineKeyboardButton("Диапазон дат", callback_data=f"report_oper_diap{num}")]])
        reports_dict[num] = text
        await app.edit_message_text(chat_id=message.chat.id, text=text, message_id=message.id, reply_markup=markup)

async def report_overs(num, message):
    await app.edit_message_text(chat_id=message.chat.id, text="\U0001F551Отчёт создаётся...", message_id=message.id)
    connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
    cursor = connection.cursor()
    cursor.execute("SELECT api FROM Sellers WHERE num = ?", (num,))
    api = cursor.fetchall()
    api_key = api[0][0]
    connection.close()
    api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
    headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
    params = {"dateFrom": '2019-06-20'}
    response = requests.get(api_url, headers=headers, params=params, timeout=10)
    if response.status_code == 400 or response.status_code == 401 or response.status_code == 404:
        print(response.status_code)
        await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
    else:
        text = f"**Отчёт по остаткам** на {datetime.now().strftime(format='%d.%m.%Y %H:%M')}\n\n"
        try:
            if response.status_code == 429:
                stocks_many = requests_dict[f'{num}'][2]
            else:   
                stocks_many = response.json()
                if len(requests_dict[f'{num}']) == 2:
                    (requests_dict[f'{num}']).append(stocks_many)
                else:
                    requests_dict[f'{num}'][2] = stocks_many
        except:
            await app.edit_message_text(chat_id=message.chat.id, text="\U0000274CПроизошла ошибка при получении данных. Повторите попытку через пару минут", message_id=message.id)
            return
        home = 0
        to_client = 0
        from_client = 0
        home_count = 0
        to_client_count = 0
        from_client_count = 0
        home_dict = {}
        to_client_dict = {}
        from_client_dict = {}
        for stock in stocks_many:
            if stock['quantity'] != 0:
                if stock["subject"] not in home_dict:
                    home_dict[f"{stock['subject']}"] = stock['quantity']
                else:
                    home_dict[f"{stock['subject']}"] += stock['quantity']
                home += stock['quantity']
                home_count += (stock["Price"] - (stock["Price"] * stock["Discount"] / 100)) * stock['quantity']
            if stock['inWayToClient'] != 0:
                if stock["subject"] not in to_client_dict:
                    to_client_dict[f"{stock['subject']}"] = stock['inWayToClient']
                else:
                    to_client_dict[f"{stock['subject']}"] += stock['inWayToClient']
                to_client += stock['inWayToClient']
                to_client_count += (stock["Price"] - (stock["Price"] * stock["Discount"] / 100)) * stock['inWayToClient']
            if stock['inWayFromClient'] != 0:
                if stock["subject"] not in from_client_dict:
                    from_client_dict[f"{stock['subject']}"] = stock['inWayFromClient']
                else:
                    from_client_dict[f"{stock['subject']}"] += stock['inWayFromClient']
                from_client += stock['inWayFromClient']
                from_client_count += (stock["Price"] - (stock["Price"] * stock["Discount"] / 100)) * stock['inWayFromClient']
        from_client_dict = dict(sorted(from_client_dict.items()))
        home_dict = dict(sorted(home_dict.items()))
        to_client_dict = dict(sorted(to_client_dict.items()))
        text += f"\U0001F4CD**На складах**: {home} шт. на сумму {round(home_count)}₽\n"
        i = 0
        for el in home_dict:
            i += 1
            text += f"{i}){el} - {home_dict[el]} шт.\n"
        text += f"\n\U0001F4CD**В пути к клиенту**: {to_client} шт. на сумму {round(to_client_count)}₽\n"
        i = 0
        for el in to_client_dict:
            i += 1
            text += f"{i}){el} - {to_client_dict[el]} шт.\n"
        text += f"\n\U0001F4CD**В пути от клиента**: {from_client} шт. на сумму {round(from_client_count)}₽\n"
        i = 0
        for el in from_client_dict:
            i += 1
            text += f"{i}){el} - {from_client_dict[el]} шт.\n"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Назад\U00002B05", callback_data=f"rep_back_now")]])
        await app.edit_message_text(chat_id=message.chat.id, text=text, message_id=message.id, reply_markup=markup)
        











async def sender():
    print("Start")
    connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, api, notific, last, name, num, last_canc, last_sell, is_supp FROM Sellers")
    all_sellers = cursor.fetchall()
    for seller in all_sellers:
        if seller[2] == 1:
            fl = True
            api_key = seller[1]
            all_orders = []
            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"dateFrom": (date.today() - timedelta(days=90))}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 401:
                cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                connection.commit()
                try:
                    await app.send_message(chat_id=seller[0], text=f"\U0000274CОшибка авторизации токена **{seller[4]}**. \U0001F507Уведомления отключены автоматически. \U0001F50EПроверьте статус токена в личном кабинете!")
                except:
                    pass
                    print("no message 401")
            elif response.status_code == 200:
                data_many = response.json()
                try:
                    if len(requests_dict[f'{seller[5]}']) != 0:
                        requests_dict[f'{seller[5]}'][0] = data_many
                except:
                    (requests_dict[f'{seller[5]}']) = [data_many]
                fl = True
                all_orders = data_many
                flag = True
                comission = ""
                warehouses = ""
                osts = ""
                spis_nmids = []
                stat7 = ""
                stat14 = ""
                stat30 = ""
                len_i = 0
                kolvo = 0
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S") > datetime.strptime(seller[3], "%Y-%m-%d %H:%M:%S"):
                        if data['isCancel'] == False:
                            kolvo += 1
                        if data['nmId'] not in spis_nmids:
                            spis_nmids.append(data['nmId'])
                spis_nmids = sorted(spis_nmids)
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S") > datetime.strptime(seller[3], "%Y-%m-%d %H:%M:%S") and data['isCancel'] == False:
                        if flag == True:
                            cursor.execute('UPDATE Sellers SET last = ? WHERE api = ?', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), seller[1]))
                            connection.commit()
                            cursor.execute("SELECT * FROM fast_temp WHERE api = ?", (seller[1],))
                            deletes = cursor.fetchall()
                            for delete in deletes:
                                if delete[0] == seller[1]:
                                    await app.delete_messages(chat_id=seller[0], message_ids=delete[1])
                            flag = False
                        text = f"\U0001F4C6Дата: {data['date'][:10]} \U0001F551Время: {data['date'][11:]}"
                        api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {
                            "settings": {
                                "sort": {
                                    "ascending": False
                                },
                                "filter": {
                                    "textSearch": f"{data['nmId']}",
                                    "withPhoto": -1
                                },
                                "cursor": {
                                    "limit": 1
                                }
                            }
                        }
                        response = requests.post(api_url, headers=headers, json=params, timeout=10)
                        data2 = response.json()
                        try:
                            text += f"\n\n\U0000270FНазвание: **{data2['cards'][0]['title']}**\n\U0001F194Артикул: `{data2['cards'][0]['nmID']}` / {data['supplierArticle']} (Размер: {data['techSize']})\n\U0001F69B{data['warehouseName']} \U000027A1 {data['oblastOkrugName']} / {data['regionName']}\n\U0001F4B5Цена заказа: {data['priceWithDisc']}₽"
                        except:
                            print("data2_false")
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            response = requests.get(api_url, headers=headers, timeout=10)
                            comission = response.json()
                        try:
                            for cat in comission["report"]:
                                if cat["subjectName"] == data['category']:
                                    itcom = cat["kgvpMarketplace"]
                                    break
                            itcomsum = round((data['priceWithDisc'] * itcom / 100), 1)
                        except:
                            pass
                        try:
                            text += f"\n\U0001F4B8Комиссия WB: {itcom}% ({itcomsum}₽)\n\U0001F3F7СПП: {data['spp']}% (Цена для покупателя: {data['finishedPrice']}₽)\n\U0001F69A\U0001F4B5Логистика WB: "
                        except:
                            print("itcomsum_false")
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"date": date.today()}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            warehouses = response.json()
                        for warehouse in warehouses["response"]['data']["warehouseList"]:
                            if warehouse["warehouseName"] == data['warehouseName']:
                                need_warehouse = warehouse
                                break
                        width = data2['cards'][0]['dimensions']['width']
                        height = data2['cards'][0]['dimensions']['height']
                        length = data2['cards'][0]['dimensions']['length']
                        first_liter = need_warehouse["boxDeliveryBase"]
                        next_liter = need_warehouse["boxDeliveryLiter"]
                        first_liter = float(f"{first_liter}".replace(',','.'))
                        next_liter = float(f"{next_liter}".replace(',','.'))
                        v = round((width * height * length / 1000), 1)
                        cost = round((first_liter + (v-1.0)*next_liter), 1)
                        try:
                            text += f"{cost}₽\n      Габариты: {width}*{height}*{length} см. ({v} л.)\n      Тариф склада: {first_liter}₽ за первый л. Далее {next_liter}₽ за л.\n"
                        except:
                            print("cost_false")
                        api_url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {"nmId": data['nmId']}
                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                        feed = response.json()
                        try:
                            text += f"\U0001F31FОценка: {feed['data']['valuation']}\n\U0001F4ACОтзывы: {feed['data']['feedbacksCount']}\n"
                        except:
                            print(data['nmId'])
                            print(response.status_code)
                            print("feed_false")
                        time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
                        time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                        time_14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                        time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                        if fl == True:
                            try:
                                api_url = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_7, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat7 = response.json()
                                spis_stat7 = stat7['data']['cards']
                                spis_stat7_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat7:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat7_new.append(s)
                                stat7['data']['cards'] = spis_stat7_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_14, "end": time_now}, "page": 1}

                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat14 = response.json()
                                spis_stat14 = stat14['data']['cards']
                                spis_stat14_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat14:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat14_new.append(s)
                                stat14['data']['cards'] = spis_stat14_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_30, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat30 = response.json()
                                spis_stat30 = stat30['data']['cards']
                                spis_stat30_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat30:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat30_new.append(s)
                                stat30['data']['cards'] = spis_stat30_new
                            except:
                                print(stat7, stat14, stat30)
                        try:
                            text += f"\U0001F45BПроцент выкупа (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']}\n"
                            text += f"\U0001F4C8Количество заказов в день, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']}\n"
                            text += f"\U0001F4CAЧисло продаж, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']}\n"
                        except:
                            print("stat_false")
                        try:
                            obor = round(stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['stocks']['stocksWb'] /  stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount'] * 7)
                            if obor < 30:
                                obor_it = "\U0001F7E2Дефицит"
                            else:
                                obor_it = "\U0001F534Профицит"
                            text += f"**{obor_it}** товара по результатам оценки.\n\U0001F4E6Остаток на складах:\n"
                        except:
                            print("obor_false")
                        if fl == True or osts == "":
                            try:
                                api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                params = {"dateFrom": "2019-06-20"}
                                response = requests.get(api_url, headers=headers, params=params, timeout=10)
                                if response.status_code == 429:
                                    osts = requests_dict[f'{seller[5]}'][2]
                                elif response.status_code == 200:
                                    osts = response.json()
                                    try:
                                        if len(requests_dict[f'{seller[5]}']) == 2:
                                            (requests_dict[f'{seller[5]}']).append(osts)
                                        elif len(requests_dict[f'{seller[5]}']) == 1:
                                            (requests_dict[f'{seller[5]}']).append(0)
                                            (requests_dict[f'{seller[5]}']).append(osts)
                                        else:
                                            requests_dict[f'{seller[5]}'][2] = osts
                                    except:
                                        requests_dict[f'{seller[5]}'] = [0, 0, osts]
                            except:
                                print("osts_get_false")
                                pass
                        values = {}
                        try:
                            for ost in osts:
                                if ost["nmId"] == data2['cards'][0]['nmID']:
                                    if ost['techSize'] not in values:
                                        values[f"{ost['techSize']}"] = ost['quantity']
                                    else:
                                        values[f"{ost['techSize']}"] = (values[f"{ost['techSize']}"] + ost['quantity'])
                            sort_spis = sorted(values)
                            for el in sort_spis:
                                text += f"    Товар: {el}. Остаток: {values[f'{el}']}\n"
                        except:
                            print("osts_false")
                        count_yest = 0
                        count_yest_all = 0
                        price_yest_all = 0
                        count_today = 0
                        count_today_all = 0
                        price_today_all = 0
                        try:
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                        count_yest += 1
                                        count_yest_all += 1
                                        price_yest_all += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and data['isCancel'] == False:
                                        count_yest_all += 1
                                        price_yest_all += datas['priceWithDisc']
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                        count_today += 1
                                        count_today_all += 1
                                        price_today_all += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                        count_today_all += 1
                                        price_today_all += datas['priceWithDisc']
                            text += f"\U0001F4CDВчера таких: {count_yest} на {round(count_yest*data['priceWithDisc'], 1)}₽\n\U0001F4CDВчера всего: {count_yest_all} на {round(price_yest_all, 1)}₽\n\U0001F4CDСегодня таких: {count_today} на {round(count_today*data['priceWithDisc'], 1)}₽\n\U0001F4CDСегодня всего: {count_today_all} на {round(price_today_all, 1)}₽"
                            text = f"\U0001F6D2Новый заказ! [#{count_today_all - kolvo + len_i + 1}]\n" + text
                        except:
                            print("allstat_false")
                        if len(data2['cards'][0]['photos']) < 3:
                            text += f"<a href={data2['cards'][0]['photos'][0]['big']}>\n\U0001F7E3</a>"
                        else:
                            try:
                                url1 = data2['cards'][0]['photos'][0]['big']
                                url2 = data2['cards'][0]['photos'][1]['big']
                                url3 = data2['cards'][0]['photos'][2]['big']
                                urllib.request.urlretrieve(url1, "Test1.jpg")
                                urllib.request.urlretrieve(url2, "Test2.jpg")
                                urllib.request.urlretrieve(url3, "Test3.jpg")
                                images = [Image.open(x) for x in ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']]
                                widths, heights = zip(*(i.size for i in images))

                                total_width = sum(widths)
                                max_height = max(heights)

                                new_im = Image.new('RGB', (total_width, max_height))

                                x_offset = 0
                                for im in images:
                                    new_im.paste(im, (x_offset,0))
                                    x_offset += im.size[0]

                                new_im.save('test.jpg')
                                img = Image.open(r"test.jpg") 
                                file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
                                file_ext = "test.jpg".split('.')[-1]
                                file_type = file_types[file_ext]
                                with open("test.jpg", 'rb') as f:
                                    url = 'https://telegra.ph/upload'
                                    response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=10)
                                telegraph_url = json.loads(response.content)
                                telegraph_url = telegraph_url[0]['src']
                                telegraph_url = f'https://telegra.ph{telegraph_url}'
                                text += f"<a href={telegraph_url}>&#8205;</a>"
                            except:
                                print("photo_false")
                        len_i += 1
                        fl = False
                        try:
                            await app.send_message(chat_id=seller[0], text=text)
                        except:
                            cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                            connection.commit()
                            print("cant_send")
            if seller[8] == True:
                api_key = seller[1]
                warehouses_url = 'https://supplies-api.wildberries.ru/api/v1/warehouses'
                warehouses_headers = {'Authorization': seller[1], 'Content-Type': 'application/json'}
                warehouses_response = requests.get(warehouses_url, headers=warehouses_headers)
                spis_wh = warehouses_response.json()
                cursor.execute('SELECT nmId FROM Supplies WHERE api_key = ?', (seller[1],))
                spis_nmId = cursor.fetchall()
                nmid_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
                nmid_headers = {'Authorization': seller[1], 'Content-Type': 'application/json'}
                nmid_params = {
                    "settings": {
                        "sort": {
                        "ascending": False
                        },
                        "filter": {
                            "withPhoto": -1
                        },
                        "cursor": {
                            "limit": 100
                        }
                    }
                }
                data2 = requests.post(nmid_url, headers=nmid_headers, json=nmid_params, timeout=15)
                if data2.status_code == 200:
                    nmids = data2.json()
                    spis_nmids = []
                    for id in nmids['cards']:
                        if id['nmID'] not in spis_nmids:
                            spis_nmids.append(id['nmID'])
                    for nmid_resp in nmids['cards']:
                        if (nmid_resp['nmID'],) not in spis_nmId:
                            url = "https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm=" + str(nmid_resp['nmID'])
                            warehouses_response = requests.get(url = url, timeout=10)
                            warehousess = warehouses_response.json()
                            for size in warehousess['data']['products'][0]['sizes']:
                                for stock in size['stocks']:
                                    cursor.execute('INSERT INTO Supplies (api_key, id, nmId, size, whouse, osts) VALUES (?, ?, ?, ?, ?, ?)', (seller[1], seller[0], nmid_resp['nmID'], size["origName"], stock['wh'], stock['qty']))
                            connection.commit()
                    for nmid_resp in nmids['cards']:
                        url = "https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm=" + str(nmid_resp['nmID'])
                        warehouses_response = requests.get(url = url, timeout=10)
                        warehousess = warehouses_response.json()
                        cursor.execute('SELECT size, whouse, osts FROM Supplies WHERE api_key = ? and id = ? and nmId = ?', (seller[1], seller[0], nmid_resp['nmID']))
                        one_nm = cursor.fetchall()
                        try:
                            url = "https://discounts-prices-api.wb.ru/api/v2/list/goods/filter"
                            headers = {'Authorization': seller[1], 'Content-Type': 'application/json'}
                            params = {"limit": 10, "filterNmID": nmid_resp['nmID']}
                            price_resp = requests.get(url, headers=headers, params=params, timeout=10)
                            price = price_resp.json()
                        except:
                            pass
                        if warehousess['data']['products'] == []:
                            cursor.execute('DELETE FROM Supplies WHERE nmId = ?', (nmid_resp['nmID'],))
                            connection.commit()
                        else:
                            for nm in one_nm:
                                for size in warehousess['data']['products'][0]['sizes']:
                                    if size['origName'] == nm[0]:
                                        for wh in size['stocks']:
                                            if wh['wh'] == nm[1]:
                                                if wh['qty'] > nm[2]:
                                                    cursor.execute('UPDATE Supplies SET osts = ? WHERE api_key = ? and id = ? and nmId = ? and size = ? and whouse = ?', (wh['qty'], seller[1], seller[0], nmid_resp['nmID'], nm[0], nm[1]))
                                                    connection.commit()
                                                if wh['qty'] < nm[2]:
                                                    if fl == True:
                                                        comission = ""
                                                        warehouses = ""
                                                        osts = ""
                                                        stat7 = ""
                                                        stat14 = ""
                                                        stat30 = ""
                                                        len_i = 0
                                                        kolvo = 0
                                                    town_wh = ""
                                                    for one_wh in spis_wh:
                                                        if one_wh['ID'] == nm[1]:
                                                            town_wh = one_wh['name']
                                                            break
                                                    need_price = 0
                                                    try:
                                                        for sizze in price['data']['listGoods'][0]['sizes']:
                                                            if sizze['techSizeName'] == nm[0]:
                                                                need_price = round(sizze['discountedPrice'])
                                                    except:
                                                        print("price_false")
                                                    for i in range(nm[2] - wh['qty']):
                                                        cursor.execute('UPDATE Supplies SET osts = ? WHERE api_key = ? and id = ? and nmId = ? and size = ? and whouse = ?', (wh['qty'], seller[1], seller[0], nmid_resp['nmID'], nm[0], nm[1]))
                                                        connection.commit()
                                                        text = f"\U0001F4C6Дата: {datetime.now().strftime(format='%d.%m.%Y')} \U0001F551Время: {datetime.now().strftime(format='%H:%M')} +- 5 минут"
                                                        text += "\n\n\U0001F680Fast Mode"
                                                        try:
                                                            text += f"\n\n\U0000270FНазвание: **{nmid_resp['title']}**\n\U0001F194Артикул: `{nmid_resp['nmID']}` / {nmid_resp['vendorCode']} (Размер: {nm[0]})\n\U0001F69B{town_wh} \U000027A1 ...\n\U0001F4B5Цена заказа: {need_price}₽"
                                                        except:
                                                            print("data2_false")
                                                        if fl == True:
                                                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
                                                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                            response = requests.get(api_url, headers=headers, timeout=10)
                                                            comission = response.json()
                                                        try:
                                                            for cat in comission["report"]:
                                                                if cat["subjectName"] == nmid_resp['subjectName']:
                                                                    itcom = cat["kgvpMarketplace"]
                                                                    break
                                                            itcomsum = round((need_price * itcom / 100), 1)
                                                        except:
                                                            pass
                                                        try:
                                                            text += f"\n\U0001F4B8Комиссия WB: {itcom}% ({itcomsum}₽)\n\U0001F69A\U0001F4B5Логистика WB: "
                                                        except:
                                                            print("itcomsum_false")
                                                        if fl == True:
                                                                api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
                                                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                                params = {"date": date.today()}
                                                                response = requests.get(api_url, headers=headers, params=params, timeout=10)
                                                                warehouses = response.json()
                                                        try:
                                                            for warehouse in warehouses["response"]['data']["warehouseList"]:
                                                                if warehouse["warehouseName"] == town_wh:
                                                                    need_warehouse = warehouse
                                                                    break
                                                            width = nmid_resp['dimensions']['width']
                                                            height = nmid_resp['dimensions']['height']
                                                            length = nmid_resp['dimensions']['length']
                                                            first_liter = need_warehouse["boxDeliveryBase"]
                                                            next_liter = need_warehouse["boxDeliveryLiter"]
                                                            first_liter = float(f"{first_liter}".replace(',','.'))
                                                            next_liter = float(f"{next_liter}".replace(',','.'))
                                                            v = round((width * height * length / 1000), 1)
                                                            cost = round((first_liter + (v-1.0)*next_liter), 1)
                                                        except:
                                                            print("cost_false")
                                                        try:
                                                            text += f"{cost}₽\n      Габариты: {width}*{height}*{length} см. ({v} л.)\n      Тариф склада: {first_liter}₽ за первый л. Далее {next_liter}₽ за л.\n"
                                                        except:
                                                            print("cost_false")
                                                        api_url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
                                                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                        params = {"nmId": nmid_resp['nmID']}
                                                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                                                        feed = response.json()
                                                        try:
                                                            text += f"\U0001F31FОценка: {feed['data']['valuation']}\n\U0001F4ACОтзывы: {feed['data']['feedbacksCount']}\n"
                                                        except:
                                                            print(nmid_resp['nmID'])
                                                            print(response.status_code)
                                                            print("feed_false")
                                                        time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
                                                        time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                                                        time_14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                                                        time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                                                        if fl == True:
                                                            try:
                                                                api_url = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
                                                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                                params = {"nmIDs": spis_nmids, "period": {"begin": time_7, "end": time_now}, "page": 1}
                                                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                                                stat7 = response.json()
                                                                spis_stat7 = stat7['data']['cards']
                                                                spis_stat7_new = []
                                                                for i in range(len(spis_nmids)):
                                                                    for s in spis_stat7:
                                                                        if s['nmID'] == spis_nmids[i]:
                                                                            spis_stat7_new.append(s)
                                                                stat7['data']['cards'] = spis_stat7_new
                                                                params = {"nmIDs": spis_nmids, "period": {"begin": time_14, "end": time_now}, "page": 1}

                                                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                                                stat14 = response.json()
                                                                spis_stat14 = stat14['data']['cards']
                                                                spis_stat14_new = []
                                                                for i in range(len(spis_nmids)):
                                                                    for s in spis_stat14:
                                                                        if s['nmID'] == spis_nmids[i]:
                                                                                spis_stat14_new.append(s)
                                                                stat14['data']['cards'] = spis_stat14_new
                                                                params = {"nmIDs": spis_nmids, "period": {"begin": time_30, "end": time_now}, "page": 1}
                                                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                                                stat30 = response.json()
                                                                spis_stat30 = stat30['data']['cards']
                                                                spis_stat30_new = []
                                                                for i in range(len(spis_nmids)):
                                                                    for s in spis_stat30:
                                                                        if s['nmID'] == spis_nmids[i]:
                                                                            spis_stat30_new.append(s)
                                                                stat30['data']['cards'] = spis_stat30_new
                                                            except:
                                                                print(stat7, stat14, stat30)
                                                        try:
                                                            text += f"\U0001F45BПроцент выкупа (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat14['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat30['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']}\n"
                                                            text += f"\U0001F4C8Количество заказов в день, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat14['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat30['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']}\n"
                                                            text += f"\U0001F4CAЧисло продаж, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat14['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat30['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']}\n"
                                                        except:
                                                            print("stat_false")
                                                        try:
                                                            obor = round(stat7['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['stocks']['stocksWb'] /  stat7['data']['cards'][spis_nmids.index(nmid_resp['nmID'])]['statistics']['selectedPeriod']['buyoutsCount'] * 7)
                                                            if obor < 30:
                                                                obor_it = "\U0001F7E2Дефицит"
                                                            else:
                                                                obor_it = "\U0001F534Профицит"
                                                            text += f"**{obor_it}** товара по результатам оценки.\n\U0001F4E6Остаток на складах:\n"
                                                        except:
                                                            print("obor_false")
                                                        if fl == True or osts == "":
                                                            try:
                                                                api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
                                                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                                params = {"dateFrom": "2019-06-20"}
                                                                response = requests.get(api_url, headers=headers, params=params, timeout=10)
                                                                if response.status_code == 429:
                                                                    osts = requests_dict[f'{seller[5]}'][2]
                                                                elif response.status_code == 200:
                                                                    osts = response.json()
                                                                    try:
                                                                        if len(requests_dict[f'{seller[5]}']) == 2:
                                                                            (requests_dict[f'{seller[5]}']).append(osts)
                                                                        elif len(requests_dict[f'{seller[5]}']) == 1:
                                                                            (requests_dict[f'{seller[5]}']).append(0)
                                                                            (requests_dict[f'{seller[5]}']).append(osts)
                                                                        else:
                                                                            requests_dict[f'{seller[5]}'][2] = osts
                                                                    except:
                                                                        requests_dict[f'{seller[5]}'] = [0, 0, osts]
                                                            except:
                                                                print("osts_get_false")
                                                                pass
                                                        values = {}
                                                        try:
                                                            for ost in osts:
                                                                if ost["nmId"] == nmid_resp['nmID']:
                                                                    if ost['techSize'] not in values:
                                                                        values[f"{ost['techSize']}"] = ost['quantity']
                                                                    else:
                                                                        values[f"{ost['techSize']}"] = (values[f"{ost['techSize']}"] + ost['quantity'])
                                                            sort_spis = sorted(values)
                                                            for el in sort_spis:
                                                                text += f"    Товар: {el}. Остаток: {values[f'{el}']}\n"
                                                        except:
                                                            print("osts_false")
                                                        count_yest = 0
                                                        count_yest_all = 0
                                                        price_yest_all = 0
                                                        count_today = 0
                                                        count_today_all = 0
                                                        price_today_all = 0
                                                        api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
                                                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                                        params = {"dateFrom": (date.today() - timedelta(days=90))}
                                                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                                                        if response.status_code == 200:
                                                            data_many = response.json()
                                                            try:
                                                                if len(requests_dict[f'{seller[5]}']) != 0:
                                                                    requests_dict[f'{seller[5]}'][0] = data_many
                                                            except:
                                                                (requests_dict[f'{seller[5]}']) = [data_many]
                                                        try:
                                                            for datas in data_many:
                                                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                                                    if datas['nmId'] == nmid_resp['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                                                        count_yest += 1
                                                                        count_yest_all += 1
                                                                        price_yest_all += datas['priceWithDisc']
                                                                    elif datas['orderType'] == "Клиентский" and data['isCancel'] == False:
                                                                        count_yest_all += 1
                                                                        price_yest_all += datas['priceWithDisc']
                                                            for datas in data_many:
                                                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                                                    if datas['nmId'] == nmid_resp['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                                                        count_today += 1
                                                                        count_today_all += 1
                                                                        price_today_all += datas['priceWithDisc']
                                                                    elif datas['orderType'] == "Клиентский" and datas['isCancel'] == False:
                                                                        count_today_all += 1
                                                                        price_today_all += datas['priceWithDisc']
                                                            text += f"\U0001F4CDВчера таких: {count_yest} на {round(count_yest*data['priceWithDisc'], 1)}₽\n\U0001F4CDВчера всего: {count_yest_all} на {round(price_yest_all, 1)}₽\n\U0001F4CDСегодня таких: {count_today} на {round(count_today*data['priceWithDisc'], 1)}₽\n\U0001F4CDСегодня всего: {count_today_all} на {round(price_today_all, 1)}₽"
                                                            text = f"\U0001F6D2Новый заказ! [#{count_today_all - kolvo + len_i + 1}]\n" + text
                                                        except:
                                                            print("allstat_false")
                                                        if len(nmid_resp['photos']) < 3:
                                                            text += f"<a href={nmid_resp['photos'][0]['big']}>\n\U0001F7E3</a>"
                                                        else:
                                                            try:
                                                                url1 = nmid_resp['photos'][0]['big']
                                                                url2 = nmid_resp['photos'][1]['big']
                                                                url3 = nmid_resp['photos'][2]['big']
                                                                urllib.request.urlretrieve(url1, "Test1.jpg")
                                                                urllib.request.urlretrieve(url2, "Test2.jpg")
                                                                urllib.request.urlretrieve(url3, "Test3.jpg")
                                                                images = [Image.open(x) for x in ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']]
                                                                widths, heights = zip(*(i.size for i in images))

                                                                total_width = sum(widths)
                                                                max_height = max(heights)

                                                                new_im = Image.new('RGB', (total_width, max_height))

                                                                x_offset = 0
                                                                for im in images:
                                                                    new_im.paste(im, (x_offset,0))
                                                                    x_offset += im.size[0]

                                                                new_im.save('test.jpg')
                                                                img = Image.open(r"test.jpg") 
                                                                file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
                                                                file_ext = "test.jpg".split('.')[-1]
                                                                file_type = file_types[file_ext]
                                                                with open("test.jpg", 'rb') as f:
                                                                    url = 'https://telegra.ph/upload'
                                                                    response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=10)
                                                                telegraph_url = json.loads(response.content)
                                                                telegraph_url = telegraph_url[0]['src']
                                                                telegraph_url = f'https://telegra.ph{telegraph_url}'
                                                                text += f"<a href={telegraph_url}>&#8205;</a>"
                                                            except:
                                                                print("photo_false")
                                                        len_i += 1
                                                        fl = False
                                                        try:
                                                            message = await app.send_message(chat_id=seller[0], text=text)
                                                            cursor.execute("INSERT INTO fast_temp (api, mess_id) VALUES (?, ?)", (seller[1], message.id))
                                                            connection.commit()
                                                        except:
                                                            cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                                                            connection.commit()
                                                            print("cant_send")


            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/sales"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"dateFrom": (date.today() - timedelta(days=90))}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data_many = response.json()
                if len(requests_dict[f'{seller[5]}']) == 1:
                    (requests_dict[f'{seller[5]}']).append(data_many)
                else:
                    requests_dict[f'{seller[5]}'][1] = data_many
                if fl == True:
                    comission = ""
                    warehouses = ""
                    osts = ""
                    stat7 = ""
                    stat14 = ""
                    stat30 = ""
                flag = True
                spis_nmids = []
                len_i = 0
                len_i_vozv =0
                kolvo = 0
                kolvo_vozv = 0
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S") > datetime.strptime(seller[7], "%Y-%m-%d %H:%M:%S"):
                        if data['saleID'][0] == "S":
                            kolvo += 1
                        else:
                            kolvo_vozv += 1
                        if data['nmId'] not in spis_nmids:
                            spis_nmids.append(data['nmId'])
                    spis_nmids = sorted(spis_nmids)
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S") > datetime.strptime(seller[7], "%Y-%m-%d %H:%M:%S") and data['saleID'][0] == "S":
                        if flag == True:
                            cursor.execute('UPDATE Sellers SET last_sell = ? WHERE api = ?', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), seller[1]))
                            connection.commit()
                            flag = False
                        text = f"\U0001F4C6Дата: {data['date'][:10]} \U0001F551Время: {data['date'][11:]}"
                        api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {
                            "settings": {
                                "sort": {
                                    "ascending": False
                                },
                                "filter": {
                                    "textSearch": f"{data['nmId']}",
                                    "withPhoto": -1
                                },
                                "cursor": {
                                    "limit": 1
                                }
                            }
                        }
                        response = requests.post(api_url, headers=headers, json=params, timeout=10)
                        data2 = response.json()
                        try:
                            text += f"\n\n\U0000270FНазвание: **{data2['cards'][0]['title']}**\n\U0001F194Артикул: `{data2['cards'][0]['nmID']}` / {data['supplierArticle']} (Размер: {data['techSize']})\n"
                        except:
                            print("data2_false")
                        time_fl = False
                        for order in all_orders:
                            if order['srid'] == data['srid']:
                                time_fl = True
                                text += f"\U0001F4C6Дата заказа: {order['date'].replace('T', ' ')}\n"
                                break
                        if time_fl == True:
                            text += f"\U0001F4C6Дата продажи: {data['date'].replace('T', ' ')}\n"
                            text += f"\U0001F55D{str(datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(order['date'], '%Y-%m-%dT%H:%M:%S'))[0]} суток с даты заказа\n"
                        else:
                            text += f"\U0001F4C6Дата продажи: {data['date'].replace('T', ' ')}\n"
                            text += "\U0001F55DБолее 7 суток с даты заказа\n"
                        text += f"\U0001F69B{data['warehouseName']} \U000027A1 {data['oblastOkrugName']} / {data['regionName']}\n\U0001F4B5Продано за: {data['priceWithDisc']}₽"
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            response = requests.get(api_url, headers=headers, timeout=10)
                            comission = response.json()
                        try:
                            for cat in comission["report"]:
                                if cat["subjectName"] == data['category']:
                                    itcom = cat["kgvpMarketplace"]
                                    break
                            itcomsum = round((data['priceWithDisc'] * itcom / 100), 1)
                        except:
                            pass
                        try:
                            text += f"\n\U0001F4B8Комиссия WB: {itcom}% ({itcomsum}₽)\n\U0001F4B3К выплате: {data['forPay']}₽\n"
                        except:
                            print("itcomsum_false")
                        api_url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {"nmId": data['nmId']}
                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                        feed = response.json()
                        try:
                            text += f"\U0001F31FОценка: {feed['data']['valuation']}\n\U0001F4ACОтзывы: {feed['data']['feedbacksCount']}\n"
                        except:
                            print("feed_false")
                        time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
                        time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                        time_14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                        time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                        if fl == True:
                            try:
                                api_url = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_7, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat7 = response.json()
                                spis_stat7 = stat7['data']['cards']
                                spis_stat7_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat7:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat7_new.append(s)
                                stat7['data']['cards'] = spis_stat7_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_14, "end": time_now}, "page": 1}

                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat14 = response.json()
                                spis_stat14 = stat14['data']['cards']
                                spis_stat14_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat14:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat14_new.append(s)
                                stat14['data']['cards'] = spis_stat14_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_30, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=10)
                                stat30 = response.json()
                                spis_stat30 = stat30['data']['cards']
                                spis_stat30_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat30:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat30_new.append(s)
                                stat30['data']['cards'] = spis_stat30_new
                            except:
                                print(stat7, stat14, stat30)
                        try:
                            text += f"\U0001F45BПроцент выкупа (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']}\n"
                            text += f"\U0001F4C8Количество заказов в день, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']}\n"
                            text += f"\U0001F4CAЧисло продаж, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']}\n"
                        except:
                            print("stat_false")
                        try:
                            obor = round(stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['stocks']['stocksWb'] /  stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount'] * 7)
                            if obor < 30:
                                obor_it = "\U0001F7E2Дефицит"
                            else:
                                obor_it = "\U0001F534Профицит"
                            text += f"**{obor_it}** товара по результатам оценки.\n\U0001F4E6Остаток на складах:\n"
                        except:
                            print("obor_false")
                        if fl == True or osts == "":
                            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"dateFrom": "2019-06-20"}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            try:
                                if response.status_code == 429:
                                    osts = requests_dict[f'{seller[5]}'][2]
                                elif response.status_code == 200:
                                    osts = response.json()
                                    try:
                                        if len(requests_dict[f'{seller[5]}']) == 2:
                                            (requests_dict[f'{seller[5]}']).append(osts)
                                        elif len(requests_dict[f'{seller[5]}']) == 1:
                                            (requests_dict[f'{seller[5]}']).append(0)
                                            (requests_dict[f'{seller[5]}']).append(osts)
                                        else:
                                            requests_dict[f'{seller[5]}'][2] = osts
                                    except:
                                        requests_dict[f'{seller[5]}'] = [0, 0, osts]
                            except:
                                print("osts_get_false")
                                pass
                        values = {}
                        try:
                            for ost in osts:
                                if ost["nmId"] == data2['cards'][0]['nmID']:
                                    if ost['techSize'] not in values:
                                        values[f"{ost['techSize']}"] = ost['quantity']
                                    else:
                                        values[f"{ost['techSize']}"] = (values[f"{ost['techSize']}"] + ost['quantity'])
                            sort_spis = sorted(values)
                            for el in sort_spis:
                                text += f"    Товар: {el}. Остаток: {values[f'{el}']}\n"
                        except:
                            print("osts_false")
                        count_yest = 0
                        count_yest_all = 0
                        price_yest_all = 0
                        count_today = 0
                        count_today_all = 0
                        price_today_all = 0
                        try:
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['saleID'][0] == "S":
                                        count_yest += 1
                                        count_yest_all += 1
                                        price_yest_all += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['saleID'][0] == "S":
                                        count_yest_all += 1
                                        price_yest_all += datas['priceWithDisc']
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['saleID'][0] == "S":
                                        count_today += 1
                                        count_today_all += 1
                                        price_today_all += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['saleID'][0] == "S":
                                        count_today_all += 1
                                        price_today_all += datas['priceWithDisc']
                            text += f"\U0001F4CDВчера таких: {count_yest} на {round(count_yest*data['priceWithDisc'], 1)}₽\n\U0001F4CDВчера всего: {count_yest_all} на {round(price_yest_all, 1)}₽\n\U0001F4CDСегодня таких: {count_today} на {round(count_today*data['priceWithDisc'], 1)}₽\n\U0001F4CDСегодня всего: {count_today_all} на {round(price_today_all, 1)}₽"
                            text = f"\U0001F4B0Продажа! [#{count_today_all - kolvo + len_i + 1}]\n" + text
                        except:
                            print("allstat_false")
                        if len(data2['cards'][0]['photos']) < 3:
                            text += f"<a href={data2['cards'][0]['photos'][0]['big']}>\n\U0001F7E3</a>"
                        else:
                            try:
                                url1 = data2['cards'][0]['photos'][0]['big']
                                url2 = data2['cards'][0]['photos'][1]['big']
                                url3 = data2['cards'][0]['photos'][2]['big']
                                urllib.request.urlretrieve(url1, "Test1.jpg")
                                urllib.request.urlretrieve(url2, "Test2.jpg")
                                urllib.request.urlretrieve(url3, "Test3.jpg")
                                images = [Image.open(x) for x in ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']]
                                widths, heights = zip(*(i.size for i in images))

                                total_width = sum(widths)
                                max_height = max(heights)

                                new_im = Image.new('RGB', (total_width, max_height))

                                x_offset = 0
                                for im in images:
                                    new_im.paste(im, (x_offset,0))
                                    x_offset += im.size[0]

                                new_im.save('test.jpg')
                                img = Image.open(r"test.jpg") 
                                file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
                                file_ext = "test.jpg".split('.')[-1]
                                file_type = file_types[file_ext]
                                with open("test.jpg", 'rb') as f:
                                    url = 'https://telegra.ph/upload'
                                    response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=10)
                                telegraph_url = json.loads(response.content)
                                telegraph_url = telegraph_url[0]['src']
                                telegraph_url = f'https://telegra.ph{telegraph_url}'
                                text += f"<a href={telegraph_url}>&#8205;</a>"
                            except:
                                print("photo_false")
                        len_i += 1
                        fl = False
                        try:
                            await app.send_message(chat_id=seller[0], text=text)
                        except:
                            cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                            connection.commit()
                            print("cant_send")
                    elif data['orderType'] == "Клиентский" and datetime.strptime(data['date'], "%Y-%m-%dT%H:%M:%S") > datetime.strptime(seller[7], "%Y-%m-%d %H:%M:%S") and data['saleID'][0] == "R":
                        text = f"\U0001F4C6Дата: {data['date'][:10]} \U0001F551Время: {data['date'][11:]}"
                        api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {
                            "settings": {
                                "sort": {
                                    "ascending": False
                                },
                                "filter": {
                                    "textSearch": f"{data['nmId']}",
                                    "withPhoto": -1
                                },
                                "cursor": {
                                    "limit": 1
                                }
                            }
                        }
                        response = requests.post(api_url, headers=headers, json=params, timeout=10)
                        data2 = response.json()
                        try:
                            text += f"\n\n\U0000270FНазвание: **{data2['cards'][0]['title']}**\n\U0001F194Артикул: `{data2['cards'][0]['nmID']}` / {data['supplierArticle']} (Размер: {data['techSize']})\n"
                        except:
                            print("data2_false")
                        time_fl = False
                        time_fl2 = False
                        temp_text = ""
                        for order in all_orders:
                            if order['srid'] == data['srid']:
                                time_fl = True
                                text += f"\U0001F4C6Дата заказа: {order['date'].replace('T', ' ')}\n"
                                break
                        for datass in data_many:
                            if datass['srid'] == data['srid'] and datass['date'] != data['date']:
                                time_fl2 = True
                                text += f"\U0001F4C6Дата продажи: {datass['date'].replace('T', ' ')}\n"
                                temp_text += f"\U0001F55D{str(datetime.strptime(data['date'], '%Y-%m-%dT%H:%M:%S') - datetime.strptime(datass['date'], '%Y-%m-%dT%H:%M:%S'))[0]} суток с даты продажи\n"
                                break
                        if time_fl2 == False:
                            temp_text += "\U0001F55DБолее 7 суток с даты продажи\n"
                        text += f"\U0001F4C6Дата возврата на склад: {data['date'].replace('T', ' ')}\n"
                        text += temp_text
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            response = requests.get(api_url, headers=headers, timeout=10)
                            comission = response.json()
                        try:
                            for cat in comission["report"]:
                                if cat["subjectName"] == data['category']:
                                    itcom = cat["kgvpMarketplace"]
                                    break
                            itcomsum = round((data['priceWithDisc'] * itcom / 100), 1)
                        except:
                            pass
                        try:
                            text += f"\U0001F4B5Цена товара: {data['priceWithDisc']}₽\n\U0001F4B8Комиссия WB: {itcom * (-1)}% ({itcomsum}₽)\n\U0001F4B1К возврату: {data['forPay'] * (-1)}₽\n"
                        except:
                            print("itcomsum_false")
                        text += f"\U0001F69B{data['warehouseName']} \U00002B05 {data['oblastOkrugName']} / {data['regionName']}\n"
                        api_url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {"nmId": data['nmId']}
                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                        feed = response.json()
                        try:
                            text += f"\U0001F31FОценка: {feed['data']['valuation']}\n\U0001F4ACОтзывы: {feed['data']['feedbacksCount']}\n"
                        except:
                            print("feed_false")
                        time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
                        time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                        time_14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                        time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                        if fl == True:
                            try:
                                api_url = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
                                headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_7, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=20)
                                stat7 = response.json()
                                spis_stat7 = stat7['data']['cards']
                                spis_stat7_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat7:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat7_new.append(s)
                                stat7['data']['cards'] = spis_stat7_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_14, "end": time_now}, "page": 1}

                                response = requests.post(api_url, headers=headers, json=params, timeout=20)
                                stat14 = response.json()
                                spis_stat14 = stat14['data']['cards']
                                spis_stat14_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat14:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat14_new.append(s)
                                stat14['data']['cards'] = spis_stat14_new
                                params = {"nmIDs": spis_nmids, "period": {"begin": time_30, "end": time_now}, "page": 1}
                                response = requests.post(api_url, headers=headers, json=params, timeout=20)
                                stat30 = response.json()
                                spis_stat30 = stat30['data']['cards']
                                spis_stat30_new = []
                                for i in range(len(spis_nmids)):
                                    for s in spis_stat30:
                                        if s['nmID'] == spis_nmids[i]:
                                            spis_stat30_new.append(s)
                                stat30['data']['cards'] = spis_stat30_new
                            except:
                                print(stat7, stat14, stat30)
                        try:
                            text += f"\U0001F45BПроцент выкупа (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']}\n"
                            text += f"\U0001F4C8Количество заказов в день, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']}\n"
                            text += f"\U0001F4CAЧисло продаж, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']}\n"
                        except:
                            print("stat_false")
                        try:
                            obor = round(stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['stocks']['stocksWb'] /  stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount'] * 7)
                            if obor < 30:
                                obor_it = "\U0001F7E2Дефицит"
                            else:
                                obor_it = "\U0001F534Профицит"
                            text += f"**{obor_it}** товара по результатам оценки.\n\U0001F4E6Остаток на складах:\n"
                        except:
                            print("obor_false")
                        if fl == True:
                            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"dateFrom": "2019-06-20"}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            if response.status_code == 429:
                                osts = requests_dict[f'{seller[5]}'][2]
                            elif response.status_code == 200:
                                osts = response.json()
                                try:
                                    if len(requests_dict[f'{seller[5]}']) == 2:
                                        (requests_dict[f'{seller[5]}']).append(osts)
                                    elif len(requests_dict[f'{seller[5]}']) == 1:
                                        (requests_dict[f'{seller[5]}']).append(0)
                                        (requests_dict[f'{seller[5]}']).append(osts)
                                    else:
                                        requests_dict[f'{seller[5]}'][2] = osts
                                except:
                                    requests_dict[f'{seller[5]}'] = [0, 0, osts]
                        values = {}
                        try:
                            for ost in osts:
                                if ost["nmId"] == data2['cards'][0]['nmID']:
                                    if ost['techSize'] not in values:
                                        values[f"{ost['techSize']}"] = ost['quantity']
                                    else:
                                        values[f"{ost['techSize']}"] = (values[f"{ost['techSize']}"] + ost['quantity'])
                            sort_spis = sorted(values)
                            for el in sort_spis:
                                text += f"    Товар: {el}. Остаток: {values[f'{el}']}\n"
                        except:
                            print("osts_false")
                        count_yest_vozv = 0
                        count_yest_all_vozv = 0
                        count_today_vozv = 0
                        count_today_all_vozv = 0
                        price_yest_all_vozv = 0
                        price_today_all_vozv = 0
                        try:
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['saleID'][0] == "R":
                                        count_yest_vozv += 1
                                        count_yest_all_vozv += 1
                                        price_yest_all_vozv += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['saleID'][0] == "R":
                                        count_yest_all_vozv += 1
                                        price_yest_all_vozv += datas['priceWithDisc']
                            for datas in data_many:
                                if datetime.strptime(datas['date'][:10], "%Y-%m-%d") == datetime.strptime(date.today().strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['saleID'][0] == "R":
                                        count_today_vozv += 1
                                        count_today_all_vozv += 1
                                        price_today_all_vozv += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['saleID'][0] == "R":
                                        count_today_all_vozv += 1
                                        price_today_all_vozv += datas['priceWithDisc']
                            text += f"\U0001F4CDВчера таких: {count_yest_vozv} на {round(count_yest_vozv*data['priceWithDisc'] * (-1), 1)}₽\n\U0001F4CDВчера всего: {count_yest_all_vozv} на {round(price_yest_all_vozv, 1)}₽\n\U0001F4CDСегодня таких: {count_today_vozv} на {round(count_today_vozv*data['priceWithDisc'], 1)}₽\n\U0001F4CDСегодня всего: {count_today_all_vozv} на {round(price_today_all_vozv, 1)}₽"
                            text = f"\U0001F501Возврат на склад WB! [#{count_today_all_vozv - kolvo_vozv + len_i_vozv + 1}]\n" + text
                        except:
                            print("allstat_false")
                        if len(data2['cards'][0]['photos']) < 3:
                            text += f"<a href={data2['cards'][0]['photos'][0]['big']}>\n\U0001F7E3</a>"
                        else:
                            try:
                                url1 = data2['cards'][0]['photos'][0]['big']
                                url2 = data2['cards'][0]['photos'][1]['big']
                                url3 = data2['cards'][0]['photos'][2]['big']
                                urllib.request.urlretrieve(url1, "Test1.jpg")
                                urllib.request.urlretrieve(url2, "Test2.jpg")
                                urllib.request.urlretrieve(url3, "Test3.jpg")
                                images = [Image.open(x) for x in ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']]
                                widths, heights = zip(*(i.size for i in images))

                                total_width = sum(widths)
                                max_height = max(heights)

                                new_im = Image.new('RGB', (total_width, max_height))

                                x_offset = 0
                                for im in images:
                                    new_im.paste(im, (x_offset,0))
                                    x_offset += im.size[0]

                                new_im.save('test.jpg')
                                img = Image.open(r"test.jpg") 
                                file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
                                file_ext = "test.jpg".split('.')[-1]
                                file_type = file_types[file_ext]
                                with open("test.jpg", 'rb') as f:
                                    url = 'https://telegra.ph/upload'
                                    response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=10)
                                telegraph_url = json.loads(response.content)
                                telegraph_url = telegraph_url[0]['src']
                                telegraph_url = f'https://telegra.ph{telegraph_url}'
                                text += f"<a href={telegraph_url}>&#8205;</a>"
                            except:
                                print("photo_false")
                        len_i_vozv += 1
                        fl = False
                        try:
                            await app.send_message(chat_id=seller[0], text=text)
                        except:
                            cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                            connection.commit()
                            print("cant_send")
            else:
                print(response.status_code)
    connection.close()

async def cancel_sender():
    print("Start_cancel")
    connection = sqlite3.connect("C:/Users/Administrator/My_bots/BerryStatsBot/Sellers.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, api, notific, last, name, num, last_canc, last_sell FROM Sellers")
    all_sellers = cursor.fetchall()
    for seller in all_sellers:
        if seller[2] == 1:
            fl = True
            api_key = seller[1]
            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/orders"
            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
            params = {"dateFrom": (date.today() - timedelta(days=90))}
            response = requests.get(api_url, headers=headers, params=params, timeout=10)
            if response.status_code == 401:
                cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                connection.commit()
                try:
                    await app.send_message(chat_id=seller[0], text=f"\U0000274CОшибка авторизации токена **{seller[4]}**. \U0001F507Уведомления отключены автоматически. \U0001F50EПроверьте статус токена в личном кабинете!")
                except:
                    pass
                    print("no message 401")
            elif response.status_code == 200:
                data_many = response.json()
                try:
                    if len(requests_dict[f'{seller[5]}']) != 0:
                        requests_dict[f'{seller[5]}'][0] = data_many
                except:
                    (requests_dict[f'{seller[5]}']) = [data_many]
                fl = True
                flag = True
                comission = ""
                warehouses = ""
                osts = ""
                spis_nmids = []
                stat7 = ""
                stat14 = ""
                stat30 = ""
                len_i_cancel = 0
                kolvo_cancel = 0
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                        kolvo_cancel += 1
                        if data['nmId'] not in spis_nmids:
                            spis_nmids.append(data['nmId'])
                spis_nmids = sorted(spis_nmids)
                for data in data_many:
                    if data['orderType'] == "Клиентский" and datetime.strptime(data['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                        text = f"\U0001F4C6Дата: {data['date'][:10]} \U0001F551Время: {data['date'][11:]}"
                        api_url = "https://suppliers-api.wildberries.ru/content/v2/get/cards/list?locale=ru"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {
                            "settings": {
                                "sort": {
                                    "ascending": False
                                },
                                "filter": {
                                    "textSearch": f"{data['nmId']}",
                                    "withPhoto": -1
                                },
                                "cursor": {
                                    "limit": 1
                                }
                            }
                        }
                        response = requests.post(api_url, headers=headers, json=params, timeout=10)
                        data2 = response.json()
                        try:
                            text += f"\n\n\U0000270FНазвание: **{data2['cards'][0]['title']}**\n\U0001F194Артикул: `{data2['cards'][0]['nmID']}` / {data['supplierArticle']} (Размер: {data['techSize']})\n\U0001F69B{data['warehouseName']} \U000027A1 {data['oblastOkrugName']} / {data['regionName']}\n\U0001F4B5Цена заказа: {data['priceWithDisc']}₽"
                        except:
                            print("data2_false")
                        text += f"\n\U0001F4C6Дата заказа: {data['date'][:10]}\n\U0001F4C6Дата отмены: {data['cancelDate'].replace('T',' ')}"
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/commission"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            response = requests.get(api_url, headers=headers, timeout=10)
                            comission = response.json()
                        try:
                            for cat in comission["report"]:
                                if cat["subjectName"] == data['category']:
                                    itcom = cat["kgvpMarketplace"]
                                    break
                            itcomsum = round((data['priceWithDisc'] * itcom / 100), 1)
                        except:
                            pass
                        try:
                            text += f"\n\U0001F4B8Комиссия WB: {itcom}% ({itcomsum}₽)\n\U0001F3F7СПП: {data['spp']}% (Цена для покупателя: {data['finishedPrice']}₽)\n\U0001F69A\U0001F4B5Логистика WB: "
                        except:
                            print("itcomsum_false")
                        if fl == True:
                            api_url = "https://common-api.wildberries.ru/api/v1/tariffs/box"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"date": date.today()}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            warehouses = response.json()
                        for warehouse in warehouses["response"]['data']["warehouseList"]:
                            if warehouse["warehouseName"] == data['warehouseName']:
                                need_warehouse = warehouse
                                break
                        width = data2['cards'][0]['dimensions']['width']
                        height = data2['cards'][0]['dimensions']['height']
                        length = data2['cards'][0]['dimensions']['length']
                        first_liter = need_warehouse["boxDeliveryBase"]
                        next_liter = need_warehouse["boxDeliveryLiter"]
                        first_liter = float(f"{first_liter}".replace(',','.'))
                        next_liter = float(f"{next_liter}".replace(',','.'))
                        v = round((width * height * length / 1000), 1)
                        cost = round((first_liter + (v-1.0)*next_liter), 1)
                        try:
                            text += f"{cost}₽\n      Габариты: {width}*{height}*{length} см. ({v} л.)\n      Тариф склада: {first_liter}₽ за первый л. Далее {next_liter}₽ за л.\n"
                        except:
                            print("cost_false")
                        api_url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks/products/rating/nmid"
                        headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                        params = {"nmId": data['nmId']}
                        response = requests.get(api_url, headers=headers, params=params, timeout=10)
                        feed = response.json()
                        try:
                            text += f"\U0001F31FОценка: {feed['data']['valuation']}\n\U0001F4ACОтзывы: {feed['data']['feedbacksCount']}\n"
                        except:
                            print("feed_false")
                        time_now = (datetime.now() - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M:%S")
                        time_7 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
                        time_14 = (datetime.now() - timedelta(days=14)).strftime("%Y-%m-%d %H:%M:%S")
                        time_30 = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
                        if fl == True:
                            api_url = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/detail"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"nmIDs": spis_nmids, "period": {"begin": time_7, "end": time_now}, "page": 1}
                            response = requests.post(api_url, headers=headers, json=params, timeout=10)
                            stat7 = response.json()
                            spis_stat7 = stat7['data']['cards']
                            spis_stat7_new = []
                            for i in range(len(spis_nmids)):
                                for s in spis_stat7:
                                    if s['nmID'] == spis_nmids[i]:
                                        spis_stat7_new.append(s)
                            stat7['data']['cards'] = spis_stat7_new
                            params = {"nmIDs": spis_nmids, "period": {"begin": time_14, "end": time_now}, "page": 1}
                            response = requests.post(api_url, headers=headers, json=params, timeout=10)
                            stat14 = response.json()
                            spis_stat14 = stat14['data']['cards']
                            spis_stat14_new = []
                            for i in range(len(spis_nmids)):
                                for s in spis_stat14:
                                    if s['nmID'] == spis_nmids[i]:
                                        spis_stat14_new.append(s)
                            stat14['data']['cards'] = spis_stat14_new
                            params = {"nmIDs": spis_nmids, "period": {"begin": time_30, "end": time_now}, "page": 1}
                            response = requests.post(api_url, headers=headers, json=params, timeout=10)
                            stat30 = response.json()
                            spis_stat30 = stat30['data']['cards']
                            spis_stat30_new = []
                            for i in range(len(spis_nmids)):
                                for s in spis_stat30:
                                    if s['nmID'] == spis_nmids[i]:
                                        spis_stat30_new.append(s)
                            stat30['data']['cards'] = spis_stat30_new
                        try:
                            text += f"\U0001F45BПроцент выкупа (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['conversions']['buyoutsPercent']}\n"
                            text += f"\U0001F4C8Количество заказов в день, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['avgOrdersCountPerDay']}\n"
                            text += f"\U0001F4CAЧисло продаж, шт. (7/14/30 дней): {stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat14['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']} / {stat30['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount']}\n"
                        except:
                            print("stat_false")
                        try:
                            obor = round(stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['stocks']['stocksWb'] /  stat7['data']['cards'][spis_nmids.index(data2['cards'][0]['nmID'])]['statistics']['selectedPeriod']['buyoutsCount'] * 7)
                            if obor < 30:
                                obor_it = "\U0001F7E2Дефицит"
                            else:
                                obor_it = "\U0001F534Профицит"
                            text += f"**{obor_it}** товара по результатам оценки.\n\U0001F4E6Остаток на складах:\n"
                        except:
                            print("obor_false")
                        if fl == True:
                            api_url = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"
                            headers = {'Authorization': api_key, 'Content-Type': 'application/json'}
                            params = {"dateFrom": "2019-06-20"}
                            response = requests.get(api_url, headers=headers, params=params, timeout=10)
                            if response.status_code == 429:
                                osts = requests_dict[f'{seller[5]}'][2]
                            elif response.status_code == 200:
                                osts = response.json()
                                try:
                                    if len(requests_dict[f'{seller[5]}']) == 2:
                                        (requests_dict[f'{seller[5]}']).append(osts)
                                    elif len(requests_dict[f'{seller[5]}']) == 1:
                                        (requests_dict[f'{seller[5]}']).append(0)
                                        (requests_dict[f'{seller[5]}']).append(osts)
                                    else:
                                        requests_dict[f'{seller[5]}'][2] = osts
                                except:
                                    requests_dict[f'{seller[5]}'] = [0, 0, osts]
                        values = {}
                        try:
                            for ost in osts:
                                if ost["nmId"] == data2['cards'][0]['nmID']:
                                    if ost['techSize'] not in values:
                                        values[f"{ost['techSize']}"] = ost['quantity']
                                    else:
                                        values[f"{ost['techSize']}"] = (values[f"{ost['techSize']}"] + ost['quantity'])
                            sort_spis = sorted(values)
                            for el in sort_spis:
                                text += f"    Товар: {el}. Остаток: {values[f'{el}']}\n"
                        except:
                            print("osts_false")
                        count_yest_cancel = 0
                        count_yest_all_cancel = 0
                        price_yest_all_cancel = 0
                        count_today_cancel = 0
                        count_today_all_cancel = 0
                        price_today_all_cancel = 0
                        try:
                            for datas in data_many:
                                if datetime.strptime(datas['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=2)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == True:
                                        count_yest_cancel += 1
                                        count_yest_all_cancel += 1
                                        price_yest_all_cancel += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['isCancel'] == True:
                                        count_yest_all_cancel += 1
                                        price_yest_all_cancel += datas['priceWithDisc']
                            for datas in data_many:
                                if datetime.strptime(datas['cancelDate'][:10], "%Y-%m-%d") == datetime.strptime((date.today() - timedelta(days=1)).strftime("%Y-%m-%d"), "%Y-%m-%d"):
                                    if datas['nmId'] == data2['cards'][0]['nmID'] and datas['orderType'] == "Клиентский" and datas['isCancel'] == True:
                                        count_today_cancel += 1
                                        count_today_all_cancel += 1
                                        price_today_all_cancel += datas['priceWithDisc']
                                    elif datas['orderType'] == "Клиентский" and datas['isCancel'] == True:
                                        count_today_all_cancel += 1
                                        price_today_all_cancel += datas['priceWithDisc']
                            text += f"\U0001F4CDПозавчера таких: {count_yest_cancel} на {round(count_yest_cancel*data['priceWithDisc'], 1)}₽\n\U0001F4CDПозавчера всего: {count_yest_all_cancel} на {round(price_yest_all_cancel, 1)}₽\n\U0001F4CDВчера таких: {count_today_cancel} на {round(count_today_cancel*data['priceWithDisc'], 1)}₽\n\U0001F4CDВчера всего: {count_today_all_cancel} на {round(price_today_all_cancel, 1)}₽"
                            text = f"\U0000274CОтмена заказа!\n(Не забрали с ПВЗ\U0001F7E3) [#{count_today_all_cancel - kolvo_cancel + len_i_cancel + 1}]\n" + text
                        except:
                            print("allstat_false")
                        if len(data2['cards'][0]['photos']) < 3:
                            text += f"<a href={data2['cards'][0]['photos'][0]['big']}>\n\U0001F7E3</a>"
                        else:
                            try:
                                url1 = data2['cards'][0]['photos'][0]['big']
                                url2 = data2['cards'][0]['photos'][1]['big']
                                url3 = data2['cards'][0]['photos'][2]['big']
                                urllib.request.urlretrieve(url1, "Test1.jpg")
                                urllib.request.urlretrieve(url2, "Test2.jpg")
                                urllib.request.urlretrieve(url3, "Test3.jpg")
                                images = [Image.open(x) for x in ['Test1.jpg', 'Test2.jpg', 'Test3.jpg']]
                                widths, heights = zip(*(i.size for i in images))

                                total_width = sum(widths)
                                max_height = max(heights)

                                new_im = Image.new('RGB', (total_width, max_height))

                                x_offset = 0
                                for im in images:
                                    new_im.paste(im, (x_offset,0))
                                    x_offset += im.size[0]

                                new_im.save('test.jpg')
                                img = Image.open(r"test.jpg") 
                                file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
                                file_ext = "test.jpg".split('.')[-1]
                                file_type = file_types[file_ext]
                                with open("test.jpg", 'rb') as f:
                                    url = 'https://telegra.ph/upload'
                                    response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=10)
                                telegraph_url = json.loads(response.content)
                                telegraph_url = telegraph_url[0]['src']
                                telegraph_url = f'https://telegra.ph{telegraph_url}'
                                text += f"<a href={telegraph_url}>&#8205;</a>"
                            except:
                                print("photo_false")
                        len_i_cancel += 1
                        fl = False
                        try:
                            await app.send_message(chat_id=seller[0], text=text)
                        except:
                            cursor.execute("UPDATE Sellers SET notific = ? WHERE id = ?", (0, seller[0]))
                            connection.commit()
                            print("cant_send")
            else:
                print(response.status_code)
    connection.close()


scheduler = AsyncIOScheduler()
scheduler.add_job(sender, "interval", minutes=8)
scheduler.add_job(cancel_sender, "cron", hour='0', minute='3')

scheduler.start()
app.run()

        