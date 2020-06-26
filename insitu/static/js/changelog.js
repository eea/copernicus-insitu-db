$(document).ready(function () {
  let scroll_size = $('#id_changelog_container').height()
  $('#id_changelog').DataTable({
    "lengthChange": false,
    "searching": false,
    "pageLength": 5,
    "ordering": false,
    "bInfo": false,
    "columnDefs": [
      { "orderable": false, "targets": 0 }
    ],
    "dom": 't<"bottom"flp><"clear">',
    "bScrollCollapse" : false,
    "sScrollY": scroll_size,
  });
});
