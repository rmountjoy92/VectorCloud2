$( document ).ready(function() {
    $(".rc-panel-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        $(".plugin-panels-container").each(function(e) {
            var container = $(this)
            if ($(this).attr('vector_id') == vector_id){
                container.find('.rc-video-feed').attr('src', '');
                container.find('.rc-video-feed-loading').removeClass('hide');
                $.ajax({
                    url: container.find('.rc-video-feed').attr('data-url'),
                    type: 'GET',
                    data: {vector_id: vector_id},
                    success: function(data){
                        container.find('.rc-video-feed').attr('src', data);
                    }
                });
            }
        });

        show_panel(".rc-panel", vector_id, $(this));
    });
    $(".rc-video-feed").on('load', function (e) {
        var vector_id = $(this).closest('.plugin-panels-container').attr('vector_id');
        $(".plugin-panels-container").each(function(e) {
            $(this).find('.rc-video-feed-loading').addClass('hide');
        });
    });

    $(".plugin-btn").on('click', function(e) {
        var vector_id = $(this).closest('.plugin-icons-container').attr('vector_id');
        $(".plugin-panels-container").each(function(e) {
            if ($(this).attr('vector_id') == vector_id){
                $(this).find('.rc-video-feed').attr('src', '');
                $(this).find('.rc-video-feed-loading').removeClass('hide');
            }
        });
    });
});