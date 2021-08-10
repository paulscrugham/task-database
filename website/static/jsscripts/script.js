// Source: adapted from https://www.w3schools.com/howto/howto_js_filter_table.asp

function searchFilter(input_id, table_id, col_index) {
  var input, filter, table, tr, td, i, txtValue;
  input = document.getElementById(input_id);
  filter = input.value.toUpperCase();  // get upper case to match with table contents
  table = document.getElementById(table_id);
  tr = table.getElementsByTagName("tr");

  // iterate over rows and hide row if search term is not present
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[col_index];  // select column to filter with its index
    if (td) {
      txtValue = td.textContent || td.innerText;
      if (txtValue.toUpperCase().indexOf(filter) > -1) {  // get upper case to match with search term
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";  // hides the row
      }
    }
  }
}