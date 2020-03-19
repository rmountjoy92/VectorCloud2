var socket = io();

socket.on('vector_busy', function(vector_id) {
    if (vector_id.length > 0) {
        $(".vector-busy").each(function(e) {
            if ($(this).attr('vector_id') == vector_id){
                $(this).removeClass('hide');
            }
        });
    } else {
        $(".vector-busy").removeClass('hide');
    }
});
socket.on('vector_free', function(vector_id) {
    if (vector_id.length > 0) {
        if ($(this).attr('vector_id') == vector_id){
            $(this).addClass('hide');
        }
    } else {
        $(".vector-busy").addClass('hide');
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



$( document ).ready(function() {

    $('#settings-sidenav').sidenav({
        edge: 'right',
        draggable: false,
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

    var plugins = {};
    $(".plugin-name").each(function(e) {
        plugins[$(this).text()] = null
    });
    $('.command-bar').each(function() {
        var el = $(this);
        var id = el.attr('data-id');
        el.autocomplete({
            data: plugins,
            onAutocomplete: function (e) {
                var plugin_name = e;
                $("#run-plugin-row-" + id).removeClass('hide');
                $("#run-plugin-title-" + id).text(plugin_name);
                $("#run-plugin-form-" + id).empty();
                $(".plugin-option-name").each(function(i, e) {
                    if ($(this).attr('data-plugin') == plugin_name){
                        $("#run-plugin-form-" + id).append(
                            `<div class="input-field col s12"><input id="${$(this).text()}-${1}" name="${$(this).text()}" type="text"><label for="${$(this).text()}-${1}">${$(this).text()}</label></div>`
                        )
                        if ($(this).text() == "vector_id"){
                            $("#run-plugin-form-" + id).find('input[name="vector_id"]').val(id)
                        }
                    }
                });
                $("#run-plugin-form-" + id).append(
                    `<input class="hide" value="${plugin_name}" name="plugin_name">`
                );
                M.updateTextFields();
            }
        });
    });

    $(".run-plugin-btn").on('click', function(e) {
        var url = $(this).attr('data-url')
        var id = $(this).attr('data-id')
        $.ajax({
            url: url,
            type: 'POST',
            data: $("#run-plugin-form-" + id).serialize(),
            success: function(data){

            }
        });
    });

    $(".cancel-run-plugin-btn").on('click', function(e) {
        var id = $(this).attr('data-id');
        $("#run-plugin-row-" + id).addClass('hide');
        $("#run-plugin-form-" + id).empty();
    });

    $("#open-settings-sidenav-btn").on('click', function(e) {
        $("#settings-sidenav").sidenav('open');
        $("#close-settings-sidenav-btn").removeClass('hide');
    });

    $("#close-settings-sidenav-btn").on('click', function(e) {
        $("#settings-sidenav").sidenav('close');
        $(this).addClass('hide');
    });

    $(".show-repository-plugins-btn").on('click', function(e) {
        var plugins_list = $(this).closest('.repository-collection-item').find('.repository-plugins-list');
        if (plugins_list.hasClass('hide')){
            plugins_list.removeClass('hide');
        } else {
            plugins_list.addClass('hide');
        }
    });

    $(".show-plugin-info-btn").on('click', function(e) {
        var plugin_info = $(this).closest('.card').find('.plugin-info-row');
        if (plugin_info.hasClass('hide')){
            plugin_info.removeClass('hide');
            $(this).addClass('theme-primary-text');
        } else {
            plugin_info.addClass('hide');
            $(this).removeClass('theme-primary-text');
        }
    });

    $(".delete-plugin-btn").on('click', function(e) {
        var r = confirm("Are you sure you want to delete this plugin?");
        if (r == true) {
            $.ajax({
                url: $(this).attr('data-url'),
                type: 'GET',
                data: {plugin_name: $(this).attr('data-plugin')},
                success: function(data){
                    if (data == "success"){
                        var toastHTML = '<span>Plugin uninstalled.</span><button onclick="location.reload();" class="btn-flat toast-action reload-ui-button">Reload</button>';
                        M.toast({html: toastHTML});
                    } else {
                        M.toast({html: data, classes: 'theme-warning'});
                    }
                }
            });
        }
    });

    $(".install-plugin-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            data: {plugin_name: $(this).attr('data-plugin')},
            success: function(data){
                if (data == "success"){
                    var toastHTML = '<span>Plugin installed.</span><button onclick="location.reload();" class="btn-flat toast-action reload-ui-button">Reload</button>';
                    M.toast({html: toastHTML});
                } else {
                    M.toast({html: data, classes: 'theme-warning'});
                }
            }
        });
    });

});

function show_panel(panel, vector_id, btn=null) {
    console.log(vector_id)
    $(".plugin-panels-container").each(function(e) {
        if ($(this).attr('vector_id') == vector_id) {
            $(this).find(".plugin-panel").addClass('hide');
            $(this).find(panel).removeClass('hide');
        }
    });
    $(".plugin-icons-container").each(function(e) {
        if ($(this).attr('vector_id') == vector_id) {
            $(this).find('.plugin-btn:not(.color-ignore)').removeClass('theme-primary-text');
            $(this).find('.plugin-btn:not(.color-ignore)').addClass('theme-secondary-text');
        }
    });
    if (btn != null) {
        btn.removeClass('theme-secondary-text');
        btn.addClass('theme-primary-text');
    }
}