// Source: adapted from https://www.w3schools.com/howto/howto_js_filter_table.asp

function searchFilter(input_id, table_id, col_index) {
  // Declare variables
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById(input_id);
  filter = input.value.toUpperCase();
  table = document.getElementById(table_id);
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[col_index];
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}