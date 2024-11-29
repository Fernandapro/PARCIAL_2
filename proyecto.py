from flask import Flask, render_template, request, jsonify
import pyodbc
import pandas as pd
from sklearn.linear_model import LinearRegression

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
                "hechos": row[1].split(','),  
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
        bebes = consultar_manual_para_padres_interno()  
        print("Hechos disponibles en la base de datos:", bebes)  # Muestra los hechos disponibles

        conclusiones = encadenamiento_hacia_adelante(hechos, bebes)
        print("Conclusiones generadas:", conclusiones) 

        if conclusiones:
            return jsonify({"conclusiones": list(conclusiones)}), 200
        else:
            return jsonify({"message": "No se encontraron problemas con los hechos ingresados."}), 404

    except Exception as e:
        print("Error al procesar la solicitud:", e)
        return jsonify({"error": "Error interno del servidor."}), 500
    






#anterior
   

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




# Datos de entrenamiento
data = {
    'peso': [14, 16, 18, 20, 22, 24, 26, 11],
    'talla': [64, 66, 68, 70, 72, 74, 76, 58],
    'duracion_fiebre': [1, 1.5, 2, 2.5, 3, 3.5, 4, 1],
    'dosis': [8, 9, 10, 11, 12, 13, 14, 6]
}
df = pd.DataFrame(data)
X = df[['peso', 'talla', 'duracion_fiebre']]
y = df['dosis']

# Inicializar y entrenar el modelo
model = LinearRegression()
model.fit(X, y)





@app.route('/recomendacion_diclo_k', methods=['POST'])
def calcular_dosificacion():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        peso = float(data.get('peso', 0))
        talla = float(data.get('talla', 0))
        duracion_fiebre = float(data.get('duracion_fiebre', 0))

        # Validar entradas
        if not nombre or not (0 < peso < 200 and 30 < talla < 300 and 0 <= duracion_fiebre < 48):
            return jsonify({"error": "Datos inválidos. Verifique los valores ingresados."}), 400

        if duracion_fiebre < 2:
            try:
                dosis = model.predict([[peso, talla, duracion_fiebre]])[0]
                dosis = max(0, dosis)
                mensaje = f"Dosis recomendada: {dosis:.1f} gotas de Diclo-K cada 8 horas por 3 días."
            except Exception as e:
                print("Error al predecir la dosis:", e)
                return jsonify({"error": "No se pudo calcular la dosis. Intente más tarde."}), 500
        else:
            dosis = None
            mensaje = f"La fiebre ha persistido durante {duracion_fiebre} horas. Consulte a un médico para exámenes adicionales."

        # Guardar en base de datos
        try:
            conexion = conectar_db()
            with conexion.cursor() as cursor:
                cursor.execute('''
                    INSERT INTO Dosificaciones (nombre, peso, talla, duracion_fiebre)
                    VALUES (?, ?, ?, ?)
                ''', (nombre, peso, talla, duracion_fiebre))
                conexion.commit()
        finally:
            if conexion:
                conexion.close()

        return jsonify({"message": mensaje, "dosis": dosis}), 200

    except Exception as e:
        print("Error en calcular_dosificacion:", e)
        return jsonify({"error": "Error interno del servidor."}), 500


@app.route('/historial_dosificaciones', methods=['GET'])
def historial_dosificaciones():
    try:
        conexion = conectar_db()
        with conexion.cursor() as cursor:
            cursor.execute('SELECT id, nombre, peso, talla, duracion_fiebre FROM Dosificaciones')
            resultados = cursor.fetchall()

        historial = []
        for row in resultados:
            id_, nombre, peso, talla, duracion_fiebre = row
            if duracion_fiebre < 2:
                try:
                    dosis = model.predict([[peso, talla, duracion_fiebre]])[0]
                    dosis = max(0, dosis)
                except Exception as e:
                    print("Error al predecir la dosis en historial:", e)
                    dosis = None
            else:
                dosis = None

            historial.append({
                "id": id_,
                "nombre": nombre,
                "peso": peso,
                "talla": talla,
                "duracion_fiebre": duracion_fiebre,
                "dosis": dosis
            })

        return jsonify(historial), 200

    except Exception as e:
        print("Error en historial_dosificaciones:", e)
        return jsonify({"error": "Error interno del servidor."}), 500

if __name__ == '__main__':
    app.run(debug=True)
