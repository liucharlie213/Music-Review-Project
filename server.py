"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
import datetime
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, url_for, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.config['SECRET_KEY'] = 'sandcsecretkey'

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.73.36.248/project1
#
# For example, if you had username zy2431 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://zy2431:123123@34.73.36.248/project1"
#
# Modify these with your own credentials you received from TA!
DATABASE_USERNAME = "crl2157"
DATABASE_PASSWRD = "6585"
DATABASE_HOST = "34.148.107.47" # change to 34.28.53.86 if you used database 2 for part 2
DATABASEURI = f"postgresql://{DATABASE_USERNAME}:{DATABASE_PASSWRD}@{DATABASE_HOST}/project1"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

#comment below
#with engine.connect() as conn:
#	create_table_command = """CREATE TABLE IF NOT EXISTS test (id serial,name text)"""
#	res = conn.execute(text(create_table_command))

#	insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
#	res = conn.execute(text(insert_table_command))
	# you need to commit for create, insert, update queries to reflect
#	conn.commit()

@app.before_request
def before_request():
	"""
	This function is run at the beginning of every web request 
	(every time you enter an address in the web browser).
	We use it to setup a database connection that can be used throughout the request.
	The variable g is globally accessible.
	"""
	try:
		g.conn = engine.connect()
	except:
		print("uh oh, problem connecting to database")
		import traceback; traceback.print_exc()
		g.conn = None

@app.teardown_request
def teardown_request(exception):
	"""
	At the end of the web request, this makes sure to close the database connection.
	If you don't, the database could run out of memory!
	"""
	try:
		g.conn.close()
	except Exception as e:
		pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/index')
def index():
        if 'username' in session: 

               username = session['username']
               user_query = f"SELECT * FROM listener WHERE username = '{username}'"
               cur = g.conn.execute(text(user_query))
               user = cur.fetchone()
               cur.close()
                # DEBUG: this is debugging code to see what request looks like
               print(request.args)

               solo_id_name_query = "Select artist_id, stage_name from artist_solo"
               cursor = g.conn.execute(text(solo_id_name_query))
               solo_ids_names = []
               album_solo = []
               for result in cursor:
                       solo_ids_names.append((result[0], result[1]))
                       album_solo_query = f"SELECT album_id, name from album where artist_id = '{result[0]}'"
                       cur = g.conn.execute(text(album_solo_query))
                       for res in cur:
                               album_solo.append((res[0], res[1]))
                       cur.close()
               cursor.close()

               band_id_name_query = "Select artist_id, stage_name from artist_band"
               cursor = g.conn.execute(text(band_id_name_query))
               band_ids_names = []
               album_band = []
               for result in cursor:
                       band_ids_names.append((result[0], result[1]))
                       album_band_query = f"SELECT album_id, name from album where artist_id = '{result[0]}'"
                       cur = g.conn.execute(text(album_band_query))
                       for res in cur:
                               album_band.append((res[0], res[1]))
                       cur.close()
               cursor.close()

#               context = dict(album_solo_data = album_solo, album_band_data = album_band, solo_id_data = solo_ids_names, band_id_data = band_ids_names)               
               top_query = "SELECT title, username, date_posted, rating, review, num_likes, review_id FROM review ORDER BY num_likes DESC limit 3"
#                review_info_query = f"SELECT title, username, date_posted, rating, review, num_likes, review_id from review wher>
               cursor = g.conn.execute(text(top_query))
               top_reviews = []
               for result in cursor:
                       top_reviews.append((result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
               cursor.close()
               context = dict(album_solo_data = album_solo, album_band_data = album_band, solo_id_data = solo_ids_names, band_id_data = band_ids_names, top_reviews = top_reviews)
               return render_template("index.html", **context)

        else: 
               return redirect(url_for('login'))	

@app.route('/solo/<artist_id>')
def view_solo(artist_id):
	print(request.args)
	artist_name_query = f"SELECT stage_name FROM artist_solo where artist_id = '{artist_id}'"
	cursor = g.conn.execute(text(artist_name_query))
	name = []
	for result in cursor:
		name.append(result[0])
	cursor.close()

	artist_info_query = f"SELECT gov_name, dob, nationality, genre, label FROM artist_solo WHERE artist_id = '{artist_id}'"
	cursor = g.conn.execute(text(artist_info_query))
	info = []
	for result in cursor:
		info.append((result[0], result[1], result[2], result[3], result[4]))
	cursor.close()

	artist_albums_query = f"SELECT name, album_id FROM album where artist_id = '{artist_id}'"
	cursor =  g.conn.execute(text(artist_albums_query))
	albums = []
	for result in cursor:
		albums.append((result[0], result[1]))
	cursor.close()

	context = dict(album_data = albums, artist_name = name, artist_info = info)
	return render_template("solo.html", **context)

@app.route('/band/<artist_id>')
def view_band(artist_id):
        print(request.args)
        artist_name_query = f"SELECT stage_name FROM artist_band where artist_id = '{artist_id}'"
        cursor = g.conn.execute(text(artist_name_query))
        name = []
        for result in cursor:
                name.append(result[0])
        cursor.close()

        artist_info_query = f"SELECT members, dobs, nationalities, genre, label FROM artist_band where artist_id = '{artist_id}'"
        cursor = g.conn.execute(text(artist_info_query))
        info = []
        for result in cursor:
                info.append((result[0], result[1], result[2], result[3], result[4]))
        cursor.close()

        artist_albums_query = f"SELECT name, album_id FROM album where artist_id = '{artist_id}'"
        cursor =  g.conn.execute(text(artist_albums_query))
        albums = []
        for result in cursor:
                albums.append((result[0], result[1]))
        cursor.close()

        context = dict(album_data = albums, artist_name = name, artist_info = info)
        return render_template("band.html", **context)

@app.route('/album/solo/<album_id>')
def album_solo_view(album_id):
        print(request.args)

        artist_id_query = f"SELECT artist_id from album where album_id = '{album_id}'"
        cursor = g.conn.execute(text(artist_id_query))
        artist_id = []
        for result in cursor:
                artist_id.append(result[0])
        cursor.close()

        artist_query = f"SELECT stage_name from artist_solo where artist_id = '{artist_id[0]}'"
        cursor = g.conn.execute(text(artist_query))
        artist = []
        for result in cursor:
                artist.append(result[0])
        cursor.close()

        info_query = f"SELECT name, release_date, duration, num_songs, songs from album where album_id = '{album_id}'"
        cursor = g.conn.execute(text(info_query))
        info = []
        for result in cursor:
                info.append((result[0], result[1], result[2], result[3], result[4]))
        cursor.close()

        review_query = f"Select review_id from album_has_review where album_id = '{album_id}'"
        cursor = g.conn.execute(text(review_query))
        review_ids = []
        for result in cursor:
                review_ids.append((result[0]))
        cursor.close()
 
 #       reviews = []
#        if len(review_ids) != 0:
        reviews = []
        for id in review_ids:
                review_info_query = f"SELECT title, username, date_posted, rating, review, num_likes, review_id from review where review_id = '{id}'"
                cursor = g.conn.execute(text(review_info_query))
                review_info = []
                for result in cursor:
                        review_info.append((result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
                        reviews.append(review_info[0])
                cursor.close()

        context = dict(album_artist_id = artist_id, album_artist = artist, album_info = info, review_info = reviews, review_ids = review_ids)
        #else:
         #       context = dict(album_artist_id = artist_id, album_artist = artist, album_info = info, review_info = reviews, review_ids = review_ids)
        return render_template('album_solo.html', **context)

@app.route('/album/band/<album_id>')
def album_band_view(album_id):
        print(request.args)

        artist_id_query = f"SELECT artist_id from album where album_id = '{album_id}'"
        cursor = g.conn.execute(text(artist_id_query))
        artist_id = []
        for result in cursor:
                artist_id.append(result[0])
        cursor.close()

        artist_query = f"SELECT stage_name from artist_band where artist_id = '{artist_id[0]}'"
        cursor = g.conn.execute(text(artist_query))
        artist = []
        for result in cursor:
                artist.append(result[0])
        cursor.close()

        info_query = f"SELECT name, release_date, duration, num_songs, songs from album where album_id = '{album_id}'"
        cursor = g.conn.execute(text(info_query))
        info = []
        for result in cursor:
                info.append((result[0], result[1], result[2], result[3], result[4]))
        cursor.close()

        review_query = f"Select review_id from album_has_review where album_id = '{album_id}'"
        cursor = g.conn.execute(text(review_query))
        review_ids = []
        for result in cursor:
                review_ids.append((result[0]))
        cursor.close()

        reviews = []
        for id in review_ids:
                review_info_query = f"SELECT title, username, date_posted, rating, review, num_likes from review where review_id = '{id}'"
                cursor = g.conn.execute(text(review_info_query))
                review_info = []
                for result in cursor:
                        review_info.append((result[0], result[1], result[2], result[3], result[4], result[5]))
                        reviews.append(review_info[0])
                cursor.close()

        context = dict(album_artist_id = artist_id, album_artist = artist, album_info = info, review_info = reviews, review_ids = review_ids)

        return render_template('album_band.html', **context)


@app.route('/search', methods = ['GET'])
def search():
        print(request.args)
        query = request.args.get('query')
        search_solo_query = f"SELECT artist_id, stage_name from artist_solo where stage_name = '{query}'"
        cursor = g.conn.execute(text(search_solo_query))
        search_solo_results = []
        for result in cursor:
                search_solo_results.append((result[0], result[1]))
        cursor.close()

        search_band_query = f"SELECT artist_id, stage_name from artist_band where stage_name = '{query}'"
        cursor = g.conn.execute(text(search_band_query))
        search_band_results = []
        for result in cursor:
                search_band_results.append((result[0], result[1]))
        cursor.close()

        search_album_query = f"SELECT album_id, name from album where name = '{query}'"
        cursor = g.conn.execute(text(search_album_query))
        search_album_results = []
        for result in cursor:
                search_album_results.append((result[0], result[1]))
        cursor.close()

        if not search_solo_results and not search_band_results and not search_album_results:
                return render_template('no_result.html')

        elif len(search_solo_results) == 1:

                artist_info_query = f"SELECT gov_name, dob, nationality, genre, label FROM artist_solo WHERE artist_id = '{search_solo_results[0][0]}'"
                cursor = g.conn.execute(text(artist_info_query))
                info = []
                for result in cursor:
                        info.append((result[0], result[1], result[2], result[3], result[4]))
                cursor.close()

                artist_albums_query = f"SELECT name, album_id FROM album where artist_id = '{search_solo_results[0][0]}'"
                cursor =  g.conn.execute(text(artist_albums_query))
                albums = []
                for result in cursor:
                        albums.append((result[0], result[1]))
                cursor.close()
                name = []
                name.append(search_solo_results[0][1])
                context = dict(album_data = albums, artist_name = name, artist_info = info)
                return render_template("solo.html", **context)

        elif len(search_band_results) == 1:

                artist_info_query = f"SELECT members, dobs, nationalities, genre, label FROM artist_band WHERE artist_id = '{search_band_results[0][0]}'"
                cursor = g.conn.execute(text(artist_info_query))
                info = []
                for result in cursor:
                        info.append((result[0], result[1], result[2], result[3], result[4]))
                cursor.close()

                artist_albums_query = f"SELECT name, album_id FROM album where artist_id = '{search_band_results[0][0]}'"
                cursor =  g.conn.execute(text(artist_albums_query))
                albums = []
                for result in cursor:
                        albums.append((result[0], result[1]))
                cursor.close()
                name = []
                name.append(search_band_results[0][1])
                context = dict(album_data = albums, artist_name = name, artist_info = info)
                return render_template("band.html", **context)

        elif len(search_album_results) == 1:

                artist_id_query = f"SELECT artist_id from album where name = '{query}'"
                cursor = g.conn.execute(text(artist_id_query))
                artist_id = cursor.fetchone()[0]                
                cursor.close()
                album_id_query = f"SELECT album_id from album where name = '{query}'"
                cursor = g.conn.execute(text(album_id_query))
                album_id = cursor.fetchone()[0] 
 #               print(id)
                artist_query = f"""SELECT  CASE WHEN s.artist_id IS NOT NULL THEN 0
                                     WHEN b.artist_id IS NOT NULL THEN 1
                             END AS artist_type
                             FROM album a
                             LEFT JOIN artist_solo s ON a.artist_id = s.artist_id
                             LEFT JOIN artist_band b ON a.artist_id = b.artist_id
                             WHERE a.artist_id = '{artist_id}'"""
                cursor = g.conn.execute(text(artist_query))
                artist_type = cursor.fetchone()[0]   
                cursor.close() 
#                print(artist_type)
                if artist_type == 0: #solo
                        artist_id_query = f"SELECT artist_id from album where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(artist_id_query))
                        artist_id_arr = []
                        for result in cursor:
                                 artist_id_arr.append(result[0])
                        cursor.close()

                        artist_query = f"SELECT stage_name from artist_solo where artist_id = '{artist_id}'"
                        cursor = g.conn.execute(text(artist_query))
                        artist = []
                        for result in cursor:
                                 artist.append(result[0])
                        cursor.close()
                        info_query = f"SELECT name, release_date, duration, num_songs, songs from album where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(info_query))
                        info = []
                        for result in cursor:
                                 info.append((result[0], result[1], result[2], result[3], result[4]))
                        cursor.close()
                        review_query = f"Select review_id from album_has_review where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(review_query))
                        review_ids = []
                        for result in cursor:
                                 review_ids.append((result[0]))
                        cursor.close()

                        reviews = []
                        if len(review_ids):
                                 for id in review_ids:
                                        review_info_query = f"SELECT title, username, date_posted, rating, review, num_likes, review_id from review where review_id = '{id}'"
                                 cursor = g.conn.execute(text(review_info_query))
                                 review_info = []
                                 for result in cursor:
                                        review_info.append((result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
                                        reviews.append(review_info[0])
                                 cursor.close()
                                 context = dict(album_artist_id = artist_id_arr, album_artist = artist, album_info = info, review_info = reviews, reviews_ids = review_ids)
                        else: 
                                 context = dict(album_artist_id = artist_id_arr, album_artist = artist, album_info = info, review_info = reviews, reviews_ids = review_ids)
                        return render_template('album_solo.html', **context)            

                if artist_type == 1: #band
                        artist_id_query = f"SELECT artist_id from album where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(artist_id_query))
                        artist_id_arr = []
                        for result in cursor:
                                 artist_id_arr.append(result[0])
                        cursor.close()

                        artist_query = f"SELECT stage_name from artist_band where artist_id = '{artist_id}'"
                        cursor = g.conn.execute(text(artist_query))
                        artist = []
                        for result in cursor:
                                 artist.append(result[0])
                        cursor.close()
                        info_query = f"SELECT name, release_date, duration, num_songs, songs from album where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(info_query))
                        info = []
                        for result in cursor:
                                 info.append((result[0], result[1], result[2], result[3], result[4]))
                        cursor.close()
                        review_query = f"Select review_id from album_has_review where album_id = '{album_id}'"
                        cursor = g.conn.execute(text(review_query))
                        review_ids = []
                        for result in cursor:
                                 review_ids.append((result[0]))
                        cursor.close()

                        reviews = []
                        for id in review_ids:
                                 review_info_query = f"SELECT title, username, date_posted, rating, review, num_likes, review_id from review where review_id = '{id}'"
                        cursor = g.conn.execute(text(review_info_query))
                        review_info = []
                        for result in cursor:
                                 review_info.append((result[0], result[1], result[2], result[3], result[4], result[5], result[6]))
                                 reviews.append(review_info[0])
                        cursor.close()

                        context = dict(album_artist_id = artist_id_arr, album_artist = artist, album_info = info, review_info = reviews, reviews_ids = review_ids)
                        return render_template('album_band.html', **context) 


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_query = f"SELECT * FROM listener WHERE username = '{username}' AND password = '{password}'"
        cur = g.conn.execute(text(login_query))
        user = cur.fetchone()
        if user:
            # User found, redirect to dashboard
            session['username'] = username
            cur.close()
            return redirect(url_for('dashboard'))
        else:
            # User not found, render login page with error message
            cur.close()
            return render_template('error_page.html', error='Invalid username or password')
    else:
        # If the request method is GET, render the login form
        return render_template('login.html')

@app.route('/logout')
def logout():
	return render_template('logout.html')

@app.route('/dashboard')
def dashboard():
    # Retrieve user information from session
    username = session.get('username')
    if username:
        # Fetch user information from database
        
        user_query = f"SELECT * FROM listener WHERE username = '{username}'"
        cur = g.conn.execute(text(user_query))
        user = cur.fetchone()
        if user:
                user_info_query = f"SELECT username, name, dob, email FROM listener WHERE username = '{username}'"
                cursor = g.conn.execute(text(user_info_query))
                info = []
                for result in cursor:
                        info.append((result[0], result[1], result[2], result[3]))
                cursor.close()
               
                user_review_query = f"SELECT title, date_posted, rating, review, num_likes, review_id from review where username = '{username}'"
                cursor1 = g.conn.execute(text(user_review_query))
                reviews = []
               # artist_ids = []
                for result1 in cursor1:
                        album_id_query = f"SELECT album_id FROM album_has_review WHERE review_id = '{result1[5]}'"
                        cursor2 = g.conn.execute(text(album_id_query))
                        for result2 in cursor2:
                            album_id = result2[0]
                        cursor2.close()

                        album_query = f"SELECT name FROM album WHERE album_id = '{album_id}'"
                        cursor3 = g.conn.execute(text(album_query))
                        for result3 in cursor3:
                            album_name = result3[0]
                        cursor3.close()
                        reviews.append((result1[0], result1[1], result1[2], result1[3], result1[4], album_id, album_name))
                cursor1.close()
                
                playlist_query = f"SELECT name, date_created, description, albums FROM playlist where username = '{username}'" 
                cursor = g.conn.execute(text(playlist_query))
                playlist_info = []
                for result in cursor:
                        playlist_info.append((result[0], result[1], result[2], result[3]))
                cursor.close()
                cur.close()
              
                return render_template('dashboard.html', user=username, user_info = info, user_review = reviews, playlist_info = playlist_info)
    # Redirect to login page if user is not logged in or user information not found
    return redirect(url_for('login'))

@app.route('/playlist', methods = ['GET', 'POST'])
def playlist():
        if 'username' in session: 
               if request.method == 'POST':
                        username = session['username']
                        name = request.form['playlist_name']
                        desc = request.form['playlist_desc']
                        timestamp = datetime.datetime.now()
                        date_created = timestamp.strftime("%Y-%m-%d")
                        user_query = f"SELECT * from playlist where username = '{username}'"
                        cursor = g.conn.execute(text(user_query))
                        if not cursor.fetchone():
                                num_albums = 0
                                g.conn.execute(text(f"INSERT into playlist (name, date_created, description, username, num_albums, albums) VALUES ('{name}', '{date_created}', '{desc}', '{username}', '{num_albums}', '{{}}' )"))
                                g.conn.commit()
                                cursor.close()
                                return render_template('playlist.html')
                        else:
#                                old_name = g.conn.execute(text(f"SELECT name from playlist where username = '{username}'")).fetchone()[0]                               
#                                g.conn.execute(text(f"UPDATE playlist_contains_album SET playlist_name = '{name}' where username = '{username}' AND playlist_name = '{old_name}'"))
#                                g.conn.commit()
                                cursor = g.conn.execute(text(f"SELECT album_id from playlist_contains_album where username = '{username}'"))
                                pl_albums = []
                                for result in cursor:
                                        pl_albums.append(result[0])
                                g.conn.execute(text(f"DELETE FROM playlist_contains_album where username = '{username}'"))
                                g.conn.commit()
                                g.conn.execute(text(f"UPDATE playlist SET name = '{name}', date_created = '{date_created}', description = '{desc}' where username = '{username}'"))
                                g.conn.commit()
                                for album in pl_albums:
                                        g.conn.execute(text(f"INSERT into playlist_contains_album (album_id, playlist_name, username) VALUES ('{album}', '{name}', '{username}')"))
                                        g.conn.commit()
                                cursor.close()
                                return render_template('playlist.html')
               else: 
                        return render_template('playlist.html')
        else:  
               return redirect(url_for('login'))

@app.route('/addplaylist', methods = ['POST'])
def addplaylist():
#need to update number of albums
	if 'username' in session:
		username = session['username']
		cursor = g.conn.execute(text(f"SELECT name from playlist where username = '{username}'"))
		playlist_exist = []
		for result in cursor:
			playlist_exist.append(result[0])
		cursor.close()
		if not playlist_exist:
			return render_template('no_playlist.html')
		else:
			album_name = request.form['album_name']
			cursor = g.conn.execute(text(f"SELECT album_id from album where name = '{album_name}'"))
			album_id = []
			for result in cursor:
				album_id.append(result[0])
			cursor.close()
			if not len(album_id):
				return render_template('no_album.html')
			else:
				cursor = g.conn.execute(text(f"SELECT name from playlist where username = '{username}'"))
				playlist_name = cursor.fetchone()[0]
				cursor.close()
				print(playlist_name)
				g.conn.execute(text(f"UPDATE playlist SET albums = array_append(albums, '{album_name}') where name = '{playlist_name}'"))
				g.conn.commit()
				g.conn.execute(text(f"INSERT into playlist_contains_album (album_id, playlist_name, username) VALUES ('{album_id[0]}', '{playlist_name}', '{username}')"))
				g.conn.commit()
				num_albums = g.conn.execute(text(f"SELECT COUNT(*) from playlist_contains_album where playlist_name = '{playlist_name}' AND username = '{username}'")).fetchone()[0]
				g.conn.execute(text(f"UPDATE playlist SET num_albums = {num_albums} where name = '{playlist_name}' and username = '{username}'"))
				g.conn.commit()
			return redirect(url_for('dashboard'))
	else:	
		return redirect(url_for('login'))
	
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
       if request.method == 'POST':
                username = request.form['username']
                name = request.form['name']
                dob = request.form['dob']
                password = request.form['password']
                email = request.form['email']
                print(username, name, dob, password, email)
                print(type(username),type(name), type(dob), type(password), type(email))
                g.conn.execute(text(f"INSERT INTO listener (username, name, dob, password, email) VALUES ('{username}', '{name}', '{dob}', '{password}', '{email}')"))
                g.conn.commit()
                return redirect(url_for('login'))
       else: 
                return render_template('signup.html')

@app.route('/like_review', methods=['POST'])
def like_review():
	username = session['username']
	review_id = request.form['review_id']
	cursor = g.conn.execute(text(f"SELECT username from user_likes_review where username = '{username}' AND review_id = '{review_id}'"))
	user = []
	for result in cursor:
		print(result)
		user.append(result[0])
	cursor.close()
	if len(user) != 0:
		return render_template('likes.html')
	g.conn.execute(text(f"UPDATE review SET num_likes = num_likes+1 where review_id = '{review_id}'"))
	g.conn.commit()
	g.conn.execute(text(f"INSERT INTO user_likes_review (username, review_id) VALUES ('{username}', '{review_id}')"))
	g.conn.commit()
	return redirect(url_for('index'))

def generate_review_id():
    # Get the current highest review ID from the database
    cur = g.conn.execute(text("SELECT MAX(SUBSTRING(review_id FROM 2)::INTEGER) as max_num FROM review WHERE review_id LIKE 'C%'"))
    max_num = cur.fetchone()[0]
    print(max_num)
    cur.close()

    new_num = max_num + 1

    # Return the new review ID in the desired format
    return 'C' + str(new_num)

@app.route('/review',  methods=['GET', 'POST'])
def review():
        if 'username' in session: 
                username = session['username']
                user_query = f"SELECT * FROM listener WHERE username = '{username}'"
                cur = g.conn.execute(text(user_query))
                user = cur.fetchone()[0]
                cur.close()
                
                if request.method == 'POST':
                        title = request.form['review_title']
                        review = request.form['review_text']
                        rating = str(request.form['rating'])
                        timestamp = datetime.datetime.now()
                        date_posted = timestamp.strftime("%Y-%m-%d")
                        review_id = generate_review_id()
#                        num_likes = "None"

                        # Get the number of words in the review
                        num_words = str(len(review.split()))

                        album_name = request.form['album_title']
                        album_query = f"SELECT * from album where name = '{album_name}'"
                        cur = g.conn.execute(text(album_query))
                        album_id_var = []
                        for result in cur:
                                album_id_var.append(result[0])
#                        album_id_var = cur.fetchone()[0]
                        cur.close()
                        if not len(album_id_var):
                                return render_template('no_album.html')
                        g.conn.execute(text(f"INSERT INTO review (review_id, num_words, title, rating, date_posted, username, review, num_likes) VALUES ('{review_id}', '{num_words}', '{title}', '{rating}', '{date_posted}', '{user}', '{review}', 0)"))
                        g.conn.commit()
                       
                        g.conn.execute(text(f"INSERT INTO album_has_review (album_id, review_id) VALUES ('{album_id_var[0]}', '{review_id}')"))
                        g.conn.commit()
                        
                        g.conn.execute(text(f"INSERT INTO user_posts_review (username, review_id) VALUES ('{user}', '{review_id}')"))
                        g.conn.commit()

                        # Redirect to the review page
                        return redirect(url_for('review'))
                        
                else:
                        return render_template('review.html')
        else: 
                return redirect(url_for('login'))



if __name__ == "__main__":
	import click

	@click.command()
	@click.option('--debug', is_flag=True)
	@click.option('--threaded', is_flag=True)
	@click.argument('HOST', default='0.0.0.0')
	@click.argument('PORT', default=8111, type=int)
	def run(debug, threaded, host, port):
		"""
		This function handles command line parameters.
		Run the server using:
			python server.py
		Show the help text using:
			python server.py --help
		"""

		HOST, PORT = host, port
		print("running on %s:%d" % (HOST, PORT))
		app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()
