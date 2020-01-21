var socket = io();
socket.on('connect', function() {
    socket.emit('request_stats', {vector_id: "all"});
    socket.emit('request_logbook');
    socket.emit('request_scripts');
});
socket.on('stats', function(stats) {
    console.log(stats)
    $("#status-connected-" + stats.name).attr("src", 'static/images/icons/vector-green.svg')
    $("#status-ip-" + stats.name).text("IP: " + stats.ip);
    $("#status-name-" + stats.name).text(stats.name);
    $("#status-version-" + stats.name).text("OS Version: " +  stats.version);
    $("#status-serial-" + stats.name).text("Serial: " +  stats.serial);
    $("#status-battery_voltage-" + stats.name).text("Battery Voltage: " +  stats.battery_voltage);
    $("#status-battery_level-" + stats.name).text("Battery Level: " +  stats.battery_level);
    $("#status-status_charging-" + stats.name).text("Charging Status: " +  stats.status_charging);
    $("#status-cube_id-" + stats.name).text("Cube ID: " +  stats.cube_id);
    $("#status-cube_battery_volts-" + stats.name).text("Cube Battery Volts: " +  stats.cube_battery_volts);
    $("#status-cube_battery_level-" + stats.name).text("Cube Battery Level: " +  stats.cube_battery_level);
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

socket.on('logbook', function(message) {
    $("#feed-rows-ul").empty();
    $("#feed-rows-ul").append(message);
});

socket.on('scripts', function(message) {
    $("#scripts-collection").empty();
    $("#scripts-collection").append(message);
});

$( document ).ready(function() {
    $("#logbook-info-modal").modal();
    $("#add-edit-script-modal").modal();

    $(".command-bar").on('keyup', function(e) {
        if (e.key == "Enter"){
            socket.emit('request_robot_do', {
                command: $(this).val(),
                refresh_stats: true,
                vector_id: $(this).attr("data-id")
            });
            $(this).val('');
        }
    });

    $(".status-docked").on('click', function(e) {
        if ($(this).hasClass('theme-primary-text')){
            socket.emit('request_robot_do', {
                command: "robot.behavior.drive_off_charger()",
                refresh_stats: true,
                vector_id: $(this).attr("data-id")
            });
        } else {
            socket.emit('request_robot_do', {
                command: "robot.behavior.drive_on_charger()",
                refresh_stats: true,
                vector_id: $(this).attr("data-id")
            });
        }

    });

    $(".ping-vector").on('click', function(e) {
        socket.emit('request_robot_do', {
            command: "robot.behavior.say_text('ping')",
            vector_id: $(this).attr("data-id")
        });
    });

    $(".refresh-vector").on('click', function(e) {
        socket.emit('request_stats', {vector_id: $(this).attr("data-id")});
    });

    function hide_info_tabs(el, id){
        if (el.hasClass('hide')){
            $(".status-tabs-" + id).each(function(e) {
                $(this).addClass('hide');
            });
            el.removeClass('hide');
        } else {
            el.addClass('hide');
        }
    }

    $(".status-cube").on('click', function(e) {
        var id = $(this).attr("data-id");
        hide_info_tabs($("#status-cube-row-" + id), id);

        if ($(this).hasClass('theme-secondary-text')) {
            socket.emit('request_robot_do', {
                command: "robot.world.connect_cube()",
                vector_id: id
            });
        }
    });

    $(".status-info").on('click', function(e) {
        var id = $(this).attr("data-id")
        hide_info_tabs($("#status-info-row-" + id), id);
    });

    $(".status-battery").on('click', function(e) {
        var id = $(this).attr("data-id")
        hide_info_tabs($("#status-battery-row-" + id), id);
    });

    $(".status-remote").on('click', function(e) {
        var id = $(this).attr("data-id");
        hide_info_tabs($("#status-video-feed-row-" + id), id);
        $("#video-feed-preload-circle-" + id).removeClass('hide');
        $("#status-video-feed-" + id).attr("src", $("#status-video-feed-" + id).attr('data-url'));
    });

    $(".status-video-feed").on('load', function (e) {
        var id = $(this).attr("data-id");
        $("#video-feed-preload-circle-" + id).addClass('hide');
        socket.emit('request_logbook');
    });

    $(".status-close-video-feed").on('click', function(e) {
        var id = $(this).attr("data-id");
        var name = $(this).attr("data-name");
        $("#status-video-feed-" + id).attr("src", "static/images/avatar.jpg");
        $("#status-video-feed-row-" + id).addClass('hide');
        socket.emit('logbook_log', {name: name + " closed the stream.", log_type: 'success'});
    });

    $("#add-edit-script-save-btn").on('click', function(e) {
        socket.emit('add_edit_script', {
            name: $("#add-edit-script-name").val(),
            description: $("#add-edit-script-description").val(),
            commands: $("#add-edit-script-commands").val(),
            args: $("#add-edit-script-args").val(),
            script_id: $("#add-edit-script-id").val(),
        });
        $("#add-edit-script-form").trigger('reset');
        $("#add-edit-script-modal").modal('close');
        socket.emit("request_scripts");
    });

});

function init_scripts() {
    $(".edit-script-btn").on('click', function(e) {
        $("#add-edit-script-form").trigger('reset');
        $("#add-edit-script-name").val($(this).attr('data-name'));
        $("#add-edit-script-description").val($(this).attr('data-description'));
        $("#add-edit-script-commands").val($(this).attr('data-commands').replace(/,/g, '\n'));
        $("#add-edit-script-args").val($(this).attr('data-args').replace(' --', '\n'));
        M.textareaAutoResize($('#add-edit-script-commands'));
        $("#add-edit-script-id").val($(this).attr('data-id'));
        M.updateTextFields();
        $("#add-edit-script-modal").modal('open');
    });
}

function init_logbook() {
    $(".show-logbook-info").on('click', function(e) {
        $("#logbook-info-code").text($(this).attr('data-info'));
        $("#logbook-info-title").text($(this).attr('data-name'));
        $("#logbook-info-modal").modal('open');
    });
}