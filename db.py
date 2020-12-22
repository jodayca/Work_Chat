from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# Mysql Configurations

app.config["MYSQL_DATABASE_USER"] = "jayala"
app.config["MYSQL_DATABASE_PASSWORD"] = "Fin5a2811"
app.config["MYSQL_DATABASE_DB"] = "work_chat"
app.config["MYSQL_DATABASE_HOST"] = "localhost"


mysql.init_app(app)