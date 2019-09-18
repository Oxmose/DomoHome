/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * UI Elements
 *------------------------------*/

var temperatureSpans = new Array(0);

var tempUnit        = "&deg;C";
var tempRefreshRate = 10000;

/* -------------------------------*
 * UI Settings
 *------------------------------*/
function initUI() {
    getElements();

    setUIUpdater();
}

function getElements() {
    /* Get temperature spans */
    temperatureSpans.push($('#temperature_span_0'));
    temperatureSpans.push($('#temperature_span_1'));
}
/* -------------------------------*
 * UI Updater
 *------------------------------*/
function setUIUpdater() {
    /* Set temperature thread updater */
    updateTemp();


}

function updateTemp(){
    $.ajax({ 
        url: "/getTemp",
        complete: function(){
            setTimeout(updateTemp, tempRefreshRate);
        }
    }).then(function(data) {
        tempStr = "Unknown temperature";
        if(data.error == 0) {
            tempStr = parseFloat(data.temp).toFixed(2) + tempUnit;
        }
        
        for (i = 0; i < temperatureSpans.length; ++i) { 
            temperatureSpans[i].fadeOut(200);
            temperatureSpans[i].html(tempStr);
            temperatureSpans[i].fadeIn(200);
        }
    });
}