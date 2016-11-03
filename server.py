from flask import Flask, render_template, jsonify, request, session, redirect
import requests
import os
import model

app = Flask(__name__)

app.secret_key = "talknerdytome"
SHARED_SECRET = os.environ["SHARED_SECRET"]
KEYSTRING = os.environ["KEYSTRING"]

# ROUTES & HELPER FXNS
# *************************************************

@app.route('/')
def index():
    """Shnerdy introduction (need), login/OAuth form (need), logout button if user not in session (need)"""

    # print "\n\n\n\n****************\nTHIS IS THE SESSION: ", session, "\n\n\n"
    access_token = session.get('access_token')
    # print "\n\n\n ACCESS TOKEN: ", access_token, "\n\n\n"

    # Logoout or login only shows if the user is logged in
    if access_token is None:
        user_sess = None

    return render_template('index.html', user_sess=user_sess)

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




# *************************************************
if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0", port=5003)

    model.connect_to_db(app)




