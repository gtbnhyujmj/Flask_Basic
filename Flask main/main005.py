from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# UserMixin = 給你的 User 模型加上 Flask-Login 需要的一些基本功能（例如是否已認證）。
# login_user(user) = 呼叫後，使用者就會被視為「已登入」
# login_required = 用來保護某些頁面，只有登入的人才能進入。

# current_user = 代表目前已登入的使用者（類似 session 中的帳號）

from flask_sqlalchemy import SQLAlchemy
# SQLAlchemy = 用來處理資料庫操作的


# Werkzeug 是一個提供 WSGI 支援的 Python 庫
# WSGI = Web Server Gateway Interface，是一個 Python 的標準，用來定義如何讓 Web 伺服器與 Python 應用程式溝通。
from werkzeug.security import generate_password_hash, check_password_hash
# generate_password_hash = 用來將密碼進行雜湊處理
# check_password_hash = 用來檢查密碼是否正確


# Flask實體
app = Flask(__name__)

===

# 設定 SQLite 資料庫路徑
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app) # 這行建立了一個 SQLAlchemy 的實例，並綁定到這個 Flask 實例 (名稱 = app) 上。

# 解釋：
# app.config 是 Flask 應用的設定字典，你可以在裡面加入各種設定。
# SQLALCHEMY_DATABASE_URI 是 SQLAlchemy 的設定鍵，用來告訴它要連接哪個資料庫。
# URI是URL的上位版本

# 'sqlite:///users.db' 是資料庫的位置與格式，這裡使用 SQLite 資料庫，並且資料庫檔案名稱為 users.db。
# 'PostgreSQL' 會不太一樣 >>> "postgresql://user:password@localhost/dbname"

# ///users.db 表示資料庫檔案在目前目錄下，叫做 users.db。
# 會產生一個db在 /instance/users.db，但是不要打instance，會掛掉。

===

# 使用者資料表
# 這是定義一個資料表模型 named = User。
# 它繼承自 db.Model，代表 SQLAlchemy 會把這個 Python 類別對應成一張資料表。
class User(db.Model): # <<< 這段class = 我定義一個叫User的模型，這個模型的內容繼受於db.Model這個模型。
    # 各欄位說明
    
    id = db.Column(db.Integer, primary_key=True) 
    # id = 資料表的主鍵，每個資料都會有唯一的 id。
    # db.Integer: 資料型別：整數
    # primary_key=True: 設定這個欄位是主鍵
    
    username = db.Column(db.String(80), unique=True, nullable=False) 
    # username = 使用者名稱，必須是唯一的，且不能為空。
    # db.String(80): 資料型別：最多 80 字的字串
    # unique=True: 這個欄位值不能重複（用來當帳號很好）
    # nullable=False: 不能是空值（必填欄位）
    
    password_hash = db.Column(db.String(128), nullable=False)
    # password_hash = 密碼的雜湊值，不能為空。
    # db.String(128): 儲存長度最多 128 的字串
    # nullable=False: 必填欄位

===

# 建立資料表（只需要第一次）
# 這段程式是告訴 SQLAlchemy：「根據我定義的模型(看上面)，如果資料庫還沒有對應的資料表，就幫我建立出來。」
with app.app_context():
    db.create_all()

===

@app.route('/')
def home():
    return render_template('home.html')

===

# 建立註冊頁的路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST': # <<< 如果是提交表單（按下註冊按鈕）進來的，就是 POST 方法。
        
        # 從 HTML 表單中取得輸入的使用者名稱
        username = request.form['username'] # request.form 裡面的 username 裡面的資料
        password = request.form['password']
        hashed_pw = generate_password_hash(password) # 加密密碼

        # 建立一個新的 User 物件（也就是一筆新的使用者資料）
        new_user = User(username=username, password_hash=hashed_pw) # 打包資料，對應User這張資料表的定義。
        
        db.session.add(new_user) # 將這筆新資料加到資料庫的交易（Session）中
        db.session.commit() # 提交交易，把資料真的寫入資料庫

        return redirect(url_for('home')) # 完成後自動跳轉瀏覽器到home.html
    
    # 這裡是if...else的結構，不過 >>> 
    # 當 if 後會以 return 結束函式，就不需要寫 else，可以直接接在後面寫。
    # = 電腦看到 return 會結束函式，所以他一定是最後一行。
    return render_template('register.html')
    # 如果是用 GET 方法進來（例如點網址），就顯示註冊頁面的 HTML
    # 先點按鈕，所以先執行這行。然後填完資料，按按鈕，執行上面的if。

#=========================================================================================#

# 登入頁的路由：使用者訪問 /login 頁面時，會執行這個函式
@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果是按下登入按鈕送出表單，就會是 POST 方法
    if request.method == 'POST':
        
        # 從 HTML 表單中取得使用者輸入的帳號與密碼
        username = request.form['username']
        password = request.form['password']

        # 根據使用者名稱去資料庫中查找第一筆符合的使用者資料
        user = User.query.filter_by(username=username).first()

        # 如果找不到這個使用者，就提示錯誤訊息，並重新顯示登入頁
        if user is None:
            flash('找不到使用者')  # flash 是用來顯示短暫訊息的功能
            return render_template('login.html')  # 顯示登入頁面

        # 如果使用者存在，就比對輸入的密碼與資料庫中儲存的加密密碼
        if check_password_hash(user.password_hash, password):
            # 密碼正確，就把使用者的資訊存進 session（這邊是手動方式）
            session['user_id'] = user.id
            session['username'] = user.username

            # 登入成功後，導向到 dashboard（會員中心）頁面
            return redirect(url_for('dashboard'))
        else:
            # 密碼錯誤，顯示錯誤訊息並重回登入頁
            flash('密碼錯誤')
            return render_template('login.html')

    # 如果是用 GET 方法（直接點進來），就顯示登入頁
    return render_template('login.html')

===

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
