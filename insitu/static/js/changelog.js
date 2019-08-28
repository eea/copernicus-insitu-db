$(document).ready(function () {
  let scroll_size = $('#id_changelog_container').height()
  $('#id_changelog').DataTable({
    "order": [[ 0, "desc" ]],
    "lengthChange": false,
    "searching": false,
    "pageLength": 5,
    "bInfo": false,
    "columnDefs": [
      { "orderable": false, "targets": 0 }
    ],
    "dom": 't<"bottom"flp><"clear">',
    "bScrollCollapse" : false,
    "sScrollY": scroll_size,
  });
});
