function updateFilterOptions(filter, option_data) {
  let select = $('#' + filter);
  select.find('option').remove();
  select.append('<option value="All">All</option>');
  $.each(option_data.options, function(_i, option){
    let selected = '';
    if(option_data.selected == option){
      selected = ' selected';
    }
    select.append(
      '<option value="' + option + '"' + selected + '>' + option + '</option>');
  });
}
$(document).ready(function () {


  var filters = {};

  var queryString = window.location.search.substring(1);

  queryString.split('&').forEach(function(param) {
    if(!param) {
      return
    }
      var parts = param.split('=');
      filters[parts[0]] = decodeURIComponent(parts[1]);
  });

  var isOk = function(value) {
    return value && value !== 'All'
  }

  Object.keys(filters).forEach(function(key) {
    $('#' + key).val(filters[key])
  })

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
        let cols = [];
        let created = new Date().toDateString();
        cols[0] = {text: 'https://cis2.eea.europa.eu , ' + created, alignment: 'right', margin:[50, 10], };
        let objFooter = {};
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
    "stateSaveParams": function(_settings, data){
      data.service = $('#service').val();
      data.component = $('#component').val();
      data.entity = $('#entity').val();
      data.group = $('#group').val();
      data.status = $('#status').val();
      data.area = $('#area').val();



      var keys = ['service', 'component', 'entity', 'group', 'status', 'area']
      var queryString = ''
      for(var key of keys) {
        if(isOk(data[key])) {
          queryString += `${queryString.length ? "&" : ""}${key}=${encodeURIComponent(data[key])}`
        }
      }

      if(queryString.length) {
        window.history.pushState({}, '', '?' + queryString);
      } else {
        window.history.pushState({}, '', window.location.pathname);
      }


    },
    "stateLoadParams": function (_settings, data) {
      Object.keys(filters).forEach(function(key) {
        data[key] = filters[key]
      })
    
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
    "drawCallback": function(_settings) {
      let info = $(this).closest('.dataTables_wrapper').find('.dataTables_info');
      info.toggle(this.api().page.info().recordsDisplay > 9);
    },
  }).fnFilterOnReturn();

  $('#service,#entity,#component,#group,#status,#area').on('change', function (_event) {
    let table = $table.DataTable();
    table.ajax.reload();
  });

  $('#reset-btn').on('click', function () {
    $('#service,#entity,#component,#group,#status,#area').val('All');
    let table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });
});
