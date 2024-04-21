//exampleJS.js Java script example file
// created Apr 21, 2024
// modified Apr 21, 2024

document.write("js file loaded successfully");

var lEDStatusArea = document.getElementById("LEDStatusArea");

// LED toggle button Click function to set toggle the
// connected LED
var ledMode = document.getElementById("ledToggle");
ledMode.onclick= function(){
    event.preventDefault();    
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange=function(){
        if (xhr.readyState === 4){            
           receivedData = JSON.parse(xhr.responseText);           
           if (receivedData.buttonUpdate === 'true'){
                var LEDStatus = receivedData.LEDStatus;
                if (LEDStatus === 'ON'){
                    lEDStatusArea.innerHTML = "";
                    lEDStatusArea.innerHTML = "<p class = 'ledStatus'>LED Status: ON</p>";
                }
                else{
                    lEDStatusArea.innerHTML = "";
                    lEDStatusArea.innerHTML = "<p class = 'ledStatus'>LED Status: OFF</p>";
                }
            }
        }
    }
    xhr.open("post","/ledToggle",false);
    var sendInfo ={mode:'toggle'},
    jsonData=JSON.stringify(sendInfo);
    xhr.send(jsonData);
    return;
};
