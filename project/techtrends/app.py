import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
import logging

logging.basicConfig(
     level=logging.DEBUG,
     format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
     datefmt='%m/%d/%Y, %H:%M:%S'
 )

# total number of database connections established so far
db_connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    global db_connection_count
    db_connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.info('A non-existing article is accessed and a 404 page is returned.')
        return render_template('404.html'), 404
    else:
        app.logger.info('Article "{}" is retrieved!'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('"About Us" retrieved.')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            app.logger.info('Article "{}" is created!'.format(title))
            return redirect(url_for('index'))

    return render_template('create.html')

@app.route("/healthz")
def healthz():
    db_connection_success = __db_connection_test()
    if db_connection_success == 0:
        return app.response_class(
            status=500,
            response=json.dumps({'result': 'ERROR - unhealthy'}),
            mimetype='application/json'
        )
    else:
        return app.response_class(
            response=json.dumps({'result': 'OK - healthy'}),
            mimetype='application/json'
        )

@app.route("/metrics")
def metrics():
    post_count = __get_post_count()
    response = app.response_class(
        response=json.dumps({'data': {'db_connection_count': db_connection_count,
                                      'post_count': post_count}}),
        mimetype='application/json'
    )
    return response

def __get_post_count():
    connection = get_db_connection()
    count = connection.execute('SELECT count() as total FROM posts').fetchone()
    connection.close()
    return count['total']

def __db_connection_test():
    connection = get_db_connection()
    table_count = connection.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='posts'").fetchone()
    connection.close()
    return table_count[0]

# start the application on port 3111
if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3111')
