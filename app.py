from flask import Flask, render_template, request, redirect, url_for,  send_from_directory

import sqlite3

import os

app = Flask(__name__)
app.config['DEBUG'] = False




def db():
    conexion = sqlite3.connect('SYSTEMDATABASECRUD.db') #la base de datos se crea automaticamente y se crea la conexion
    cursor = conexion.cursor() #para leer se inicializa un cursor
    with open('dbshema.sql', 'r') as archivo_sql: #se abre el archivo y se le realiza un lectura 'read'
        cursor.executescript(archivo_sql.read())
    conexion.commit() #asegura que los cambios se guardaron
    conexion.close() #se cierra la conexion
    return


def accion_consulta_db(nombre_db, accion, parametros=()):
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    cursor.execute(accion, parametros)
    respuesta = cursor.fetchall()
    conexion.close()
    return respuesta

def accion_modificar_db(nombre_db, accion, parametros=()):
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    cursor.execute(accion, parametros)
    conexion.commit()
    conexion.close()
    return 




@app.route("/clientes")
def clientes():
    #db() #esto una vez lo tengo que hacer, lo hago en el index, 
    clientes = accion_consulta_db('SYSTEMDATABASECRUD.db', 'SELECT * FROM cliente')
    print(clientes)
    return render_template('clientes.html', clientes=clientes)


@app.route("/")
def func():
    return redirect(url_for('clientes'))


@app.route("/agregar", methods=['POST', 'GET']) #actua como api
def agregar():
    #db()
    dni = request.form['dni']
    nombre = request.form['nombre']
    apellido = request.form['apellido']
    mail = request.form['mail']
    foto = request.files['foto']
    if foto and foto.filename != '':
        foto_path = os.path.join(app.config['CARPETA'], foto.filename)
        foto.save(foto_path)
        nombre_foto = foto.filename
    else:
        nombre_foto = ''
    accion_modificar_db('SYSTEMDATABASECRUD.db', 'INSERT INTO cliente (dni, nombre, apellido, mail, foto) VALUES (?, ?, ?, ?, ?)', (dni, nombre, apellido, mail, nombre_foto))
    
    return redirect(url_for('clientes'))

@app.route("/agregarcliente")
def agregarcliente():
    return render_template('agregarcliente.html')

    
@app.route("/perfilcliente/<int:dni>")
def perfilcliente(dni):
    cliente = accion_consulta_db('SYSTEMDATABASECRUD.db', 'SELECT * FROM cliente WHERE dni == ?', (str(dni), )) #es un tupla de un solo dato (dato, )
    print(cliente)
    return render_template('perfilcliente.html', cliente=cliente)


@app.route("/modificarcliente/<int:dni>")
def modificarcliente(dni):
    cliente = accion_consulta_db('SYSTEMDATABASECRUD.db', 'SELECT * FROM cliente WHERE dni == ?', (str(dni), )) #es un tupla de un solo dato (dato, )
    return render_template('modificarcliente.html', cliente=cliente)


def eliminarFotoDelServer(nombre_db, consultaFoto, parametros=()):
    conexion = sqlite3.connect(nombre_db)
    cursor = conexion.cursor()
    cursor.execute(consultaFoto, parametros)
    fotoEliminada = cursor.fetchone()
    os.remove(os.path.join(app.config['CARPETA'], fotoEliminada[0]))
    return fotoEliminada

@app.route("/modificar", methods=['POST', 'GET'])
def modificar():
    nuevoNombre = request.form['nombre']
    nuevoApellido = request.form['apellido']
    nuevoMail = request.form['mail']
    dni = request.form['dni']
    fotoNueva = request.files['foto']
    nombre_nuevaFoto = fotoNueva.filename

    fotoEliminar = accion_consulta_db('SYSTEMDATABASECRUD.db', 'SELECT foto FROM cliente WHERE dni = ?', (str(dni), ))
    
    print(fotoNueva.filename, fotoEliminar)

    if fotoNueva.filename != '':
        fotoNueva.save(os.path.join('uploads/' + fotoNueva.filename))
        fotoEliminar = eliminarFotoDelServer('SYSTEMDATABASECRUD.db', 'SELECT foto FROM cliente WHERE dni = ?', (str(dni), ))
        accion_modificar_db('SYSTEMDATABASECRUD.db', 'UPDATE cliente SET nombre = ?, apellido = ?, mail = ?, foto = ? WHERE dni = ?', (nuevoNombre, nuevoApellido, nuevoMail, nombre_nuevaFoto, dni) )
    else:
        accion_modificar_db('SYSTEMDATABASECRUD.db', 'UPDATE cliente SET nombre = ?, apellido = ?, mail = ? WHERE dni = ?', (nuevoNombre, nuevoApellido, nuevoMail, dni) )


    return redirect(url_for('clientes'))


@app.route("/eliminar/<int:dni>")
def eliminar(dni):
    eliminarFotoDelServer('SYSTEMDATABASECRUD.db', 'SELECT foto FROM cliente WHERE dni = ?', (str(dni), ))
    accion_modificar_db('SYSTEMDATABASECRUD.db', 'DELETE FROM cliente WHERE dni = ?', (str(dni), ))
    return redirect(url_for('clientes'))



#MANEJO DE IMAGENES
#poder eliminar la foto del servidor
CARPETA = os.path.join('uploads')
app.config['CARPETA']=CARPETA #Hago referencia a la carpeta de uploads

#para ver la imagen
@app.route("/uploads/<nombreFoto>")
def uploads(nombreFoto):
    # le digo en que carpeta y lo que le pase por parametro que es el nombre de la foto
    return send_from_directory(app.config['CARPETA'], nombreFoto)


if __name__ == '__main__':
    app.run()



