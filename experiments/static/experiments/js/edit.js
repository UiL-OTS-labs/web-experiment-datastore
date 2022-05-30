function hideExtraForms(existingGroups) {
    $('.target-group-form').each((idx, el) => {
        if (idx >= existingGroups) {
            $(el).hide();
        }
    });
}

$(function() {
    $('#add_group').click((event) => {
        event.preventDefault();
        let hidden = $('.target-group-form:hidden');
        hidden.first().show();

        if (hidden.length - 1 <= 0) {
            $('#add_group').hide();
        }
    });
});
