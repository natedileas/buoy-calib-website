import os
import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

    return redirect(url_for('index'))


@app.route('/process', methods=['GET', 'POST'])
def process():

    form = ProcessForm(request.form)
    print form
    print request.form
    if request.method == 'POST' and form.validate():
        # process the form data and redirect to the progress / jobs page
        # TODO spawn a job from this
        task = download.apply_async((str(form.scene_id.data), ))
        return redirect(url_for('jobs'))
    else:
        return render_template('process.html', form=form)


@app.route('/jobs', methods=['GET'])
def jobs():
    return render_template('jobs.html')


@app.route('/enum_tasks', methods=['GET'])
def enum_tasks():
    i = celery.control.inspect()
    active_tasks = i.active()
    reserved_tasks = i.reserved()
    return jsonify(active=active_tasks, reserved=reserved_tasks)


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
