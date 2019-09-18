/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * UI Elements
 *------------------------------*/

var temperatureSpans   = new Array(0);
var tempUnitCRadio     = null;
var dialogSaveButton   = null;
var dialog             = null;
var pwmSliderTooltip   = null;
var container          = null;
var picker             = null;
        
var tempRefreshRate  = 10000;

/* -------------------------------*
 * UI Settings
 *------------------------------*/
function initUI() {
    getElements();

    setDialog();
    setSettingsDialog();
    setUIUpdater();
}

function getElements() {
    /* Get temperature spans */
    temperatureSpans.push($('#temperature_span_0'));
    temperatureSpans.push($('#temperature_span_1'));

    /* Get dialog */
    dialog = document.querySelector('dialog');

    /* Get dialogs elements */
    tempUnitCRadio   = $('#temp_unit_c_label');
    dialogSaveButton = $('#dialog_save_button');    
    pwmSliderTooltip = $('#pwm_slider_tooltip');
    container        = document.getElementById('color-picker');
    picker           = new CP(container, false, container);
}

function setDialog() {
    dialog.querySelector('.close').addEventListener('click', function () {
        dialog.close();
        picker.exit();
    });
    dialog.querySelector('.closeabout').addEventListener('click', function () {
        dialog.close();
    });
}

function setSettingsDialog() {
    dialog.querySelector('.save').addEventListener('click', function() {
        $.ajax({ 
            url: "/setTempUnit/".concat(tempUnitCRadio.hasClass('is-checked') ? "0" : "1")
        }).then(function() {
            dialog.close();
        });
    });
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
            tempUnit = "&deg;C";
            if(data.unit != 0)
                tempUnit = "&deg;F";
            tempStr = parseFloat(data.temp).toFixed(2) + tempUnit;
        }
        
        for (i = 0; i < temperatureSpans.length; ++i) { 
            temperatureSpans[i].fadeOut(200);
            temperatureSpans[i].html(tempStr);
            temperatureSpans[i].fadeIn(200);
        }
    });
}

function updatePWMSliderTooltip(value) {
    pwmSlider.html("" + value);
}
        

function showPWMDialog(id) {
    document.getElementById("dialog_title").innerHTML = "PWM Settings";
    document.getElementById("dialog_info").innerHTML = "Set the PWM value";

    document.getElementById("pwm_settings").style.display = "block";
    document.getElementById("rgb_settings").style.display = "none";
    document.getElementById("app_settings").style.display = "none";

    document.getElementById("cancel_save_block").style.display = "block";
    document.getElementById("close_block").style.display = "none";

    dialog.showModal();
}

function showRGBDialog(id) {
    document.getElementById("dialog_title").innerHTML = "RGB Settings";
    document.getElementById("dialog_info").innerHTML = "Set the RGB value";

    document.getElementById("pwm_settings").style.display = "none";
    document.getElementById("rgb_settings").style.display = "block";
    document.getElementById("app_settings").style.display = "none";

    document.getElementById("cancel_save_block").style.display = "block";
    document.getElementById("close_block").style.display = "none";

    dialog.showModal();
    picker.enter();
}

function showAbout() {
    document.getElementById("dialog_title").innerHTML = "About";
    document.getElementById("dialog_info").innerHTML = "<p style=\"text-align:justify\">Domohome &copy; Oxmose 2019<br /><br />Domohome is a domotic application aimed at managing electronic objects in the house.<br /><br /><a target=\"_blank\" href=\"https://github.com/Oxmose/DomoHome\">Github page</a></p>";

    document.getElementById("pwm_settings").style.display = "none";
    document.getElementById("rgb_settings").style.display = "none";
    document.getElementById("app_settings").style.display = "none";

    document.getElementById("cancel_save_block").style.display = "none";
    document.getElementById("close_block").style.display = "block";

    dialog.showModal();
}

function showSettings() {
    document.getElementById("dialog_title").innerHTML = "Settings";
    document.getElementById("dialog_info").innerHTML = "General application settings";

    document.getElementById("pwm_settings").style.display = "none";
    document.getElementById("rgb_settings").style.display = "none";
    document.getElementById("app_settings").style.display = "block";

    document.getElementById("cancel_save_block").style.display = "block";
    document.getElementById("close_block").style.display = "none";

    dialog.showModal();
}