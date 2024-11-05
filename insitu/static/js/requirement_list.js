function updateFilterOptions(filter, option_data) {
  let select = $('#' + filter);
  select.find('option').remove();
  select.append('<option value="All">All</option>');
  $.each(option_data.options, function (_i, option) {
    let selected = '';
    if (option_data.selected == option) {
      selected = ' selected';
    }
    select.append(
      '<option value="' + option + '"' + selected + '>' + option + '</option>');
  });
}
$(document).ready(function () {
  let buttonCommon = {
    exportOptions: {
      format: {
        header: function (data, _columnIdx) {
          return data.split('<span')[0].replace(/^\s+|\s+$/g, '');
        },
        body: function (data, row, _column, _node) {
          if (row === 0) {
            return $.parseHTML(data)[0].innerHTML.replace(/^\s+|\s+$/g, '');
          }
          if (row <= 10 && row >= 5) {
            let goal = $.parseHTML(data)[0].innerHTML;
            let breakthrough = $.parseHTML(data)[1].innerHTML;
            let threshold = $.parseHTML(data)[2].innerHTML;
            let metrics = '';
            if (goal) {
              metrics += 'Threshold: ' + '\n' + $.parseHTML(data)[0].innerHTML + '\n';
            }
            if (breakthrough) {
              metrics += 'Breakthrough: ' + '\n' + $.parseHTML(data)[1].innerHTML + '\n';
            }
            if (threshold) {
              metrics += 'Goal: ' + '\n' + $.parseHTML(data)[2].innerHTML + '\n';
            }
            return metrics.replace(/^\s+|\s+$/g, '');
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

  var $table = $('#requirements').dataTable({
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
        filename: 'CIS2_Requirements',
        title: 'CIS2 Requirements',
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
          filename: 'CIS2_Requirements.',
          title: 'CIS2 Requirements',
          text: 'Save as Excel',
        },
    ],
    "language": {
      "infoFiltered": "<span class='green-text'>(filtered from _MAX_ total records)<span>",
    },
    "ajax": {
      "url": $('#ajax-url').data('ajax-url'),
      "data": function (d) {
        d.dissemination = $('#dissemination').val();
        d.quality_control_procedure = $('#quality_control_procedure').val();
        d.group = $('#group').val();
        d.product = $('#product').val();
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
      data.dissemination = $('#dissemination').val();
      data.quality_control_procedure = $('#quality_control_procedure').val();
      data.group = $('#group').val();
      data.product = $('#product').val();
      data.status = $('#status').val();
      data.state = $('#state').val();
      data.component = $('#component').val();


      var keys = ['dissemination', 'quality_control_procedure', 'group', 'product', 'status', 'state', 'component']
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
    
      $('#dissemination').val(data.dissemination);
      $('#quality_control_procedure').val( data.quality_control_procedure);
      $('#group').val(data.group);
      $('#product').val(data.product);
      $('#status').val(data.status);
      $('#state').val(data.state);
      $('#component').val(data.component);
    },
    "drawCallback": function (_settings) {
      let info = $(this).closest('.dataTables_wrapper').find('.dataTables_info');
      info.toggle(this.api().page.info().recordsDisplay > 9);
    },
    "columnDefs": [
      {
        "render": function (data, _type, _row) {
          function generate_div(color, data) {
            return "<div class='col-sm-12 " + color + " no-padding-left'>" + data +
              "</div>";
          }

          let threshold = data.split('T: ').pop().split(' - B: ').shift();
          let breakthrough = data.split('B: ').pop().split(' - G: ').shift();
          let goal = data.split('G: ').pop();
          return (
            generate_div('orange', threshold) +
            generate_div('blue', breakthrough) +
            generate_div('green', goal));
        },
        "targets": [5, 6, 7, 8, 9, 10],
        "bSortable": false
      }
    ]
  }).fnFilterOnReturn();

  $('#dissemination,#quality_control_procedure,#group,#product,#status,#state,#component').on(
    'change', function (_event) {
      let table = $table.DataTable();
      table.ajax.reload();
    }
  );

  $('#reset-btn').on('click', function () {
    $('#dissemination,#quality_control_procedure,#group,#product,#status,#state,#component').val('All');
    let table = $table.DataTable();
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
