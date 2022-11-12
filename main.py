from flask import Flask, redirect, url_for, render_template, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid
import re
import bcrypt

app = Flask(__name__)
app.secret_key = "EEA24B71D34B87C5E53C98E57A344"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
#date regex 
pattern = re.compile("[0-9]{4}-[0-1]{1}[0-9]{1}-[0-3][0-9] [0-2][0-9]:[0-6][0-9]:[0-6][0-9]")

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    password_hash = db.Column(db.String(255))
    uniqueId = db.Column(db.String(255))
    
    
    def __init__(self, name, password):
        self.name = name
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt())
        self.uniqueId = str(uuid.uuid4())
        
class tasks(db.Model):
    _id = db.Column("id", db.Integer, primary_key = True)
    name = db.Column(db.String(255))
    startDate = db.Column(db.String(255))
    endDate = db.Column(db.String(255))
    done = db.Column(db.Boolean)
    userId = db.Column(db.String(255))
    
    def __init__(self, name, startDate, endDate, done, id):
        self.name = name
        self.startDate = startDate
        self.endDate = endDate
        self.done = done
        self.userId = id
        


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login/", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pass"].encode("utf-8")
        session["user"] = user
        
        found_user = users.query.filter_by(name = user).first()
        if found_user:
            if bcrypt.checkpw(password, found_user.password_hash):
                flash("Logged in succesfully")
                return redirect(url_for("user"))
            
            else:
                session.pop("user", None)
                session.pop("pass", None)
                flash("Wrong username or password")
                return render_template("login.html")
        else:
            flash(f"User {user} not found, plese login with another username or register a user")
            return render_template("login.html")
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))
    return render_template("login.html")
    
    
@app.route("/register/", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        user = request.form["nm"]
        password = request.form["pass"].encode("utf-8")
        if len(password) == 0 or len(user) == 0:
            flash("Username or password cannot be empty")
            return render_template("register.html")
        
        found_user = users.query.filter_by(name = user).first()
        if found_user:
            flash("User already registered by this username, please login", "info")
            return redirect(url_for("login"))
        else:
            session["user"] = user
            usr = users(user, password)
            db.session.add(usr)
            db.session.commit()
            flash("User registered successfully", "info")
            return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already logged in")
            return redirect(url_for("user"))
        return render_template("register.html")
        
    
@app.route("/logout/")
def logout():
    flash("You have been logged out", "info")
    session.pop("user", None)
    session.pop("taskId", None)
    return redirect(url_for("login"))


@app.route("/user/")
def user():
    if "user" in session:
        found_user = users.query.filter_by(name = session["user"]).first()
        toDoTasks = tasks.query.filter_by(userId = found_user.uniqueId).all()
        return render_template("user.html", values = toDoTasks, size = len(toDoTasks))
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
@app.route("/createTask/", methods=["POST", "GET"])
def createTask():
    if "user" in session:
        if request.method == "POST":
            name = request.form["name"]
            startDate = request.form["startDate"]
            endDate = request.form["endDate"]

            if len(name) == 0:
                flash("Task's name cannot be empty")
                return render_template("createTask.html")

            if not(pattern.match(startDate)):
                now = datetime.now()
                startDate = now.strftime("%Y-%m-%d %H:%M:%S")
                flash("Wrong start date and time pattern when creating task, please edit to correct", "info")

            if not(pattern.match(endDate)):
                endDate = "-"
                flash("Wrong end date and time pattern when creating task, please edit to correct", "info")

            if(request.form["finished"] == "True"):
                finished = 1
            else:
                finished = 0
            
            user = users.query.filter_by(name = session["user"]).first()
            task = tasks(name, startDate, endDate, finished, user.uniqueId)
            db.session.add(task)
            db.session.commit()
            flash("Task added successfully", "info")
            return redirect(url_for("user"))
        else:
            return render_template("createTask.html")
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
@app.route("/complete", methods=["POST"])
def complete():
    if "user" in session:
        if request.method == "POST":
            id = request.form.get('Complete')
            
            found_user = users.query.filter_by(name = session["user"]).first()
            toDoTasks = tasks.query.filter_by(userId = found_user.uniqueId).all()
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            toDoTasks[int(id)].done = 1
            toDoTasks[int(id)].endDate = date_time
            
            db.session.commit()
            return redirect(url_for("user"))
        else:
            return redirect(url_for("user"))
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
@app.route("/delete", methods=["POST"])
def delete():
    if "user" in session:
        id = request.form.get('Delete')
        found_user = users.query.filter_by(name = session["user"]).first()
        toDoTasks = tasks.query.filter_by(userId = found_user.uniqueId).all()
        task = tasks.query.filter_by(_id = toDoTasks[int(id)]._id)
        task.delete()
        db.session.commit()
        flash("Task deleted", "info")
        return redirect(url_for("user"))
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
    
@app.route("/linkToEdit", methods=["POST", "GET"])
def linkToEdit():
    if "user" in session:
        id = request.form.get('Edit')
        print(id)
        session["taskId"] = id
        return redirect(url_for("edit"))
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))
    
@app.route("/edit", methods=["POST", "GET"])
def edit():
    if "user" in session:
        id = session["taskId"]
        found_user = users.query.filter_by(name = session["user"]).first()
        toDoTasks = tasks.query.filter_by(userId = found_user.uniqueId).all()

        #if tempered with value
        task = toDoTasks[len(toDoTasks)-1]
        lastId = task._id
        #taskDone = str(task.done)

        if task.done == 1:
            taskDone = str("True")
        else:
            taskDone = str("False")

        
        if(int(id) > lastId):
            return render_template("edit.html", name = task.name, startDate = task.startDate, endDate = task.endDate, finished = taskDone)
        task = tasks.query.filter_by(_id = toDoTasks[int(id)]._id).first()
        
        if request.method == "POST":

            task.name = request.form["name"]

            if not(pattern.match(request.form["startDate"])):
                flash("Date format needs to be: YYYY-MM-DD hh:mm:ss", "info")
            else:
                task.startDate = request.form["startDate"]

            if not(pattern.match(request.form["endDate"])):
                flash("Date format needs to be: YYYY-MM-DD hh:mm:ss", "info")
            else:
                task.startDate = request.form["endDate"]

            if request.form["finished"].lower() == "true" or request.form["finished"] == "1":
                task.done = 1
                taskDone = str("True")
            elif request.form["finished"].lower() == "false" or request.form["finished"] == "0":
                task.done = 0
                taskDone = str("False")

            #taskDone = str(task.done)
            db.session.commit()
            flash("Information was changed", "info")
            
        return render_template("edit.html", name = task.name, startDate = task.startDate, endDate = task.endDate, finished = taskDone)
    else:
        flash("You are not logged in")
        return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)