$( document ).ready(function() {
    $(".ping-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        socket.emit('run_plugin', {
            name: "ping",
            vector_id: vector_id
        });
    });
});