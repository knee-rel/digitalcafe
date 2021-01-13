from flask import Flask
from flask import render_template
from flask import request
from flask import Flask, redirect
from flask import session
from flask import flash, render_template
import ordermanagement as om
from bson.json_util import loads, dumps
from flask import make_response

import database as db
import authentication
import logging

app = Flask(__name__)

app.secret_key = b's@g@d@c0ff33!'

logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.INFO)

@app.route('/')
def index():
    return render_template('index.html', page="Index")

@app.route('/products')
def products():
    product_list = db.get_products()
    return render_template('products.html', page="Products", product_list=product_list)

# @app.route('/api/products',methods=['GET'])
# def api_get_products():
#     resp = make_response( dumps(db.get_products()) )
#     resp.mimetype = 'application/json'
#     return resp

@app.route('/api/products/<int:code>',methods=['GET'])
def api_get_products():
    resp = make_response(dumps(db.get_products()))
    resp.mimetype = 'application/json'
    return resp

@app.route('/productdetails')
def productdetails():
    code = request.args.get('code', '')
    product = db.get_product(int(code))

    return render_template('productdetails.html', code=code, product=product)

@app.route('/branches')
def branches():
    branch_list = db.get_branches()
    return render_template('branches.html', page="Branches", branch_list=branch_list)

@app.route('/branchdetails')
def branchdetails():
    code = request.args.get('code', '')
    branch = db.get_branch(code)

    return render_template('branchdetails.html', code=code, branch=branch)

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', page="About Us")

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop("user", None)
    session.pop("cart", None)
    return render_template('login.html')

@app.route('/auth', methods = ['GET','POST'])
def auth():
    username = request.form.get('username')
    password = request.form.get('password')

    is_successful, user = authentication.login(username, password)
    app.logger.info('%s', is_successful)
    if(is_successful):
        session["user"] = user
        return redirect('/')
    else:
        flash("Invalid username or password. Please try again.")
        return redirect('/login')

@app.route('/logout')
def logout():
    session.pop("user",None)
    session.pop("cart",None)
    return redirect('/')

@app.route('/cart')
def cart():
    return render_template('cart.html')
    
# @app.route('/addtocart')
# def addtocart():
#     code = request.args.get('code', '')
#     product = db.get_product(int(code))
#     prod=dict()

#     prod['code'] = code
#     prod["qty"] = 1
#     prod["name"] = product["name"]
#     prod["subtotal"] = int(product["price"])*int(prod["qty"])

#     if(session.get("cart") is None):
#         session["cart"]={}

#     cart = session["cart"]
#     cart[code]=prod 
#     session["cart"]=cart
#     return redirect('/cart')

@app.route('/addtocart')
def addtocart():
    code = request.args.get('code', '')
    product = db.get_product(int(code))
    item=dict()
    # A click to add a product translates to a 
    # quantity of 1 for now

    item["code"] = code
    item["qty"] = 1
    item["name"] = product["name"]
    item["subtotal"] = int(product["price"])*int(item["qty"])

    if(session.get("cart") is None):
        session["cart"]={}

    cart = session["cart"]
    cart[code]=item
    session["cart"]=cart
    return redirect('/cart')

@app.route('/updatecart', methods=['POST'])
def updatecart():
    code = request.form.getlist("code")
    qty = request.form.getlist("qty")

    cart = session["cart"]

    for prod in range(len(code)):
        product = db.get_product(int(code[prod]))
        cart[code[prod]]["qty"] = int(qty[prod])
        cart[code[prod]]["subtotal"] = int(qty[prod]) * int(product["price"])

    session["cart"] = cart
    
    return redirect('/cart')

@app.route('/removeitem')
def removeitem():
    code = request.args.get('code', '')
    cart = session["cart"]
    cart.pop(code, None)
    session["cart"]=cart

    return redirect('/cart')

@app.route("/removeall")
def removeall():
    session.pop("cart", None)
    return redirect("/cart")

@app.route('/checkout')
def checkout():
    # clear cart in session memory upon checkout
    om.create_order_from_cart()
    session.pop("cart",None)
    return redirect('/ordercomplete')

@app.route('/ordercomplete')
def ordercomplete():
    return render_template('ordercomplete.html')

@app.route('/vieworders')
def vieworders():
    orders = db.get_orders()
    order_list = []
    for prod in orders:
        for order in prod["details"]:
            order_list.append(order)

    return render_template('vieworders.html', order_list=order_list)

@app.route('/password')
def changepassword():
    return render_template('changepassword.html')

@app.route('/password-change', methods = ['POST'])
def passwordchange():
    old_pass = request.form.get('old-pass')
    new_pass = request.form.get('new-pass')
    confirm_pass= request.form.get('confirm-pass')

    is_success, match_with_old, same_with_new = authentication.valid_change(old_pass, new_pass, confirm_pass)
    app.logger.info('%s', is_success)
    if(is_success):
        db.change_pass(session['user']['username'], new_pass)
        return redirect('/login')
    else:
        if not match_with_old:
            flash("Old password is incorrect.")
        if not same_with_new:
            flash("New passwords do not match.")

        return redirect('/password')















