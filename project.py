from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog APP"


# Connect to Database and create database session
engine = create_engine('sqlite:///catalogitemwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# login decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # verify value of state to protect against cross-site reference forgery
    # attacks
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    # exchange this short-lived token for a long-lived token here

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/v2.9/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&'
           'client_secret=%s&fb_exchange_token=%s') % (
           app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    # extract access token from response
    token = 'access_token=' + data['access_token']

    # Use token to get user info from API
    # userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token so i don't need to make api calls
    # token = result.split("&")[0]

    # i should able to make api calls with my new token
    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    # populate my login session
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.4/me/picture?%s&'
           'redirect=0&height=200&width=200' % token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    # separate  API call for my profile picture
    login_session['picture'] = data["data"]["url"]

    # see if user exists as goo* to retrieve a user or create new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius:150px;'
               '-webkit-border-radius:150px;-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
# when user logout
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
        facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius:150px;'
               '-webkit-border-radius:150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view categories Information
@app.route('/category/<string:category_name>/items/JSON')
def categoryListJSON(category_name):
    categories = session.query(Category).order_by(asc(Category.name))
    category = session.query(Category).filter_by(name=category_name).one()
    creator = getUserInfo(category.user_id)
    items = session.query(MenuItem).filter_by(
        category_name=category_name).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/category/<string:category_name>/<string:item_title>/JSON')
def menuItemJSON(category_name, item_title):
    Menu_Item = session.query(MenuItem).filter_by(name=category_name).one()
    return jsonify(Menu_Item=Menu_Item.serialize)


@app.route('/category/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[r.serialize for r in categories])


# Show all categories
@app.route('/')
@app.route('/category/')
def showCategories():
    try:
        categories = session.query(Category).order_by(asc(Category.name))
        items = session.query(MenuItem).order_by(MenuItem.id.desc()).limit(10)
        if 'username' not in login_session:
            return render_template('publicCategories.html',
                                   categories=categories,
                                   items=items)
        else:
            return render_template('categories.html',
                                   categories=categories,
                                   items=items)
    except:
        return redirect(url_for('showCategories'))


# Show a category items
@app.route('/category/<string:category_name>/')
@app.route('/category/<string:category_name>/items/')
def showList(category_name):
    try:
        categories = session.query(Category).order_by(asc(Category.name))
        category = session.query(Category).filter_by(name=category_name).one()
        creator = getUserInfo(category.user_id)
        items = session.query(MenuItem).filter_by(
            category_name=category_name).all()
        # total_items= items.count()
        if 'username' not in login_session:
            return render_template('publicItems.html',
                                   items=items, category=category,
                                   categories=categories,
                                   creator=creator)
        else:
            return render_template('items.html',
                                   items=items,
                                   category=category,
                                   categories=categories,
                                   creator=creator)
    except:
        return redirect(url_for('showCategories'))


# show a specific item
@app.route('/category/<string:category_name>/<string:item_title>')
def showItem(category_name, item_title):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        creator = getUserInfo(category.user_id)
        item = session.query(MenuItem).filter_by(title=item_title).one()
        if 'username' not in login_session:
            return render_template('publicItem.html',
                                   item=item,
                                   category=category,
                                   creator=creator)
        else:
            return render_template('item.html',
                                   item=item,
                                   category=category,
                                   creator=creator)
    except:
        return redirect(url_for('showCategories'))


# Delete a specific item
@app.route('/category/<string:category_name>/'
           '<string:item_title>/delete', methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_title):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        itemToDelete = (session.query(MenuItem).filter_by(title=item_title)
                        .one())
        if login_session['user_id'] != itemToDelete.user_id:
            return ("<script>function myFunction() {alert('You are not"
                    "authorized to delete this item . Please create your own"
                    "items.');}</script><body onload='myFunction()''>")
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            flash('Menu Item Successfully Deleted')
            return redirect(url_for('showCategories'))
        else:
            return render_template('deleteItem.html', item=itemToDelete)
    except:
        return redirect(url_for('showCategories'))


# edit a specific item
@app.route('/category/<string:category_name>/<string:item_title>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_title):
    try:
        category = session.query(Category).filter_by(name=category_name).one()
        editedItem = session.query(MenuItem).filter_by(title=item_title).one()
        categories = session.query(Category).order_by(asc(Category.name))
        if login_session['user_id'] != editedItem.user_id:
            return ("<script>function myFunction() {alert('You are not"
                    "authorized to edit this Category Item . Please create"
                    "your own Items in order to edit"
                    "items.');}</script><body onload='myFunction()''>")
        if request.method == 'POST':
            if request.form['title']:
                editedItem.title = request.form['title']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category_name']:
                editedItem.category_name = request.form['category_name']
            session.add(editedItem)
            session.commit()
            flash('Menu Item Successfully Edited')
            return redirect(url_for('showCategories'))
        else:
            return render_template('editItem.html',
                                   category_name=category_name,
                                   item=editedItem, categories=categories)
    except:
        return redirect(url_for('showCategories'))


# Create a new item
@app.route('/category/items/new/', methods=['GET', 'POST'])
def newItem():
    try:
        if 'username' not in login_session:
            return redirect('/login')
        categories = session.query(Category).order_by(asc(Category.name))
        if request.method == 'POST':
            newItem = MenuItem(
                title=request.form[
                    'title'], description=request.form['description'],
                category_name=request.form['category_name'],
                user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash('New Menu %s Item Successfully Created' % (newItem.title))
            return redirect(url_for('showCategories'))
        else:
            return render_template('newItem.html', categories=categories)
    except:
        return redirect(url_for('showCategories'))


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
