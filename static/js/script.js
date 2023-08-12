const minLon = -79.212197;
const maxLon = -79.192965;
const minLat = -4.043386;
const maxLat = -4.028344;

const extent = ol.proj.transformExtent([minLon, minLat, maxLon, maxLat], 'EPSG:4326', 'EPSG:3857');

const map = new ol.Map({
    target: 'map',
    layers: [
        new ol.layer.Tile({
            source: new ol.source.OSM({
                url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                attributions: ''
            }),
            visible: true
        })
    ],
    controls: [],
    view: new ol.View({
        center: ol.extent.getCenter(extent),
        extent: extent,
        zoom: 15
    })
});

function agregarMarcadorEnMapa(latitud, longitud, nombre, descripcion) {
    const coordenadas = ol.proj.fromLonLat([longitud, latitud]);

    // Crear un marcador en la posición especificada
    const marcador = new ol.Feature({
        geometry: new ol.geom.Point(coordenadas)
    });

    // Agregar el nombre y la descripción del marcador como propiedades
    marcador.set('nombre', nombre);
    marcador.set('descripcion', descripcion);
    marcador.set('coordenadas', coordenadas);

    // Estilo del marcador
    marcador.setStyle(new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({ color: 'red' }),
            stroke: new ol.style.Stroke({ color: 'white', width: 2 })
        }),
        text: new ol.style.Text({
            text: nombre,
            font: '12px Arial',
            fill: new ol.style.Fill({ color: 'black' }),
            offsetY: -15,
            textAlign: 'center',
            textBaseline: 'middle'
        })
    }));

    // Añadir el marcador a una capa de marcadores
    const capaMarcadores = new ol.layer.Vector({
        source: new ol.source.Vector({
            features: [marcador]
        })
    });

    // Añadir la capa de marcadores al mapa
    map.addLayer(capaMarcadores);
}

function mostrarPuntos(puntos) {
    // Eliminar la capa de marcadores existente antes de agregar nuevos marcadores
    map.getLayers().forEach(function (layer) {
        if (layer instanceof ol.layer.Vector) {
            map.removeLayer(layer);
        }
    });

    for (const puntoKey in puntos) {
        if (puntos.hasOwnProperty(puntoKey)) {
            const punto = puntos[puntoKey];
            const latitud = punto.latitud;
            const longitud = punto.longitud;
            const codigo = punto.codigo;
            const descripcion = punto.descripcion;

            const palabra = "A";

            if (codigo.includes(palabra)) {
                agregarMarcadorEnMapa(latitud, longitud, codigo, descripcion);
            }
        }
    }
}


map.on('singleclick', function (evt) {
    var feature = map.forEachFeatureAtPixel(evt.pixel, function (feature) {
        return feature;
    });

    if (feature) {
        const nombreMarcador = feature.get('nombre');
        const descripcionMarcador = feature.get('descripcion');
        const coordenadas = feature.get('coordenadas');
        console.log(nombreMarcador, descripcionMarcador, coordenadas);

        const infoContent = document.getElementById('info-content');
        const contenido = `<p><strong>${nombreMarcador}</strong></p><p>${descripcionMarcador}</p>`;

        // Actualizar el contenido del recuadro con la información del marcador
        infoContent.innerHTML = contenido;

        // Mostrar el recuadro
        infoContent.style.display = 'block';
    } else {
        console.log("No hay un marcador en esta ubicación.");

        const infoContent = document.getElementById('info-content');

        // Ocultar el recuadro si no hay marcador
        infoContent.style.display = 'none';
    }
});

function buscarMarcador() {
    const buscado = document.getElementById('search-input').value.toLowerCase();

    let encontrado = false;

    for (const puntoKey in puntos) {
        if (puntos.hasOwnProperty(puntoKey)) {
            const punto = puntos[puntoKey];
            const nombre = punto.codigo.toLowerCase();
            const descripcion = punto.descripcion.toLowerCase();

            if (nombre.includes(buscado) || descripcion.includes(buscado)) {
                hacerZoomAMarcador(punto.latitud, punto.longitud, 20);
                encontrado = true;
                break;
            }
        }
    }

    if (!encontrado) {
        console.log("no");
    }
}



function hacerZoomAMarcador(latitud, longitud, zoomLevel) {
    const view = map.getView();
    const center = ol.proj.fromLonLat([longitud, latitud]);
    view.animate({
        center: center,
        zoom: zoomLevel,
        duration: 1000 // Duración de la animación en milisegundos
    });
}


//----------------------------------------------
// Obtener el formulario y el logo por su ID
const formulario = document.getElementById('search-form');
const logo = document.getElementById('logo');

// Agregar un escuchador de eventos para el evento 'click' en el logo
logo.addEventListener('click', function() {
  // Mostrar el formulario y ocultar el logo
  formulario.style.display = 'block';
  logo.style.display = 'none';
});


//----------------------------------------------------------------------
function crearGrafo(puntos) {
    const grafo = {};

    if (puntos && Array.isArray(puntos)) {
        puntos.forEach((punto) => {
            if (punto && punto.codigo && punto.conexiones_salientes) {
                const conexionesConDistancia = punto.conexiones_salientes.map((conexion) => ({
                    nodoDestino: conexion,
                    distancia: calcularDistancia(punto, conexion) // Aquí debes implementar la función calcularDistancia()
                }));

                // Agregar la latitud y longitud del nodo de origen al objeto
                const nodoConCoordenadas = {
                    codigo: punto.codigo,
                    latitud: punto.latitud,
                    longitud: punto.longitud,
                    conexiones: conexionesConDistancia,
                };

                grafo[punto.codigo] = nodoConCoordenadas;
            } else {
                console.log(`El objeto punto con código ${punto.codigo} o conexiones_salientes no existe o es undefined.`);
            }
        });

        console.log("Grafo con distancias y coordenadas creado:");
        const inicio = document.getElementById('origen').value;
        const fin = document.getElementById('destino').value;
        const resultado = calcularCaminoMasCorto(grafo, inicio, fin);

        const coordinates = [];

        for (let i = 0; i < resultado.length; i++) {
            const longitud = resultado[i].longitud;
            const latitud = resultado[i].latitud;
            const coordinate = ol.proj.fromLonLat([longitud, latitud]);
            coordinates.push(coordinate);
        }
        console.log("coordenadas a dibujar",coordinates);
        dibujarRuta(map, coordinates);

    } else {
        console.log("El objeto puntos no existe o no es un arreglo.");
    }
}



function calcularDistancia(puntoOrigen, puntoDestino) {
  const R = 6371000; // Radio medio de la Tierra en metros (1 kilómetro = 1000 metros)

  const lat1 = puntoOrigen.latitud;
  const lon1 = puntoOrigen.longitud;
  const lat2 = puntoDestino.latitud;
  const lon2 = puntoDestino.longitud;

  // Convertir las latitudes y longitudes de grados a radianes
  const radianesLat1 = (lat1 * Math.PI) / 180;
  const radianesLon1 = (lon1 * Math.PI) / 180;
  const radianesLat2 = (lat2 * Math.PI) / 180;
  const radianesLon2 = (lon2 * Math.PI) / 180;

  const dLon = radianesLon2 - radianesLon1;

  const a =
    Math.pow(Math.cos(radianesLat2) * Math.sin(dLon), 2) +
    Math.pow(
      Math.cos(radianesLat1) * Math.sin(radianesLat2) -
        Math.sin(radianesLat1) * Math.cos(radianesLat2) * Math.cos(dLon),
      2
    );
  const b =
    Math.sin(radianesLat1) * Math.sin(radianesLat2) +
    Math.cos(radianesLat1) * Math.cos(radianesLat2) * Math.cos(dLon);

  const distancia = R * Math.atan2(Math.sqrt(a), b);

  return distancia;
}

// Función para calcular el camino más corto usando el algoritmo de Dijkstra
function calcularCaminoMasCorto(grafo, inicio, fin) {
  // Verificar que el grafo y los puntos de inicio y fin existan
  if (!grafo) {
    console.log('Error: El grafo no existe.');
    return null;
  }

  if (!inicio) {
    console.log('Error: El punto de inicio no está definido.');
    return null;
  }

  if (!fin) {
    console.log('Error: El punto de fin no está definido.');
    return null;
  }

  const distancia = {};
  const visitados = {};
  const anterior = {};

  // Inicializar las distancias a infinito y el nodo anterior a nulo
  for (let nodo in grafo) {
    distancia[nodo] = Infinity;
    anterior[nodo] = null;
  }

  // La distancia del nodo de inicio a sí mismo es cero
  distancia[inicio] = 0;

  while (Object.keys(visitados).length < Object.keys(grafo).length) {
    // Encontrar el nodo con la distancia mínima no visitado
    let nodoActual = null;
    for (let nodo in distancia) {
      if (!visitados[nodo] && (nodoActual === null || distancia[nodo] < distancia[nodoActual])) {
        nodoActual = nodo;
      }
    }

    // Marcar el nodo actual como visitado
    visitados[nodoActual] = true;

    // Actualizar las distancias de los nodos vecinos no visitados
    if (grafo[nodoActual] && grafo[nodoActual].conexiones) {
      grafo[nodoActual].conexiones.forEach((conexion) => {
        const distanciaAcumulada = distancia[nodoActual] + conexion.distancia;
        if (distanciaAcumulada < distancia[conexion.nodoDestino.codigo]) {
          distancia[conexion.nodoDestino.codigo] = distanciaAcumulada;
          anterior[conexion.nodoDestino.codigo] = nodoActual;
        }
      });
    }
  }

  // Construir el camino más corto con las coordenadas de los nodos
  const caminoMasCorto = [];
  let nodoActual = fin;
  while (nodoActual !== inicio) {
    if (nodoActual === null) {
      console.log('Error: No se encontró un camino entre los puntos de inicio y fin.');
      return null;
    }
    const nodoConCoordenadas = {
      codigo: nodoActual,
      latitud: grafo[nodoActual].latitud,
      longitud: grafo[nodoActual].longitud,
    };
    caminoMasCorto.unshift(nodoConCoordenadas);
    nodoActual = anterior[nodoActual];
  }
  const nodoInicioConCoordenadas = {
    codigo: inicio,
    latitud: grafo[inicio].latitud,
    longitud: grafo[inicio].longitud,
  };
  caminoMasCorto.unshift(nodoInicioConCoordenadas);

  // Devolver el array con las coordenadas del camino más corto
  return caminoMasCorto;
}


function dibujarRuta(map, coordinates) {
    if (!Array.isArray(coordinates) || coordinates.length < 2) {
        console.error("Las coordenadas proporcionadas no son válidas.");
        return;
    }

    // Remover las capas de ruta existentes del mapa
    map.getLayers().forEach(layer => {
        if (layer.get("name") === "rutaLayer") {
            map.removeLayer(layer);
        }
    });

    const drawSource = new ol.source.Vector();
    const drawLayer = new ol.layer.Vector({
        source: drawSource,
        style: new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'blue',
                width: 5,
            }),
        }),
        zIndex: 100, // Ajusta este valor según sea necesario
        name: "rutaLayer", // Asignar un nombre a la capa para identificación
    });

    const routeFeature = new ol.Feature({
        geometry: new ol.geom.LineString(coordinates)
    });

    drawSource.addFeature(routeFeature);

    // Agregar la nueva capa del camino al mapa
    map.addLayer(drawLayer);

    console.log("Capa de ruta agregada al mapa.");
}







