import database as db
from flask import session
from datetime import datetime

def create_order_from_cart():
    order = {}
    order.setdefault("username",session["user"]["username"])
    order.setdefault("orderdate",datetime.utcnow())
    order_details = []
    cart = session["cart"]
    for k, v in cart.items():
        order_details.append({"code":k,
                            "name":v["name"],
                            "qty":v["qty"],
                            "subtotal":v["subtotal"]})
    order.setdefault("details",order_details)
    db.create_order(order)
