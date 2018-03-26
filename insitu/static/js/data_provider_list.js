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
$(document).ready(function (){
  var buttonCommon = {
    exportOptions: {
      format: {
        body: function ( data, row, column, node ){
          if (row === 7 ){
            if(data.indexOf('glyphicon-ok-circle') != -1){
              return 'Yes'
            }
            else{
              return 'No'
            }
          }
          if (row === 0 || row === 3 || row === 4){
            return $.parseHTML(data)[0].innerHTML
          }

          return data
        }
      }
    }
  }
  var $table = $('#providers').dataTable({
    "processing": true,
    "serverSide": true,
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.is_network = $('#is_network').val();
        d.provider_type = $('#provider_type').val();
        d.state = $('#state').val();
      },
      "dataSrc": function (json) {
        $.each(json.filters, function(key, value){
          updateFilterOptions(key, value)
        });
        return json.data;
      }
    },
    "dom": "<'row'<'col-sm-12'B>>" +
           "<'row'<'col-sm-6'i><'col-sm-6'f><'col-sm-4 display-margin'l><'col-sm-8'p>>" +
           "<'row'<'col-sm-12'tr>>" +
           "<'row'<'col-sm-12'p>>",
    "lengthMenu": [
      [ 10, 25, 50, -1 ],
      [ '10 rows', '25 rows', '50 rows', 'Show all' ]
    ],
    "buttons": [
      $.extend( true, {}, buttonCommon,{
        extend: 'pdf',
        exportOptions: { orthogonal: 'export' },
        text: 'Save as PDF',
        filename: 'CIS2_DataProviders',
        title: 'CIS2 Data Providers',
        orientation: 'landscape',
        customize: function ( doc ){
          var cols = [];
          var created = new Date().toDateString();
          cols[0] = {text: 'https://cis2.eea.europa.eu , ' + created, alignment: 'right', margin:[50, 10], };
          var objFooter = {};
          objFooter['columns'] = cols;
          doc['footer']=objFooter;
        }
      }),
      $.extend( true, {}, buttonCommon,{
        extend: 'csv',
        filename: 'CIS2_DataProviders.',
        title: 'CIS2 Data Providers',
        extension: 'xlsx',
        text: 'Save as Excel',
      }),
    ],
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>",
    },
    "stateSave": true,
    "stateSaveParams": function(settings, data){
      data.is_network = $('#is_network').val();
      data.provider_type = $('#provider_type').val();
      data.state = $('#state').val();
    },
    "stateLoadParams": function (settings, data) {
      $('#is_network').val(data.is_network);
      $('#provider_type').val(data.provider_type);
      $('#state').val(data.state);
    },
    "columnDefs": [
      {
        "render": function (data, type, row) {
          if (data) {
            return "<span class='glyphicon glyphicon-ok-circle " +
              "text-success'></span>";
          }
          else {
            return "<span class='glyphicon glyphicon-remove-circle " +
              "text-danger'></span>";
          }
        },
        "targets": [7],
        "bSortable": false
      }
    ]
  }).fnFilterOnReturn();

  $('#is_network,#provider_type,#state').on('change', function (event) {
    var table = $table.DataTable();
    table.ajax.reload();
  });

  $('#reset-btn').on('click', function () {
    $('#is_network,#provider_type,#state').val('All');
    var table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });
});
