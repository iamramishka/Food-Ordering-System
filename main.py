import sqlite3
import hashlib

#Connect to SQLite database
conn = sqlite3.connect('food_ordering.db')
cursor = conn.cursor()

#Create tables if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS restaurants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    restaurant_id INTEGER,
                    item TEXT,
                    price REAL,
                    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id))''')

cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    item TEXT,
                    quantity INTEGER,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (user_id) REFERENCES users(id))''')

#Sample data
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('ramishka', hashlib.sha256('123'.encode()).hexdigest()))
cursor.execute("INSERT OR IGNORE INTO restaurants (name) VALUES (?)", ('Pizza Palace',))
cursor.execute("INSERT OR IGNORE INTO menu (restaurant_id, item, price) VALUES (?, ?, ?)", (1, 'Margherita Pizza', 10.99))
cursor.execute("INSERT OR IGNORE INTO menu (restaurant_id, item, price) VALUES (?, ?, ?)", (1, 'Pepperoni Pizza', 12.99))
cursor.execute("INSERT OR IGNORE INTO menu (restaurant_id, item, price) VALUES (?, ?, ?)", (1, 'Veggie Supreme Pizza', 11.99))

conn.commit()

def login():
    username = input("Username: ")
    password = hashlib.sha256(input("Password: ").encode()).hexdigest()
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        print(f"Login successful! Welcome, {username}!")
        return user[0]
    else:
        print("Invalid username or password.")
        return None

def register():
    username = input("Enter a username: ")
    password = hashlib.sha256(input("Enter a password: ").encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    print("Registration successful! Please log in.")

def browse_restaurants():
    cursor.execute("SELECT * FROM restaurants")
    restaurants = cursor.fetchall()
    print("Available Restaurants:")
    for restaurant in restaurants:
        print(f"{restaurant[0]}. {restaurant[1]}")

def browse_menu(restaurant_id):
    cursor.execute("SELECT * FROM menu WHERE restaurant_id=?", (restaurant_id,))
    menu_items = cursor.fetchall()
    print("Menu for Restaurant:")
    for item in menu_items:
        print(f"{item[0]}. {item[2]} - ${item[3]}")

def place_order(user_id):
    restaurant_id = int(input("Please enter the number of the restaurant you'd like to browse: "))
    browse_menu(restaurant_id)
    item_id = int(input("Please enter the number of the item you'd like to add to your cart (or 0 to go back): "))
    if item_id == 0:
        return
    quantity = int(input("Quantity: "))
    cursor.execute("SELECT item, price FROM menu WHERE id=?", (item_id,))
    item_info = cursor.fetchone()
    if item_info:
        item_name, price = item_info
        cursor.execute("INSERT INTO orders (user_id, item, quantity) VALUES (?, ?, ?)", (user_id, item_name, quantity))
        conn.commit()
        print(f"{item_name} added to cart.")
    else:
        print("Invalid item selection.")

def view_cart(user_id):
    cursor.execute("SELECT item, price, quantity FROM orders WHERE user_id=?", (user_id,))
    cart_items = cursor.fetchall()
    total = 0
    print("Your Cart:")
    for item in cart_items:
        item_name, price, quantity = item
        print(f"{item_name} - ${price} x {quantity}")
        total += price * quantity
    print("\nTotal:", total)

def main():
    print("Welcome to Our Food Ordering System!")
    while True:
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = input("Please enter your choice: ")
        if choice == "1":
            user_id = login()
            if user_id:
                while True:
                    print("1. Browse Restaurants")
                    print("2. View Cart")
                    print("3. Logout")
                    inner_choice = input("Please enter your choice: ")
                    if inner_choice == "1":
                        browse_restaurants()
                        place_order(user_id)
                    elif inner_choice == "2":
                        view_cart(user_id)
                    elif inner_choice == "3":
                        print("Logged out successfully. Goodbye!")
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == "2":
            register()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
