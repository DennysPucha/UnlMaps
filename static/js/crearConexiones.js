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

function agregarMarcadorEnMapa(latitud, longitud, nombre, descripcion, foto, valoracion) {
    const coordenadas = ol.proj.fromLonLat([longitud, latitud]);

    // Crear un marcador en la posición especificada con una imagen o logo como icono
    const marcador = new ol.Feature({
        geometry: new ol.geom.Point(coordenadas)
    });

    // Agregar el nombre y la descripción del marcador como propiedades
    marcador.set('nombre', nombre);
    marcador.set('descripcion', descripcion);
    marcador.set('coordenadas', coordenadas);
    marcador.set('foto', foto);
    marcador.set('valoracion', valoracion);

// Estilo del marcador con una imagen o logo
const markerStyle = new ol.style.Style({
    image: new ol.style.Icon({
        anchor: [0.5, 1], // Punto de anclaje para centrar el icono en las coordenadas
        src: nombre.includes('A') ? "/static/imagenes/Ubic.png" : (nombre.includes('N') ? "/static/imagenes/Ubic2.png" : "/static/imagenes/Ubic.png"), // URL de la imagen o logo
        scale: 0.05 // Escala del icono (ajusta según sea necesario)
    }),
    text: new ol.style.Text({
        text: nombre,
        font: 'bold 50px Arial',
        fill: new ol.style.Fill({ color: 'black' }),
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
            const foto = punto.foto;
            const valoracion = punto.valoracion;
            agregarMarcadorEnMapa(latitud, longitud, codigo, descripcion,foto, valoracion);

        }
    }
}
function dibujarConexiones(puntos) {
    // Definir el estilo de línea
    const lineStyle = new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: 'black',
            width: 3
        })
    });

    // Crear una fuente de datos para las líneas
    const lineSource = new ol.source.Vector();

    // Iterar sobre cada punto en la lista de puntos
    for (const punto of puntos) {
        // Obtener las coordenadas de origen desde el punto actual
        const origenCoordenadas = ol.proj.fromLonLat([parseFloat(punto.longitud), parseFloat(punto.latitud)]);

        // Obtener las conexiones salientes (destinos) del punto actual
        const conexionesSalientes = punto.conexiones_salientes;

        // Iterar sobre cada conexión saliente (destino)
        for (const conexion of conexionesSalientes) {
            // Obtener las coordenadas de destino desde la conexión actual
            const destinoCoordenadas = ol.proj.fromLonLat([parseFloat(conexion.longitud), parseFloat(conexion.latitud)]);

            // Imprimir las coordenadas de la línea a dibujar
            console.log('Coordenadas de línea a dibujar:', origenCoordenadas, destinoCoordenadas);

            // Crear una característica de línea con las coordenadas de origen y destino
            const lineFeature = new ol.Feature({
                geometry: new ol.geom.LineString([destinoCoordenadas, origenCoordenadas])
            });

            // Aplicar el estilo de línea a la característica
            lineFeature.setStyle(lineStyle);

            // Agregar la característica a la fuente de datos de líneas
            lineSource.addFeature(lineFeature);
        }
    }

    // Crear una capa de líneas con la fuente de datos de líneas
    const lineLayer = new ol.layer.Vector({
        source: lineSource
    });

    // Agregar la capa de líneas al mapa (asegúrate de tener una variable 'map' que representa tu mapa OpenLayers)
    map.addLayer(lineLayer);
}





