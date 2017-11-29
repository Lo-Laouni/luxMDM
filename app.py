from flask import Flask, render_template, request, redirect, url_for, jsonify,abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, Form, validators
from wtforms.validators import input_required, data_required, email, length, any_of
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_table import Table, Col
from flask_restful import Resource, Api, reqparse


app = Flask(__name__)
app.config['SECRET_KEY'] = 'b613htY80Xf85Ak47'
DB_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="loiclaouni",
    password="mdmdatabase",
    hostname="loiclaouni.mysql.pythonanywhere-services.com",
    databasename="loiclaouni$luxdb",
)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'False'
Bootstrap(app)
luxdb = SQLAlchemy(app)
loginManager= LoginManager()
loginManager.init_app(app)
loginManager.login_view = 'login'

api = Api(app)


@app.route('/api/v1/luxmdm', methods=['GET', 'POST'])
class clientData(Resource):
    def get(self):
        pass  # return configuration commands, instructional commands

    def post(self):

        parser = reqparse.RequestParser()
        parser.add_argument('data', type=list, required=True, location='json')

        args = parser.parse_args(strict=True)
        deviceData = {'serial': args.data[0], 'deviceos': args.data[1], 'deviceUser': args.data[2]}
        # deviceData should be verified and stored in database if necessary
        handler = deviceTable(deviceData['serial'], deviceData['deviceos'], deviceData['deviceUser'])
        luxdb.session.add(handler)
        luxdb.session.commit()
        return deviceData
api.add_resource(clientData, '/api/v1/luxmdm')


@app.route('/api/v1/luxpostdata', methods=['POST'])
def newDevice():
    if not request.json:
        abort(400)
    data = {'data':request.json['data']}
    received = data['data']
    handler = userTable(received[0], received[1], received[2])
    luxdb.session.add(handler)
    luxdb.session.commit()
    return jsonify({'data':data}), 201


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('devicemon'))

    form = loginpage(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        user = adminTable.query.filter_by(uname=form.username.data).first()
        if user:
            if user.passwd == form.password.data:
                login_user(user, remember=form.remember.data)
                return redirect(url_for('devicemon'))

    return render_template('login.html', form=form)


@app.route('/devicemon.html')
@login_required
def devicemon():
    devices = deviceTable.query.with_entities(deviceTable.deviceSerialNum, deviceTable.deviceOS, deviceTable.deviceUser)
    devrowcount = deviceTable.query.with_entities(deviceTable.deviceSerialNum, deviceTable.deviceOS, deviceTable.deviceUser).count()
    devTables = regdevTable(devices)
    columns=[devTables.deviceSerialNum, devTables.deviceOS, devTables.deviceUser]

    return render_template('devicemon.html', name=current_user.uname, dev=devices, rows=devrowcount)


@app.route('/sysmon.html')
@login_required
def sysmon():
    return render_template('sysmon.html')


@app.route('/manage.html', methods=['GET', 'POST'])
# @login_required
def manage():
    global dev
    form = searchManage(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        device = deviceTable.query.filter_by(deviceUser=form.deviceUser.data).first()
        if device:
            dev = device
            return dev
    return render_template('manage.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


class loginpage(FlaskForm):
    username = StringField('Username', [validators.length(min=4, max=25), input_required()])
    password = PasswordField('Password', [validators.data_required()])
    remember = BooleanField('remember me')


class searchManage(FlaskForm):
    deviceUser = StringField(input_required())


class adminTable(UserMixin, luxdb.Model):
    __tablename__ = 'admin'
    id = luxdb.Column('ID', luxdb.Unicode, primary_key=True)
    name = luxdb.Column('Name', luxdb.Unicode)
    uname = luxdb.Column('Username', luxdb.Unicode)
    passwd = luxdb.Column('Password', luxdb.Unicode)
    contact = luxdb.Column('Contact', luxdb.Unicode)

    def __init__(self, id, name, uname, passwd, contact):
        self.id = id
        self.name = name
        self.uname = uname
        self.passwd = passwd
        self.contact = contact

@loginManager.user_loader
def load_user(user_id):
    return adminTable.query.get(str(user_id))


class userTable(luxdb.Model):
    __tablename__='users'
    matriculation = luxdb.Column('Matriculation_ID', luxdb.Unicode, primary_key=True)
    nameUser = luxdb.Column('Name', luxdb.Unicode, nullable=False)
    dept = luxdb.Column('Department', luxdb.Unicode, nullable=False)
    device = luxdb.relationship('deviceTable', backref='userTable', lazy='dynamic')

    def __init__(self, matriculation, nameuser, dept):
        self.matriculation = matriculation
        self.nameUser = nameuser
        self.dept = dept


class deviceTable(luxdb.Model):
    __tablename__ = 'devices'
    deviceSerialNum = luxdb.Column('Serial Number', luxdb.Unicode, primary_key=True)
    deviceOS = luxdb.Column('Operating System', luxdb.Unicode, nullable=False)
    activationDate = luxdb.Column('Provision_Date', luxdb.Date, nullable=False)
    deviceUser = luxdb.Column('device_user', luxdb.Unicode, luxdb.ForeignKey(userTable.matriculation), nullable=False)

    def __init__(self, deviceserialnum, deviceos, deviceuser):
        self.deviceSerialNum = deviceserialnum
        self.deviceOS = deviceos
        self.deviceUser = deviceuser


class regdevTable(Table):
    deviceSerialNum = Col('Serial Number')
    deviceOS = Col('Operating System')
    deviceUser = Col('device_user')


if __name__ == '__main__':
    app.run()