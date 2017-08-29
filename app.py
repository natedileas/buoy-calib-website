import os
import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from celery import Celery

from form import ProcessForm


app = Flask(__name__, static_folder='static')
# from os.urandom(25)
app.config['SECRET_KEY'] = '\x81\xf6F\xad\xc0\xe2N\xf2\xdb\x89\x0b\xee\xd0x\x9c\x18\x1a\x91\xbf\x88\xa1/\xab\x14U'

# Celery configuration
# redis is the async arch behind celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf['CELERY_ACCEPT_CONTENT'] = ['json', 'pickle']
celery.conf.update(app.config)

# flask WTF config, stands for cross-site request forgery prevention
app.config['CSRF_ENABLED'] = True

# database stuff
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120))
    scene_id = db.Column(db.String(120))
    buoy_id = db.Column(db.String(120))
    atmo_source = db.Column(db.String(12))

    def __init__(self, email, task_id, scene_id, buoy_id, atmo_source):
        self.email = email
        self.task_id = task_id
        self.scene_id = scene_id
        self.buoy_id = buoy_id
        self.atmo_source = atmo_source

    def __repr__(self):
        return '<Scene ID: {0} Buoy ID: {1}>'.format(self.scene_id, self.buoy_id)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    return redirect(url_for('index'))


@app.route('/process', methods=['GET', 'POST'])
def process():

    form = ProcessForm(request.form)
    if request.method == 'POST' and form.validate():
        # process the form data
        scene_id = str(form.scene_id.data)
        print scene_id
        task = download.apply_async((scene_id, ))
        # create entry in the database
        new_task = Task('ndileas@gmail.com', str(task.id), scene_id, scene_id, 'narr')
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for('jobs'))   # redirect to the jobs page

    return render_template('process.html', form=form)


@app.route('/jobs', methods=['GET'])
def jobs():
    return render_template('jobs.html')


@app.route('/enum_tasks', methods=['GET'])
def enum_tasks():
    tasks = Task.query.all()
    task_list = [{'task_id': str(t.task_id)} for t in tasks]

    return jsonify(tasks=task_list)


@app.route('/status/<task_id>')
def taskstatus(task_id):
    task = download.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current'),
            'total': task.info.get('total'),
            'status': task.info.get('status')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


import urllib2

CHUNK = 1024 #* 1024 * 8

@celery.task(bind=True)
def download(self, auth=False):
    """
    needs source url (from webs ite) and destination save location


    """
    source_url = 'http://www.spitzer.caltech.edu/uploaded_files/images/0006/3034/ssc2008-11a12_Huge.jpg'
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

    req = urllib2.Request(source_url, headers=hdr)

    if auth:
        out_file = str(auth) + '.jpeg'
    else:
        out_file = 'test2.jpeg'

    try:
        opened = urllib2.urlopen(req)
    except urllib2.HTTPError as e:
        print(e)

    total_size = int(opened.info().getheader('Content-Length').strip())

    progress = 0
    self.update_state(state='PROGRESS')

    with open(out_file, 'wb') as f:
        while True:
            chunk = opened.read(CHUNK)
            if not chunk: break
            f.write(chunk)
            progress += CHUNK
            self.update_state(state='PROGRESS',
                meta={'current': progress, 'total': total_size, 'status': 'asdfghjk'})

    return {'current': total_size, 'total': total_size, 'status': 'Download completed!'}


if __name__ == '__main__':
    app.run(debug=True)
