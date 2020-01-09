var socket = io();
socket.on('connect', function() {
    socket.emit('request_stats', {vector_id: "all"});
});
socket.on('stats', function(stats) {
    console.log(stats)
    $("#status-connected-" + stats.name).attr("src", 'static/images/icons/vector-green.svg')
    $("#status-ip-" + stats.name).text("IP: " + stats.ip);
    $("#status-name-" + stats.name).text(stats.name);
    $("#status-version-" + stats.name).text("OS Version: " +  stats.version);
    if (stats.cube_id && stats.cube_id.length > 0){
        $("#status-cube-" + stats.name).removeClass('theme-secondary-text').addClass('theme-primary-text');
    }
    if (stats.status_charging == true){
        $("#status-battery-" + stats.name).text('battery_charging_full');
        $("#status-battery-" + stats.name).removeClass('theme-secondary-text').addClass('theme-primary-text');
        $("#status-docked-" + stats.name).removeClass('theme-secondary-text').addClass('theme-primary-text');
    } else if (stats.battery_level < 2){
        $("#status-battery-" + stats.name).text('battery_alert');
        $("#status-battery-" + stats.name).addClass('theme-secondary-text').removeClass('theme-primary-text');
        $("#status-docked-" + stats.name).addClass('theme-secondary-text').removeClass('theme-primary-text');
    } else if (stats.battery_level >= 2){
        $("#status-battery-" + stats.name).text('battery_full');
        $("#status-battery-" + stats.name).addClass('theme-secondary-text').removeClass('theme-primary-text');
        $("#status-docked-" + stats.name).addClass('theme-secondary-text').removeClass('theme-primary-text');
    }

    $("#command-bar-" + stats.name).on('keyup', function(e) {
        if (e.key == "Enter"){
            M.toast({html: "Sent!"})
            socket.emit('request_robot_do', {
                command: $(this).val(),
                refresh_stats: true
            });
            $(this).val('');
        }
    });

    $("#status-docked-"  + stats.name).on('click', function(e) {
        if ($(this).hasClass('theme-primary-text')){
            M.toast({html: "Undocking"})
            socket.emit('request_robot_do', {
                command: "robot.behavior.drive_off_charger()",
                refresh_stats: true,
            });
        } else {
            M.toast({html: "Docking"})
            socket.emit('request_robot_do', {
                command: "robot.behavior.drive_on_charger()",
                refresh_stats: true,
            });
        }

    });

    $("#ping-vector-"  + stats.name).on('click', function(e) {
        M.toast({html: "Sent!"})
        socket.emit('request_robot_do', {
            command: "robot.behavior.say_text('ping')",
        });
    });

    $("#refresh-vector-"  + stats.name).on('click', function(e) {
        M.toast({html: "Refreshing"})
        socket.emit('request_stats', {vector_id: "all"});
    });
});

socket.on('server_message', function(message) {
    if (message.refresh_stats == true){
        socket.emit('request_stats', {vector_id: "all"});
    }
    if (message.classes == undefined){
        message.classes = ""
    }
    M.toast({html: message.html, classes: message.classes})
});

socket.on('new_logbook_item', function(message) {
    console.log(message)
});