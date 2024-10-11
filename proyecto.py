from flask import Flask, render_template, request, jsonify
import pyodbc

app = Flask(__name__)

def conectar_db():
    try:
        conexion = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=DESKTOP-CSHKECE\\SQLEXPRESS;'
            'DATABASE=PROYECTO SIS EXPERTOS;'
            'UID=sa;'
            'PWD=Quinilla57.;'
        )
        print("La conexión a la base de datos fue exitosa.")
        return conexion
    except pyodbc.Error as e:
        print("ERROR al conectar con la base de datos:", e)
        return None




@app.route('/')
def index():
    return render_template('interfaz.html')


class hechos:
    def __init__(self, hechos, conclusion, id=None):
        self.hechos = hechos
        self.conclusion = conclusion
        self.id = id
        
@app.route('/insertar_hechos', methods=['POST'])
def insertar_hechos():
    data = request.get_json()
    hechos = ','.join(data['hechos'])
    conclusion = data['conclusion']

    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO bebes (hechos, conclusion) VALUES (?, ?)
        ''', (hechos, conclusion))
        conexion.commit()
        conexion.close()
        return jsonify({"message": f"hechos '{conclusion}' insertada correctamente."})
    return jsonify({"message": "Error al insertar la hechos."})

@app.route('/eliminar_hechos', methods=['POST'])
def eliminar_hechos():
    data = request.get_json()
    hechos_id = data.get('id')

    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute('DELETE FROM bebes WHERE id = ?', (hechos_id,))
        conexion.commit()
        conexion.close()
        return jsonify({"message": f"hechos con ID {hechos_id} eliminada correctamente."})
    return jsonify({"message": "Error al eliminar la hechos."})


@app.route('/consultar_manual_para_padres', methods=['GET'])
def consultar_manual_para_padres_interno():
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute('SELECT id, hechos, conclusion FROM bebes')
        bebes = []
        for row in cursor.fetchall():
            bebes.append({
                "id": row[0],
                "hechos": row[1].split(','),  #   hechos se manejen como una lista
                "conclusion": row[2]
            })
        conexion.close()
        return bebes
    return []  # Devuelve una lista vacía si hay un error en la conexión


@app.route('/consultar', methods=['POST'])
def consultar():
    try:
        data = request.get_json()
        print("Datos recibidos en /consultar:", data)  # Muestra los datos recibidos en la consola
        
        if 'hechos' not in data:
            return jsonify({"error": "Faltan hechos en la solicitud."}), 400

        hechos = set(data['hechos'])
        print("Hechos procesados:", hechos)  # Muestra los hechos procesados
        bebes = consultar_manual_para_padres_interno()  # Usa la versión que devuelve una lista
        print("Hechos disponibles en la base de datos:", bebes)  # Muestra los hechos disponibles

        conclusiones = encadenamiento_hacia_adelante(hechos, bebes)
        print("Conclusiones generadas:", conclusiones)  # Muestra las conclusiones generadas

        if conclusiones:
            return jsonify({"conclusiones": list(conclusiones)}), 200
        else:
            return jsonify({"message": "No se encontraron problemas con los hechos ingresados."}), 404

    except Exception as e:
        print("Error al procesar la solicitud:", e)
        return jsonify({"error": "Error interno del servidor."}), 500
    
   

def encadenamiento_hacia_adelante(hechos, bebes):

# Agregar logging para depuración
    print("Hechos disponibles en la base de datos:", bebes)
    print("Hechos procesados:", hechos)


    conclusiones = set()
    nuevo_hecho_agregado = True

    while nuevo_hecho_agregado:
        nuevo_hecho_agregado = False

        for bebe in bebes:
            # Limpiar y normalizar los hechos antes de la comparación
            hechos_bebe = set(hecho.strip() for hecho in bebe['hechos'])
            if hechos_bebe.issubset(hechos) and bebe['conclusion'] not in conclusiones:
                conclusiones.add(bebe['conclusion'])
                hechos.update(hechos_bebe)  # Actualiza los hechos conocidos
                nuevo_hecho_agregado = True

    return conclusiones

def obtener_hechos():
    hechos = set()
    while True:
        hecho = input("Ingrese un hecho (o 'consultar' para obtener el diagnóstico): ").strip()
        if hecho.lower() == 'consultar':
            break
        if hecho:
            hechos.add(hecho)
    return hechos

def mostrar_menu():
    print("\nMenú:")
    print("1. Añadir hechos")
    print("2. Eliminar hechos por ID")
    print("3. Consultar la salud del bebe")
    print("4. Actualizar base de datos")
    print("5. Salir")

def registrar_log(action, details):
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute('''
            INSERT INTO Logs (action, details) VALUES (?, ?)
        ''', (action, details))
        conexion.commit()
        conexion.close()
        print("Registro de log insertado correctamente.")
    else:
        print("No se pudo registrar el log. Conexión fallida.")

def main():
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == '1':
            hechos = input("Ingrese las hechos separadas por comas: ").split(',')
            conclusion = input("Ingrese la conclusión: ").strip()
            insertar_hechos([c.strip() for c in hechos], conclusion)

        elif opcion == '2':
            hechos_id = int(input("Ingrese el ID de la hechos a eliminar: ").strip())
            eliminar_hechos(hechos_id)

        elif opcion == '3':
            bebes = consultar_manual_para_padres_interno()
            hechos = obtener_hechos()
            conclusiones = encadenamiento_hacia_adelante(hechos, bebes)

            if conclusiones:
                print("Posibles problemas del automóvil:")
                for conclusion in conclusiones:
                    print(conclusion)
            else:
                print("No se encontraron problemas con los hechos ingresados.")

        elif opcion == '4':
            print("Updating database... (Make sure to insert rules in the database )")
            registrar_log("Updating the data base", "The data base was updated.")

        elif opcion == '5':
            print("Leaving...")
            registrar_log("Salir", "El usuario ha salido del programa.")
            break
        
        else:
            print("Opción inválida.Please try again.")

if __name__ == '__main__':
    app.run(debug=True)






















