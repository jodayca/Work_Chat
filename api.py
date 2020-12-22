from flask import render_template, request, redirect, flash, url_for, session, send_from_directory
import pymysql
from app import app
from db import mysql
import bcrypt
import os

# Define to route where save the images profile
UPLOAD_FOLDER = os.path.abspath("./static/uploads_profile/")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Home Page
@app.route('/')
def Index():
    return render_template('home.html')

#Login
@app.route('/Login', methods=['GET', 'POST'])
def Login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        _username = request.form['username']
        _pass = request.form['password'].encode('utf-8')  
    
        sql = "SELECT * FROM work_chat.users WHERE NICK_NAME = %s"
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql, (_username))
        conn.commit()
        user = cur.fetchone()
        cur.close()

        if (user):
            if bcrypt.hashpw(_pass, user['PASSWORD_USER'].encode('utf-8')) == user['PASSWORD_USER'].encode('utf-8'):
                session['id'] = user['ID_USER']
                session['username'] = user['NICK_NAME']
                session['email'] = user['EMAIL_USER']
                
                if user['PROFILE_COMPLETE'] == 'YES':
                    return redirect(url_for('Chats', user=session['username']))
                else:
                    return redirect(url_for('Profile', user=session['username'], choise='change'))
        else:
            flash('Error el Usuario o Contraseña no Coinciden!', 'danger')
            return render_template('login.html')
    flash('Error el Usuario o Contraseña no Coinciden!', 'danger')
    return render_template('login.html')

#Registro
@app.route('/Join', methods=['GET', 'POST'])
def Join():
    if request.method == 'GET':
        return render_template('join.html')
    else:
        _username = request.form['username']
        _email = request.form['email']
        _pass = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(_pass, bcrypt.gensalt())

        if "@inv.com.gt" in _email:
            sql = "SELECT NICK_NAME, EMAIL_USER  FROM work_chat.users WHERE NICK_NAME = %s OR EMAIL_USER = %s"
            data = (_username, _email)
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute(sql, (data))
            conn.commit()
            account = cur.fetchone()
            print(account)
            if account != None:
                if account['NICK_NAME'] == _username:
                    flash('El nombre de usuario no está disponible, inteta con otro !', 'info')
                    return render_template('join.html')
                elif account['EMAIL_USER'] == _email:
                    flash('El correo ya está siendo utilizado por otra usuario!', 'warning')
                    return render_template('join.html')
            else:
                sql = "INSERT INTO work_chat.users(NICK_NAME,PASSWORD_USER,EMAIL_USER) VALUES(%s, %s, %s)"
                data = (_username, hash_password, _email)
                cur.execute(sql, (data))
                conn.commit()
                flash('Usuario agregado con exito!', 'success')
                return redirect(url_for('Login'))
        else:
            flash('El correo no pertenece a la organización!' , 'warning')
            return render_template('join.html')


#Profile Image
@app.route('/Profile-Img/<string:user>', methods=['POST'])
def ProfileImg(user):
    if request.method == 'POST':

        file = request.files['file']
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        sql = "UPDATE work_chat.users SET AVATAR = %s WHERE ID_USER = %s"
        url = "./uploads_profile/" + filename 
        data = (url, session['id'])
        cur.execute(sql, (data))
        conn.commit()
        flash('La imagen fue agregada con éxito !', 'success')
        return redirect(url_for('Profile', user=session['username'], choise='change'))


#Profile
@app.route('/Profile/<string:user>/<string:choise>', methods=['GET', 'POST'])
def Profile(user, choise):
    if request.method == 'GET':
        sql = "SELECT ID_USER,NICK_NAME,PASSWORD_USER,NAMES,LAST_NAMES,EMAIL_USER,AVATAR,TYPE,DATE_FORMAT(DATE_ADD,'%%d-%%m-%%Y') as UNIO FROM work_chat.users  INNER JOIN work_chat.types_users ON ID_TYPE = TYPE_USER WHERE NICK_NAME = %s"
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(sql, (user))
        conn.commit()
        user = cur.fetchone()
        cur.close()
        
        if choise == 'change':
            return render_template("profile_change.html", user=user)   
        else:
            return render_template('profile.html', user=user)
    else:
        _names = request.form['names']
        _last_names = request.form['last_names']
        _pass  = request.form['pass'].encode('utf-8')
        _pass_new = request.form['pass_new'].encode('utf-8')
        _pass_conf = request.form['pass_conf'].encode('utf-8')
        
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        sql = "SELECT * FROM work_chat.users WHERE ID_USER = %s"
        cur.execute(sql, (session['id']))
        conn.commit()
        user = cur.fetchone()
        cur.close()

        if (user):
            conn = mysql.connect()
            cur = conn.cursor(pymysql.cursors.DictCursor)

            if _pass != b'':
                if bcrypt.hashpw(_pass, user['PASSWORD_USER'].encode('utf-8')) != user['PASSWORD_USER'].encode('utf-8'):
                    flash('La contraseña ingresada no es correcta!', 'danger')
                    return redirect(url_for('Profile', user=session['username'], choise='change'))
            elif _pass_new != _pass_conf:
                flash('Las contraseñas no coinciden!', 'warning')
                return redirect(url_for('Profile', user=session['username'], choise='change'))
            else:
                if _pass_new != b'':
                    sql = "UPDATE work_chat.users SET NAMES = %s, LAST_NAMES = %s, PASSWORD_USER = %s, PROFILE_COMPLETE = %s  WHERE ID_USER = %s"
                    data = (_names, _last_names, _pass_new, 'YES', session['id'])
                    cur.execute(sql, (data))
                    conn.commit()
                    cur.close()
                    return redirect(url_for('Chats', user=session['username']))
                else: 
                    sql = "UPDATE work_chat.users SET NAMES = %s, LAST_NAMES = %s, PROFILE_COMPLETE = %s  WHERE ID_USER = %s"   
                    data = (_names, _last_names, 'YES',  session['id'])
                    cur.execute(sql, (data))
                    conn.commit()
                    cur.close()
                    return redirect(url_for('Chats', user=session['username']))
        else:
            return redirect(url_for('Logout'))


#Chats
@app.route('/Chats/<string:user>', methods=['GET', 'POST'])
def Chats(user):
    if request.method == 'GET':
        return render_template('chats.html')
    

#Lista de Contactos
@app.route('/Contacts-List')
def ConctactList():
    sql = "SELECT C.ID_USER_CONTACT, U.NICK_NAME FROM work_chat.contacts AS C INNER JOIN work_chat.users AS U ON C.ID_USER_CONTACT = U.ID_USER WHERE C.ID_USER = %s"
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute(sql, (session['id']))
    conn.commit()
    data = cur.fetchall()
    return render_template('list_contact.html', contacts=data)


#Agregar Contacto o Contactos Nuevos
@app.route('/Contacts-New', methods=['GET','POST'])
def ContactsNew():
    if request.method == 'GET':
        sql = "SELECT * FROM work_chat.users AS U WHERE ID_USER NOT IN(SELECT ID_USER_CONTACT FROM work_chat.contacts WHERE ID_USER = %s ORDER BY ID_USER) AND ID_USER <> %s "
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(sql, (session['id'], session['id']))
        conn.commit()
        data = cur.fetchall()
        return render_template('add_contactos.html', contacts=data)
    else:
        conn = mysql.connect()
        cur = conn.cursor(pymysql.cursors.DictCursor)

        _numContacts = len(request.form.getlist('check-contact'))

        for getid in request.form.getlist('check-contact'):
            sql = "INSERT INTO work_chat.contacts(ID_USER,ID_USER_CONTACT) VALUES(%s, %s)"
            id = (getid)
            cur.execute(sql, (session['id'], id))
            conn.commit()
            if _numContacts > 1:
                flash('Usuarios agregados con éxito!', 'success')
            else:
                flash('Usuario agregado con éxito!', 'success')
            
        return redirect('/Contacts-List')

    return 'Agregado'


#Lista los Grupos
@app.route('/Group-List', methods=['GET', 'POST'])
def GroupList():
    if request.method == 'GET':
        sql = "SELECT DISTINCT N.NAME_GROUP, G.ID_GROUPS FROM work_chat.chats_groups AS G INNER JOIN work_chat.chats_names_groups AS N ON G.ID_GROUPS = N.ID_GROUPS WHERE G.ID_USER = %s"
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(sql, (session['id']))
        conn.commit()
        data = cur.fetchall()
        return render_template('list_groups.html', groups=data)
    return 'Agregado'   


#Agrega un nuevo Grupo
@app.route('/Group-New', methods=['GET', 'POST'])
def GroupNew():
    if request.method == 'GET':
        sql = "SELECT * FROM work_chat.users WHERE ID_USER <> %s "
        conn = mysql.connect()
        cur = conn.cursor()
        cur.execute(sql, (session['id']))
        conn.commit()
        data = cur.fetchall()
        return render_template('add_groups.html', contacts=data)
    else:
        conn = mysql.connect()
        cur = conn.cursor()
        getLastGp = "SELECT DISTINCT G.ID_GROUPS FROM work_chat.chats_groups AS G INNER JOIN work_chat.chats_names_groups AS N ON G.ID_GROUPS = N.ID_GROUPS WHERE G.ID_USER = %s ORDER BY G.ID_GROUPS DESC LIMIT 1"
        cur.execute(getLastGp, (session['id']))
        conn.commit()
        cont = cur.fetchone()

        if cont == None :
            id_group = 1
        else:
            id_group = int(''.join(map(str, cont))) + 1

        _nameGroup = request.form['nameGroup']

        for getid in request.form.getlist('check-contact'):
            id_contact = (getid)
            data = (id_group, session['id'], id_contact)
            sqlgp = "INSERT INTO work_chat.chats_groups(ID_GROUPS,ID_USER,ID_USER_CONTACT) VALUES(%s, %s, %s)"
            cur.execute(sqlgp, (data))
            conn.commit()
            
        sqlgpname ="INSERT INTO work_chat.chats_names_groups(ID_GROUPS,NAME_GROUP) VALUES(%s, %s)"
        cur.execute(sqlgpname,(id_group, _nameGroup))
        conn.commit()
        flash('Grupo agregado con éxito!', 'success')
        return redirect('/Group-List')

#Logout
@app.route('/Logout')
def Logout():
    session.clear()
    return redirect(url_for('Login'))