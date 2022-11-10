from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "EEA24B71D34B87C5E53C98E57A344"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    
    def __init__(self, name, email):
        self.name = name
        self.email = email
        


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        session["user"] = user
        
        found_user = users.query.filter_by(name = user).first()
        if found_user:
            session["email"] = found_user.email
        else:
            usr = users(user, None)
            db.session.add(usr)
            db.session.commit()
        
        
        flash("Logged in succesfully")
        return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))
        return render_template("login.html")
    
@app.route("/logout/")
def logout():
    flash("You have been logged out", "info")
    session.pop("user", None)
    session.pop("email", None)
    return redirect(url_for("login"))

@app.route("/user/", methods=["POST", "GET"])
def user():
    email = None
    if "user" in session:
        user = session["user"]
        
        if request.method == "POST":
            email = request.form["email"]
            session["email"] = email
            found_user = users.query.filter_by(name = user).first()
            found_user.email = email # pakeitimas data
            db.session.commit()
            flash("Email was saved", "info")
        else:
            if "email" in session:
                email = session["email"]
        
        return render_template("user.html", email = email)
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
 
@app.route("/allUsers")
def allUsers():
       return render_template("allUsers.html", values = users.query.all())
   # found_user = users.query.filter_by(name = user).delete()
   # db.session.commit()
   
   # found_users = users.query.all()
   # for found_user in found_users:
   #    user.delete()
   # db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)