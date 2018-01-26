function updateFilterOptions(filter, option_data) {
  var select = $('#' + filter);
  select.find('option').remove();
  select.append('<option value="All">All</option>')
  $.each(option_data.options, function(i, option){
    var selected = '';
    if(option_data.selected == option){
      selected = ' selected';
    }
    select.append(
      '<option value="' + option + '"' + selected + '>' + option + '</option>');
  });
}
$(document).ready(function () {
  var $table = $('#requirements').dataTable({
    "processing": true,
    "serverSide": true,
    "dom": "<'row'<'col-sm-5'i><'col-sm-12'f><'col-sm-4 display-margin'l><'col-sm-8'p>>" +
           "<'row'<'col-sm-12'tr>>" +
           "<'row'<'col-sm-12'p>>",
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>",
    },
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.dissemination = $('#dissemination').val();
        d.quality_control_procedure = $('#quality_control_procedure').val();
        d.group = $('#group').val();
        d.state = $('#state').val()
      },
      "dataSrc": function (json) {
        $.each(json.filters, function(key, value){
          updateFilterOptions(key, value)
        });
        return json.data;
      }
    },
    "stateSave": true,
    "stateSaveParams": function(settings, data){
      data.dissemination = $('#dissemination').val();
      data.quality_control_procedure = $('#quality_control_procedure').val();
      data.group = $('#group').val();
      data.state = $('#state').val();
    },
    "stateLoadParams": function (settings, data) {
      $('#dissemination').val(data.dissemination);
      $('#quality_control_procedure').val(data.quality_control_procedure);
      $('#group').val(data.group);
      $('#state').val(data.state);
    },
    "columnDefs": [
      {
        "render": function (data, type, row) {
          function generate_div(color, data) {
            return "<div class='col-sm-12 " + color + " no-padding-left'>" + data +
              "</div>";
          }

          var threshold = data.split('T: ').pop().split(' - B: ').shift();
          var breakthrough = data.split('B: ').pop().split(' - G: ').shift();
          var goal = data.split('G: ').pop();
          return (
            generate_div('green', threshold) +
            generate_div('blue', breakthrough) +
            generate_div('orange', goal));
        },
        "targets": [4, 5, 6, 7, 8],
        "bSortable": false
      }
    ]
  }).fnFilterOnReturn();

  $('#dissemination,#quality_control_procedure,#group,#state').on('change', function (event) {
    var table = $table.DataTable();
    table.ajax.reload();
  });

  $('#reset-btn').on('click', function () {
    $('#dissemination,#quality_control_procedure,#group,#state').val('All');
    var table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });

  $('[data-toggle="popover"]').popover({
    trigger: 'hover',
    placement: 'top',
    html: true,
    template: '<div class="popover popover-width-limit" role="tooltip"><div class="popover-arrow"></div><h3 class="popover-title"></h3><div class="popover-content"></div></div>'
  });
});
