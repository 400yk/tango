$(document).ready(function() {
    $("#likes").click(function() {
        $(this).hide();
        var catid;
        catid = $(this).attr("data-catid");
        $.get('/rango/like_category/', {category_id: catid}, function(data) {
            $("#like_count").html(data);
            $("#likes").hide();     
        });
    });
});
