from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import wikipedia
import requests
import json
import openai
import random
import keys.keys as keys

app = Flask(__name__)
app.config['SECRET_KEY'] = 'jpeur'

class CityForm(FlaskForm):
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/", methods=['GET', 'POST'])
def home():
    form = CityForm()
    location = False
    fun_facts = []
    restaurants = []
    attractions = []
    form_submitted = False  # flag for whether a form submission has occurred
    yelp_key = keys.yelp_key
    API_HOST = 'https://api.yelp.com'
    SEARCH_PATH = '/v3/businesses/search'

    random_restaurants = []
    random_attractions = []

    if form.validate_on_submit():
        form_submitted = True  # form has been submitted
        city_name = form.city.data
        state_name = form.state.data
        form.city.data = ''
        form.state.data = ''

        location = f"{city_name}, {state_name}"

        # Yelp API request for restaurants
        url_params = {
            'term': 'restaurants',
            'location': location.replace(' ', '+'),
            'limit': 10,
            'radius': 8047
        }
        url = '{0}{1}'.format(API_HOST, SEARCH_PATH)
        headers = {'Authorization': 'Bearer %s' % yelp_key}
        response = requests.request('GET', url, headers=headers, params=url_params)
        restaurants = response.json().get('businesses', [])

        for restaurant in restaurants:
            restaurant['address'] = ", ".join(restaurant['location']['display_address'])

        # Yelp API request for attractions
        url_params['term'] = 'attractions'
        response = requests.request('GET', url, headers=headers, params=url_params)
        attractions = response.json().get('businesses', [])

        for attraction in attractions:
            attraction['address'] = ", ".join(attraction['location']['display_address'])

        random_restaurants = random.sample(restaurants, 3)

        for restaurant in random_restaurants:
            restaurant['address'] = ", ".join(restaurant['location']['display_address'])

        # Randomly select 3 attractions from the broader range
        random_attractions = random.sample(attractions, 3)

        for attraction in random_attractions:
            attraction['address'] = ", ".join(attraction['location']['display_address'])

        # fetch fun facts
        try:
            summary = wikipedia.summary(location, sentences = 3)
            fun_facts.extend(summary.split('. ')[:3])  # split into individual sentences for bullets
        except wikipedia.exceptions.PageError:
            fun_facts.append('No information available for this city.')
        except wikipedia.exceptions.DisambiguationError as e:
            fun_facts.append('Multiple possibilities found, please specify. For example: {}'.format(', '.join(e.options[:3])))

    return render_template('home.html', form=form, location=location, fun_facts=fun_facts, form_submitted=form_submitted, restaurants=random_restaurants, attractions=random_attractions)

if __name__ == "__main__":
    app.run(debug=True)
