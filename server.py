from flask import Flask, render_template, jsonify, request, session, redirect, flash
import requests
import os
from model import User, Term, connect_to_db

app = Flask(__name__)

app.secret_key = "talknerdytome"
SHARED_SECRET = os.environ["SHARED_SECRET"]
KEYSTRING = os.environ["KEYSTRING"]
# KEYSTRING = os.environ.get("KEYSTRING", "whatever")
# if not KEYSTRING:
#     raise ValueError("Hey, you didn't source...")

# ROUTES & HELPER FXNS
# *************************************************

@app.route('/')
def index():
    """Shnerdy introduction (need), login/OAuth form (need), logout button if user not in session (need)"""

    print "\n\n\n\n****************\nTHIS IS THE SESSION: ", session, "\n\n\n"
    access_token = session.get('access_token')
    print "\n\n\n ACCESS TOKEN: ", access_token, "\n\n\n"

    return render_template('index.html', access_token=access_token)

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

    return render_template("display_results.html", result_list=result_list, num_items=num_items)

@app.route('/login', methods=['POST'])
def validate_user():
    """Add user to the db if they are a new user, validate user if they are a returning user."""

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter(User.username == username).first()

    if not user:
        flash("Username doesn't exist -- please register!")
        return redirect('/')

    if user.password != password:
        flash("Whoops -- try that password again.")
        return redirect('/')

    session['access_token'] = user.id
    flash("Successful Login -- Welcome, %s!" % user.first_name)

    return redirect('/')
    # return redirect('/%s' % user.id)


@app.route('/<int:user_id>')
def show_user_terms(user_id):
    """Show the user their categories and terms, allow them to add new terms and edit fields."""

    print "Hey you're at %s's page!" % user.id

    return render_template(user_page.html)


@app.route('/logout')
def logout_user():
    """Log the Shnerdy User out."""

    del session['access_token']
    flash("You've successfully logged out of Shnerdy.")
    return redirect('/')




# *************************************************
if __name__ == "__main__":

    connect_to_db(app)
    app.run(debug=True, host="0.0.0.0", port=5003)





