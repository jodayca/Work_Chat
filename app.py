from flask import Flask

app = Flask(__name__)
app.secret_key = 'XxxxaaaL%@dEL*><!'

# Import Routes File

#from api import Index, Login_View, Join_View, Register
from api import *

if __name__ == "__main__":
    app.debug = True
    app.run()

