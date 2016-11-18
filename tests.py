import unittest
from server import app
from model import User, Term, connect_to_db, db, example_data

class NotLoggedIn(unittest.TestCase):
    """Test cases for Flask where the user is not logged in."""

    def setUp(self):
        """Set up before each test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def tearDown(self):
        """Tear down after each test."""

        pass

    def test_home(self):
        """First Test"""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<li>Step 2: Search shirts!</li>', result.data)
        self.assertIn('<h1>SHNERDY</h1>', result.data)
        self.assertIn('<input type="submit" id="oauth" name="oauth" value="Login with Google">', result.data)
        self.assertNotIn('<a href="/logout">Logout</a>', result.data)

class LoggedInMonica(unittest.TestCase):
    """Test cases for users who are logged in"""

    def setUp(self):
        """Set up before each test."""
        
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        with self.client as c:
            with c.session_transaction() as sess:
                sess['access_token'] = 'test'
                sess['user'] = 2

        connect_to_db(app, 'postgresql:///testdbshnerdy')

        db.create_all()
        example_data()

    def tearDown(self):
        """Tear down after each test."""

        db.session.close()
        db.drop_all()

    def test_home_2(self):
        """Test home page as a logged in user."""

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<li>Step 2: Search shirts!</li>', result.data)
        self.assertIn('<h1>SHNERDY</h1>', result.data)
        self.assertNotIn('<input type="submit" id="oauth" name="oauth" value="Login with Google">', result.data)
        self.assertIn('<a href="/logout">Logout</a>', result.data)

    def test_user_home_no_categories_2(self):
        """Test user page who has no categories set up"""

        result = self.client.get('/2')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>Search Shnerdy!</h1>', result.data)
        self.assertIn('<div id="if_cat-empty">', result.data)
        self.assertNotIn('<div id="snearch_form">', result.data)


class LoggedInPhoebe(unittest.TestCase):
    """Test cases for users who are logged in"""

    def setUp(self):
        """Set up before each test."""
        
        self.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'key'
        with self.client as c:
            with c.session_transaction() as sess:
                sess['access_token'] = 'test'
                sess['user'] = 1

        connect_to_db(app, 'postgresql:///testdbshnerdy')

        db.create_all()
        example_data()

    def tearDown(self):
        """Tear down after each test."""

        db.session.close()
        db.drop_all()

    def test_user_home_with_categories_2(self):
        """Test user page who has categories set up"""

        result = self.client.get('/1')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>Search Shnerdy!</h1>', result.data)
        self.assertNotIn('<div id="if_cat-empty">', result.data)
        self.assertIn('<div id="snearch_form">', result.data)
        self.assertIn('Bagpipes', result.data)

    def test_user_listy_page(self):
        """Test the route that directs the user to a listy of their selected terms."""

        result = self.client.post('/listy',
                                  data={'categories' : 'Music', 'user_id' : 1})

        self.assertEqual(result.status_code, 200)
        self.assertIn('<input type="checkbox" name="search_term" value="Music" checked="checked">Music<br>', result.data)
        self.assertNotIn('Smelly Cat', result.data)

    def test_update_dropdown(self):
        """Test the route that updates the dropdown information"""

        result = self.client.post('/update_dropdown',
                                  data={'user_id' : 1})
        
        self.assertEqual(result.status_code, 200)
        self.assertIn('Smelly Cat', result.data)
        self.assertIn('Music', result.data)

    def test_update_category(self):
        """Test the route that udpates the category on the user page."""

        result = self.client.post('/add_category',
                                  data={'category' : 'Massage', 'user_id' : 1})

        self.assertEqual(result.status_code, 200)
        self.assertIn("'Massage' has been added as a category!", result.data)

    def test_add_term(self):
        """Test the route that updates the term on the user page."""

        result = self.client.post('/add_term',
                                  data={'term' : 'Fluffy Cat',
                                        'user_id' : 1,
                                        'parent_id' : 4})

        self.assertEqual(result.status_code, 200)
        self.assertIn("'Fluffy Cat' has been added as a term!", result.data)

    def test_snearch_summary(self):
        """Test the route that displays the user's search summary."""

        result = self.client.post('/snearch_summary',
                                  data={'user' : 1,
                                        'search_term' : ["Smelly Cat", "Grumpy Cat"]})

        self.assertEqual(result.status_code, 200)
        self.assertIn('<h3>Snearch Results:</h3>', result.data)
        self.assertIn('<input type="button" id="next" value="Next Shirt, Please!"></button>', result.data)

    def test_request_more_shirts(self):
        """Test the route that gets more shirts from the Etsy API when shirts are running low."""

        result = self.client.get('/request_more_shirts',
                                      data={'total_count' : 30,
                                            'countdown' : 15,
                                            'num_avail_shirts' : 2,
                                            'API_requests' : 1,
                                            'term' : 'Guitar'})

        self.assertEqual(result.status_code, 200)
        self.assertIn('Guitar', result.data)

    def test_logout(self):
        """Test the route that logs the user out."""

        result = self.client.get('/logout',
                                 data={},
                                 follow_redirects=True)

        self.assertEqual(result.status_code, 200)
        self.assertIn('<li>Step 2: Search shirts!</li>', result.data)
        self.assertIn('<h1>SHNERDY</h1>', result.data)
        self.assertIn('<input type="submit" id="oauth" name="oauth" value="Login with Google">', result.data)
        self.assertNotIn('<a href="/logout">Logout</a>', result.data)


if __name__ == '__main__':
    unittest.main()
