#Importando  flask y algunos paquetes
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date
from datetime import datetime
from flask import Flask, render_template
from conexionBD import *  #Importando conexion BD
from funciones import *  #Importando mis Funciones
from routes import * #Vistas

import re
from werkzeug.security import generate_password_hash, check_password_hash
#from flask_mail import Mail
from flask_mail import Mail, Message


# Configuración para Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465  # Puerto de tu servidor SMTP (generalmente 587 para TLS, 465 para SSL)
#app.config['MAIL_USE_TLS'] = True  # Cambia a False si estás usando SSL
app.config['MAIL_USE_SSL'] = True  # Cambia a True si estás usando SSL
app.config['MAIL_USERNAME'] = 'pruebaflasksistemas@gmail.com'  # correo de envio de mensaje
app.config['MAIL_PASSWORD'] = 'mzpj ouxh hmgv bvxt'  # contraseña generada para aplicaciones de terceros

mail = Mail(app)

@app.route('/dashboard', methods=['GET', 'POST'])
def loginUser():
    conexion_MySQLdb = connectionBD()
    if 'conectado' in session:
        return render_template('public/dashboard/home.html', dataLogin = dataLoginSesion())
    else:
        msg = ''
        if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
            email      = str(request.form['email'])
            password   = str(request.form['password'])
            
            # Comprobando si existe una cuenta
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM login_python WHERE email = %s", [email])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['password'],password):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas 
                    session['conectado']        = True
                    session['id']               = account['id']
                    session['tipo_user']        = account['tipo_user']
                    session['nombre']           = account['nombre']
                    session['apellido']         = account['apellido']
                    session['email']            = account['email']
                    session['sexo']             = account['sexo']
                    #session['pais']             = account['pais']
                    session['create_at']        = account['create_at']
                    session['te_gusta_la_programacion']     = account['te_gusta_la_programacion']

                    msg = "Ha iniciado sesión correctamente."
                    return render_template('public/dashboard/home.html', msjAlert = msg, typeAlert=1, dataLogin = dataLoginSesion())                    
                else:
                    msg = 'Datos incorrectos, por favor verfique!'
                    return render_template('public/modulo_login/index.html', msjAlert = msg, typeAlert=0)
            else:
                return render_template('public/modulo_login/index.html', msjAlert = msg, typeAlert=0)
    return render_template('public/modulo_login/index.html', msjAlert = 'Debe iniciar sesión.', typeAlert=0)


# Registrando una cuenta de Usuario
@app.route('/registro-usuario', methods=['GET', 'POST'])
def registerUser():
    msg = ''
    conexion_MySQLdb = connectionBD()
    if request.method == 'POST':
        tipo_user = 2
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        password = request.form['password']
        repite_password = request.form['repite_password']
        sexo = request.form['sexo']
        create_at = date.today()

        cursor = conexion_MySQLdb.cursor(dictionary=True)
        cursor.execute('SELECT * FROM login_python WHERE email = %s', (email,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            msg = 'Ya existe el Email!'
        elif password != repite_password:
            msg = 'Disculpa, las claves no coinciden!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Disculpa, formato de Email incorrecto!'
        elif not email or not password or not repite_password:
            msg = 'El formulario no debe estar vacío!'
        else:
            password_encriptada = generate_password_hash(password, method='pbkdf2:sha256')
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute('INSERT INTO login_python (tipo_user, nombre, apellido, email, password, sexo, create_at) VALUES (%s, %s, %s, %s, %s, %s, %s)', (tipo_user, nombre, apellido, email, password_encriptada, sexo, create_at))
            conexion_MySQLdb.commit()
            cursor.close()
            msg = 'Cuenta creada correctamente!'
            
            # Enviar correo electrónico de bienvenida
            send_welcome_email(email)

        return render_template('public/modulo_login/index.html', msjAlert=msg, typeAlert=1)
    return render_template('public/layout.html', dataLogin=dataLoginSesion(), msjAlert=msg, typeAlert=0)
    # Función para enviar correo de bienvenida
def send_welcome_email(email):
    subject = "Bienvenido a Pizzeria Merlin"
    sender = app.config.get("MAIL_USERNAME")
    msg = Message(subject, sender=sender, recipients=[email])

    # Cuerpo del correo con HTML que incluye una etiqueta de imagen
    msg.html = (
        f"""
    ¡Hola!

    ¡Bienvenido a Pizzeria Merlin, tu destino para las mejores pizzas deliciosas! Estamos emocionados de tenerte como parte de nuestra comunidad.

    En Pizzeria Merlin, nos dedicamos a brindarte una experiencia gastronómica excepcional. Cada pizza que preparamos está hecha con los ingredientes más frescos y con un toque de amor.

    Explora nuestro menú variado y descubre una amplia gama de sabores que satisfarán tu paladar. Como miembro registrado, disfrutarás de ofertas exclusivas y sorpresas especiales.

    ¿Alguna vez has probado una pizza que despierte tus sentidos? ¡En Pizzeria Merlin, eso es lo que encontrarás!

    Gracias por elegirnos. Siempre estamos aquí para hacer tu experiencia con nosotros memorable. Si tienes alguna pregunta o comentario, no dudes en contactarnos.

    ¡Bienvenido a la familia Merlin!

    Saludos,
    El equipo de Pizzeria Merlin
    """
        
    )

    # Adjunta la imagen al correo
    with app.open_resource("static/assets/imgs/logo.png") as img:
        msg.attach("merlin.jpg", "image/jpg", img.read(), "inline")

    mail.send(msg)
     
@app.route('/actualizar-mi-perfil/<id>', methods=['POST'])
def actualizarMiPerfil(id):
    if 'conectado' in session:
        msg = ''
        if request.method == 'POST':
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            email = request.form['email']
            sexo = request.form['sexo']

            if request.form['password']:
                password = request.form['password']
                repite_password = request.form['repite_password']

                if password != repite_password:
                    msg = 'Las claves no coinciden'
                    return render_template('public/dashboard/home.html', msjAlert=msg, typeAlert=0, dataLogin=dataLoginSesion())
                else:
                    nueva_password = generate_password_hash(password, method='sha256')
                    conexion_MySQLdb = connectionBD()
                    cur = conexion_MySQLdb.cursor()
                    cur.execute("""
                        UPDATE login_python 
                        SET 
                            nombre = %s, 
                            apellido = %s, 
                            email = %s, 
                            sexo = %s, 
                            password = %s
                        WHERE id = %s""", (nombre, apellido, email, sexo, nueva_password, id))
                    conexion_MySQLdb.commit()
                    cur.close()
                    conexion_MySQLdb.close()
                    msg = 'Perfil actualizado correctamente'
                    return render_template('public/dashboard/home.html', msjAlert=msg, typeAlert=1, dataLogin=dataLoginSesion())
            else:
                msg = 'Perfil actualizado con éxito'
                conexion_MySQLdb = connectionBD()
                cur = conexion_MySQLdb.cursor()
                cur.execute("""
                    UPDATE login_python 
                    SET 
                        nombre = %s, 
                        apellido = %s, 
                        email = %s, 
                        sexo = %s
                    WHERE id = %s""", (nombre, apellido, email, sexo, id))
                conexion_MySQLdb.commit()
                cur.close()
                return render_template('public/dashboard/home.html', msjAlert=msg, typeAlert=1, dataLogin=dataLoginSesion())
        return render_template('public/dashboard/home.html', dataLogin=dataLoginSesion())
        
from flask import request, redirect, url_for, session

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Obtener el producto según su ID desde la lista de productos
    product = next((p for p in products if p['id'] == product_id), None)

    # Inicializar el carrito en la sesión si aún no existe
    if 'cart' not in session:
        session['cart'] = []

    # Agregar el producto al carrito
    session['cart'].append({'id': product['id'], 'name': product['name'], 'price': product['price']})

    return redirect(url_for('catalog'))

if __name__ == "__main__":
    app.run(debug=True, port=8000)
    
#pruebaflasksistemas@gmail.com CONTRSEÑA:PRUEBA.1234