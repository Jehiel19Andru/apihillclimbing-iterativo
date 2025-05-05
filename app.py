import math
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# Base de ciudades
coord_original = {
    'Jiloyork': (19.916012, -99.580580), 'Toluca': (19.289165, -99.655697),
    'Atlacomulco': (19.799520, -99.873844), 'Guadalajara': (20.677754, -103.346253),
    'Monterrey': (25.691611, -100.321838), 'QuintanaRoo': (21.163111, -86.802315),
    'Michoacan': (19.701400, -101.208296), 'Aguascalientes': (21.876410, -102.264386),
    'CDMX': (19.432713, -99.133183), 'QRO': (20.597194, -100.386670)
}
coord_created = {}

# Funciones de distancia y optimización
def distancia(coord1, coord2):
    # Coordenadas en radianes
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    # Diferencias
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radio de la Tierra en kilómetros
    R = 6371.0
    return R * c

def evalua_ruta(ruta):
    coord = {**coord_original, **coord_created}
    return sum(distancia(coord[ruta[i]], coord[ruta[i+1]]) for i in range(len(ruta)-1))

def hill_climbing(ciudades):
    random.shuffle(ciudades)
    mejor_ruta = ciudades[:]
    for _ in range(1000):
        i, j = random.sample(range(len(ciudades)), 2)
        nueva_ruta = mejor_ruta[:]
        nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]
        if evalua_ruta(nueva_ruta) < evalua_ruta(mejor_ruta):
            mejor_ruta = nueva_ruta
    return mejor_ruta, evalua_ruta(mejor_ruta)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/generate_route', methods=['POST'])
def generate_route():
    coord = {**coord_original, **coord_created}
    ruta_optima, distancia_total = hill_climbing(list(coord.keys()))
    return jsonify({"ruta": ruta_optima, "distancia": round(distancia_total, 2), "coordenadas": coord})

@app.route('/cities', methods=['GET'])
def get_cities():
    return jsonify({"cities": list(coord_original.keys())})

@app.route('/created_cities', methods=['GET'])
def get_created_cities():
    return jsonify({"cities": list(coord_created.keys())})

@app.route('/get_city_data/<name>', methods=['GET'])
def get_city_data(name):
    if name in coord_original:
        lat, lon = coord_original[name]
    elif name in coord_created:
        lat, lon = coord_created[name]
    else:
        return jsonify({"error": "Ciudad no encontrada."}), 404
    return jsonify({"lat": lat, "lon": lon})

@app.route('/add_city', methods=['POST'])
def add_city():
    data = request.json
    name = data.get("name")
    lat = data.get("lat")
    lon = data.get("lon")

    if not name or not lat or not lon:
        return jsonify({"error": "Nombre, latitud y longitud son obligatorios."}), 400

    coord_created[name] = (float(lat), float(lon))
    return jsonify({"message": f"Ciudad '{name}' agregada correctamente.", "cities": list(coord_created.keys())})

@app.route('/edit_city', methods=['POST'])
def edit_city():
    data = request.json
    name = data.get("name")
    lat = data.get("lat")
    lon = data.get("lon")

    if name in coord_created:
        coord_created[name] = (float(lat), float(lon))
        return jsonify({"message": f"Ciudad '{name}' actualizada correctamente."})
    return jsonify({"error": "Ciudad no encontrada."}), 404

@app.route('/delete_city', methods=['DELETE'])
def delete_city():
    data = request.json
    name = data.get("name")

    if name in coord_created:
        del coord_created[name]
        return jsonify({"message": f"Ciudad '{name}' eliminada correctamente.", "cities": list(coord_created.keys())})
    return jsonify({"error": "Ciudad no encontrada."}), 404

if __name__ == '__main__':
    app.run(debug=True)
