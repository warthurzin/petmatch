from flask import Flask, redirect, Response, request
from dataclasses import dataclass
import requests
from oauthlib.oauth2 import WebApplicationClient

server = Flask(__name__)

oauth = WebApplicationClient(client_id=)

@dataclass
class GoogleHosts:
    authorization_endpoint: str
    token_endpoint: str
    userinfo_endpoint: str
    certs: str

def get_google_oauth_hosts() -> GoogleHosts:
    hosts = requests.get('https://accounts.google.com/.well-known/openid-configuration')
    if hosts.status_code != 200:
        raise Exception('It can not recover the endpoints of authetication of the Google!')
    data = hosts.json()
    return GoogleHosts(authorization_endpoint=data.get('authorization_endpoint'),
                       token_endpoint=data.get('token_endpoint'),
                       userinfo_endpoint=data.get('userinfo_endpoint'),
                       certs=data.get('jwks_uri'))

@server.route('/auth/login', methods=['GET'])
def login() -> Response:
    hosts = get_google_oauth_hosts()
    redirect_uri = oauth.prepare_authorization_request(authorization_url=hosts.authorization_endpoint,
                                                       redirect_url='https://localhost:8081/auth/callback',
                                                       scope=['openid', 'email', 'profile'])
    return redirect(location=redirect_uri[0])

@server.route('/auth/callback', methods=['GET'])
def callback():
    code = request.args.get("code")
    if not code:
        return "Authorization code not found", 400
    try:
        hosts = get_google_oauth_hosts()
        token_url, headers, body = oauth.prepare_token_request(
            hosts.token_endpoint,
            authorization_response=request.url,
            client_secret=
        )
        token_response = requests.post(token_url, headers=headers, data=body)
        if token_response.status_code != 200:
            return "Failed to exchange authorization code for token", 400
        tokens = token_response.json()   
        if "access_token" not in tokens or not tokens["access_token"]:
            return "Access token is missing or invalid", 400
        user_info_response = requests.get(
            hosts.userinfo_endpoint,
            headers={'Authorization': f'Bearer {tokens["access_token"]}'}
        ) 
        if user_info_response.status_code != 200:
            return "Failed to fetch user info", 400
        user_info = user_info_response.json()
        return redirect(f"https://localhost:8080/profile?name={user_info.get('name')}&email={user_info.get('email')}")
    except Exception as e:
        return f"An error occurred: {str(e)}", 500
    #return Response("Callback function reached!", status=200)

if __name__ == '__main__':
    server.run(port=8081, debug=True, ssl_context='adhoc')