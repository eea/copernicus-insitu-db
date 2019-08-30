function GetTemplateSimple(identifier) {

  return identifier.DataTable({
    "lengthChange": false,
    "searching": false,
    "bInfo": false,
    "pageLength": 5,
  });
}

function GetTemplateDouble(identifier) {

  return identifier.DataTable({
    "lengthChange": false,
    "searching": false,
    "bInfo": false,
    "pageLength": 5,
    "columnDefs": [
      { "width": "50%", "targets": 0 },
      { "width": "50%", "targets": 1 }
    ],
  });
}


$(document).ready(function () {
  GetTemplateSimple($('#user_data'));
  GetTemplateSimple($('#user_providers'))
  GetTemplateSimple($('#user_requirements'));
  GetTemplateDouble($('#user_data_requirements'));
  GetTemplateDouble($('#user_provider_relationships'));
  GetTemplateDouble($('#user_product_requirements'));
});
