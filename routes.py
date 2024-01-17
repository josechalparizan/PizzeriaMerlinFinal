from flask import Flask, render_template, redirect, url_for, session
from funciones import *  #Importando mis Funciones
from flask import request, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#Declarando nombre de la aplicación e inicializando, crear la aplicación Flask
app = Flask(__name__)
application = app

app.secret_key = '97110c78ae51a45af397be6534caef90ebb9b1dcb3380af008f90b23a5d1616bf19bc29098105da20fe'

#Redireccionando cuando la página no existe
@app.errorhandler(404)
def not_found(error):
    if 'conectado' in session:
        return render_template('public/dashboard/home.html', dataLogin = dataLoginSesion(),error404=True)
    else:
        return render_template('public/modulo_login/index.html')
    
   
#Creando mi Decorador para el Home
@app.route('/')
def inicio():
    if 'conectado' in session:
        return render_template('public/dashboard/home.html', dataLogin = dataLoginSesion())
    else:
        return render_template('public/modulo_login/index.html')
    
    
@app.route('/login')
def login():
    if 'conectado' in session:
        return render_template('public/dashboard/home.html', dataLogin = dataLoginSesion())
    else:
        return render_template('public/modulo_login/index.html')

@app.route('/catalogo')
def catalogo():
    if 'conectado' in session:
        return render_template('public/modulo_compras/index_compras.html', dataLogin = dataLoginSesion())
    else:
        return render_template('public/modulo_login/index.html')

@app.route('/carrito')
def carrito():
    if 'conectado' in session:
        return render_template('public/modulo_carrito/index_carrito.html', dataLogin = dataLoginSesion())
    else:
        return render_template('public/modulo_login/index.html')

# Datos de las bebidas
bebidas_data = [
    {"nombre": "MALTEADA", "precio": 10000},
    {"nombre": "LIMONADA NATURAL", "precio": 4500},
    {"nombre": "MALTEADA", "precio": 10000},
    {"nombre": "LIMONADA NATURAL", "precio": 4500},
    {"nombre": "MALTEADA", "precio": 10000},
    {"nombre": "LIMONADA NATURAL", "precio": 4500},
    {"nombre": "MALTEADA", "precio": 10000},
    {"nombre": "LIMONADA NATURAL", "precio": 4500},
    {"nombre": "MALTEADA", "precio": 10000},
    {"nombre": "LIMONADA NATURAL", "precio": 4500},
    # ... Agrega el resto de las bebidas con sus datos
]

# Configuración de paginación
ITEMS_PER_PAGE = 4

@app.route('/nosotros')
def nosotros():
    if 'conectado' in session:
        page = request.args.get('page', 1, type=int)
        start_idx = (page - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        bebidas_subset = bebidas_data[start_idx:end_idx]
        return render_template('public/acercade/index_acercade.html', dataLogin=dataLoginSesion(), bebidas=bebidas_subset, page=page, ITEMS_PER_PAGE=ITEMS_PER_PAGE)
    else:
        return render_template('public/modulo_login/index.html')

#Ruta para editar el perfil del cliente
@app.route('/edit-profile', methods=['GET', 'POST'])
def editProfile():
    if 'conectado' in session:
        return render_template('public/dashboard/pages/Profile.html', dataUser = dataPerfilUsuario(), dataLogin = dataLoginSesion())
    return redirect(url_for('inicio'))

    
# Cerrar session del usuario
@app.route('/logout')
def logout():
    msgClose = ''
    # Eliminar datos de sesión, esto cerrará la sesión del usuario
    session.pop('conectado', None)
    session.pop('id', None)
    session.pop('email', None)
    msgClose ="La sesión fue cerrada correctamente"
    return render_template('public/modulo_login/index.html', msjAlert = msgClose, typeAlert=1)


