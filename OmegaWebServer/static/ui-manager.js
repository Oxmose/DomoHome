/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * Settings
 *------------------------------*/
var tempRefreshRate  = 10000;
var settings         = null;
var switches         = [];
var pwm              = [];
var rgb              = [];

/* -------------------------------*
 * UI Elements
 *------------------------------*/

var temperatureSpans   = new Array(0);
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
    getObjects();
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

function getObjects() {
    $.ajax({ 
        url: "/getObjects"
    }).then(function(data) {
        if(data.error == 0) {
            objects = data.objects;
            for(var key in objects) {
                if(objects[key].type == 0) {
                    switches.push({id: key, name: objects[key].name, state: objects[key].state});
                }
                else if(objects[key].type == 1 || objects[key].type == 3) {
                    pwm.push({id: key, name: objects[key].name, state: objects[key].state});
                }
                else if(objects[key].type == 2 || objects[key].type == 4) {
                    rgb.push({id: key, name: objects[key].name, state: objects[key].state});
                }
            }
        }
        else {
            getObjects();
        }

        updateObjects();
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
        }).then(function(data) {
            dialog.close();
            updateTemp();
        });

        getSettings();
    });

    dialog.showModal();
}

function updateObjects() {
    if(switches.length != 0) {
        list = $('#switches_block_list');
        for(let i = 0; i < switches.length; ++i) {
            item = $('<li>')
            item.html('<label for="' + switches[i].id + '_sw_chkbox" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect"> \
                            <input type="checkbox" id="' + switches[i].id + '_sw_chkbox" class="mdl-checkbox__input"> \
                            <span class="mdl-checkbox__label">' + switches[i].name + '</span> \
                        </label>');
            list.append(item);
        }
        if(switches.length == 1) {
            $('#switches_block_container').append("<br />");
        }
    }
    else {
        $('#switches_block').hide();
    }

    if(pwm.length != 0) {
        list = $('#pwm_block_list');
        for(let i = 0; i < pwm.length; ++i) {
            item = $('<li>')
            item.html('<label for="' + pwm[i].id + '_pwm_chkbox" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect"> \
                            <button onclick="showPWMDialog(' + pwm[i].id + ')" \
                                class="mdl-button mdl-js-button mdl-button--icon mdl-button--colored" \
                                style="margin-top: -5px;"> \
                                <i class="material-icons">settings_applications</i> \
                            </button>&nbsp;&nbsp;&nbsp; \
                            <input type="checkbox" id="' + pwm[i].id + '_pwm_chkbox" class="mdl-checkbox__input"> \
                            <span class="mdl-checkbox__label">' + pwm[i].name + '</span> \
                        </label>');
            list.append(item);
        }
        if(pwm.length == 1) {
            $('#pwm_block_container').append("<br />");
        }
    }
    else {
        $('#pwm_block').hide();
    }

    if(rgb.length != 0) {
        list = $('#rgb_block_list');
        for(let i = 0; i < rgb.length; ++i) {
            item = $('<li>')
            item.html('<label for="' + rgb[i].id + '_rgb_chkbox" class="mdl-checkbox mdl-js-checkbox mdl-js-ripple-effect"> \
                            <button onclick="showRGBDialog(' + rgb[i].id + ')" \
                                class="mdl-button mdl-js-button mdl-button--icon mdl-button--colored" \
                                style="margin-top: -5px;"> \
                                <i class="material-icons">settings_applications</i> \
                            </button>&nbsp;&nbsp;&nbsp; \
                            <input type="checkbox" id="' + rgb[i].id + '_rgb_chkbox" class="mdl-checkbox__input"> \
                            <span class="mdl-checkbox__label">' + rgb[i].name + '</span> \
                        </label>');
            list.append(item);
        }
        if(rgb.length == 1) {
            $('#rgb_block_container').append("<br />");
        }
    }
    else {
        $('#rgb_block').hide();
    }


}