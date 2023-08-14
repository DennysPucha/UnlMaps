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

// Crear una capa para mostrar la ubicación del dispositivo
const vectorSource = new ol.source.Vector();
const vectorLayer = new ol.layer.Vector({
    source: vectorSource
});
map.addLayer(vectorLayer);

// Crear un objeto Geolocation
const geolocation = new ol.Geolocation({
    trackingOptions: {
        enableHighAccuracy: true
    },
    projection: map.getView().getProjection()
});

// Crear un estilo personalizado para el punto de ubicación
const iconStyle = new ol.style.Style({
    image: new ol.style.Icon({
        src: '/static/imagenes/punto.png', // Ruta a tu imagen de icono personalizado
        scale: 0.5, // Escala del icono (ajústala según sea necesario)
        anchor: [0.5, 1], // Punto de anclaje para centrar el icono en las coordenadas
        anchorXUnits: 'fraction',
        anchorYUnits: 'fraction'
    })
});

// Actualizar la ubicación del dispositivo en la capa vectorial y aplicar el nuevo estilo
geolocation.on('change:position', () => {
    const coordinates = geolocation.getPosition();

    vectorSource.clear();

    // Crear una nueva característica con el estilo personalizado
    const locationFeature = new ol.Feature({
        geometry: new ol.geom.Point(coordinates)
    });
    locationFeature.setStyle(iconStyle); // Aplicar el estilo personalizado

    vectorSource.addFeature(locationFeature);

    console.log('Ubicación actual:', ol.proj.toLonLat(coordinates));
});

// Iniciar la geolocalización
geolocation.setTracking(true);



function agregarMarcadorEnMapa(latitud, longitud, nombre, descripcion, valoracion) {
    const coordenadas = ol.proj.fromLonLat([longitud, latitud]);

    // Crear un marcador en la posición especificada con una imagen o logo como icono
    const marcador = new ol.Feature({
        geometry: new ol.geom.Point(coordenadas)
    });

    // Agregar el nombre y la descripción del marcador como propiedades
    marcador.set('nombre', nombre);
    marcador.set('descripcion', descripcion);
    marcador.set('coordenadas', coordenadas);
    marcador.set('valoracion', valoracion);

    // Estilo del marcador con una imagen o logo
    const markerStyle = new ol.style.Style({
        image: new ol.style.Icon({
            anchor: [0.5, 1], // Punto de anclaje para centrar el icono en las coordenadas
            src: "/static/imagenes/Ubic.png",    // URL de la imagen o logo
            scale: 0.05      // Escala del icono (ajusta según sea necesario)
        }),
        text: new ol.style.Text({
            text: nombre,
            font: 'bold 50px Arial',
            fill: new ol.style.Fill({ color: 'black ' }),
            offsetY: -15,
            textAlign: 'center',
            textBaseline: 'middle'
        })
    });

    marcador.setStyle(markerStyle);

    // Añadir el marcador a una fuente de datos
    const markerSource = new ol.source.Vector({
        features: [marcador]
    });

    // Añadir una capa de marcadores al mapa
    const markerLayer = new ol.layer.Vector({
        source: markerSource,
        minResolution: 0.1, // Definir la resolución mínima
        maxResolution: 1 // Definir la resolución máxima
    });

    // Agregar la capa de marcadores al mapa
    map.addLayer(markerLayer);

    // Ajustar la vista del mapa para que los marcadores siempre mantengan el mismo tamaño
    map.getView().on('change:resolution', function () {
        const currentResolution = map.getView().getResolution();
        const newScale = 0.03 / currentResolution; // Ajusta el valor según el tamaño deseado
        markerStyle.getImage().setScale(newScale);
        markerStyle.getText().setScale(newScale);
    });
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
            const valoracion = punto.valoracion;

            const palabra = "A";

            if (codigo.includes(palabra)) {
                agregarMarcadorEnMapa(latitud, longitud, codigo, descripcion, valoracion);
            }
        }
    }
}

//----------------------------------------------
// Obtener el formulario y el logo por su ID
const formulario = document.getElementById('search-form');
const logoContainer = document.getElementById('logo-container');
const logo = document.getElementById('logo');
const origen = document.getElementById('origen');
const destino = document.getElementById('destino');
const cancelar = document.getElementById('cancelar');

// Agregar un escuchador de eventos para el evento 'click' en el logo
logo.addEventListener('click', function() {
  // Mostrar el formulario y ocultar el logo
  formulario.style.display = 'block';
  logoContainer.style.display = 'none';
  logo.style.display = 'none';
});

// Obtener el botón de buscar por su ID
const buscarBoton = document.getElementById('botonBuscar');

// Agregar un escuchador de eventos para el evento 'click' en el botón de buscar
buscarBoton.addEventListener('click', function() {
  // Ocultar el formulario y mostrar el logo
  formulario.style.display = 'none';
  logoContainer.style.display = 'block';
  logo.style.display = 'block';
  origen.value = '';
  destino.value = '';

});

cancelar.addEventListener('click', function() {
  // Ocultar el formulario y mostrar el logo
  formulario.style.display = 'none';
  logoContainer.style.display = 'block';
  logo.style.display = 'block';
  origen.value = '';
  destino.value = '';

});

map.on('singleclick', function (evt) {
    var feature = map.forEachFeatureAtPixel(evt.pixel, function (feature) {
        return feature;
    });

    if (feature) {
        const nombreMarcador = feature.get('nombre');
        const descripcionMarcador = feature.get('descripcion');
        const coordenadas = feature.get('coordenadas');

        const valoraciones = feature.get('valoracion');

        console.log(nombreMarcador, descripcionMarcador, coordenadas, valoraciones);

        const infoContent = document.getElementById('info-content');
        const contenido = `<p><strong>${nombreMarcador}</strong></p><p>${descripcionMarcador}</p>`;


        // Generar los iconos de estrella conforme al número de valoraciones
        const iconosEstrella = '<span class="valoracion-icon">' + '<i class="fas fa-star"></i>'.repeat(valoraciones) + '</span>';

        // Agregar botones "Origen" y "Destino" debajo de los iconos de estrella
        const botonesOrigenDestino = `
            ${iconosEstrella}
            <div class="botones-container">
                <button id="botonOrigen" class="boton-estilo">Origen</button>
                <button id="botonDestino" class="boton-estilo">Destino</button>
            </div>
        `;

        // Actualizar el contenido del recuadro con la información del marcador, la imagen y los botones
        infoContent.innerHTML =  contenido + botonesOrigenDestino;

        const botonOrigen = document.getElementById('botonOrigen');
        const botonDestino = document.getElementById('botonDestino');

        botonOrigen.addEventListener('click', function () {
            formulario.style.display = 'block';
            logoContainer.style.display = 'none';
            logo.style.display = 'none';
            origen.value = nombreMarcador;
            console.log("Botón Destino presionado");
        });

        botonDestino.addEventListener('click', function () {
            formulario.style.display = 'block';
            logoContainer.style.display = 'none';
            logo.style.display = 'none';
            destino.value = nombreMarcador;
            console.log("Botón Destino presionado");
        });

        infoContent.style.display = 'block';
    } else {
        const infoContent = document.getElementById('info-content');

        // Ocultar el recuadro si no hay marcador
        infoContent.style.display = 'none';
    }
});



function calcularArregloFallos(patron) {
    const m = patron.length;
    const fallos = new Array(m).fill(0);

    let len = 0;
    let i = 1;

    while (i < m) {
        if (patron[i] === patron[len]) {
            len++;
            fallos[i] = len;
            i++;
        } else {
            if (len !== 0) {
                len = fallos[len - 1];
            } else {
                fallos[i] = 0;
                i++;
            }
        }
    }

    return fallos;
}

function buscarMarcador() {
    const buscado = document.getElementById('search-input').value.toLowerCase();

    let encontrado = false;

    for (const puntoKey in puntos) {
        if (puntos.hasOwnProperty(puntoKey)) {
            const punto = puntos[puntoKey];
            const nombre = punto.codigo.toLowerCase();
            const descripcion = punto.descripcion.toLowerCase();

            const fallosNombre = calcularArregloFallos(nombre);
            const fallosDescripcion = calcularArregloFallos(descripcion);

            if (nombre.includes(buscado, fallosNombre) || descripcion.includes(buscado, fallosDescripcion)) {
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

//----------------------------------------------------------------------
function crearGrafo(puntos) {
    const grafo = {};

    if (puntos && Array.isArray(puntos)) {
        puntos.forEach((punto) => {
            if (punto && punto.codigo && punto.conexiones_salientes) {
                const conexionesConDistancia = punto.conexiones_salientes.map((conexion) => ({
                    nodoDestino: conexion,
                    distancia: calcularDistancia(punto, conexion) // Implementa la función calcularDistancia()
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
        const inicio = document.getElementById('origen').value.toUpperCase();
        const fin = document.getElementById('destino').value.toUpperCase();

        const resultado = calcularCaminoMasCorto(grafo, inicio, fin);

        const coordinates = resultado.caminoMasCorto.map((nodo) => {
            return ol.proj.fromLonLat([nodo.longitud, nodo.latitud]);
        });

        console.log("coordenadas a dibujar", coordinates);
        console.log("Distancia total ", resultado.distanciaTotal);
        dibujarRuta(map, coordinates,resultado.distanciaTotal);

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

  if (!inicio ) {
      alert("El punto de inicio no está definido. ");
      map.getLayers().forEach(layer => {
        if (layer.get("name") === "rutaLayer") {
            map.removeLayer(layer);
        }
      });
    return null;
  }

  if (!fin) {
    alert("El punto de fin no está definido.");
    map.getLayers().forEach(layer => {
    if (layer.get("name") === "rutaLayer") {
            map.removeLayer(layer);
        }
    });
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

  // Calcular la distancia total del camino más corto
  let distanciaTotal = 0;
  let nodoActual = fin;
  while (nodoActual !== inicio) {
    if (nodoActual === null) {
      alert("No se encontró un camino entre los puntos de inicio y fin.");
      return null;
    }
    const nodoAnterior = anterior[nodoActual];
    const conexion = grafo[nodoAnterior].conexiones.find(c => c.nodoDestino.codigo === nodoActual);
    distanciaTotal += conexion.distancia;
    nodoActual = nodoAnterior;
  }

  // Construir el camino más corto con las coordenadas de los nodos
  const caminoMasCorto = [];
  nodoActual = fin;
  while (nodoActual !== inicio) {
    if (nodoActual === null) {
      alert("No se encontró un camino entre los puntos de inicio y fin.");
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

  // Devolver un objeto que contiene el array con las coordenadas del camino más corto y la distancia total
  return {
    caminoMasCorto: caminoMasCorto,
    distanciaTotal: distanciaTotal
  };
}


function dibujarRuta(map, coordinates, distancia) {
    // Remover las capas de ruta existentes del mapa
    map.getLayers().forEach(layer => {
        if (layer.get("name") === "rutaLayer") {
            map.removeLayer(layer);
        }
    });

    if (!Array.isArray(coordinates) || coordinates.length < 2) {
        console.error("Las coordenadas proporcionadas no son válidas.");
        return;
    }

    const drawSource = new ol.source.Vector();
    const drawLayer = new ol.layer.Vector({
        source: drawSource,
        style: new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: 'rgba(0, 122, 255, 0.8)', // Azul con transparencia
                width: 8,
                lineCap: 'round', // Extremos de línea redondeados
                lineJoin: 'round', // Unión de segmentos redondeada
            }),
            text: new ol.style.Text({
                text: `Distancia: ${distancia.toFixed(2)} metros\nTiempo estimado: ${formatearTiempo(calcularTiempoParaCaminar(distancia))}`,
                font: 'Bold 20px Arial, sans-serif',
                fill: new ol.style.Fill({ color: 'black' }),
                offsetY: -15,
                textAlign: 'center',
                textBaseline: 'middle',
            }),
        }),
        zIndex: 100, // Ajusta este valor según sea necesario
        name: "rutaLayer", // Asignar un nombre a la capa para identificación
    });

    const routeFeature = new ol.Feature({
        geometry: new ol.geom.LineString(coordinates),
    });

    drawSource.addFeature(routeFeature);

    // Agregar la nueva capa del camino al mapa
    map.addLayer(drawLayer);

    // Calcular el centro de las coordenadas de la ruta
    const routeExtent = routeFeature.getGeometry().getExtent();
    const routeCenter = ol.extent.getCenter(routeExtent);

    // Centrar el mapa en el centro de la ruta
    map.getView().setCenter(routeCenter);

    console.log("Capa de ruta agregada al mapa y centrado en la ruta.");
}

function formatearTiempo(tiempoEnMinutos) {
    const horas = Math.floor(tiempoEnMinutos / 60);
    const minutos = Math.floor(tiempoEnMinutos % 60);
    const segundos = Math.floor((tiempoEnMinutos * 60) % 60);

    return `${horas.toString().padStart(2, '0')}h${minutos.toString().padStart(2, '0')}m${segundos.toString().padStart(2, '0')}s`;
}

function calcularTiempoParaCaminar(distancia) {
    const velocidadCaminarMetrosPorMinuto = 83.33; // Velocidad promedio de caminar en metros por minuto

    if (distancia <= 0) {
        console.error("La distancia debe ser un valor positivo.");
        return null;
    }

    const tiempoEnMinutos = distancia / velocidadCaminarMetrosPorMinuto;
    return tiempoEnMinutos;
}








