let spreadsheet="SPREADSHEET_ID";

function myFunction() {
  try{
    var sheet = SpreadsheetApp.openById(spreadsheet).getSheetByName("paper1");
    var data = sheet.getDataRange().getLastRow();
    Logger.log(data)
  }catch(e){
    Logger.log("You can't get marks of that paper this time !")
  }

}

function searchWord(word, key, sheet) {
  var results = [];
  try{
    var sheet = SpreadsheetApp.openById(spreadsheet).getSheetByName(sheet);
    var data = sheet.getDataRange().getValues();
    for (var i = 0; i < data.length; i++) {
        if (String(data[i][key]).indexOf(word) !== -1) {
          results.push(data[i]);
        }
    }
  }catch(e){

  }
  return results;
}

function doPost(e) {
  let data = e.parameter;

  // Process the received data or perform any other necessary actions
  let sp = data.sheet_id;
  let message = data.message;
  let res = searchWord(message, 3, sp);
  let response;

  if(res.length > 0){
    // Create a response object
    response = {
      status: "success",
      message: "Received POST request successfully",
      data: res
    };
  }else{
    // Create a response object
    response = {
      status: "failed",
      message: "Data not found",
    };
  }

  // Return the response as JSON
  return ContentService.createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON);
}
