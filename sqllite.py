import sqlite3


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file) # выполняет подключение к базе данных
        self.cursor = self.connection.cursor()
    
    
    def create_tables(self):
        with self.connection:
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER UNIQUE PRIMARY KEY, parent TEXT DEFAULT '', pay INT DEFAULT 0);""")
            self.cursor.execute("""CREATE TABLE IF NOT EXISTS promocode(id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT, promo_code TEXT NOT NULL, procent INT DEFAULT 1);""")

    def add_user(self, user_id, parent, user_name):
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `parent`, `user_name`) VALUES (?, ?, ?)", (user_id, parent, user_name, ))
    
    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchall()
            return bool(len(result))
        
    def get_users(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `users`").fetchall()
            return result
        
    def get_promocode(self):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `promocode`").fetchall()
            return result
        
    def set_pay(self, user_id):
        with self.connection:
            result = self.cursor.execute(f"UPDATE users SET pay = 1 WHERE user_id = {user_id}")
            return result

    def del_promocode(self, id):
        with self.connection:
            self.cursor.execute(f"DELETE FROM promocode WHERE id = {id}")

        
    def get_parent(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT parent FROM `users` WHERE parent = ?", (user_id,)).fetchall()
            return result
        
    def check_promo_code(self, promo_code):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM `promocode` WHERE `promo_code` = ?", (promo_code,)).fetchone()
            return result
        
    def add_promocode(self, promocode, procent):
        with self.connection:
            return self.cursor.execute("INSERT INTO `promocode` (`promo_code`, `procent`) VALUES (?, ?)", (promocode, procent, ))