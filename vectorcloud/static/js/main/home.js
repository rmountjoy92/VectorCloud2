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

function load_repositories() {
    $.ajax({
        url: $("#repositories-container").attr('data-url'),
        type: 'GET',
        success: function(data){
            $("#repositories-container").empty();
            $("#repositories-container").append(data);
            init_repositories();
        }
    });
}

function init_repositories() {
    init_tooltips();

    $(".show-repository-plugins-btn").on('click', function(e) {
        var plugins_list = $(this).closest('.repository-collection-item').find('.repository-plugins-list');
        if (plugins_list.hasClass('hide')){
            plugins_list.removeClass('hide');
            $(this).addClass('theme-primary-text');
        } else {
            plugins_list.addClass('hide');
            $(this).removeClass('theme-primary-text');
        }
    });

    $(".update-repository-btn").on('click', function(e) {
        var el = $(this);
        $.ajax({
            url: el.attr('data-url'),
            data: {id: el.attr('data-id')},
            type: 'GET',
            success: function(data){
                el.tooltip('destroy');
                load_repositories();
                M.toast({html: 'Repository updated'});
            }
        });
    });

    $(".toggle-repository-auto-update-btn").on('click', function(e) {
        var el = $(this);
        $.ajax({
            url: el.attr('data-url'),
            type: 'GET',
            data: {repo_id: el.attr('data-id'), toggle: el.attr('data-toggle')},
            success: function(data){
                el.tooltip('destroy');
                load_repositories();
            }
        });
    });

    $(".delete-repository-btn").on('click', function(e) {
        var r = confirm('Are you sure you want to do that? Any installed plugins will no longer be able to update from this repository.')
        var el = $(this)
        if (r == true) {
            $.ajax({
                url: el.attr('data-url'),
                type: 'GET',
                data: {id: el.attr('data-id')},
                success: function(data){
                    load_repositories();
                    M.toast({html: 'Repository deleted'})
                }
            });
        }
    });

    $(".install-plugin-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            data: {plugin_name: $(this).attr('data-plugin'), repo_id: $(this).attr('data-repo_id')},
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

    $(".install-all-plugins-from-repo-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            data: {repo_id: $(this).attr('data-id')},
            success: function(data){
                var toastHTML = '<span>Plugins installed.</span><button onclick="location.reload();" class="btn-flat toast-action reload-ui-button">Reload</button>';
                M.toast({html: toastHTML});
            }
        });
    });
    $(".reinstall-plugin-from-repo-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            data: {plugin_name: $(this).attr('data-plugin_name'), repo_id: $(this).attr('data-repo_id')},
            success: function(data){
                var toastHTML = '<span>Plugin reinstalled.</span><button onclick="location.reload();" class="btn-flat toast-action reload-ui-button">Reload</button>';
                M.toast({html: toastHTML});
            }
        });
    });
}

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
    $("#add-repository-modal").modal();

    $('#settings-sidenav').sidenav({
        edge: 'right',
        draggable: false,
    });

    load_repositories();

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

    $("#add-repository-clone-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            data: {url: $("#add-repository-repo_url").val()},
            success: function(data){
                load_repositories();
                $("#add-repository-repo_url").val('');
                $("#add-repository-modal").modal('close');
                M.toast({html: 'Repository added'});
            }
        });
    });

    $("#update-all-repositories-btn").on('click', function(e) {
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            success: function(data){
                load_repositories();
                M.toast({html: 'Repositories updated'})
            }
        });
    });

    $("#restart-system-btn").on('click', function(e) {
        M.toast({html: 'Server restarting please wait..'})
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'GET',
            success: function(data){
                M.toast({html: data, classes: "theme-warning"})
            }
        });
    });

});