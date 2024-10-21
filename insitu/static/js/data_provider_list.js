function updateFilterOptions(filter, option_data) {
  let select = $('#' + filter);
  select.find('option').remove();
  select.append('<option value="All">All</option>');
  $.each(option_data.options, function (_i, option) {
    let selected = '';
    let option_label = option;
    if (option == "true" || option == "Yes" || option == true) {
      option_label = "Yes";
    } else if (option == "false" || option == "No" || option == false) {
      option_label = "No";
    }
    if (filter == 'is_network') {
      if (option_data.selected == 'true' || option_data.selected == 'false') {
        selected = ' selected';
      }
    }
    else {
      if (option_data.selected == option) {
        selected = ' selected';
      }
    }
    select.append(
      '<option value="' + option + '"' + selected + '>' + option_label + '</option>');
  });
}
$(document).ready(function () {
  var columnIndex = $('#columns-number').data('columns-number');
  var buttonCommon = {
    exportOptions: {
      format: {
        body: function (data, row, _column, _node) {
          if (row === 7) {
            if (data.indexOf('glyphicon-ok-circle') != -1) {
              return 'Yes';
            }
            else {
              return 'No';
            }
          }
          if (row === 0 || row === 3 || row === 4) {
            return $.parseHTML(data)[0].innerHTML;
          }

          return data;
        }
      }
    }
  };

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

  var $table = $('#providers').dataTable({
    "processing": true,
    "serverSide": true,
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.is_network = $('#is_network').val();
        d.provider_type = $('#provider_type').val();
        d.state = $('#state').val();
        d.component = $('#component').val();
      },
      "dataSrc": function (json) {
        $.each(json.filters, function (key, value) {
          updateFilterOptions(key, value);
        });
        return json.data;
      }
    },
    "dom": "<'row'<'col-sm-12'B>>" +
      "<'row'<'col-sm-6'i><'col-sm-6'f><'col-sm-4 display-margin'l><'col-sm-8'p>>" +
      "<'row'<'col-sm-12'tr>>" +
      "<'row'<'col-sm-12'p>>",
    "lengthMenu": [
      [10, 25, 50, -1],
      ['10 rows', '25 rows', '50 rows', 'Show all']
    ],
    "buttons": [{
        extend: 'pdf',
        exportOptions: { orthogonal: 'export' },
        text: 'Save as PDF',
        filename: 'CIS2_DataProviders',
        title: 'CIS2 Data Providers',
        orientation: 'landscape',
        customize: function (doc) {
          let cols = [];
          let created = new Date().toDateString();
          cols[0] = { text: 'https://cis2.eea.europa.eu , ' + created, alignment: 'right', margin: [50, 10], };
          let objFooter = {};
          objFooter.columns = cols;
          doc.footer = objFooter;
        }
      },
      {
        extend: 'excel',
        filename: 'CIS2_DataProviders.',
        title: 'CIS2 Data Providers',
        text: 'Save as Excel',
      },
    ],
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>",
    },
    "stateSave": true,
    "stateSaveParams": function (_settings, data) {
      data.is_network = $('#is_network').val();
      data.provider_type = $('#provider_type').val();
      data.state = $('#state').val();
      data.component = $('#component').val();

      var keys = ['is_network', 'provider_type', 'state', 'component']
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

      $('#is_network').val(data.is_network);
      $('#provider_type').val(data.provider_type);
      $('#state').val(data.state);
      $('#component').val();
    },
    "drawCallback": function (_settings) {
      let info = $(this).closest('.dataTables_wrapper').find('.dataTables_info');
      info.toggle(this.api().page.info().recordsDisplay > 9);
    },
    "columnDefs": [
      {
        "render": function (data, _type, _row) {
          if (data) {
            return "<span class='glyphicon glyphicon-ok-circle " +
              "text-success'></span>";
          }
          else {
            return "<span class='glyphicon glyphicon-remove-circle " +
              "text-danger'></span>";
          }
        },
        "targets": [columnIndex],
        "bSortable": false
      }
    ]
  }).fnFilterOnReturn();

  $('#is_network,#provider_type,#state,#component').on('change', function (_event) {
    let table = $table.DataTable();
    table.ajax.reload();
  });

  $('#reset-btn').on('click', function () {
    $('#is_network,#provider_type,#state,#component').val('All');
    let table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });
});
