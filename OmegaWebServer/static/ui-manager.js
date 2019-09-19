/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * Settings
 *------------------------------*/
var tempRefreshRate  = 10000;
var settings         = null;

/* -------------------------------*
 * UI Elements
 *------------------------------*/

var temperatureSpans   = new Array(0);
var tempUnitCRadio     = null;
var tempUnitFRadio     = null;
var dialogSaveButton   = null;
var dialog             = null;
var pwmSliderTooltip   = null;
var container          = null;
var picker             = null;
var dialogTitle        = null;
var dialogInfo         = null;
var pwmSettings        = null;
var rgbSettings        = null;
var appSettings        = null;
var cancelSaveBlock    = null;
var closeBlock         = null;

/* -------------------------------*
 * UI Settings
 *------------------------------*/
function initUI() {
    getSettings();
    getElements();

    setDialog();
    setUIUpdater();
}

function getSettings() {
    $.ajax({ 
        url: "/getSettings"
    }).then(function(data) {
        if(data.error == 0) {
            settings = data.settings;
        }
        else {
            getSettings();
        }
    });
}

function getElements() {
    /* Get temperature spans */
    temperatureSpans.push($('#temperature_span_0'));
    temperatureSpans.push($('#temperature_span_1'));

    /* Get dialog */
    dialog = document.querySelector('dialog');

    /* Get dialogs elements */
    tempUnitCRadio   = $('#temp_unit_c_label');
    tempUnitFRadio   = $('#temp_unit_f_label');
    dialogSaveButton = $('#dialog_save_button');    
    pwmSliderTooltip = $('#pwm_slider_tooltip');
    container        = document.getElementById('color-picker');
    picker           = new CP(container, false, container);
    dialogTitle      = $('#dialog_title');
    dialogInfo       = $('#dialog_info');
    pwmSettings      = $('#pwm_settings');
    rgbSettings      = $('#rgb_settings');
    appSettings      = $('#app_settings');
    cancelSaveBlock  = $('#cancel_save_block');
    closeBlock       = $('#close_block');
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


/* -------------------------------*
 * UI Updater
 *------------------------------*/
function setUIUpdater() {
    /* Set temperature thread updater */
    updateLoopTemp();
}

function updateLoopTemp(){
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

function updateTemp(){
    $.ajax({ 
        url: "/getTemp"
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
    dialogTitle.html("PWM Settings");
    dialogInfo.html("Set the PWM value");

    pwmSettings.css("display", "block");
    rgbSettings.css("display", "none");
    appSettings.css("display", "none");

    cancelSaveBlock.css("display", "block");
    closeBlock.css("display", "none");

    dialog.showModal();
}

function showRGBDialog(id) {
    dialogTitle.html("RGB Settings");
    dialogInfo.html("Set the RGB value");

    pwmSettings.css("display", "none");
    rgbSettings.css("display", "block");
    appSettings.css("display", "none");

    cancelSaveBlock.css("display", "block");
    closeBlock.css("display", "none");

    dialog.showModal();
    picker.enter();
}

function showAbout() {
    dialogTitle.html("About");
    dialogInfo.html("<p style=\"text-align:justify\">Domohome &copy; Oxmose 2019<br /><br />Domohome is a domotic application aimed at managing electronic objects in the house.<br /><br /><a target=\"_blank\" href=\"https://github.com/Oxmose/DomoHome\">Github page</a></p>");

    pwmSettings.css("display", "none");
    rgbSettings.css("display", "none");
    appSettings.css("display", "none");

    cancelSaveBlock.css("display", "none");
    closeBlock.css("display", "block");

    dialog.showModal();
}

function showSettings() {
    dialogTitle.html("Settings");
    dialogInfo.html("General application settings");

    pwmSettings.css("display", "none");
    rgbSettings.css("display", "none");
    appSettings.css("display", "block");

    cancelSaveBlock.css("display", "block");
    closeBlock.css("display", "none");

    console.log(settings);
    if(settings.tempUnit == 0) {
        tempUnitCRadio.addClass('is-checked');
        tempUnitFRadio.removeClass('is-checked');
    }
    else {
        tempUnitCRadio.removeClass('is-checked');
        tempUnitFRadio.addClass('is-checked');
    }
    dialog.querySelector('.save').addEventListener('click', function() {
        $.ajax({ 
            url: "/setTempUnit/".concat(tempUnitCRadio.hasClass('is-checked') ? "0" : "1")
        }).then(function() {
            dialog.close();
            updateTemp();
        });
    });

    dialog.showModal();
}