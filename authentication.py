from flask import session
import database as db

def login(username, password):
    is_valid_login = False
    user=None
    temp_user = db.get_user(username)
    if(temp_user != None):
        if(temp_user["password"]==password):
            is_valid_login=True
            user={"username":username,
                  "first_name":temp_user["first_name"],
                  "last_name":temp_user["last_name"]}
   
    return is_valid_login, user

def valid_change(old_pass, new_pass, confirm_pass):
    old_correct = False
    new_same = False
    valid = False
    temp_user = db.get_user(session["user"]["username"])
    if(old_pass == temp_user["password"]):
        old_correct = True
    if(new_pass == confirm_pass):
        new_same = True

    if old_correct and new_same:
        valid = True

    return old_correct, new_same, valid
