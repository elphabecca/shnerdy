from flask import Flask, render_template, jsonify, request, session, redirect, flash, url_for
from flask_oauth import OAuth
import requests
import os
import pdb
import json
from model import User, Term, Rating, Shirt, connect_to_db, db
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# app.secret_key = "talknerdytome"
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY", "talknerdytome")
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
    """Shnerdy introduction, login/OAuth form, logout button if user not in session"""

    access_token = session.get('access_token')
    session_user_id = session.get('user')

    return render_template('index.html', access_token=access_token, session_user_id=session_user_id)


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
        session['user'] = user.id
        flash("Welcome to Shnerdy, %s!" % google_first_name)

        return redirect('/%s' % user.id)

    session['user'] = user.id
    flash("Welcome back, %s!" % user.first_name)
    return redirect('/%s' % user.id)


@app.route('/<int:user_id>')
def show_user_terms(user_id):
    """Show the user their categories and terms, allow them to add new terms and edit fields."""

    session_user_id = session.get('user')
    user = User.query.get(user_id)
    terms = Term.query.filter(Term.user_id == user_id, Term.parent_id != None).all()
    categories = Term.query.filter(Term.user_id == user_id, Term.parent_id == None).all()

    return render_template('user_page.html',
                            user=user,
                            categories=categories,
                            terms=terms,
                            session_user_id=session_user_id)


@app.route('/update_dropdown', methods=['POST'])
def update_dropdown():
    """Given the user id, returns a list of categories for that user."""

    user_id = request.form.get('user_id')
    categories = Term.query.filter(Term.user_id == user_id, Term.parent_id == None).all()
    cat_list = []
    for category in categories:
        cat_list.append(category.term)

    results_dict = {'cat_list' : cat_list}

    return jsonify(results_dict)


@app.route('/add_category', methods=['POST'])
def add_category():
    """Add category to the db."""

    category = str(request.form.get('category'))
    user_id = int(request.form.get('user_id'))

    # Add the new category to the db:
    new_category = Term(term=category,
                    user_id=user_id)
    db.session.add(new_category)
    db.session.commit()

    category_object = Term.query.filter(Term.term == category).first()
    category_id = category_object.id

    results_dict = {"category_name" : category,
                    "user_id" : user_id,
                    "category_id" : category_id}

    return jsonify(results_dict)

@app.route('/add_term', methods=['POST'])
def add_term():
    """Add term to the db."""

    term = str(request.form.get('term'))
    user_id = int(request.form.get('user_id'))
    parent_id = int(request.form.get('parent_id'))

    # Add the new category to the db:
    new_term = Term(term=term,
                    user_id=user_id,
                    parent_id=parent_id)
    db.session.add(new_term)
    db.session.commit()

    results_dict = {'message' : "'%s' has been added as a term!" % term,
                    "term_name" : term,
                    "parent_id" : parent_id}

    return jsonify(results_dict)


@app.route('/listy', methods=['POST'])
def show_me_list():
    """Given the user ID and the Category name, generate a list of terms to search Etsy for."""

    session_user_id = session.get('user')
    category = str(request.form.get('categories'))
    user_id = int(request.form.get('user_id'))
    list_o_terms = [category]

    parent_id = Term.query.filter(Term.term == category).first()
    parent_id = parent_id.id
    terms = Term.query.filter(Term.user_id == user_id, Term.parent_id == parent_id).all()

    for term in terms:
        list_o_terms.append(str(term.term))

    return render_template('user_list_terms.html',
                            list_o_terms=list_o_terms,
                            session_user_id=session_user_id)


def get_etsy_count_and_few_results(search_term):
    """Return counts of shirts per term from the Etsy API"""

    # The details of the search
    url = 'https://openapi.etsy.com/v2/listings/active?api_key=' + KEYSTRING
    payload = {'tags' : search_term,
               'includes': 'Images(url_570xN)',
               'limit' : 10,
               'category' : 'Clothing/Shirt'}

    # The response, and a loop to get pages of the response in one json dictionary.
    response = requests.get(url, params=payload)
    json_response = response.json()
    count = json_response["count"]
    results = json_response["results"]

    return (count, results)

def add_to_curr_search_dict(term, count, results, curr_search_dict):
    """Add search results to the current search dictionary."""
    
    curr_search_dict[term] = {'total_count' : count,
                              'countdown' : count,
                              'num_avail_shirts' : len(results),
                              'API_requests' : 1,
                              'items' : []}

    item_listings = curr_search_dict[term]['items']
    
    for listing in results:
            temp_dict = {}
            temp_dict["etsy_id"] = listing["listing_id"]
            temp_dict["tags"] = listing["tags"]
            temp_dict["image_url"] = listing["Images"][0]["url_570xN"]
            temp_dict["price"] = listing["price"]
            temp_dict["url"] = listing["url"]
            temp_dict["user_search_term"] = term

            item_listings.append(temp_dict)
    
    print "\n\n\n**********\n %s items for '%s' have now been added to the dictionary.\n**********\n\n\n" % (len(results), term)


@app.route('/snearch_summary', methods=['POST'])
def create_shnummary():
    """return a result summary to the user."""

    session_user_id = session.get('user')
    search_terms = request.form.getlist('search_term')
    
    curr_search_dict = {}
    result_sum = 0

    for term in search_terms:
        count, results = get_etsy_count_and_few_results(term)
        add_to_curr_search_dict(term, count, results, curr_search_dict)
        result_sum += int(count)

        # If there are no results for a particular term add a flash message to alert them
        # if count == 0:
        #     flash("The search for '%s' didn't return any results." % term)

    return render_template('snearch_summary.html',
                           search_terms=search_terms,
                           session_user_id=session_user_id,
                           result_sum=result_sum,
                           curr_search_dict=curr_search_dict)
  

def create_new_results_dict(term,
                            total_count,
                            countdown,
                            num_avail_shirts,
                            API_requests,
                            results):
    """create a dict to append to the curr_search_dict"""
    new_results_dict = {}
    new_results_dict[term] = {'total_count' : total_count,
                              'countdown' : countdown,
                              'num_avail_shirts' : num_avail_shirts,
                              'API_requests' : API_requests,
                              'items' : []}

    item_listings = new_results_dict[term]['items']
    
    for listing in results:
            temp_dict = {}
            temp_dict["etsy_id"] = listing["listing_id"]
            temp_dict["tags"] = listing["tags"]
            temp_dict["image_url"] = listing["Images"][0]["url_570xN"]
            temp_dict["price"] = listing["price"]
            temp_dict["url"] = listing["url"]
            temp_dict["user_search_term"] = term

            item_listings.append(temp_dict)

    return new_results_dict


@app.route('/request_more_shirts')
def request_more_shirts():
    """Request more shirts from the Etsy API and return them"""
    
    total_count = int(request.args.get('total_count'))
    countdown = int(request.args.get('countdown'))
    num_avail_shirts = int(request.args.get('num_avail_shirts'))
    API_requests = int(request.args.get('API_requests'))
    term = str(request.args.get('term'))

    offset = API_requests * 10

    # The details of the search
    url = 'https://openapi.etsy.com/v2/listings/active?api_key=' + KEYSTRING
    payload = {'tags' : term,
               'includes': 'Images(url_570xN)',
               'limit' : 10,
               'category' : 'Clothing/Shirt',
               'offset' : str(offset)}

    
    response = requests.get(url, params=payload)
    json_response = response.json()
    results = json_response["results"]

    # Update shirt data:
    num_avail_shirts += len(results)
    API_requests += 1

    new_results_dict = create_new_results_dict(term,
                                               total_count,
                                               countdown,
                                               num_avail_shirts,
                                               API_requests,
                                               results)

    # return new results to front end
    return jsonify(new_results_dict)


@app.route('/check_dupes')
def check_dupes():
    """Check for duplicates in shirt data"""

    etsy_id = str(request.args.get('etsy_id'))
    term = str(request.args.get('term'))
    dupe_dict = json.loads(request.args.get("dict_pass"))

    if etsy_id not in dupe_dict.keys():
        dupe_dict[etsy_id] = dupe_dict.get(etsy_id, {'count' : 0, 'term' : []})

    dupe_dict[etsy_id]['count'] += 1
    dupe_dict[etsy_id]['term'].append(term)

    if dupe_dict[etsy_id]['count'] > 1:
        return_dict = {'dupe' : "True", "dupeDict" : dupe_dict, "dupe_results" : dupe_dict[etsy_id]}
        return jsonify(return_dict)
    else:
        return_dict = {'dupe' : "False", "dupeDict" : dupe_dict}
        return jsonify(return_dict)


@app.route('/yay_shirt', methods=['POST'])
def add_shirt_to_db_yay():
    """Add shirt to the db"""

    user_id = session.get('user')
    shirt_img = str(request.form.get('img'))
    shirt_price = str(request.form.get('price'))
    shirt_url = str(request.form.get('url'))
    etsy_id = str(request.form.get('etsy_id'))

    new_rating = Rating(etsy_id=etsy_id,
                        rating=True,
                        user_id=user_id)
    db.session.add(new_rating)

    new_shirt = Shirt(id=etsy_id,
                      price=shirt_price,
                      img=shirt_img,
                      url=shirt_url,
                      user_id=user_id)
    db.session.add(new_shirt)

    db.session.commit()

    return "SUCCESS"

@app.route('/nay_shirt', methods=['POST'])
def add_shirt_to_db_nay():
    """Add shirt to the db"""

    session_user_id = session.get('user')
    etsy_id = str(request.form.get('etsy_id'))

    new_rating = Rating(etsy_id=etsy_id,
                        rating=False,
                        user_id=session_user_id)
    
    db.session.add(new_rating)
    db.session.commit()

    return "SUCCESS"

@app.route('/favorites')
def display_favorites():
    """Display the shirts the user has indicated they like."""

    session_user_id = session.get('user')

    shirts = Shirt.query.filter(Shirt.user_id == session_user_id).all()

    num_shirts = len(shirts)

    return render_template('favorite_shirts.html',
                            shirts=shirts,
                            num_shirts=num_shirts,
                            session_user_id=session_user_id)

@app.route('/logout')
def logout_user():
    """Log the Shnerdy User out, delete their access token from the session."""

    del session['access_token']
    del session['user']
    flash("You've successfully logged out of Shnerdy.")
    return redirect('/')




# *************************************************
if __name__ == "__main__":

    connect_to_db(app, os.environ.get("DATABASE_URL"))
    # DebugToolbarExtension(app)
    # db.create_all(app=app)
    DEBUG = "NO_DEBUG" not in os.environ
    PORT = int(os.environ.get("PORT", 5000))

    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
    

    # for vagrant: (host="0.0.0.0", port=5003)






