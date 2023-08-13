$(document).ready(function() {
    let isEditing = false;
    let facultadId = "";

    function mostrarAlerta() {
        $("#mensajeOperacion").removeClass("d-none");
        setTimeout(function() {
            $("#mensajeOperacion").addClass("d-none");
        }, 5000);
    }

    // Al hacer clic en el botón "Editar", redirige a la nueva página de edición
    $(".btn-editar").click(function () {
        facultadId = $(this).data("facultad-id");
        if (facultadId) {
            // Asigna el valor del data-facultad-id al campo oculto
            $("#editar_facultad_id").val(facultadId);
            // Redirige a la nueva página de edición de facultades
            window.location.href = "{% url 'editar_facultad' facultad_id=" + facultadId + " %}";
        } else {
            console.error("Error: facultadId está vacío o no es un valor numérico válido.");
        }
    });
    // Al hacer clic en el botón "Cancelar" (añadir), redirige nuevamente a la página de gestión de facultades
    $("#cancelarAgregar").click(function() {
        // Redirige a la página de gestión de facultades
        window.location.href = "{% url 'gestionar_facultades' %}";
    });

     $(".btn-eliminar").click(function() {
    if (!isEditing) {
        const objetoNombre = $(this).parent().prev().text().trim();
        if (confirm(`¿Estás seguro que deseas eliminar "${objetoNombre}"?`)) {
            // Obtener el data-facultad-id del elemento
            facultadId = $(this).parent().data("facultad-id");
            // Crear un formulario para enviar la solicitud POST
            const form = $("<form></form>").attr({
                "method": "post",
                "action": "{% url 'eliminar_facultad' %}",
            });
            // Agregar el token csrf al formulario
            const csrfInput = $("<input>").attr({
                "type": "hidden",
                "name": "csrfmiddlewaretoken",
                "value": "{{ csrf_token }}",
            });
            // Agregar el ID de la facultad al formulario
            const idInput = $("<input>").attr({
                "type": "hidden",
                "name": "facultad_id",
                "value": facultadId,
            });
            // Agregar los campos al formulario
            form.append(csrfInput, idInput);
            // Agregar el formulario al body y enviarlo
            $("body").append(form);
            form.submit();
        }
    } else {
        mostrarAlerta();
    }
});

    // Acción cuando el usuario confirma eliminar la facultad
    $("#confirmarEliminarFacultad").click(function() {
        const facultadId = $(this).data("facultad-id");
        if (facultadId) {
            // Redirigir a la página de eliminar la facultad
            window.location.href = `/eliminar_facultad/${facultadId}/`;
        } else {
            console.error("Error: facultadId está vacío o no es un valor numérico válido.");
        }
    });
});