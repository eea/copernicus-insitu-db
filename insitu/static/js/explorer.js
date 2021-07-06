var csrf_token = $.cookie('csrftoken');
$.ajaxSetup({
    beforeSend: function(xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrf_token);
    }
});

function ExplorerEditor(queryId) {
    this.queryId = queryId;
    this.$table = $('#preview');
    this.$rows = $('#rows');
    this.$form = $("form");
    this.$snapshotField = $("#id_snapshot");
    this.$paramFields = this.$form.find(".param");

    this.$submit = $("#refresh_play_button, #save_button");
    if (!this.$submit.length) { this.$submit = $("#refresh_button"); }

    this.editor = CodeMirror.fromTextArea(document.getElementById('id_sql'), {
        mode: "text/x-sql",
        lineNumbers: 't',
        autofocus: true,
        height: 500,
        extraKeys: {
            "Ctrl-Enter": function() { this.doCodeMirrorSubmit(); }.bind(this),
            "Cmd-Enter": function() { this.doCodeMirrorSubmit(); }.bind(this),
            "Cmd-/": function() { this.editor.toggleComment(); }.bind(this)
        }
    });
    this.editor.on("change", function(cm, change) {
        document.getElementById('id_sql').classList.add('changed-input');
    });
    this.bind();

    if($.cookie('schema_sidebar_open') == 1){
      this.showSchema(true);
    }
}

ExplorerEditor.prototype.getParams = function() {
    var o = false;
    if(this.$paramFields.length) {
        o = {};
        this.$paramFields.each(function() {
            o[$(this).data('param')] = $(this).val();
        });
    }
    return o;
};

ExplorerEditor.prototype.serializeParams = function(params) {
    var args = [];
    for(var key in params) {
        args.push(key + '%3A' + params[key]);
    }
    return args.join('%7C');
};

ExplorerEditor.prototype.doCodeMirrorSubmit = function() {
    // Captures the cmd+enter keystroke and figures out which button to trigger.
    this.$submit.click();
};

ExplorerEditor.prototype.savePivotState = function(state) {
    bmark = btoa(JSON.stringify(_(state).pick('aggregatorName', 'rows', 'cols', 'rendererName', 'vals')));
    $el = $('#pivot-bookmark');
    $el.attr('href', $el.data('baseurl') + '#' + bmark);
};

ExplorerEditor.prototype.updateQueryString = function(key, value, url) {
    // http://stackoverflow.com/a/11654596/221390
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi"),
        hash = url.split('#');

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?';
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
};

ExplorerEditor.prototype.formatSql = function() {
    $.post('../format/', {sql: this.editor.getValue(), timeout: 0, }, function(data) {
        this.editor.setValue(data.formatted);
    }.bind(this));
};

ExplorerEditor.prototype.showRows = function() {
    var rows = this.$rows.val(),
        $form = $("#editor");
    $form.attr('action', this.updateQueryString("rows", rows, window.location.href));
    $form.submit();
};

ExplorerEditor.prototype.showSchema = function(noAutofocus) {
    $("#schema_frame").attr('src', '../schema/' + $('#id_connection').val());
    if (noAutofocus === true) {
        $("#schema_frame").addClass('no-autofocus');
    }
    $("#query_area").removeClass("col-md-12").addClass("col-md-9");
    var schema$ = $("#schema");
    schema$.addClass("col-md-3");
    schema$.show();
    $("#show_schema_button").hide();
    $("#hide_schema_button").show();
    $.cookie('schema_sidebar_open', 1);
    return false;
};

ExplorerEditor.prototype.hideSchema = function() {
    $("#query_area").removeClass("col-md-9").addClass("col-md-12");
    var schema$ = $("#schema");
    schema$.removeClass("col-md-3");
    schema$.hide();
    $(this).hide();
    $("#show_schema_button").show();
    $.cookie('schema_sidebar_open', 0);
    return false;
};

ExplorerEditor.prototype.bind = function() {
    $("#show_schema_button").click(this.showSchema);
    $("#hide_schema_button").click(this.hideSchema);

    $("#format_button").click(function(e) {
        e.preventDefault();
        this.formatSql();
    }.bind(this));

    $("#rows").keyup(function() {
        var curUrl = $("#fullscreen").attr('href');
        var newUrl = curUrl.replace(/rows=\d+/, 'rows=' + $("#rows").val());
        $("#fullscreen").attr('href', newUrl);
    }.bind(this));

    $("#save_button").click(function() {
        var params = this.getParams(this);
        if(params) {
            this.$form.attr('action', '../' + this.queryId + '/?params=' + this.serializeParams(params));
        }
        this.$snapshotField.hide();
        this.$form.append(this.$snapshotField);
    }.bind(this));

    $("#save_only").click(function() {
        var params = this.getParams(this);
        if(params) {
            this.$form.attr('action', '../' + this.queryId + '/?show=0&params=' + this.serializeParams(params));
        } else {
            this.$form.attr('action', '../' + this.queryId + '/?show=0');
        }
        this.$snapshotField.hide();
        this.$form.append(this.$snapshotField);
    }.bind(this));

    $("#refresh_button").click(function(e) {
        e.preventDefault();
        var params = this.getParams();
        if(params) {
            window.location.href = '../' + this.queryId + '/?params=' + this.serializeParams(params);
        } else {
            window.location.href = '../' + this.queryId + '/';
        }
    }.bind(this));

    $("#refresh_play_button").click(function() {
        this.$form.attr('action', '../play/');
    }.bind(this));

    $("#playground_button").click(function(e) {
        e.preventDefault();
        this.$form.attr('action', '../play/?show=0');
        this.$form.submit();
    }.bind(this));

    $("#create_button").click(function() {
        this.$form.attr('action', '../new/');
    }.bind(this));

    $(".download-button").click(function(e) {
        var url = '../download?format=' + $(e.target).data('format');
        var params = this.getParams();
        if(params) {
            url = url + '&params=' + params;
        }
        this.$form.attr('action', url);
    }.bind(this));

    $(".download-query-button").click(function(e) {
        var url = '../download?format=' + $(e.target).data('format');
        var params = this.getParams();
        if(params) {
            url = url + '&params=' + params;
        }
        this.$form.attr('action', url);
    }.bind(this));

    $(".stats-expand").click(function(e) {
        e.preventDefault();
        $(".stats-expand").hide();
        $(".stats-wrapper").show();
        this.$table.floatThead('reflow');
    }.bind(this));

    $("#counter-toggle").click(function(e) {
        e.preventDefault();
        $('.counter').toggle();
        this.$table.floatThead('reflow');
    }.bind(this));

    $(".sort").click(function(e) {
        var t = $(e.target).data('sort');
        var dir = $(e.target).data('dir');
        $('.sort').css('background-image', 'url(//cdn.datatables.net/1.10.0/images/sort_both.png)');
        if (dir == 'asc'){
            $(e.target).data('dir', 'desc');
            $(e.target).css('background-image', 'url(//cdn.datatables.net/1.10.0/images/sort_asc.png)');
        } else {
            $(e.target).data('dir', 'asc');
            $(e.target).css('background-image', 'url(//cdn.datatables.net/1.10.0/images/sort_desc.png)');
        }
        var vals = [];
        var ct = 0;
        while (ct < this.$table.find('th').length) {
           vals.push(ct++);
        }
        var options = {
            valueNames: vals
        };
        var tableList = new List('preview', options);
        tableList.sort(t, { order: dir });
    }.bind(this));

    $("#preview-tab-label").click(function() {
        this.$table.floatThead('reflow');
    }.bind(this));

    var pivotState = window.location.hash;
    var navToPivot = false;
    if (!pivotState) {
        pivotState = {onRefresh: this.savePivotState};
    } else {
        try {
            pivotState = JSON.parse(atob(pivotState.substr(1)));
            pivotState.onRefresh = this.savePivotState;
            navToPivot = true;
        } catch(e) {
            pivotState = {onRefresh: this.savePivotState};
        }
    }

    function filter_countries(event) {
        var countriesEU = [
            "Austria", "Belgium", "Bulgaria", "Czech Republic", "Cyprus", "Croatia", "Denmark", "Estonia", "Finland", "France",
            "Germany", "Greece", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Poland", "Romania", "Slovakia",
            "Slovenia", "Spain", "Sweden", "Netherlands", "Hungary"
        ]
        var countriesEEA = [
            "Belgium", "Bulgaria", "Czech Republic", "Denmark", "Cyprus", "Latvia", "Lithuania", "Luxembourg", "Spain", "France",
            "Croatia", "Italy", "Poland", "Portugal", "Romania", "Slovenia", "Hungary", "Malta", "Netherlands", "Austria", "Iceland",
            "Liechtenstein", "Norway", "Slovakia", "Finland", "Sweden", "Germany", "Estonia", "Ireland", "Greece"
        ]
        var eumetnetMembers = [
            "Austria", "Belgium", "Croatia", "Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France", "Montenegro",
            "Germany", "Greece", "Hungary", "Iceland", "Ireland", "Italy", "Latvia", "Luxembourg", "Malta", "Netherlands", "Norway",
            "Poland", "Portugal", "Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "Macedonia, The Former Yugoslav Republic Of", "United Kingdom"
        ]
        var copernicusMembers = [
            "Austria", "Belgium", "Bulgaria", "Czech Republic", "Cyprus", "Croatia", "Denmark", "Estonia", "Finland", "France", "Germany",
            "Greece", "Iceland", "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Norway", "Poland", "Romania", "Slovakia",
            "Slovenia", "Spain", "Sweden", "Netherlands", "Hungary"
        ]
        var countries = []
        if ($(".eu-members").is(":checked")){
          countries = countriesEU
        } else if ($(".eea-members").is(":checked")){
          countries = countriesEEA
        } else if ($(".metnet-members").is(":checked")){
          countries = eumetnetMembers
        } else if ($(".copernicus-members").is(":checked")){
          countries = copernicusMembers
        }
        var $selectNone = $("span:contains('"+event.data.param1 +"')").closest('.pvtFilterBox').first().find("button:contains('Select None')");
        var $applyButton = $("span:contains('"+event.data.param1 +"')").closest('.pvtFilterBox').first().find("button:contains('Apply')");
        $selectNone.trigger("click");
        $.each(countries, function( index, value ) {
         var $checkboxCountry = $("span:contains('"+event.data.param1 +"')").closest('.pvtFilterBox').first().find("span:contains('"+ value +"')").parent().first().find('input');
         $checkboxCountry.trigger('click');
         $checkboxCountry.prop( "checked", true );
       });
        $applyButton.trigger("click");
      };
    $.ajax({
      dataType: "json",
      url: "/reports/" + this.queryId + "/json",
    }).success(function(results) {
        $(".pivot-table").pivotUI(results, pivotState);
        tmpHTML = "<div><input class='radio-inline eea-members' type='radio' name='filter_members'>" +
                  "<span style='font-size: 14px;'>EEA members</span></div>" +
                  "<div><input class='radio-inline eu-members' type='radio' name='filter_members'>" +
                  "<span style='font-size: 14px;'>EU members</span></div>" +
                  "<div><input class='radio-inline metnet-members' type='radio' name='filter_members'>" +
                  "<span style='font-size: 14px;'>EUMETNET Members</span></div>" +
                  "<div><input class='radio-inline copernicus-members' type='radio' name='filter_members'>" +
                  "<span style='font-size: 14px;'>Copernicus Members</span></div>" +
                  "</div>" +
                  "<button type='button' class='btn btn-primary btn-md pivot-set-countries'>Set countries to EU countries</button>"
        $("span:contains('Data provider network country')").parent('h4').append(tmpHTML)
        $("span:contains('Data provider country')").parent('h4').append(tmpHTML)
        $("span:contains('Data provider network country')").parent('h4').find('.pivot-set-countries').click({'param1': 'Data provider network country'}, filter_countries)
        $("span:contains('Data provider country')").parent('h4').find('.pivot-set-countries').click({'param1': 'Data provider country'}, filter_countries)
    });

    if(navToPivot){
      $("#pivot-tab-label").tab("show");
    }

    setTimeout(function() {
        this.$table.floatThead({
            scrollContainer: function() {
                                return this.$table.closest('.overflow-wrapper');
                            }.bind(this)
        });
    }.bind(this), 1);

    this.$rows.change(function() { this.showRows(); }.bind(this));
    this.$rows.keyup(function(event) {
        if(event.keyCode == 13){ this.showRows(); }
    }.bind(this));
};

$(window).on('beforeunload', function () {
    // Only do this if changed-input is on the page and we're not on the playground page.
    if ($('.changed-input').length && !$('.playground-form').length) {
        return 'You have unsaved changes to your query.';
    }
});

// Disable unsaved changes warning when submitting the editor form
$(document).on("submit", "#editor", function(event){
    // disable warning
    $(window).off('beforeunload');
});