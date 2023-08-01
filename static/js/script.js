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
