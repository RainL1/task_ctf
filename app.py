from flask import Flask, session, request, render_template, redirect, url_for
from flask_session import Session
import random
import string
import os
from datetime import timedelta
import json
from functools import wraps

app = Flask(__name__)
# Генерируем уникальный секретный ключ для сессий (НЕ меняйте после запуска!)
app.secret_key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=33))

# НАСТРОЙКА СЕРВЕРНЫХ СЕССИЙ
app.config['SECRET_KEY'] = app.secret_key
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(os.path.dirname(__file__), 'flask_session')
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'f1_shop_'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

# Создаем директорию для сессий
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
sess = Session(app)

# Файл для хранения пользователей
USER_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users():
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

users = load_users()

# Список товаров (больше мерча)
goods = [
    {'id': 1, 'name': 'Red Bull T-shirt', 'price': 5, 'image': 'https://images.footballfanatics.com/red-bull-racing/red-bull-racing-2025-team-set-up-t-shirt_ss5_p-201493637+u-zcrjb8qxo0imqc69ik1y+v-ihj5khl6e8blltwmuwrk.jpg?_hv=2'},
    {'id': 2, 'name': 'McLaren Cap', 'price': 7, 'image': 'http://us.mclarenstore.com/cdn/shop/files/60691413_2.jpg?v=1739288352'},
    {'id': 3, 'name': 'Aston Martin Hoodie', 'price': 10, 'image': 'https://shop.astonmartinf1.com/dw/image/v2/BDWJ_PRD/on/demandware.static/-/Sites-master-catalog/default/dwfa5f68c5/images/large/701229401001_pp_01_AstonMartinF1.jpg?sw=800&sh=800&sm=fit'},
    {'id': 4, 'name': 'Ferrari Mug', 'price': 6, 'image': 'https://m.media-amazon.com/images/I/61bXuY8HcqL.jpg'},
    {'id': 5, 'name': 'Mercedes Keychain', 'price': 4, 'image': 'https://shop-us.mercedesamgf1.com/cdn/shop/files/MAPF1FWLEATHERKEYRING-FRONT.jpg?v=1736198612&width=1800'},
    {'id': 6, 'name': 'Mercedes T-shirt', 'price': 5, 'image': 'https://shop-us.mercedesamgf1.com/cdn/shop/files/JW5363_1_APPAREL_Photography_FrontCenterView_grey030225030225.jpg?v=1738589001&width=1600'},
    {'id': 7, 'name': 'Ferrari Cap', 'price': 7, 'image': 'https://images.footballfanatics.com/scuderia-ferrari/scuderia-ferrari-2025-team-lewis-hamilton-cap-red_ss5_p-202358980+u-cyv4xtwh0yojc1dmjekk+v-irkryngn7dusjeqb7lx8.jpg?_hv=2&w=532'},
    {'id': 8, 'name': 'Alpine Hoodie', 'price': 10, 'image': 'https://images.footballfanatics.com/alpine/alpine-f1-team-2025-full-zip-hoodie_ss5_p-201494921+u-ykt241h7l1mi5jge7mcx+v-jqeflxm4kspxn7usd9kv.jpg?_hv=2&w=532'},
    {'id': 9, 'name': 'Williams Mug', 'price': 6, 'image': 'https://i.ebayimg.com/images/g/qaoAAOSwH21fYTGa/s-l400.jpg'},
    {'id': 10, 'name': 'Haas Keychain', 'price': 4, 'image': 'https://i.etsystatic.com/46796729/r/il/5a835a/6970030815/il_1080xN.6970030815_69sv.jpg'},
    {'id': 11, 'name': 'Alpine T-shirt', 'price': 5, 'image': 'https://images.footballfanatics.com/alpine/alpine-f1-team-2025-team-t-shirt_ss5_p-201494920+u-5m3xq9kc4nrr0j9d5vmx+v-vb2z6b8v1z7j2a4f7q5m.jpg?_hv=2'},  # Ещё один для разнообразия
    {'id': 12, 'name': 'Champion Flag', 'price': 10000000, 'image': None}  # Секретный
]

# Новости (статичные на основе поиска)
news_items = [
    {'title': '5 storylines we\'re excited about ahead of the 2025 United States GP', 'description': 'From the Drivers\' Championship heating up, to George Russell looking to back up his Singapore win.'},
    {'title': 'When is the F1 US Grand Prix, how can I watch?', 'description': 'Formula 1 returns to the United States, marking the final quarter of the 2025 championship.'},
    {'title': 'United States GP: What can Ferrari salvage from rest of 2025 season?', 'description': 'Ferrari returns to venues of recent wins amid pressure from Mercedes and Red Bull.'},
    {'title': 'The Formula 1 field is closer than ever before. But will that all change in 2026?', 'description': '2025 may have the closest field in F1 history, but regulations change next year.'},
]

# Таблица конструкторов
constructors_standings = [
    {'pos': 1, 'team': 'McLaren', 'pts': 557},
    {'pos': 2, 'team': 'Red Bull', 'pts': 512},
    {'pos': 3, 'team': 'Ferrari', 'pts': 479},
    {'pos': 4, 'team': 'Mercedes', 'pts': 372},
    {'pos': 5, 'team': 'Aston Martin', 'pts': 86},
    {'pos': 6, 'team': 'RB', 'pts': 36},
    {'pos': 7, 'team': 'Haas', 'pts': 31},
    {'pos': 8, 'team': 'Williams', 'pts': 17},
    {'pos': 9, 'team': 'Alpine', 'pts': 13},
    {'pos': 10, 'team': 'Kick Sauber', 'pts': 0},
]

# Список команд
teams_list = [
    {'name': 'McLaren', 'description': 'British team based in Woking. Drivers: Lando Norris, Oscar Piastri.'},
    {'name': 'Red Bull', 'description': 'Austrian team based in Milton Keynes. Drivers: Max Verstappen, Sergio Perez.'},
    {'name': 'Ferrari', 'description': 'Italian team based in Maranello. Drivers: Charles Leclerc, Carlos Sainz.'},
    {'name': 'Mercedes', 'description': 'German team based in Brackley. Drivers: Lewis Hamilton, George Russell.'},
    {'name': 'Aston Martin', 'description': 'British team based in Silverstone. Drivers: Fernando Alonso, Lance Stroll.'},
    {'name': 'RB', 'description': 'Italian team based in Faenza. Drivers: Yuki Tsunoda, Daniel Ricciardo.'},
    {'name': 'Haas', 'description': 'American team based in Kannapolis. Drivers: Nico Hulkenberg, Kevin Magnussen.'},
    {'name': 'Williams', 'description': 'British team based in Grove. Drivers: Alex Albon, Franco Colapinto.'},
    {'name': 'Alpine', 'description': 'French team based in Enstone. Drivers: Pierre Gasly, Esteban Ocon.'},
    {'name': 'Kick Sauber', 'description': 'Swiss team based in Hinwil. Drivers: Valtteri Bottas, Zhou Guanyu.'},
]

# Таблица пилотов
drivers_standings = [
    {'pos': 1, 'driver': 'Lando Norris', 'team': 'McLaren', 'pts': 345},
    {'pos': 2, 'driver': 'Max Verstappen', 'team': 'Red Bull', 'pts': 322},
    {'pos': 3, 'driver': 'Oscar Piastri', 'team': 'McLaren', 'pts': 245},
    {'pos': 4, 'driver': 'Charles Leclerc', 'team': 'Ferrari', 'pts': 239},
    {'pos': 5, 'driver': 'Carlos Sainz', 'team': 'Ferrari', 'pts': 210},
    {'pos': 6, 'driver': 'Lewis Hamilton', 'team': 'Mercedes', 'pts': 189},
    {'pos': 7, 'driver': 'George Russell', 'team': 'Mercedes', 'pts': 183},
    {'pos': 8, 'driver': 'Sergio Perez', 'team': 'Red Bull', 'pts': 170},
    {'pos': 9, 'driver': 'Fernando Alonso', 'team': 'Aston Martin', 'pts': 62},
    {'pos': 10, 'driver': 'Nico Hulkenberg', 'team': 'Haas', 'pts': 28},
    # Можно добавить больше, если нужно
]

# Контекст-процессор для username
@app.context_processor
def inject_user():
    return dict(username=session.get('username'))

# Декоратор для要求登录
def require_login(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect(url_for('shop'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            return render_template('register.html', error='Пользователь уже существует')
        users[username] = {'password': password, 'balance': 10, 'cart': [], 'flag': None}
        save_users()
        session['username'] = username
        return redirect(url_for('shop'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('shop'))
        return render_template('login.html', error='Неверные данные')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/shop')
@require_login
def shop():
    user = users[session['username']]
    return render_template('shop.html', 
                           goods=goods, 
                           balance=user['balance'], 
                           flag=user['flag'])

@app.route('/add_to_cart', methods=['POST'])
@require_login
def add_to_cart():
    user = users[session['username']]
    item_id = int(request.form['item_id'])
    qty = int(request.form['qty'])
    
    item = next((g for g in goods if g['id'] == item_id), None)
    if not item:
        return redirect(url_for('shop'))
    
    found = False
    for cart_item in user['cart']:
        if cart_item['id'] == item_id:
            cart_item['qty'] += qty
            found = True
            break
    if not found:
        user['cart'].append({'id': item_id, 'qty': qty})
    
    save_users()
    return redirect(url_for('shop'))

@app.route('/cart')
@require_login
def cart():
    user = users[session['username']]
    cart_items = []
    total = 0
    for c in user['cart']:
        item = next((g for g in goods if g['id'] == c['id']), None)
        if item:
            subtotal = item['price'] * c['qty']
            total += subtotal
            cart_items.append({'item': item, 'qty': c['qty'], 'subtotal': subtotal})
    
    user_info = {
        'user_id': session['username'],
        'balance': user['balance']
    }
    
    return render_template('cart.html', 
                           cart_items=cart_items, 
                           total=total, 
                           balance=user['balance'], 
                           flag=user['flag'],
                           user_info=user_info)

@app.route('/update_cart', methods=['POST'])
@require_login
def update_cart():
    user = users[session['username']]
    item_id = int(request.form['item_id'])
    new_qty = int(request.form['qty'])
    
    for item in user['cart']:
        if item['id'] == item_id:
            item['qty'] = new_qty
            break
    
    save_users()
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@require_login
def checkout():
    user = users[session['username']]
    total_cost = 0
    has_flag = False
    
    for c in user['cart']:
        item = next(g for g in goods if g['id'] == c['id'])
        cost = item['price'] * c['qty']
        total_cost += cost
        if c['id'] == 12 and c['qty'] > 0:  # Секретный флаг
            has_flag = True
    
    if user['balance'] >= total_cost:
        user['balance'] -= total_cost
        if has_flag:
            user['flag'] = 'CTFLyc{GGWP_MAX_CHAMPION}'
        user['cart'] = []
        save_users()
        return redirect(url_for('shop'))
    else:
        return redirect(url_for('cart'))

@app.route('/news')
def news():
    return render_template('news.html', news_items=news_items)

@app.route('/standings')
def standings():
    return render_template('standings.html', standings=constructors_standings)

@app.route('/teams')
def teams():
    return render_template('teams.html', teams=teams_list)

@app.route('/drivers')
def drivers():
    return render_template('drivers.html', standings=drivers_standings)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/session_info')
@require_login
def session_info():
    user = users[session['username']]
    return {
        'user_id': session['username'],
        'balance': user['balance'],
        'cart_count': len(user['cart']),
        'flag': user['flag'],
        'session_id': request.cookies.get('session')
    }

if __name__ == '__main__':
    # Очистка старых сессий при запуске (опционально)
    import shutil
    session_dir = app.config['SESSION_FILE_DIR']
    if os.path.exists(session_dir):
        shutil.rmtree(session_dir, ignore_errors=True)
    os.makedirs(session_dir, exist_ok=True)
    
    print("🚀 F1 Shop Server запущен!")
    print("📁 Сессии сохраняются в:", session_dir)
    print("🌐 Доступен по http://0.0.0.0:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
