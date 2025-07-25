app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

做了什麼？ >>> 這行設定了 SQLAlchemy 使用的 資料庫連線位址（URI）。

解釋：
app.config 是 Flask 應用的設定字典，你可以在裡面加入各種設定。

'SQLALCHEMY_DATABASE_URI' 是 SQLAlchemy 的設定鍵，用來告訴它要連接哪個資料庫。

'sqlite:///users.db' 是資料庫的位置與格式： >>> sqlite 表示使用 SQLite 資料庫（輕量、內建、單一檔案）。
' >>> ///users.db 表示資料庫檔案在目前目錄下，叫做 users.db。

等於是：
告訴 Flask：「我要使用一個叫做 users.db 的 SQLite 資料庫來存資料！」

===

db = SQLAlchemy(app)

做了什麼？
這行建立了一個 SQLAlchemy 的實例，並綁定到這個 Flask 應用 app 上。

解釋：
db 會成為你操作資料庫的工具物件。

你可以用它來：
定義資料表（模型）
執行新增、查詢、刪除、修改等操作
建立與更新資料表架構（例如 db.create_all()）

===

🧪 完整例子：

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # 設定資料庫
db = SQLAlchemy(app)  # 綁定資料庫工具

# 建立一個資料表模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

# 建立資料表
with app.app_context():
    db.create_all()

===

總結:
app.config['SQLALCHEMY_DATABASE_URI'] >>> 
    設定使用哪個資料庫（這裡是 SQLite）

SQLAlchemy(app) >>> 
    建立與 Flask 應用綁定的資料庫物件 db，用來定義與操作資料表。
