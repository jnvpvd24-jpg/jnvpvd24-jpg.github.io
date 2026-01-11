from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
DATABASE = 'inventory.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   name TEXT NOT NULL,
                   price REAL NOT NULL,
                   quantity INTEGER NOT NULL
                 )''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   product_id INTEGER,
                   quantity INTEGER,
                   sale_date TEXT,
                   total_price REAL,
                   FOREIGN KEY(product_id) REFERENCES products(id)
                 )''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    products = c.fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        quantity = int(request.form['quantity'])
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)", (name, price, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_product.html')



@app.route('/bill', methods=['GET', 'POST'])
def bill():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT id, name, price, quantity FROM products")
    products = c.fetchall()

    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        product_id = int(request.form['product_id'])
        sale_qty = int(request.form['quantity'])

        c.execute("SELECT name, price, quantity FROM products WHERE id=?", (product_id,))
        product = c.fetchone()
        product_name, price, stock = product

        if stock >= sale_qty:
            new_stock = stock - sale_qty
            c.execute("UPDATE products SET quantity=? WHERE id=?", (new_stock, product_id))
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            total_price = price * sale_qty
            c.execute("INSERT INTO sales (product_id, quantity, sale_date, total_price) VALUES (?, ?, ?, ?)",
                      (product_id, sale_qty, sale_date, total_price))
            conn.commit()
            conn.close()

            bill_data = {
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'product_name': product_name,
                'quantity': sale_qty,
                'unit_price': price,
                'total_price': total_price,
                'sale_date': sale_date,
            }
            return render_template('bill_receipt.html', bill=bill_data)
        else:
            conn.close()
            return render_template('bill.html', products=products, message="Insufficient stock.")
    return render_template('bill.html', products=products)



if __name__ == '__main__':
    init_db()
    app.run(debug=True,port=5005)