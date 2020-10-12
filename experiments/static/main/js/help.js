$(function () {

    // Allows auto opening when an anchor was specified in the url
    if (window.location.hash) {
        $('body').find(window.location.hash).collapse('show');
    }

});