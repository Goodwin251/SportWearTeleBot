import telebot
from telebot import types
import sqlite3
import os
from datetime import datetime

TOKEN = 'NO'
bot = telebot.TeleBot(TOKEN)

def init_db():
    if not os.path.exists('data'):
        os.makedirs('data')
        
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        address TEXT,
        registration_date TIMESTAMP
    )
    ''')
    

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        name TEXT,
        description TEXT,
        price REAL,
        image_url TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        size TEXT,
        added_date TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_price REAL,
        status TEXT,
        order_date TIMESTAMP,
        delivery_address TEXT,
        phone TEXT,
        payment_method TEXT,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_details (
        detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        size TEXT,
        price REAL,
        FOREIGN KEY (order_id) REFERENCES orders(order_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
    ''')


    cursor.execute('SELECT COUNT(*) FROM products')
    count = cursor.fetchone()[0]
    
    if count == 0:
        products = [
            ('Футболки', 'Спортивна футболка Nike Dri-FIT', 'Чоловіча футболка для тренувань з технологією Dri-FIT', 899.99, 'nike_tshirt.jpg'),
            ('Футболки', 'Спортивна футболка Adidas', 'Жіноча футболка для бігу з вентиляцією', 799.99, 'adidas_tshirt.jpg'),
            ('Штани', 'Спортивні штани Nike', 'Чоловічі штани для тренувань з еластичним поясом', 1299.99, 'nike_pants.jpg'),
            ('Штани', 'Спортивні легінси Puma', 'Жіночі легінси для фітнесу високої посадки', 1099.99, 'puma_leggings.jpg'),
            ('Взуття', 'Кросівки для бігу Nike Air Zoom', 'Легкі кросівки з амортизацією для бігу', 3499.99, 'nike_shoes.jpg'),
            ('Взуття', 'Кросівки Adidas Ultraboost', 'Кросівки з підтримкою стопи для тривалих тренувань', 4299.99, 'adidas_shoes.jpg'),
            ('Аксесуари', 'Спортивна сумка Under Armour', 'Містка сумка для спортивного спорядження', 1499.99, 'ua_bag.jpg'),
            ('Аксесуари', 'Спортивні шкарпетки Nike (3 пари)', 'Комплект шкарпеток для тренувань з підтримкою стопи', 399.99, 'nike_socks.jpg'),
        ]
        
        cursor.executemany('INSERT INTO products (category, name, description, price, image_url) VALUES (?, ?, ?, ?, ?)', products)
    
    conn.commit()
    conn.close()

init_db()

def register_user(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('''
        INSERT INTO users (user_id, username, first_name, last_name, registration_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, datetime.now()))
        conn.commit()
    
    conn.close()

@bot.message_handler(commands=['start'])
def start(message):
    register_user(message)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    item1 = types.KeyboardButton('🛍 Каталог')
    item2 = types.KeyboardButton('🛒 Мій кошик')
    item3 = types.KeyboardButton('📦 Мої замовлення')
    item4 = types.KeyboardButton('👤 Особистий кабінет')
    item5 = types.KeyboardButton('❓ Допомога')
    markup.add(item1, item2, item3, item4, item5)
    
    bot.send_message(
        message.chat.id,
        f"Вітаємо, {message.from_user.first_name}! 👋\n\n"
        f"Це бот для замовлення спортивного одягу. "
        f"Оберіть пункт меню, щоб почати роботу.",
        reply_markup=markup
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📚 *Довідка по командах:*\n\n"
        "/start - Головне меню бота\n"
        "/catalog - Перегляд каталогу товарів\n"
        "/cart - Перегляд кошика\n"
        "/orders - Перегляд замовлень\n"
        "/profile - Особистий кабінет\n"
        "/help - Отримати цю довідку\n\n"
        "Для додаткової допомоги натисніть кнопку '❓ Допомога' в меню.",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['catalog'])
def show_catalog(message):
    show_categories(message)

def show_categories(message):
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT DISTINCT category FROM products')
    categories = cursor.fetchall()
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    for category in categories:
        markup.add(types.InlineKeyboardButton(category[0], callback_data=f'category_{category[0]}'))
    
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='back_to_main'))
    
    bot.send_message(
        message.chat.id,
        "🛍 *Категорії товарів:*\n\nОберіть категорію для перегляду:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

@bot.message_handler(commands=['cart'])
def show_cart(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT products.name, cart.quantity, cart.size, products.price, cart.cart_id, products.product_id
    FROM cart
    JOIN products ON cart.product_id = products.product_id
    WHERE cart.user_id = ?
    ''', (user_id,))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        bot.send_message(message.chat.id, "🛒 Ваш кошик порожній.")
        conn.close()
        return
    
    total_price = 0
    cart_text = "🛒 *Ваш кошик:*\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for i, (name, quantity, size, price, cart_id, product_id) in enumerate(cart_items, 1):
        item_total = quantity * price
        total_price += item_total
        
        cart_text += f"{i}. {name}\n"
        cart_text += f"   Розмір: {size}, Кількість: {quantity}, Ціна: {price} грн\n"
        cart_text += f"   Сума: {item_total:.2f} грн\n\n"
        
        item_markup = types.InlineKeyboardMarkup(row_width=3)
        item_markup.add(
            types.InlineKeyboardButton("-", callback_data=f'decrease_{cart_id}'),
            types.InlineKeyboardButton(f"{quantity}", callback_data=f'quantity_{cart_id}'),
            types.InlineKeyboardButton("+", callback_data=f'increase_{cart_id}'),
            types.InlineKeyboardButton("🗑 Видалити", callback_data=f'remove_{cart_id}')
        )
        
    cart_text += f"*Загальна сума: {total_price:.2f} грн*"
    
    markup.add(
        types.InlineKeyboardButton("🧹 Очистити кошик", callback_data='clear_cart'),
        types.InlineKeyboardButton("📦 Оформити замовлення", callback_data='checkout'),
        types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')
    )
    
    bot.send_message(
        message.chat.id,
        cart_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

@bot.message_handler(commands=['orders'])
def show_orders(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT order_id, total_price, status, order_date
    FROM orders
    WHERE user_id = ?
    ORDER BY order_date DESC
    ''', (user_id,))
    
    orders = cursor.fetchall()
    
    if not orders:
        bot.send_message(message.chat.id, "📦 У вас поки немає замовлень.")
        conn.close()
        return
    
    orders_text = "📦 *Ваші замовлення:*\n\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for order_id, total_price, status, order_date in orders:
        date_str = datetime.fromisoformat(order_date).strftime('%d.%m.%Y %H:%M')
        orders_text += f"*Замовлення #{order_id}*\n"
        orders_text += f"Дата: {date_str}\n"
        orders_text += f"Сума: {total_price:.2f} грн\n"
        orders_text += f"Статус: {status}\n\n"
        
        markup.add(types.InlineKeyboardButton(f"📝 Деталі замовлення #{order_id}", callback_data=f'order_details_{order_id}'))
    
    markup.add(types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main'))
    
    bot.send_message(
        message.chat.id,
        orders_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

@bot.message_handler(commands=['profile'])
def show_profile(message):
    user_id = message.from_user.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        bot.send_message(message.chat.id, "❗ Помилка отримання даних користувача.")
        conn.close()
        return
    
    user_id, username, first_name, last_name, phone, address, registration_date = user
    
    profile_text = "👤 *Особистий кабінет*\n\n"
    profile_text += f"Ім'я: {first_name or 'Не вказано'}\n"
    profile_text += f"Прізвище: {last_name or 'Не вказано'}\n"
    profile_text += f"Телефон: {phone or 'Не вказано'}\n"
    profile_text += f"Адреса: {address or 'Не вказана'}\n"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📝 Змінити телефон", callback_data='edit_phone'),
        types.InlineKeyboardButton("📝 Змінити адресу", callback_data='edit_address'),
        types.InlineKeyboardButton("📦 Мої замовлення", callback_data='show_orders'),
        types.InlineKeyboardButton("🔙 Назад", callback_data='back_to_main')
    )
    
    bot.send_message(
        message.chat.id,
        profile_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '🛍 Каталог':
        show_categories(message)
    elif message.text == '🛒 Мій кошик':
        show_cart(message)
    elif message.text == '📦 Мої замовлення':
        show_orders(message)
    elif message.text == '👤 Особистий кабінет':
        show_profile(message)
    elif message.text == '❓ Допомога':
        help_command(message)
    else:
        bot.send_message(message.chat.id, "Оберіть пункт меню або скористайтеся командами /help для довідки")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback_query(call):
    if call.data == 'back_to_main':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        start(call.message)
    
    elif call.data.startswith('category_'):
        category_name = call.data.split('_')[1]
        show_products_by_category(call.message, category_name)
    
    elif call.data.startswith('product_'):
        product_id = int(call.data.split('_')[1])
        show_product_details(call.message, product_id)
    
    elif call.data.startswith('add_to_cart_'):
        parts = call.data.split('_')
        product_id = int(parts[3])
        size = parts[4]
        add_to_cart(call.message, product_id, size)
        bot.answer_callback_query(call.id, "✅ Товар додано до кошика")
    
    elif call.data.startswith('increase_'):
        cart_id = int(call.data.split('_')[1])
        change_cart_quantity(call.message, cart_id, 1)
        bot.answer_callback_query(call.id, "✅ Кількість збільшено")
        show_cart(call.message)
    
    elif call.data.startswith('decrease_'):
        cart_id = int(call.data.split('_')[1])
        change_cart_quantity(call.message, cart_id, -1)
        bot.answer_callback_query(call.id, "✅ Кількість зменшено")
        show_cart(call.message)
    
    elif call.data.startswith('remove_'):
        cart_id = int(call.data.split('_')[1])
        remove_from_cart(call.message, cart_id)
        bot.answer_callback_query(call.id, "✅ Товар видалено з кошика")
        show_cart(call.message)

    elif call.data == 'clear_cart':
        clear_cart(call.message)
        bot.answer_callback_query(call.id, "✅ Кошик очищено")
        bot.send_message(call.message.chat.id, "🧹 Ваш кошик очищено")
    
    elif call.data == 'checkout':
        start_checkout(call.message)
        bot.answer_callback_query(call.id, "🛒 Оформлення замовлення")
    
    elif call.data.startswith('order_details_'):
        order_id = int(call.data.split('_')[2])
        show_order_details(call.message, order_id)

    elif call.data == 'edit_phone':
        ask_for_phone(call.message)
        bot.answer_callback_query(call.id, "📱 Введіть новий номер телефону")

    elif call.data == 'edit_address':
        ask_for_address(call.message)
        bot.answer_callback_query(call.id, "📍 Введіть нову адресу")

    elif call.data == 'show_orders':
        show_orders(call.message)
        bot.answer_callback_query(call.id, "📦 Ваші замовлення")

def show_products_by_category(message, category_name):
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT product_id, name, price, description FROM products WHERE category = ?', (category_name,))
    products = cursor.fetchall()
    
    if not products:
        bot.send_message(message.chat.id, f"У категорії '{category_name}' поки немає товарів.")
        conn.close()
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for product_id, name, price, description in products:
        button_text = f"{name} - {price:.2f} грн"
        markup.add(types.InlineKeyboardButton(button_text, callback_data=f'product_{product_id}'))
    
    markup.add(types.InlineKeyboardButton('🔙 До категорій', callback_data='back_to_categories'))
    
    bot.send_message(
        message.chat.id,
        f"🛍 *Товари в категорії '{category_name}'*\n\nОберіть товар для перегляду деталей:",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

def show_product_details(message, product_id):
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, description, price, category, image_url FROM products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    
    if not product:
        bot.send_message(message.chat.id, "❗ Товар не знайдено.")
        conn.close()
        return
    
    name, description, price, category, image_url = product
    
    product_text = f"*{name}*\n\n"
    product_text += f"*Категорія:* {category}\n"
    product_text += f"*Ціна:* {price:.2f} грн\n\n"
    product_text += f"*Опис:*\n{description}\n"
    
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    markup = types.InlineKeyboardMarkup(row_width=3)
    
    size_buttons = []
    for size in sizes:
        size_buttons.append(types.InlineKeyboardButton(size, callback_data=f'add_to_cart_{product_id}_{size}'))
    
    markup.add(*size_buttons)
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data=f'category_{category}'))
    
    try:
        if os.path.exists(f'images/{image_url}'):
            with open(f'images/{image_url}', 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=product_text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        else:
            bot.send_message(
                message.chat.id,
                product_text + "\n\n*Оберіть розмір для додавання в кошик:*",
                reply_markup=markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            product_text + "\n\n*Оберіть розмір для додавання в кошик:*",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    
    conn.close()

def add_to_cart(message, product_id, size):
    user_id = message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT cart_id, quantity FROM cart 
    WHERE user_id = ? AND product_id = ? AND size = ?
    ''', (user_id, product_id, size))
    
    existing_item = cursor.fetchone()
    
    if existing_item:
        cart_id, quantity = existing_item
        cursor.execute('''
        UPDATE cart SET quantity = quantity + 1 WHERE cart_id = ?
        ''', (cart_id,))
    else:
        cursor.execute('''
        INSERT INTO cart (user_id, product_id, quantity, size, added_date)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, product_id, 1, size, datetime.now()))
    
    conn.commit()
    conn.close()

def change_cart_quantity(message, cart_id, change):
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT quantity FROM cart WHERE cart_id = ?', (cart_id,))
    current_quantity = cursor.fetchone()[0]
    
    new_quantity = current_quantity + change
    
    if new_quantity <= 0:
        cursor.execute('DELETE FROM cart WHERE cart_id = ?', (cart_id,))
    else:
        cursor.execute('UPDATE cart SET quantity = ? WHERE cart_id = ?', (new_quantity, cart_id))
    
    conn.commit()
    conn.close()

def remove_from_cart(message, cart_id):
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM cart WHERE cart_id = ?', (cart_id,))
    
    conn.commit()
    conn.close()


def clear_cart(message):
    user_id = message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()


def start_checkout(message):
    user_id = message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM cart WHERE user_id = ?', (user_id,))
    count = cursor.fetchone()[0]
    
    if count == 0:
        bot.send_message(message.chat.id, "❗ Ваш кошик порожній. Додайте товари перед оформленням замовлення.")
        conn.close()
        return
    
    cursor.execute('SELECT phone, address FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()
    
    phone, address = user_data if user_data else (None, None)
    
    if not phone:
        ask_for_phone(message)
    elif not address:
        ask_for_address(message)
    else:
        confirm_order(message, phone, address)
    
    conn.close()

def ask_for_phone(message):
    msg = bot.send_message(
        message.chat.id,
        "📱 Будь ласка, введіть ваш номер телефону для оформлення замовлення:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_phone_step)

def process_phone_step(message):
    user_id = message.from_user.id
    phone = message.text.strip()
    
    if len(phone) < 10:
        msg = bot.send_message(
            message.chat.id,
            "❗ Номер телефону занадто короткий. Будь ласка, введіть правильний номер:"
        )
        bot.register_next_step_handler(msg, process_phone_step)
        return
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET phone = ? WHERE user_id = ?', (phone, user_id))
    conn.commit()
    
    cursor.execute('SELECT address FROM users WHERE user_id = ?', (user_id,))
    address = cursor.fetchone()[0]
    
    conn.close()
    
    if not address:
        ask_for_address(message)
    else:
        confirm_order(message, phone, address)
def ask_for_address(message):
    msg = bot.send_message(
        message.chat.id,
        "📍 Будь ласка, введіть вашу адресу доставки:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, process_address_step)

def process_address_step(message):
    user_id = message.from_user.id
    address = message.text.strip()
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET address = ? WHERE user_id = ?', (address, user_id))
    conn.commit()
    
    cursor.execute('SELECT phone FROM users WHERE user_id = ?', (user_id,))
    phone = cursor.fetchone()[0]
    
    conn.close()
    
    confirm_order(message, phone, address)

def confirm_order(message, phone, address):
    user_id = message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT products.name, cart.quantity, cart.size, products.price, products.product_id
    FROM cart
    JOIN products ON cart.product_id = products.product_id
    WHERE cart.user_id = ?
    ''', (user_id,))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        bot.send_message(message.chat.id, "❗ Ваш кошик порожній.")
        conn.close()
        return
        
    total_price = 0
    order_text = "📦 *Підтвердження замовлення*\n\n"
    
    for name, quantity, size, price, _ in cart_items:
        item_total = quantity * price
        total_price += item_total
        
        order_text += f"• {name}\n"
        order_text += f"  Розмір: {size}, Кількість: {quantity}, Ціна: {price:.2f} грн\n"
        order_text += f"  Сума: {item_total:.2f} грн\n\n"
    
    order_text += f"*Загальна сума: {total_price:.2f} грн*\n\n"
    order_text += f"*Телефон:* {phone}\n"
    order_text += f"*Адреса доставки:* {address}\n\n"
    order_text += "Бажаєте підтвердити замовлення?"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Підтвердити", callback_data='confirm_order'),
        types.InlineKeyboardButton("❌ Скасувати", callback_data='cancel_order'),
        types.InlineKeyboardButton("📝 Змінити телефон", callback_data='edit_phone'),
        types.InlineKeyboardButton("📝 Змінити адресу", callback_data='edit_address')
    )
    
    bot.send_message(
        message.chat.id,
        order_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')
def handle_confirm_order(call):
    user_id = call.message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT phone, address FROM users WHERE user_id = ?', (user_id,))
        user_data = cursor.fetchone()
        
        if not user_data:
            bot.answer_callback_query(call.id, "❗ Помилка отримання даних користувача.")
            conn.close()
            return
            
        phone, address = user_data
        
        cursor.execute('''
        SELECT products.product_id, cart.quantity, cart.size, products.price
        FROM cart
        JOIN products ON cart.product_id = products.product_id
        WHERE cart.user_id = ?
        ''', (user_id,))
        
        cart_items = cursor.fetchall()
        
        if not cart_items:
            bot.answer_callback_query(call.id, "❗ Кошик порожній.")
            conn.close()
            return
            
        total_price = sum(quantity * price for _, quantity, _, price in cart_items)
        
        cursor.execute('''
        INSERT INTO orders (user_id, total_price, status, order_date, delivery_address, phone, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, total_price, 'Нове', datetime.now(), address, phone, 'Оплата при отриманні'))
        
        order_id = cursor.lastrowid
        
        for product_id, quantity, size, price in cart_items:
            cursor.execute('''
            INSERT INTO order_details (order_id, product_id, quantity, size, price)
            VALUES (?, ?, ?, ?, ?)
            ''', (order_id, product_id, quantity, size, price))
        
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
        
        conn.commit()
        
        success_text = (
            f"✅ *Замовлення #{order_id} успішно оформлено!*\n\n"
            f"Загальна сума: {total_price:.2f} грн\n"
            f"Спосіб оплати: Оплата при отриманні\n"
            f"Статус: Нове\n\n"
            f"Дякуємо за ваше замовлення! Ми зв'яжемося з вами найближчим часом для підтвердження."
        )
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("📦 Мої замовлення", callback_data='show_orders'),
            types.InlineKeyboardButton("🛍 Продовжити покупки", callback_data='back_to_main')
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=success_text,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
        bot.answer_callback_query(call.id, "✅ Замовлення успішно оформлено!")
    
    except Exception as e:
        print(f"Error processing order: {e}")
        bot.answer_callback_query(call.id, "❗ Помилка оформлення замовлення. Спробуйте ще раз.")
    
    finally:
        conn.close()

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_order')
def handle_cancel_order(call):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="❌ Оформлення замовлення скасовано.",
        parse_mode="Markdown"
    )
    bot.answer_callback_query(call.id, "Замовлення скасовано")

def show_order_details(message, order_id):
    user_id = message.chat.id
    
    conn = sqlite3.connect('data/sportscloth_shop.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT order_id, total_price, status, order_date, delivery_address, phone, payment_method
    FROM orders
    WHERE order_id = ? AND user_id = ?
    ''', (order_id, user_id))
    
    order = cursor.fetchone()
    
    if not order:
        bot.send_message(message.chat.id, "❗ Замовлення не знайдено.")
        conn.close()
        return
    
    order_id, total_price, status, order_date, delivery_address, phone, payment_method = order
    date_str = datetime.fromisoformat(order_date).strftime('%d.%m.%Y %H:%M')
    
    cursor.execute('''
    SELECT products.name, order_details.quantity, order_details.size, order_details.price
    FROM order_details
    JOIN products ON order_details.product_id = products.product_id
    WHERE order_details.order_id = ?
    ''', (order_id,))
    
    details = cursor.fetchall()
    
    order_text = f"📦 *Замовлення #{order_id}*\n\n"
    order_text += f"*Дата:* {date_str}\n"
    order_text += f"*Статус:* {status}\n"
    order_text += f"*Телефон:* {phone}\n"
    order_text += f"*Адреса доставки:* {delivery_address}\n"
    order_text += f"*Спосіб оплати:* {payment_method}\n\n"
    
    order_text += "*Товари:*\n\n"
    
    for name, quantity, size, price in details:
        item_total = quantity * price
        order_text += f"• {name}\n"
        order_text += f"  Розмір: {size}, Кількість: {quantity}, Ціна: {price:.2f} грн\n"
        order_text += f"  Сума: {item_total:.2f} грн\n\n"
    
    order_text += f"*Загальна сума: {total_price:.2f} грн*"
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔙 До замовлень", callback_data='show_orders'),
        types.InlineKeyboardButton("🔙 Головне меню", callback_data='back_to_main')
    )
    
    bot.send_message(
        message.chat.id,
        order_text,
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
    conn.close()

if __name__ == '__main__':
    if not os.path.exists('images'):
        os.makedirs('images')
    
    bot.polling(none_stop=True)