from flask import Flask, render_template, jsonify, request, session, redirect, flash, url_for
from flask_oauth import OAuth
import requests
import os
from model import User, Term, connect_to_db, db

app = Flask(__name__)

app.secret_key = "talknerdytome"
SHARED_SECRET = os.environ["SHARED_SECRET"]
KEYSTRING = os.environ["KEYSTRING"]
# KEYSTRING = os.environ.get("KEYSTRING", "whatever")
# if not KEYSTRING:
#     raise ValueError("Hey, you didn't source...")
REDIRECT_URI = "/oauth2callback"
oauth = OAuth()

# Google OAuth Params
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key=os.environ["GOOGLE_CLIENT_ID"],
                          consumer_secret=os.environ["GOOGLE_CLIENT_SECRET"])

# ROUTES & HELPER FXNS
# *************************************************

# HOME PAGE
@app.route('/')
def index():
    """Shnerdy introduction (need), login/OAuth form (need), logout button if user not in session (need)"""

    access_token = session.get('access_token')

    return render_template('index.html', access_token=access_token)


# OAUTH HANDLING - @app.route("/oauth"), @app.route(REDIRECT_URI), @app.route('/login'), @google.tokengetter
@app.route("/oauth", methods=['POST'])
def oauth():
    """Google OAuth"""

    # If the access token does not exist, go to /login to get user auth.
    access_token = session.get('access_token')
    if access_token is None:
        return redirect('/login')

    # If the session already has an access_token exists, make sure it's valid.
    access_token = access_token[0]
    from urllib2 import Request, urlopen, URLError

    headers = {'Authorization': 'OAuth '+access_token}
    req = Request('https://www.googleapis.com/oauth2/v1/userinfo',
                  None, headers)

    # Try to get the user authorized given the current access_token.
    # If it's a bad token, pop it out and go the route of asking the user for authorization.
    try:
        res = urlopen(req)
    except URLError, e:
        if e.code == 401:
            # Unauthorized - bad token
            session.pop('access_token', None)
            return redirect(url_for('login'))
    return res.read()

@app.route('/login')
def login():
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route(REDIRECT_URI)
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    session['access_token'] = access_token, ''
    return redirect('/oauth_success')

@google.tokengetter
def get_access_token():
    return session.get('access_token')


# Helper function to get user's name and email from google once they've OAuthed in.
def get_google_info():
    """Get user's name and email from Google OAuth Login."""

    access_token = session.get('access_token')
    access_token = access_token[0]
    google_user_info_url = 'https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token=' + access_token

    google_user_info = requests.get(google_user_info_url)
    google_user_json = google_user_info.json()

    return google_user_info.json()


@app.route("/oauth_success")
def yay():
    user_info = get_google_info()

    google_user_id = str(user_info["id"])
    google_first_name = str(user_info["given_name"])
    google_email = str(user_info["email"])

    user = User.query.filter(User.oauth_id == google_user_id).first()

    if not user:
        new_user = User(first_name=google_first_name,
                        email=google_email,
                        oauth_id=google_user_id)
        db.session.add(new_user)
        db.session.commit()
        user = User.query.filter(User.oauth_id == google_user_id).first()
        flash("Welcome to Shnerdy, %s!" % google_first_name)

        return redirect('/%s' % user.id)

    flash("Welcome back, %s!" % user.first_name)
    return redirect('/%s' % user.id)


# ETSY API FUNCTIONS
def get_many_results():
    """Taking in a list of search terms, return all search results."""

    search_list = ['Wizard of Oz', 'Yellow Brick Road']

    full_response = []
    for term in search_list:
        term_results = get_etsy_stuff(term)
        term_results_list = term_results["results"]
        full_response.extend(term_results_list)

    return full_response

def get_etsy_stuff(search_term):
    """Return search_term TShirts from the etsy API"""

    # The details of the search
    url = 'https://openapi.etsy.com/v2/listings/active?api_key=' + KEYSTRING
    payload = {'tags' : search_term,
               'includes': 'Images(url_170x135)',
               'limit' : 100,
               'category' : 'Clothing/Shirt'}

    # The response, and a loop to get pages of the response in one json dictionary.
    response = requests.get(url, params=payload)
    json_response = response.json()
    pages = (json_response["count"]/100)

    offset = 100
    for page in range(pages):
        moar_response = requests.get(response.url + "&offset=" + str(offset))
        moar_json = moar_response.json()
        moar_list = moar_json["results"]
        json_response["results"].extend(moar_list)
        # print "GERBIL", len(json_response["results"])
        offset += 100

    return json_response

@app.route('/display_results')
def show_results():
    """Display all the shirt results (Title, price, image(s), url) to the User"""

    result_list = get_many_results()

    num_items = len(result_list)

    # result_list = json_response["results"]

    return render_template("display_results.html",
                           result_list=result_list,
                           num_items=num_items)


@app.route('/<int:user_id>')
def show_user_terms(user_id):
    """Show the user their categories and terms, allow them to add new terms and edit fields."""

    user = User.query.get(user_id)
    terms = Term.query.filter(Term.user_id == user_id).all()

    return render_template('user_page.html',
                            user=user,
                            terms=terms)


@app.route('/add_terms', methods=['POST'])
def add_terms():
    """Add categories and terms to the user's detail page."""

    category = str(request.form.get('category'))
    user_id = int(request.form.get('user_id'))

    # Add the new category to the db:
    new_category = Term(term=category,
                    user_id=user_id)
    db.session.add(new_category)
    db.session.commit()

    return "'%s' has been added as a category!" % category

@app.route('/logout')
def logout_user():
    """Log the Shnerdy User out, delete their access token from the session."""

    del session['access_token']
    flash("You've successfully logged out of Shnerdy.")
    return redirect('/')




# *************************************************
if __name__ == "__main__":

    connect_to_db(app)
    app.run(debug=True)


    # for vagrant: (host="0.0.0.0", port=5003)



# ********************* OLD CODE: *****************************************
# @app.route('/login', methods=['POST'])
# def validate_user():
#     """Add user to the db if they are a new user, validate user if they are a returning user."""

#     username = request.form["username"]
#     password = request.form["password"]
#     first_name = request.form["new_first_name"]
#     new_username = request.form["new_username"]
#     new_password = request.form["new_password"]

#     # RETURNING USER FLOW
#     if first_name and new_username and new_password == "nerdy_shnerdy_admin":

#     user = User.query.filter(User.username == username).first()

#     if not user:
#         flash("Username doesn't exist -- please register!")
#         return redirect('/')

#     if user.password != password:
#         flash("Whoops -- try that password again.")
#         return redirect('/')

#     session['access_token'] = user.id
#     flash("Successful Login -- Welcome, %s!" % user.first_name)

#     return redirect('/%s' % user.id)

#     # NEW USER FLOW
#     if username and password == "nerdy_shnerdy_admin":
        
#         print first_name, new_username, new_password
#         flash("Whaddup, new user!")

#         return redirect('/')

