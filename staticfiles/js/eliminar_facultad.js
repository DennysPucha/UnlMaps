function openDeleteModal(facultadId) {
    // Obtener el modal de confirmación por su ID
    var modal = document.getElementById('modalEliminarFacultad');

    // Agregar el ID de la facultad a eliminar en un atributo data del modal
    modal.setAttribute('data-facultad-id', facultadId);

    // Mostrar el modal
    var bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

// Función para enviar el formulario de eliminación cuando el usuario confirme
function confirmDelete() {
    // Obtener el ID de la facultad a eliminar del atributo data del modal
    var facultadId = document.getElementById('modalEliminarFacultad').getAttribute('data-facultad-id');

    // Construir el formulario de eliminación dinámicamente
    var form = document.createElement('form');
    form.method = 'post';
    form.action = '/ruta/para/eliminar/facultad/' + facultadId + '/'; // Reemplazar con la ruta correcta

    // Agregar el token CSRF al formulario
    var csrfToken = document.createElement('input');
    csrfToken.type = 'hidden';
    csrfToken.name = 'csrfmiddlewaretoken';
    csrfToken.value = '{{ csrf_token }}'; // Reemplazar con el token CSRF actual
    form.appendChild(csrfToken);

    // Agregar el formulario al body y enviarlo
    document.body.appendChild(form);
    form.submit();
}