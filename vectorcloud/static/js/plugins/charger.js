socket.on('stats', function(stats) {
    $(".plugin-icons-container").each(function(e) {
        if ($(this).attr('vector_id') == stats.id) {
            if (stats.status_charging == true){
                $(this).find('.dock-btn').addClass('hide');
                $(this).find('.undock-btn').removeClass('hide');
            } else {
                $(this).find('.dock-btn').removeClass('hide');
                $(this).find('.undock-btn').addClass('hide');
            }
        }
    });
});

$( document ).ready(function() {
    $(".dock-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        socket.emit('run_plugin', {
            name: "charger",
            command: "dock",
            vector_id: vector_id
        });
    });
    $(".undock-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        socket.emit('run_plugin', {
            name: "charger",
            command: "undock",
            vector_id: vector_id
        });
    });
});