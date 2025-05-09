/*jshint multistr: true */

function updateFilterOptions(filter, option_data) {
  var select = $('#' + filter);
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
    if (filter == 'copernicus_service_product') {
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

  var $table = $('#data').dataTable({
    "processing": true,
    "serverSide": true,
    "dom": "<'row'<'col-sm-12'B>>" +
      "<'row'<'col-sm-5'i><'col-sm-12'f><'col-sm-4 display-margin'l><'col-sm-8'p>>" +
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
      filename: 'CIS2_Data',
      title: 'CIS2 Data',
      orientation: 'landscape',
      customize: function (doc) {
        var cols = [];
        var created = new Date().toDateString();
        cols[0] = { text: 'https://cis2.eea.europa.eu , ' + created, alignment: 'right', margin: [50, 10], };
        var objFooter = {};
        objFooter.columns = cols;
        doc.footer = objFooter;
      }
    },
    {
      extend: 'excel',
      filename: 'CIS2_Data.',
      title: 'CIS2 Data',
      text: 'Save as Excel',
    },
    ],
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>",
    },
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.id = $('#id').val();
        d.name = $('#name').val();
        d.update_frequency = $('#update_frequency').val();
        d.area = $('#area').val();
        d.timeliness = $('#timeliness').val();
        d.data_policy = $('#data_policy').val();
        d.data_type = $('#data_type').val();
        d.copernicus_service_product = $('#copernicus_service_product').val();
        d.data_format = $('#data_format').val();
        d.quality_control_procedure = $('#quality_control_procedure').val();
        d.dissemination = $('#dissemination').val();
        d.requirement = $('#requirement').val();
        d.status = $('#status').val();
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
    "stateSave": true,
    "stateSaveParams": function (_settings, data) {
      data.update_frequency = $('#update_frequency').val();
      data.area = $('#area').val();
      data.timeliness = $('#timeliness').val();
      data.data_policy = $('#data_policy').val();
      data.data_type = $('#data_type').val();
      data.copernicus_service_product = $('#copernicus_service_product').val();
      data.data_format = $('#data_format').val();
      data.quality_control_procedure = $('#quality_control_procedure').val();
      data.dissemination = $('#dissemination').val();
      data.requirement = $('#requirement').val();
      data.status = $('#status').val();
      data.state = $('#state').val();
      data.component = $('#component').val();

      var keys = ['update_frequency', 'area', 'timeliness', 'data_policy', 'data_type',  "copernicus_service_product", 'data_format', 'quality_control_procedure', 'dissemination', 'requirement', 'status', 'state', 'component']
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

      $('#update_frequency').val(data.update_frequency);
      $('#area').val(data.area);
      $('#timeliness').val(data.timeliness);
      $('#data_policy').val(data.data_policy);
      $('#data_type').val(data.data_type);
      $('#copernicus_service_product').val(data.copernicus_service_product);
      $('#data_format').val(data.data_format);
      $('#quality_control_procedure').val(data.quality_control_procedure);
      $('#dissemination').val(data.dissemination);
      $('#requirement').val(data.requirement);
      $('#status').val(data.status);
      $('#state').val(data.state);
      $('#component').val();
    },
    "drawCallback": function (_settings) {
      var info = $(this).closest('.dataTables_wrapper').find('.dataTables_info');
      info.toggle(this.api().page.info().recordsDisplay > 9);
    },
  }).fnFilterOnReturn();

  $('#id,#name,#update_frequency,#area,#timeliness,#data_policy,#data_type,#copernicus_service_product,\
      #data_format,#quality_control_procedure,#dissemination,#requirement,#status,\
      #state,#component').on(
    'change', function (_event) {
      var table = $table.DataTable();
      table.ajax.reload();
    });

  $('#reset-btn').on('click', function () {
    $('#id,#name,#update_frequency,#area,#timeliness,#data_policy,#data_type,#copernicus_service_product,\
      #data_format,#quality_control_procedure,#dissemination,#requirement,#status,\
      #state,#component').val('All');
    var table = $table.DataTable();
    table.state.clear();
    table.ajax.reload();
    table.search('').draw();
  });
});
