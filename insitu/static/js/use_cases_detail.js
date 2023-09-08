    //triggered when modal is about to be shown
    $('#exampleModal').on('show.bs.modal', function(e) {

        //get data-id attribute of the clicked element
        
        var href = $(e.relatedTarget).data('href');
        var target = $(e.relatedTarget).data('target-name');
        if (target === "Changes requested")
        {
            $(e.currentTarget).find("#changes-requested-feedback").attr("display", "visible")
        }
        else{
            $(e.currentTarget).find("#changes-requested-feedback").hide();
        }
        $(e.currentTarget).find('form').attr("action", href);
        $(e.currentTarget).find('#target-source-name').text(target);
        });