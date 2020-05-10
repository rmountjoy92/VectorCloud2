$( document ).ready(function() {
    if ($("#user-exists").text() != "None" && $("#vector-exists").text() != "None") {
        $(location).attr('href', $("#user-exists").attr('data-home-url'));
    }

    if ($("#user-exists").text() != "None") {
        $(".add-user-row").addClass('hide');
        $(".add-vector-row").removeClass('hide');
    }

    $(".register-form").on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'POST',
            data: $(this).serialize(),
            success: function(data){
                if (data.data.err == "success"){
                    if ($("#vector-exists").text() == "None") {
                        $(".add-user-row").addClass('hide');
                        $(".add-vector-row").removeClass('hide');
                        M.toast({html: "User created", classes: "theme-success"});
                    } else {
                        $(location).attr('href', data.data.url)
                    }
                } else {
                    M.toast({html: data.data.err, classes: "theme-warning"});
                }
            }
        });
    });

    $(".vector-form").on('submit', function(e) {
        e.preventDefault();
        M.toast({html: 'Authenticating..'});
        $.ajax({
            url: $(this).attr('data-url'),
            type: 'POST',
            data: $(this).serialize(),
            success: function(data){
                var row = $("#sdk-config-error-row")
                if (data.data.success == "true"){
                    row.removeClass('theme-warning');
                    row.addClass('theme-success');
                    $("#go-to-home-btn").removeClass('hide');
                    $("#submit-vector-form-btn").text('Authenticate another');
                } else {
                    row.removeClass('theme-success');
                    row.addClass('theme-warning');
                }
                $("#sdk-config-error-row").removeClass('hide');
                $("#sdk-config-error-row").html(data.data.output);
            }
        });
    });
});