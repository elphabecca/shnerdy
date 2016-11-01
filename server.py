from flask import Flask, render_template, jsonify, request, session
import requests
import os

app = Flask(__name__)

app.secret_key = "talknerdytome"
SHARED_SECRET = os.environ["SHARED_SECRET"]
KEYSTRING = os.environ["KEYSTRING"]

# ROUTES
# *************************************************

@app.route('/')
def index():
    """Shnerdy introduction (need), login/OAuth form (need), logout button if user not in session (need)"""

    print "\n\n\n\n****************\nTHIS IS THE SESSION: ", session, "\n\n\n"
    access_token = session.get('access_token')
    print "\n\n\n ACCESS TOKEN: ", access_token, "\n\n\n"

    # Logoout or login only shows if the user is logged in
    if access_token is None:
        user_sess = None

    return render_template('index.html', user_sess=user_sess)

@app.route('/etsy_listings.json')
def get_some_stuff():
    """Hoping to return shtuff from the etsy API"""

    search_term = 'Dorothy Gale'

    url = 'https://openapi.etsy.com/v2/listings/active?api_key=' + KEYSTRING

    payload = {'tags' : search_term}
    print payload

    response = requests.get(url, params=payload)
    json_response = response.json()

    for item in json_response["results"]:
        print "\nTitle: ", item["title"], "\nListing ID: ", item["listing_id"], "\nPrice: ", item["price"], "\nURL: ", item["url"], "\nDigital: ", item["is_digital"], "\nCategory: ", item["category_path"]

    return jsonify(json_response)



# *************************************************
if __name__ == "__main__":
    app.run(debug=True)