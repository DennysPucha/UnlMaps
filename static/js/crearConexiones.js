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
    let colorRelleno, letra;
    if (nombre.includes('A')) {
        colorRelleno = 'red';
        letra = nombre;
    } else if (nombre.includes('N')) {
        colorRelleno = 'blue';
        letra = nombre;
    } else {
        colorRelleno = 'gray';
        letra = '';
    }

    marcador.setStyle(new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({ color: colorRelleno }),
            stroke: new ol.style.Stroke({ color: 'white', width: 2 })
        }),
        text: new ol.style.Text({
            text: letra,
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

      agregarMarcadorEnMapa(latitud, longitud, codigo, descripcion);

      // Obtener las conexiones salientes del punto
      const conexionesSalientes = punto.conexiones_salientes;

      // Unir cada conexión saliente con una línea en el mapa
      for (const conexion of conexionesSalientes) {
        const latitudOrigen = conexion.nodo_origen.latitud;
        const longitudOrigen = conexion.nodo_origen.longitud;
        const latitudDestino = conexion.nodo_destino.latitud;
        const longitudDestino = conexion.nodo_destino.longitud;

        const nodoOrigen = ol.proj.fromLonLat([longitudOrigen, latitudOrigen]);
        const nodoDestino = ol.proj.fromLonLat([longitudDestino, latitudDestino]);
console.log(nodoOrigen,nodoDestino);
        unirConLinea(nodoOrigen, nodoDestino, estilo);
      }
    }
  }
}



const estilo = new ol.style.Style({
  stroke: new ol.style.Stroke({
    color: 'blue',
    width: 5,
  }),
});

function unirConLinea(punto1, punto2, estilo) {

  // Crea una nueva geometría de tipo LineString con las coordenadas de los puntos
  const linea = new ol.geom.LineString([punto1, punto2]);

  // Crea una característica (feature) a partir de la geometría
  const feature = new ol.Feature(linea);

  // Establece el estilo de la línea
  feature.setStyle(estilo);

  // Crea una capa vectorial para mostrar la línea
  const capa = new ol.layer.Vector({
    source: new ol.source.Vector({
      features: [feature],
    }),
  });

  // Agrega la capa al mapa
  map.addLayer(capa);
console.log("sipasa");
  // Retorna la capa en caso de que necesites interactuar con ella más adelante
  return capa;

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
