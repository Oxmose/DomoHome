/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * Settings
 *------------------------------*/
var tempRefreshRate  = 10000;
var settings         = null;
var switches         = {};
var pwm              = {};
var rgb              = {};
var objTypes         = {};

/* -------------------------------*
 * UI Elements
 *------------------------------*/

var temperatureSpans   = new Array(0);
var humiditySpans      = new Array(0);
var tempUnitCRadio     = null;
var tempUnitFRadio     = null;
var dialogSaveButton   = null;
var dialog             = null;
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
        url: "/getSettings",
    	async: false
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
    temperatureSpans.push($('#temp_span_inside_1'));
    temperatureSpans.push($('#temp_span_inside_2'));
    
    humiditySpans.push($('#humidity_span_inside_0'))

    /* Get dialog */
    dialog = document.querySelector('dialog');

    /* Get dialogs elements */
    tempUnitCRadio   = $('#temp_unit_c_label');
    tempUnitFRadio   = $('#temp_unit_f_label');
    dialogSaveButton = $('#dialog_save_button');    
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
	var el = dialog.querySelector('.close');
    elClone = el.cloneNode(true);
	el.parentNode.replaceChild(elClone, el);
    dialog.querySelector('.close').addEventListener('click', function () {
        dialog.close();
        picker.exit();
    });
    var el = dialog.querySelector('.closeabout');
    elClone = el.cloneNode(true);
	el.parentNode.replaceChild(elClone, el);
    dialog.querySelector('.closeabout').addEventListener('click', function () {
        dialog.close();
    });
}

/* -------------------------------*
 * UI Updater
 *------------------------------*/
function setUIUpdater() {
    /* Set temperature thread updater */
    updateLoopEnv();
    
    /* Update weather */
    updateWeather();
}

function updateLoopEnv(){
    $.ajax({ 
        url: "/getEnv",
        complete: function(){
            setInterval(updateEnv, tempRefreshRate);
            
            $("#loading_screen").fadeOut(500);
        }
    }).then(function(data) {
        tempStr = "Unknown environment";
        humStr = "Unknown environment";
        if(data.error == 0) {
            tempUnit = "&deg;C";
            if(data.unit != 0)
                tempUnit = "&deg;F";
            tempStr = parseFloat(data.temp).toFixed(2) + tempUnit;
            humStr = parseFloat(data.humidity).toFixed(2) + "%";
        }
        
        for (i = 0; i < temperatureSpans.length; ++i) {
            temperatureSpans[i].html(tempStr);
            
        }
        for(i = 0; i < humiditySpans.length; ++i) {
        	humiditySpans[i].html(humStr);
        }
    });
}

function updateEnv(){
    $.ajax({ 
        url: "/getEnv"
    }).then(function(data) {
        tempStr = "Unknown temperature";
        humStr = "Unknown environment";
        if(data.error == 0) {
            tempUnit = "&deg;C";
            if(data.unit != 0)
                tempUnit = "&deg;F";
            tempStr = parseFloat(data.temp).toFixed(2) + tempUnit;
            humStr = parseFloat(data.humidity).toFixed(2) + "%";
        }
        
        for (i = 0; i < temperatureSpans.length; ++i) { 
            temperatureSpans[i].html(tempStr);
        }
        for(i = 0; i < humiditySpans.length; ++i) {
        	humiditySpans[i].html(humStr);
        }
    });
}

function updateWeather(){
	$.ajax({ 
        url: "http://api.openweathermap.org/data/2.5/weather?id=" + settings.openweatherId + "&appid=" + settings.openweatherKey
    }).then(function(data) {
    	tempFloat = 0.0;
    	tempStr = "???";
        humStr = "???";
        windStr = "???";
        if(data.cod == 200) {
            tempUnit = "&deg;C";
            windUnit = "Km/H";
            tempFloat = data.main.temp;
            if(settings.tempUnit != 0) {
            	tempFloat = (tempFloat - 273.15) * 9/5 + 32;
                tempUnit = "&deg;F";
            }
            else {
            	tempFloat -= 273.15;
            }
            	
            tempStr = parseFloat(tempFloat).toFixed(2) + tempUnit;
            humStr = parseFloat(data.main.humidity).toFixed(2) + "%";
            windStr = parseFloat(data.wind.speed).toFixed(2) + windUnit + " | " + data.wind.deg + "&deg;";
            
            $('#temp_span_outside').html(tempStr);
            $('#humidity_span_outside').html(humStr);
            $('#wind_span_outside').html(windStr);
        }
       
    });
}

function showAbout() {
    dialogTitle.html("About");
    dialogInfo.html("<p style=\"text-align:justify\">Domohome &copy; Alexy Torres 2020<br /><br />Domohome is a domotic application aimed at managing connected objects in the house.<br /><br /><a target=\"_blank\" href=\"https://github.com/Oxmose/DomoHome\">Github page</a></p>");

    pwmSettings.css("display", "none");
    rgbSettings.css("display", "none");
    appSettings.css("display", "none");

    cancelSaveBlock.css("display", "none");
    closeBlock.css("display", "block");

    dialog.showModal();
}

function showSettings() {
    dialogTitle.html("Settings");

    pwmSettings.css("display", "none");
    rgbSettings.css("display", "none");
    appSettings.css("display", "block");

    cancelSaveBlock.css("display", "block");
    closeBlock.css("display", "none");

    if(settings.tempUnit == 0) {
        tempUnitCRadio.addClass('is-checked');
        tempUnitFRadio.removeClass('is-checked');
    }
    else {
        tempUnitCRadio.removeClass('is-checked');
        tempUnitFRadio.addClass('is-checked');
    }
    
    var el = dialog.querySelector('.save');
    elClone = el.cloneNode(true);
	el.parentNode.replaceChild(elClone, el);
    dialog.querySelector('.save').addEventListener('click', function() {
        $.ajax({ 
            url: "/setTempUnit/".concat(tempUnitCRadio.hasClass('is-checked') ? "0" : "1")
        }).then(function(data) {
            dialog.close();
            updateTemp();
        });

        getSettings();
    });

    dialog.showModal();
}


/* -------------------------------*
 * Server Settings
 *------------------------------*/
function rebootServer() {
    $.ajax({ 
        url: "/reboot"
    }).then(function() {
        location.reload();
    });
}

/* -------------------------------*
 * Server Queries
 *------------------------------*/
