function updateFilterOptions(filter, option_data) {
  var select = $('#' + filter);
  select.find('option').remove();
  select.append('<option value="All">All</option>');
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
  var $table = $('#products').dataTable({
    "processing": true,
    "serverSide": true,
    "dom": "<'row'<'col-sm-12'B>>" +
           "<'row'<'col-sm-6'i><'col-sm-6'f><'col-sm-4 display-margin'l><'col-sm-8'p>>" +
           "<'row'<'col-sm-12'tr>>" +
           "<'row'<'col-sm-12'p>>",
    "lengthMenu": [
      [ 10, 25, 50, -1 ],
      [ '10 rows', '25 rows', '50 rows', 'Show all' ]
    ],
    "buttons": [{
      extend: 'pdf',
      exportOptions: { orthogonal: 'export' },
      text: 'Save as PDF',
      filename: 'CIS2_Products',
      title: 'CIS2 Products',
      orientation: 'landscape',
      customize: function (doc){
        var cols = [];
        var created = new Date().toDateString();
        cols[0] = {text: 'https://cis2.eea.europa.eu , ' + created, alignment: 'right', margin:[50, 10], };
        var objFooter = {};
        objFooter.columns = cols;
        doc.footer=objFooter;
      }
    },
    {
      extend: 'excel',
      filename: 'CIS2_Products.',
      title: 'CIS2 Products',
      text: 'Save as Excel',
    },
    ],
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>"
     },
    "stateSave": true,
    "stateSaveParams": function(settings, data){
      data.service = $('#service').val();
      data.component = $('#component').val();
      data.entity = $('#entity').val();
      data.group = $('#group').val();
      data.status = $('#status').val();
      data.area = $('#area').val();
    },
    "stateLoadParams": function (settings, data) {
      $('#service').val(data.service);
      $('#component').val(data.component);
      $('#entity').val(data.entity);
      $('#group').val(data.group);
      $('#status').val(data.status);
      $('#area').val(data.area);
    },
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.service = $('#service').val();
        d.component = $('#component').val();
        d.entity = $('#entity').val();
        d.group = $('#group').val();
        d.status = $('#status').val();
        d.area = $('#area').val();
      },
      "dataSrc": function (json) {
        $.each(json.filters, function(key, value){
          updateFilterOptions(key, value);
        });
        return json.data;
      }
    },
    "drawCallback": function(settings) {
      var info = $(this).closest('.dataTables_wrapper').find('.dataTables_info');
      info.toggle(this.api().page.info().recordsDisplay > 9);
    },
  }).fnFilterOnReturn();

  $('#service,#entity,#component,#group,#status,#area').on('change', function (event) {
    var table = $table.DataTable();
    table.ajax.reload();
  });

  $('#reset-btn').on('click', function () {
    $('#service,#entity,#component,#group,#status,#area').val('All');
    var table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });
});
