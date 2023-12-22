$(document).ready(function() {
    // Event listener for input in the search box
    $("#searchBox").on("input", function() {
        var query = $(this).val();
        if (query.length > 1) { // Avoid too many requests for single letters
            $.ajax({
                url: '/search_stocks/', // URL to Django view
                data: { 'search_text': query },
                success: function(data) {
                    var suggestionsHtml = "";
                    data.forEach(function(item) {
                        suggestionsHtml += "<div class='suggestion-item'>" + item['2. name'] + " (" + item['1. symbol'] + ")</div>";
                    });
                    $("#suggestions").html(suggestionsHtml).show();
                }
            });
        } else {
            $("#suggestions").hide();
        }
    });

    // Event listener for clicking a suggestion item
    $("#suggestions").on("click", ".suggestion-item", function() {
        $("#searchBox").val($(this).text());
        $("#suggestions").hide();
    });
});
