parser = new Parser();
var rowIndex = 0;

function readSingleFile(e) {
    var file = e.target.files[0];
    if (!file) {
      return;
    }
    var reader = new FileReader();
    reader.onload = function(e) {
      var contents = e.target.result;
      // Display file content
      console.log(contents)
    };
    reader.readAsText(file);
}

function addRow(){
  var rowHTML = "<tr id = 'row_"+rowIndex+"'><td><select id= 'row_" +rowIndex+"_command' ><option value='Delimitter'>Delimitter</option><option value='RegEx'>RegEx</option><option value='XML'>XML</option></select></td><td><input id = 'row_" + rowIndex+ "_index' type='number'></td><td><input id = 'row_" + rowIndex+ "_fieldName' type='text'></td><td><input id = 'row_" + rowIndex +"_expression' type='text'></td><td><button id = 'row_" + rowIndex +"_delete' type='button'>X</button></td></tr>"
  $('#fieldTable > tbody').append($(rowHTML));

  var deleteBtn = $('#row_'+rowIndex+'_delete').click(function(i) {
    var rowID = "#"+i.target.id.replace("_delete","");
    removeRow(rowID);
  });

  rowIndex++;
}
function removeRow(id){
  $(id).remove();
}
function getCommandTable(){
  var table = [[]];

  for(var i = 0; i< rowIndex; i++){
    table[i]["command"] = $('#row_'+i+'_command').val();
    table[i]["index"] = $('#row_'+i+'_index').val();
    table[i]["fieldName"] = $('#row_'+i+'_fieldName').val();
    table[i]["expression"] = $('#row_'+i+'_expression').val();
  }
  return table;
}
