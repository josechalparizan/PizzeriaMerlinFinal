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
from flask_mail import Mail
from flask_mail import Mail, Message
from flask import jsonify

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
        # te_gusta_la_programacion = request.form['te_gusta_la_programacion']
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
     
from flask import render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash


@app.route('/actualizar-mi-perfil/<id>', methods=['POST'])
def actualizarMiPerfil(id):
    if 'conectado' in session:
        try:
            if request.method == 'POST':
                nombre = request.form['nombre']
                apellido = request.form['apellido']
                email = request.form['email']
                sexo = request.form['sexo']

                if 'password' in request.form:
                    password = request.form['password']
                    repite_password = request.form['repite_password']

                    if password != repite_password:
                        flash('Las claves no coinciden', 'error')
                        return redirect(url_for('home'))

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
                    flash('Perfil actualizado correctamente', 'success')
                    return redirect(url_for('home'))
                else:
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
                    conexion_MySQLdb.close()
                    flash('Perfil actualizado con éxito', 'success')
                    return redirect(url_for('home'))

        except Exception as e:
            flash(f'Error al actualizar el perfil: {str(e)}', 'error')
            return redirect(url_for('home'))

        return render_template('public/dashboard/home.html', dataLogin=dataLoginSesion())
      
from flask import request, redirect, url_for, session

# Lista para almacenar productos en el carrito (puedes reemplazar esto con una base de datos)
carrito_de_compras = []

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    if 'conectado' in session:
        product_id = request.form.get('product_id')
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price')

        # Puedes almacenar la información del producto en la sesión o en una base de datos
        # Por ahora, almacenaremos la información en la sesión como un ejemplo
        if 'cart' not in session:
            session['cart'] = []

        session['cart'].append({
            'id': product_id,
            'name': product_name,
            'price': product_price
        })

        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Usuario no conectado'})


# Ruta para manejar solicitudes de agregar al carrito
@app.route('/agregar-al-carrito', methods=['POST'])
def agregar_al_carrito():
    if 'carrito' not in session:
        session['carrito'] = []

    # Verifica si la solicitud tiene datos JSON
    if request.is_json:
        # Obtén la información del producto desde la solicitud
        producto = request.json
        id = producto['id']
        nombre = producto['nombre']
        precio = producto['precio']

        # Agrega el producto al carrito en la sesión
        session['carrito'].append({'id': id, 'nombre': nombre, 'precio': precio})

        return jsonify({'mensaje': 'Producto agregado al carrito'})
    else:
        return jsonify({'error': 'El contenido de la solicitud debe estar en formato JSON'}), 415

# Ruta para manejar solicitudes de eliminar del carrito
@app.route('/eliminar-del-carrito', methods=['POST'])
def eliminar_del_carrito():
    if 'carrito' in session:
        producto = request.json
        id = producto['id']
        nombre = producto['nombre']
        precio = producto['precio']

        # Buscar y eliminar el producto del carrito en la sesión
        for item in session['carrito']:
            if item['id'] == id and item['nombre'] == nombre and item['precio'] == precio:
                session['carrito'].remove(item)
                break

        return jsonify({'mensaje': 'Producto eliminado del carrito'})
    else:
        return jsonify({'error': 'El carrito está vacío'}), 400

if __name__ == "__main__":
    app.run(debug=True, port=8000)
    
#pruebaflasksistemas@gmail.com CONTRSEÑA:PRUEBA.1234
