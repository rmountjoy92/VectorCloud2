socket.on('connect', function() {
    socket.emit('request_stats', {vector_id: "all"});
});

socket.on('stats', function(stats) {
    $(".plugin-panels-container").each(function(e) {
       if ($(this).attr('vector_id') == stats.id) {
           $("#status-connected-" + stats.name).attr("src", 'static/images/icons/vector-green.svg')
           $("#status-name-" + stats.name).text(stats.name);

           $(this).find('.status-info').empty();
           $(this).find('.status-info').append(
               `
                IP: ${stats.ip} <br>
                OS Version: ${stats.ip} <br>
                Serial: ${stats.serial} <br>
               `
           );
           $(this).find('.status-cube').empty();
           $(this).find('.status-cube').append(
               `
                Cube ID: ${stats.cube_id} <br>
                Cube Battery Volts: ${stats.cube_battery_volts} <br>
                Cube Battery Level: ${stats.cube_battery_level} <br>
               `
           );
           $(this).find('.status-battery').empty();
           $(this).find('.status-battery').append(
               `
                Battery Voltage: ${stats.battery_voltage} <br>
                Battery Level: ${stats.battery_level} <br>
                Charging Status: ${stats.status_charging} <br>
               `
           );
       }
    });
    $(".plugin-icons-container").each(function(e) {
        if ($(this).attr('vector_id') == stats.id) {
            if (stats.status_charging == true){
                $(this).find('.stats-battery-btn').removeClass('theme-secondary-text');
                $(this).find('.stats-battery-btn').addClass('theme-primary-text');
                $(this).find('.stats-battery-btn').text('battery_charging_full');
            } else if (stats.battery_level < 2){
                $(this).find('.stats-battery-btn').addClass('theme-secondary-text');
                $(this).find('.stats-battery-btn').removeClass('theme-primary-text');
                $(this).find('.stats-battery-btn').text('battery_alert');
            } else if (stats.battery_level >= 2){
                $(this).find('.stats-battery-btn').addClass('theme-secondary-text');
                $(this).find('.stats-battery-btn').removeClass('theme-primary-text');
                $(this).find('.stats-battery-btn').text('battery_full');
            }
        }
    });
});

$( document ).ready(function() {
    setInterval(function(){
        socket.emit('request_stats', {vector_id: "all"});
    }, 60000);

    $(".stats-info-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        show_panel(".stats-info-panel", vector_id, $(this))
    });
    $(".stats-cube-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        show_panel(".stats-cube-panel", vector_id, $(this))
    });
    $(".stats-battery-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        show_panel(".stats-battery-panel", vector_id)
    });
    $(".connect-to-cube-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-panels-container').attr('vector_id');
        socket.emit('run_plugin', {
            name: "cube",
            command: 'connect',
            vector_id: vector_id
        });
    });
    $(".stats-refresh-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        socket.emit('run_plugin', {
            name: "stats",
            vector_id: vector_id
        });
    });
});