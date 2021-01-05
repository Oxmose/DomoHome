/*******************************************************************************
 * UI MANAGEMENT
 ******************************************************************************/

/* -------------------------------*
 * Settings
 *------------------------------*/
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

var settingsDialog     = null;
var aboutDialog        = null;
var historyDialog      = null;
var pwmDialog          = null;
var rgbDialog          = null;

var lastAboutCloneListener = null;
var lastHistCloseListener = null;
var lastSettingsCloseListener = null;
var lastSettingsSaveListener = null;
var lastPWMSwitchBTNListener = null;
var lastPWMValueListener = null;
var lastPWMCloseListener = null;
var lastRGBSwitchBTNListener = null;
var lastRGBCloseListener = null;

window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(201, 203, 207)'
};

/* -------------------------------*
 * UI Settings
 *------------------------------*/
function initUI() {
    getSettings();
    getElements();
	getObjects();
	
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
    temperatureSpans.push($('#temp_span_inside_2'));
    
    humiditySpans.push($('#humidity_span_inside_0'))

    /* Get dialog */
    settingsDialog = document.querySelector('#settings_dialog');
    aboutDialog = document.querySelector('#about_dialog');
    historyDialog = document.querySelector('#history_dialog');
    pwmDialog = document.querySelector('#pwm_dialog');
    rgbDialog = document.querySelector('#rgb_dialog');
    
    /* Get dialogs elements */
    openweaterKeyInput = $('#openweater_key');
    openweaterIdInput  = $('#openweater_cityid');
}

/* -------------------------------*
 * UI Updater
 *------------------------------*/
function setUIUpdater() {
    /* Set temperature thread updater */
    updateLoopEnv();
}


function updateEnvUi(data) {
    tempStr = "Unknown temperature";
    humStr = "Unknown environment";
    temp = parseFloat(data.temp);
    if(data.error == 0) {
        if(data.unit == 0) {
            tempUnit = "&deg;C";
            temp -= 273.15; 
        }
        else {
            tempUnit = "&deg;F";
            temp = (temp - 273.15) * 9 / 5 + 32;
        }
        tempStr = temp.toFixed(2) + tempUnit;
        humStr = parseFloat(data.humidity).toFixed(2) + "%";
    }
    
    for (i = 0; i < temperatureSpans.length; ++i) { 
        temperatureSpans[i].html(tempStr);
    }
    for(i = 0; i < humiditySpans.length; ++i) {
    	humiditySpans[i].html(humStr);
    }
}

function updateLoopEnv(){
    /* Update weather */
    updateWeather();
    
    $.ajax({ 
        url: "/getEnv",
        complete: function(){
            $("#loading_screen").fadeOut(300);
        }
    }).then(function(data) {
        updateEnvUi(data);
    });
}

function updateEnv(){
    $.ajax({ 
        url: "/getEnv"
    }).then(function(data) {
        updateEnvUi(data);
        updateWeather();
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
            windStr = parseFloat(data.wind.speed).toFixed(2) + windUnit + "    " + data.wind.deg + "&deg;";
            
            $('#temp_span_outside').html(tempStr);
            $('#humidity_span_outside').html(humStr);
            $('#wind_span_outside').html(windStr);
        }
       
    });
}



function showAbout() {
    
    if(lastAboutCloneListener != null) {
        aboutDialog.querySelector('.close').removeEventListener('click', lastAboutCloneListener);
    }
    
    lastAboutCloseListener = function() {
      aboutDialog.close();
    };
    
    aboutDialog.querySelector('.close').addEventListener('click', lastAboutCloseListener);
    aboutDialog.showModal();
}

function showHistory() {
    console.log("Sending data");
    $.ajax({ 
        url: "/getEnvHist"
    }).then(function(data) {
        if(data.error == 0) {
    	    drawHistory(data.data);
        }
        else {
            alert("Error while gathering data: " + data.error);
        }
    });
}

function prepend(value, array) {
  var newArray = array.slice();
  newArray.unshift(value);
  return newArray;
}

function drawHistory(data) {
    var firstIndex = data[1];
    
    var tempLabel = 'Temperature (°';
    if(settings.tempUnit != 0) {
        tempLabel = tempLabel.concat('F)');
    }
    else {
        tempLabel = tempLabel.concat('C)');
    }
        
    var lineChartData = {
			labels: [],
			datasets: [{
				label: 'Humidity (%)',
				borderColor: window.chartColors.red,
				backgroundColor: window.chartColors.red,
				fill: false,
				data: [
					
				],
				yAxisID: 'y-axis-1',
			}, {
				label: tempLabel,
				borderColor: window.chartColors.blue,
				backgroundColor: window.chartColors.blue,
				fill: false,
				data: [
					
				],
				yAxisID: 'y-axis-2'
			}]
		};
		
	
	do{
	    if(data[0][firstIndex][0] == -1) {
	        break;
	    }
	    lineChartData.labels = prepend(data[0][firstIndex][2], lineChartData.labels);
	    lineChartData.datasets[0].data = prepend(data[0][firstIndex][0], lineChartData.datasets[0].data);
	    lineChartData.datasets[1].data = prepend(data[0][firstIndex][1], lineChartData.datasets[1].data);
	    if(settings.tempUnit != 0) {
	        lineChartData.datasets[1].data[0] = (lineChartData.datasets[1].data[0] - 273.15) * 9/5 + 32
	    }
	    else {
	        lineChartData.datasets[1].data[0] = lineChartData.datasets[1].data[0] - 273.15;
	    }
	    
	    if(firstIndex == 0) {
	        firstIndex = data[0].length - 1;
	    }
	    else {
	        firstIndex -= 1;
	    }
	}while(firstIndex != data[1]);
	
	
    var ctx = document.getElementById('history_chart').getContext('2d');
    Chart.defaults.global.defaultFontColor = 'white';
    Chart.scaleService.updateScaleDefaults('linear', {
        ticks: {
            autoSkip: false
        }
    });
    window.myLine = Chart.Line(ctx, {
    	data: lineChartData,
    	options: {
    		responsive: true,
    		hoverMode: 'nearest',
    		stacked: false,
    		minRotation: 90,
    		maxRotation: 90,
    		autoSkip: false,
    		title: {
    			display: true,
    			text: ''
    		},
    		scales: {
    			yAxes: [{
    				type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
    				display: true,
    				position: 'left',
    				id: 'y-axis-1',
    			}, {
    				type: 'linear', // only linear but allow scale type registration. This allows extensions to exist solely for log scale for instance
    				display: true,
    				position: 'right',
    				id: 'y-axis-2',
    
    				// grid line settings
    				gridLines: {
    					drawOnChartArea: false, // only want the grid lines for one axis to show up
    				},
    			}],
    		}
    	}
    });
    
    if(lastHistCloseListener != null) {
        historyDialog.querySelector('.close').removeEventListener('click', lastHistCloseListener);
    }
    
    lastHistCloseListener = function() {
      historyDialog.close();
    };

    historyDialog.querySelector('.close').addEventListener('click', lastHistCloseListener);
    historyDialog.showModal();
}

function showSettings() {
    console.log(settings);
    
    if(lastSettingsCloseListener != null) {
        settingsDialog.querySelector('.close').removeEventListener('click', lastSettingsCloseListener);
    }
    
    lastSettingsCloseListener = function() {
      settingsDialog.close();
    };
    
    settingsDialog.querySelector('.close').addEventListener('click', lastSettingsCloseListener);
    
    if(lastSettingsSaveListener != null) {
        settingsDialog.querySelector('.save').removeEventListener('click', lastSettingsSaveListener);
    }
    
    lastSettingsSaveListener = function() {
        $.ajax({ 
            url: "/setSettings/".concat($('#temp_unit_c_label').hasClass('is-checked') ? "0" : "1")
                                .concat("/")
                                .concat($('#openweater_cityid').val())
                                .concat("/")
                                .concat($('#env_refresh_rate').val())
                                .concat("/")
                                .concat($('#env_history').val())
        }).then(function(data) {
            settingsDialog.close();
            getSettings();
            updateEnv();
        });
    };
    
    settingsDialog.querySelector('.save').addEventListener('click', lastSettingsSaveListener);

    settingsDialog.showModal();
    
    if(settings.tempUnit == 1) {
        $('#temp_unit_c_label').removeClass('is-checked');
        $('#temp_unit_f_label').addClass('is-checked');
    }
    else {
        $('#temp_unit_f_label').removeClass('is-checked');
        $('#temp_unit_c_label').addClass('is-checked');
    }
    
    $('#openweater_cityid').val(settings.openweatherId);
    $('#openweater_cityid').parent().addClass('is-dirty');
    
    settingsDialog.querySelector('#env_refresh_rate').MaterialSlider.change(settings.envUpdatePeriod);
    settingsDialog.querySelector('#env_history').MaterialSlider.change(settings.envUpdateMemory);
    
    updateSettingsSliders();
}

function updateSettingsSliders() {
    $('#env_refresh_rate_val').html($('#env_refresh_rate').val() + 's');
    $('#env_history_val').html($('#env_history').val());
}

function updateSwitches() {
    if(switches.length != 0) {
        list = $('#switches_block');
        lastBlock = $('<div class="button_group_duo">');
        
        var i = 0;
        for (var key in switches) {
        	if(i != 0 && i % 2 == 0)
        	{
        		list.append(lastBlock);
        		lastBlock = $('<div class="button_group_duo">');
        	}
        	
        	card = $('<div class="demo-card-square mdl-card mdl-shadow--2dp switch_card">');
        	item = $('<div class="mdl-card__supporting-text">');
        	title = $('<div class="title">');
        	title.html(switches[key].name);
        	icon = $('<i class="mdl-color-text--blue-grey-800 material-icons" role="presentation" style="font-size: 80px; margin:auto">');
        	if(switches[key].state)
        	{
        		icon.html("power");
        		card.addClass("switch_card_on");
        	}
        	else 
        	{
        		icon.html("power_off");
        		card.addClass("switch_card_off");
        	}
        	
        	card.data("objId", key);
        	
        	card.click(function() {
        		toggleObject($(this));
        	});
            
            item.append(title);
            card.append(icon);
            card.append(item);
            lastBlock.append(card);
        }
        list.append(lastBlock);
    }
    else {
        $('#switches_block').hide();
    }
}

function updatePWM() {
    if(pwm.length != 0) {
        list = $('#pwm_block');
        lastBlock = $('<div class="button_group_duo">');
        
        var i = 0;
        for (var key in pwm) {
        	if(i != 0 && i % 2 == 0)
        	{
        		list.append(lastBlock);
        		lastBlock = $('<div class="button_group_duo">');
        	}
        	
        	card = $('<div class="demo-card-square mdl-card mdl-shadow--2dp switch_card">');
        	item = $('<div class="mdl-card__supporting-text">');
        	title = $('<div class="title">');
        	title.html(pwm[key].name);
        	icon = $('<i class="mdl-color-text--blue-grey-800 material-icons" role="presentation" style="font-size: 80px; margin:auto">');
        	icon.html("slow_motion_video");
        	if(pwm[key].state)
        	{
        		card.addClass("switch_card_on");
        	}
        	else 
        	{
        		card.addClass("switch_card_off");
        	}
        	
        	card.data("objId", key);
        	
        	card.click(function() {
        		showPWMModal($(this));
        	});
            
            item.append(title);
            card.append(icon);
            card.append(item);
            lastBlock.append(card);
        }
        list.append(lastBlock);
    }
    else {
        $('#pwm_block').hide();
    }
}

function updateRGB() {
    if(rgb.length != 0) {
        list = $('#rgb_block');
        lastBlock = $('<div class="button_group_duo">');
        
        var i = 0;
        for (var key in rgb) {
        	if(i != 0 && i % 2 == 0)
        	{
        		list.append(lastBlock);
        		lastBlock = $('<div class="button_group_duo">');
        	}
        	
        	card = $('<div class="demo-card-square mdl-card mdl-shadow--2dp switch_card">');
        	item = $('<div class="mdl-card__supporting-text">');
        	title = $('<div class="title">');
        	title.html(rgb[key].name);
        	icon = $('<i class="mdl-color-text--blue-grey-800 material-icons" role="presentation" style="font-size: 80px; margin:auto">');
        	icon.html("group_work");
        	if(rgb[key].state)
        	{
        		card.addClass("switch_card_on");
        	}
        	else 
        	{
        		card.addClass("switch_card_off");
        	}
        	
        	card.data("objId", key);
        	
        	card.click(function() {
        		showRGBModal($(this));
        	});
            
            item.append(title);
            card.append(icon);
            card.append(item);
            lastBlock.append(card);
        }
        list.append(lastBlock);
    }
    else {
        $('#rgb_block').hide();
    }
}

function showPWMModal(data) {
    key = data.data("objId");
    if(pwm[key].state)
    {
        $('#pwn_switch_btn').html("Turn OFF");
    }
    else 
    {
        $('#pwn_switch_btn').html("Turn ON");
    }
    
    $('#pwm_modal_title').html(pwm[key].name);
    pwmDialog.querySelector('#pwm_value').MaterialSlider.change(pwm[key].value);
    
    if(lastPWMSwitchBTNListener != null) {
        pwmDialog.querySelector('#pwn_switch_btn').removeEventListener('click', lastPWMSwitchBTNListener);
    }
    lastPWMSwitchBTNListener = function() {
      togglePWM(key, data);
    };
    pwmDialog.querySelector('#pwn_switch_btn').addEventListener('click', lastPWMSwitchBTNListener);
    
    
    if(lastPWMValueListener != null) {
        pwmDialog.querySelector('#pwm_value').removeEventListener('change', lastPWMValueListener);
    }
    lastPWMValueListener = function() {
      setPWM(key, $('#pwm_value').val(), data);
    };
    pwmDialog.querySelector('#pwm_value').addEventListener('change', lastPWMValueListener);
    
    
    if(lastPWMCloseListener != null) {
        pwmDialog.querySelector('.close').removeEventListener('click', lastPWMCloseListener);
    }
    lastPWMCloseListener = function() {
      pwmDialog.close();
    };
    pwmDialog.querySelector('.close').addEventListener('click', lastPWMCloseListener);
    
    pwmDialog.showModal();
}

function showRGBModal(data) {
    key = data.data("objId");
    if(rgb[key].state)
    {
        $('#rgb_switch_btn').html("Turn OFF");
    }
    else 
    {
        $('#rgb_switch_btn').html("Turn ON");
    }
    
    $('#rgb_modal_title').html(rgb[key].name);

    
    if(lastRGBSwitchBTNListener != null) {
        rgbDialog.querySelector('#rgb_switch_btn').removeEventListener('click', lastRGBSwitchBTNListener);
    }
    lastRGBSwitchBTNListener = function() {
      toggleRGB(key, data);
    };
    rgbDialog.querySelector('#rgb_switch_btn').addEventListener('click', lastRGBSwitchBTNListener);
    
 
    if(lastRGBCloseListener != null) {
        rgbDialog.querySelector('.close').removeEventListener('click', lastRGBCloseListener);
    }
    lastRGBCloseListener = function() {
      rgbDialog.close();
    };
    rgbDialog.querySelector('.close').addEventListener('click', lastRGBCloseListener);
    
    $('#colorpicker').farbtastic(function(color) {
        r = HEXStrtoRGB(color.substring(1, 3));
        g = HEXStrtoRGB(color.substring(3, 5));
        b = HEXStrtoRGB(color.substring(5, 7));
        setRGB(key, r, g, b, data);
    });
    picker = $.farbtastic('#colorpicker');
    picker.setColor(RGBtoHEXStr(rgb[key].value[0], rgb[key].value[1], rgb[key].value[2]))
    
    rgbDialog.showModal();
}

function updateObjects() {
    updateSwitches();
    updatePWM();
    updateRGB();

	componentHandler.upgradeDom();
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
function getObjects() {
    $.ajax({ 
        url: "/getObjects"
    }).then(function(data) {
        if(data.error == 0) {
            objects = data.objects;
            for(var key in objects) {
                if(objects[key].type == 0) {
                    switches[key] = {name: objects[key].name, state: objects[key].state, value: objects[key].value};
                    objTypes[key] = {type: objects[key].type};                    
                }
                else if(objects[key].type == 1 || objects[key].type == 3) {
                    pwm[key] = {name: objects[key].name, state: objects[key].state, value: objects[key].value};
                    objTypes[key] = {type: objects[key].type};
                }
                else if(objects[key].type == 2 || objects[key].type == 4) {
                    rgb[key] = {name: objects[key].name, state: objects[key].state, value: objects[key].value};
                    objTypes[key] = {type: objects[key].type};
                }

            }
        }
        else {
            getObjects();
        }

        updateObjects();
    });
}

function toggleObject(eventObj) {
	$.ajax({ 
        url: "/toggle/" + eventObj.data("objId")
    }).then(function(data) {
        if(data.error == 0) {
        	switches[eventObj.data("objId")].state = data.objects.state;
            if(data.objects.state) {
            	eventObj.removeClass("switch_card_off");
            	eventObj.addClass("switch_card_on");
            	eventObj.find("i").html("power");
            }
            else {
            	eventObj.addClass("switch_card_off");
            	eventObj.removeClass("switch_card_on");
            	eventObj.find("i").html("power_off");
            }
        }
        else {
            alert("Could not toggle object " + objId);
        }
    });
}

function togglePWM(key, eventObj) {
    $.ajax({ 
        url: "/togglePWM/" + key
    }).then(function(data) {
        if(data.error == 0) {
        	pwm[key].state = data.objects.state;
            if(data.objects.state) {
            	eventObj.removeClass("switch_card_off");
            	eventObj.addClass("switch_card_on");
            	$('#pwn_switch_btn').html("Turn OFF");
            }
            else {
            	eventObj.addClass("switch_card_off");
            	eventObj.removeClass("switch_card_on");
            	$('#pwn_switch_btn').html("Turn ON");
            }
        }
        else {
            alert("Could not toggle object " + objId);
        }
    });
}

function setPWM(key, value, eventObj) {
    $.ajax({ 
        url: "/setPWM/" + key + "/" + value
    }).then(function(data) {
        if(data.error == 0) {
        	pwm[key].state = data.objects.state;
        	pwm[key].value = data.objects.value;
            if(data.objects.state) {
            	eventObj.removeClass("switch_card_off");
            	eventObj.addClass("switch_card_on");
            	$('#pwn_switch_btn').html("Turn OFF");
            }
            else {
            	eventObj.addClass("switch_card_off");
            	eventObj.removeClass("switch_card_on");
            	$('#pwn_switch_btn').html("Turn ON");
            }
        }
        else {
            alert("Could not set object " + objId);
        }
    });
}

function toggleRGB(key, eventObj) {
    $.ajax({ 
        url: "/toggleRGB/" + key
    }).then(function(data) {
        if(data.error == 0) {
        	rgb[key].state = data.objects.state;
            if(data.objects.state) {
            	eventObj.removeClass("switch_card_off");
            	eventObj.addClass("switch_card_on");
            	$('#rgb_switch_btn').html("Turn OFF");
            }
            else {
            	eventObj.addClass("switch_card_off");
            	eventObj.removeClass("switch_card_on");
            	$('#rgb_switch_btn').html("Turn ON");
            }
        }
        else {
            alert("Could not toggle object " + objId);
        }
    });
}

function setRGB(key, r, g, b, eventObj) {
    $.ajax({ 
        url: "/setRGB/" + key + "/" + r + "/" + g + "/" + b
    }).then(function(data) {
        if(data.error == 0) {
        	rgb[key].state = data.objects.state;
        	rgb[key].value = data.objects.value;
            if(data.objects.state) {
            	eventObj.removeClass("switch_card_off");
            	eventObj.addClass("switch_card_on");
            	$('#rgb_switch_btn').html("Turn OFF");
            }
            else {
            	eventObj.addClass("switch_card_off");
            	eventObj.removeClass("switch_card_on");
            	$('#rgb_switch_btn').html("Turn ON");
            }
        }
        else {
            alert("Could not set object " + objId);
        }
    });
}


function decimalToHex(d, padding) {
    var hex = Number(d).toString(16);
    padding = typeof (padding) === "undefined" || padding === null ? padding = 2 : padding;

    while (hex.length < padding) {
        hex = "0" + hex;
    }

    return hex;
}

function RGBtoHEXStr(r, g, b) {
    return "#" + decimalToHex(r, 2) + decimalToHex(g, 2) + decimalToHex(b, 2);
}

function HEXStrtoRGB(value) {
    return parseInt('0x' + value);
}