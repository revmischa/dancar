from jetbridge import app
from jetbridge.models import db, User
from flask import flash, abort, jsonify, request, redirect, session, url_for, render_template as render
from flask_user import current_user, login_required
from flask.ext.login import login_user 
from flask_oauthlib.client import OAuthException, OAuth as FlaskOAuth
from flask_wtf.csrf import generate_csrf
import requests
import json

oauth = FlaskOAuth()

facebook_oauth = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key='1286003954758836',
    consumer_secret=app.config.get('FACEBOOK_SECRET'),
    request_token_params={'scope': 'email,user_friends'}
)

@app.route('/oauth/linkedin/accept_code', methods=['POST', 'OPTIONS'])
def oauth_linkedin_accept_code():
    if request.method != 'POST':  # CORS pre-flight
        return "ok"
    # body should be json and contain auth code
    # this is super lame and ugly. 
    redir_uri = url_for('oauth_linkedin_callback', _external=True)
    params = {
        'client_id': request.json['clientId'],
        'redirect_uri': request.json['redirectUri'],
        'client_secret': app.config['LINKEDIN_CONSUMER_SECRET'],
        'code': request.json['code'],
        'grant_type': 'authorization_code',
        'state': request.json['state'],
    }
    # request access_token with our code
    r = requests.post(linkedinoauth.base_url + linkedinoauth.access_token_url, data=params)
    res = json.loads(r.text)
    if 'access_token' in res:
        # great success!
        token = res['access_token']
        find_or_create_user_from_linkedin(token)
        return jsonify(token=token)
    return jsonify(msg="Error logging in with LinkedIn")

@facebookoauth.tokengetter
def get_linkedin_oauth_token():
    return session.get('fb_token')

# pass in a valid token and this will perform an API request to fetch the user's profile
# and then will either create a new user or use an existing user. will log them in as that user
def find_or_create_user_from_linkedin(li_token):
    """save our access token and fetch the user's profile with it (internal method)"""
    session['linkedin_token'] = (li_token, '')
    me = linkedinoauth.get('/v1/people/~:(id,email-address,picture-url,picture-urls::(original),first-name,last-name,site-standard-profile-request)?format=json')
    # FIXME: how to check for request failure here?

    # save token + account info
    user = User.find_or_create_from_linkedin(me.data)

    # log them in
    if user:
        login_user(user, remember=True)

    return user
