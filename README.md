# Shnerdy

Shnerdy is a tool for more efficiently finding (generally nerdy) t-shirts. This web-app saves the search terms for a user and then searches the Etsy API for all terms at once, quickly returning multiple and varied search results to the user with an image, price, and link to access the shirt for purchase. The user is able to rate shirts and visit a page of their favorites. Sign-in is done exclusively via OAuth.

##Contents
* [Tech Stack](#technologies)
* [Features](#features)
* [About Me](#aboutme)

## <a name="technologies"></a>Technologies
Backend: Python, Flask, Flask OAuth, PostgreSQL, SQLAlchemy<br/>
Frontend: JavaScript, jQuery, AJAX, Jinja2, Bootstrap, Masonry, HTML5, CSS3<br/>
APIs: Etsy, Google (OAuth)<br/>

## <a name="features"></a>Features

Users log in to Shnerdy via Google OAuth:
![shnerdy1](https://cloud.githubusercontent.com/assets/20667515/20692686/860b5aec-b58e-11e6-880d-243982faf25c.png)

Users are able to add categories or terms to they'd like to search for shirts of:
![shnerdy2](https://cloud.githubusercontent.com/assets/20667515/20692687/860d7cdc-b58e-11e6-9b54-51a44360c8ff.png)

Though the user only clicks one button, as many requests to the Etsy API are made as the user selects terms to search. Users receive a summary of their search, and then indicate if they like, dislike, or just want to go to the next shirt based on an image, price and URL for the shirt:
![shnerdy3](https://cloud.githubusercontent.com/assets/20667515/20692684/860abd8a-b58e-11e6-8daa-6b86dcdd5a23.png)

Users can always re-visit their favorite shirts:
![shnerdy4](https://cloud.githubusercontent.com/assets/20667515/20692685/860b2306-b58e-11e6-824e-415b38f1b591.png)

## <a name="aboutme"></a>About Me
I live in the San Carlos Bay Area.
Visit me on [LinkedIn](https://www.linkedin.com/in/rebeccasaines).