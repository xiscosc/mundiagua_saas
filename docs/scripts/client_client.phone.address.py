#!/usr/bin/python

import MySQLdb

password = raw_input('Enter the MYSQL password:')
# Open database connection
db = MySQLdb.connect("localhost", "root", password, "mundiagua_in")
# Open database connection
db2 = MySQLdb.connect("localhost", "root", password, "mundiagua_py")

cursor = db.cursor()
cursor2 = db2.cursor()

select_client_sql = "select c_id, c_nombre, c_email, c_cod, c_dni from mundiagua_in.cliente"
select_phone_sql = "select t_id, t_alias, t_telefono, t_c_id from mundiagua_in.telefono_cliente"
select_address_sql = "select d_id, d_direccion, d_c_id, d_alias, d_latitud, d_longitud, d_z_id from mundiagua_in.direccion_cliente"

add_client_sql = ("INSERT INTO mundiagua_py.client_client "
                  "(id, name, email, intern_code, dni) "
                  "VALUES (%(id)s, %(name)s, %(email)s, %(intern_code)s, %(dni)s)")

add_phone_sql = ("INSERT INTO mundiagua_py.client_phone "
                 "(id, alias, phone, client_id) "
                 "VALUES (%(id)s, %(alias)s, %(phone)s, %(client_id)s")

add_address_sql = ("INSERT INTO mundiagua_py.client_phone "
                 "(id, alias, address, latitude, longitude, client_id, default_zone_id) "
                 "VALUES (%(id)s, %(alias)s, %(address)s, %(latitude)s, %(longitude)s, %(client_id)s, %(default_zone_id)s")

cursor.execute(select_client_sql)

for (c_id, c_nombre, c_email, c_cod, c_dni) in cursor:
    data_client = {
        'id': c_id,
        'name': c_nombre,
        'email': c_email,
        'intern_code': c_cod,
        'dni': c_dni
    }
    cursor2.execute(add_client_sql, data_client)
    db2.commit()

cursor.execute(select_phone_sql)

for (t_id, t_alias, t_telefono, t_c_id) in cursor:
    data_phone = {'id': t_id,
                  'alias': t_alias,
                  'phone': t_telefono,
                  'client_id': t_c_id
                  }
    cursor2.execute(add_phone_sql, data_phone)
    db2.commit()

cursor.execute(select_address_sql)

for (d_id, d_direccion, d_c_id, d_alias, d_latitud, d_longitud, d_z_id) in cursor:
    data_address = {
        'id': d_id,
        'alias': d_alias,
        'address': d_direccion,
        'latitude': d_latitud,
        'longitude': d_longitud,
        "client_id": d_c_id,
        "default_zone_id": d_z_id
    }
    cursor2.execute(add_address_sql, data_address)
    db2.commit()

cursor.close()
cursor2.close()
db.close()
db2.close()
