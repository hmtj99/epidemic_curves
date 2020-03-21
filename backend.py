from flask import Flask, render_template, jsonify
from datetime import datetime
from bs4 import BeautifulSoup
from flask_sqlalchemy import SQLAlchemy
import requests
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


class Delhi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    no_of_infected = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.date} - {self.no_of_infected}"


class Gujarat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    no_of_infected = db.Column(db.Integer)

    def __repr__(self):
        return f"{self.date} - {self.no_of_infected}"


@app.route('/')
def index():
    return render_template('./index.html')


@app.route('/getData')
def get_data():
    data_points = Delhi.query.all()
    delhi_dates_list = []
    delhi_no_of_infected_list = []
    gujarat_dates_list = []
    gujarat_no_of_infected_list = []

    for point in data_points:
        delhi_dates_list.append(point.date.strftime('%d/%m/%Y'))
        delhi_no_of_infected_list.append(point.no_of_infected)

    data_points = Gujarat.query.all()

    for point in data_points:
        gujarat_dates_list.append(point.date.strftime('%d/%m/%Y'))
        gujarat_no_of_infected_list.append(point.no_of_infected)

    now = datetime.now()
    today5pm = now.replace(hour=17, minute=0, second=0, microsecond=0)
    if now > today5pm:
        response = requests.get('https://www.mohfw.gov.in/')
        soup = BeautifulSoup(response.text, 'html.parser')
        all_tds = soup.table.find_all('td')
        delhi_num_id = 0
        gujarat_num_id = 0
        for idx, td in enumerate(all_tds):
            str_td = str(td)
            if 'Delhi' in str_td:
                delhi_num_id = idx
            if 'Gujarat' in str_td:
                gujarat_num_id = idx

        delhi_current_infected = all_tds[delhi_num_id+1].contents[0]
        gujarat_current_infected = all_tds[gujarat_num_id+1].contents[0]

        now_date = datetime.now().date().strftime('%d/%m/%Y')
        if now_date not in delhi_dates_list:
            delhi_dates_list.append(now_date)
            delhi_no_of_infected_list.append(int(delhi_current_infected))
            new_data = Delhi(date=datetime.now(),
                             no_of_infected=delhi_current_infected)
            db.session.add(new_data)
            db.session.commit()
        if now_date not in gujarat_dates_list:
            gujarat_dates_list.append(now_date)
            gujarat_no_of_infected_list.append(int(gujarat_current_infected))
            new_data = Gujarat(date=datetime.now(),
                               no_of_infected=gujarat_current_infected)
            db.session.add(new_data)
            db.session.commit()

    data = {'delhi_dates': delhi_dates_list,
            'delhi_infected': delhi_no_of_infected_list,
            'gujarat_dates': gujarat_dates_list,
            'gujarat_infected': gujarat_no_of_infected_list,
            }
    return jsonify(data)


# if __name__ == "__main__":
#     app.run(host='127.0.0.1', debug=True)
    # manager.run()
