from flask import Flask, render_template, request

server = Flask(__name__) #Creating the server
@server.route('/', methods=['GET']) #Creating route in the server (path of the route) + methods that can be used in the route (get --> just get informations from the server)
#Creating a function que return a string/render_template with the html file
def index() -> str:
    return render_template('index.html')

#Creating route and function, similar the one above
@server.route('/profile', methods=['GET'])
def profile() -> str:
    name = request.args.get('name')
    email = request.args.get('email')
    return render_template('profile.html', user_name=name, user_email=email)

#If use this file as input port
if __name__ == '__main__': 
    server.run(port=8080, debug=True, ssl_context='adhoc') #Running the server in the port 8080 as debug mode, the 3º parameter --> initialize the server as https protocol
    