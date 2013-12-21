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

    $("#suggestion").keyup(function() {
        var query;
        query = $(this).val();
        $.get('/rango/suggest_category/', {suggestion: query}, function(data) {
            $("#cats").html(data);
        });
    });

    $(".add_page_btn").click(function() {
        var page_title;
        page_title = $(this).attr("page_title");
        var page_url;
        page_url = $(this).attr("page_url");
        var catid;
        catid = $(this).attr("catid");

        $.get('/rango/auto_add_page/', {'catid': catid, 'page_title': page_title, 'page_url': page_url}, function(data) {
            $("#page_list").html(data);
        });
        
    });
});
