var settings = {};

function setSettings(weatherApiKey, serverApiKey) {
    settings.weatherApiKey = weatherApiKey;
    settings.serverApiKey = serverApiKey;
    console.log("Weather API Key: " + settings.weatherApiKey);
    console.log("Server API Key: " + settings.serverApiKey);
}

function tryLogin() {
    $.ajax({
        type : 'GET',
        url : "/tryLogin",
        data : {},
        success: tryLoginCallback
    });
}

function tryLoginCallback(result) {
    if(result.error == 0) {
        /* Redirect */
        window.location.href = "dash";
    }
}

function loginFunction() {
    username  = $("#username_field").val();
    passwd = $("#password_field").val();
    $.ajax({
        type : 'POST',
        url : "/doLogin/",
        data : {'username': username, 'passwd': passwd},
        success: loginCallback
    });
}

function loginCallback(result) {
    /* If we had a result, and the error is not 0 */
    if(result.error != 0) {
        $("#username_info").attr("data-error", result.message);
        $("#password_info").attr("data-error", result.message);
        $("#username_field").addClass("invalid");
        $("#password_field").addClass("invalid");
    }
    else {
        /* Redirect */
        window.location.href = "dash";
    }
}

function initLoginBox() {

    $("#username_field").on('input',function(e){
        $("#username_info").attr("data-error", "");
        $("#username_field").removeClass("invalid");
    });

    $("#password_field").on('input',function(e){
        $("#password_info").attr("data-error", "");
        $("#password_field").removeClass("invalid");
    });

    /* Set aestetic login box */
    $('input').blur(function() {
        var $this = $(this);
        if ($this.val())
          $this.addClass('used');
        else
          $this.removeClass('used');
    });

    var $ripples = $('.ripples');

    $ripples.on('click.Ripples', function(e) {

        var $this = $(this);
        var $offset = $this.parent().offset();
        var $circle = $this.find('.ripplesCircle');

        var x = e.pageX - $offset.left;
        var y = e.pageY - $offset.top;

        $circle.css({
            top: y + 'px',
            left: x + 'px'
        });

        $this.addClass('is-active');

    });

    $ripples.on('animationend webkitAnimationEnd mozAnimationEnd oanimationend MSAnimationEnd', function(e) {
        $(this).removeClass('is-active');
    });

    /* Set auto submit on enter */
    $('#login_submit').keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#username_field").keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#password_field").keydown(function(event) {
        if (event.which === 13)  {
            event.preventDefault();
            loginFunction();
        }
    });
    $("#login_btn").click(loginFunction);
}

function updateWeather() {
	$.ajax({
        url: "http://api.openweathermap.org/data/2.5/weather?id=3009566&appid=" + settings.weatherApiKey
    }).then(function(data) {
    	tempFloat = 0.0;
        tempMinFloat = 0.0;
        tempMaxFloat = 0.0
    	tempStr = "???";
        tempMinStr = "???";
        tempMaxStr = "???"
        humStr = "???";
        windStr = "???";
        if(data.cod == 200) {
            tempUnit = "&deg;C";
            windUnit = "KmH";
            tempFloat = data.main.temp - 273.15;
            tempMinFloat = data.main.temp_min - 273.15;
            tempMaxFloat = data.main.temp_max - 273.15;

            tempStr = parseFloat(tempFloat).toFixed(1) + tempUnit;
            tempMinStr = parseFloat(tempMinFloat).toFixed(1) + tempUnit;
            tempMaxStr = parseFloat(tempMaxFloat).toFixed(1) + tempUnit;
            humStr = parseFloat(data.main.humidity).toFixed(0) + "%";
            windStr = parseFloat(data.wind.speed).toFixed(1) + windUnit + " " + data.wind.deg + "&deg;";

            $('#weather_widget_temp_value').html(tempStr);
            $('#weather_widget_temp_min').html(tempMinStr);
            $('#weather_widget_temp_max').html(tempMaxStr);
            $('#weather_widget_rain_risk').html(humStr);
            $('#weather_widget_wind_info').html(windStr);

            $('#weather_widget_icon').attr("src", "http://openweathermap.org/img/wn/" + data.weather[0].icon + "@2x.png");
            $('#weather_widget_icon').attr("alt", data.weather[0].main);
            $('#weather_widget_icon').attr("title", data.weather[0].main);
        }
    });
}

function updateEnvironment() {
	$.ajax({
        url: "/getEnvlast/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {
            tempUnit = "&deg;C";
            tempStr = parseFloat(data.lastEnv.t).toFixed(1) + tempUnit;
            humStr = parseFloat(data.lastEnv.h).toFixed(1) + "%";
            lumStr = parseFloat(data.lastEnv.l).toFixed(1) + "%";

            $('#card_env_temp').html(tempStr);
            $('#card_env_humidity').html(humStr);
            $('#card_env_lum').html(lumStr);
        }
        else {
            $('#card_env_temp').html("Cannot retreive information");
            $('#card_env_humidity').html("Cannot retreive information");
            $('#card_env_lum').html("Cannot retreive information");
        }
    });
}

function forceUpdateEnvironment() {
    $.ajax({
        url: "/updateEnvLast"
    }).then(function(data) {
        updateEnvironment();
    });
}

function loadEnvChart() {

    $.ajax({
        url: "/getHourEnv/24/3600/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {

            labels = [];
            temp   = [];
            hum    = [];
            light  = [];

            maxTemp = 0;
            maxHum = 0;
            maxLight = 0;
            minTemp = 100;
            minHum = 100;
            minLight = 100;

            for(i = 0; i < data.data.length; ++i) {
                labels.push("");
                temp.push(parseFloat(data.data[i].t).toFixed(1));
                hum.push(parseFloat(data.data[i].h).toFixed(1));
                light.push(parseFloat(data.data[i].l).toFixed(1));

                if(maxTemp < data.data[i].t) {
                    maxTemp = data.data[i].t;
                }
                if(maxHum < data.data[i].h) {
                    maxHum = data.data[i].h;
                }
                if(maxLight < data.data[i].l) {
                    maxLight = data.data[i].l;
                }

                if(minTemp > data.data[i].t) {
                    minTemp = data.data[i].t;
                }
                if(minHum > data.data[i].h) {
                    minHum = data.data[i].h;
                }
                if(minLight > data.data[i].l) {
                    minLight = data.data[i].l;
                }
            }
            maxLight += 5;
            maxHum += 5;
            maxTemp += 5;
            minLight -= 5;
            minHum -= 5;
            minTemp -= 5;


            const data0 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#3498db',
                    borderColor: '#3498db',
                    data: temp,
                }]
            };

            const data1 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#16a085',
                    borderColor: '#16a085',
                    data: hum,
                }]
            };

            const data2 = {
                labels: labels,
                datasets: [{
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: light,
                }]
            };

            const config0 = {
                type: 'line',
                data: data0,
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        yAxis: {
                            display: false,
                            max: maxTemp,
                            min: minTemp,
                            grid: {
                                drawTicks: false
                            }
                        },
                        xAxis: {
                            display: false,
                            grid: {
                                drawTicks: false
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dot"
                        }
                    }
                }
            };

            const config1 = {
                type: 'line',
                data: data1,
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        yAxis: {
                            display: false,
                            max: maxHum,
                            min: minHum,
                            grid: {
                                drawTicks: false
                            }
                        },
                        xAxis: {
                            display: false,
                            grid: {
                                drawTicks: false
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dot"
                        }
                    }
                }
            };

            const config2 = {
                type: 'line',
                data: data2,
                options: {
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        yAxis: {
                            display: false,
                            max: maxLight,
                            min: minLight,
                            grid: {
                                drawTicks: false
                            }
                        },
                        xAxis: {
                            display: false,
                            grid: {
                                drawTicks: false
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dot"
                        }
                    }
                }
            };

            const tempChart = new Chart(
                document.getElementById('temp_chart'),
                config0
            );

            const humChart = new Chart(
                document.getElementById('hum_chart'),
                config1
            );

            const lumChart = new Chart(
                document.getElementById('lum_chart'),
                config2
            );

            tempChart.canvas.parentNode.style.height = '45px';
            tempChart.canvas.parentNode.style.width  = '250px';
            humChart.canvas.parentNode.style.height = '45px';
            humChart.canvas.parentNode.style.width  = '250px';
            lumChart.canvas.parentNode.style.height = '45px';
            lumChart.canvas.parentNode.style.width  = '250px';
        }
    });
}

function toggleFTP() {
    ftpToggleBtn = $("#button_toggle_ftp");
    action = "on";
    if(ftpToggleBtn.attr("data") == "disable_ftp") {
        action = "off";
    }
    if (confirm('Are you sure you want to turn ' + action + ' the FTP?')) {
        $("#nas_status_update_progress").fadeIn(10);
        $.ajax({
            url: "/toggleFTP/" + action
        }).then(function(data) {
            if(data.error != 0) {
                alert("Could not update FTP status.");
            }
            getNASStatus();
        });
    }
}

function toggleSMBD() {
    smbdToggleBtn = $("#button_toggle_smbd");
    action = "on";
    if(smbdToggleBtn.attr("data") == "disable_smbd") {
        action = "off";
    }
    if (confirm('Are you sure you want to turn ' + action + ' the SAMBA?')) {
        $("#nas_status_update_progress").fadeIn(10);
        $.ajax({
            url: "/toggleSMBD/" + action
        }).then(function(data) {
            if(data.error != 0) {
                alert("Could not update MBD status.");
            }
            getNASStatus();
        });

    }
}

function getNASStatus() {
    $.ajax({
        url: "/getNASStatus/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {
            ftpStatusSpan  = $("#ftp_status");
            ftpToggleBtn   = $("#button_toggle_ftp");
            smbdStatusStan = $("#smbd_status");
            smbdToggleBtn  = $("#button_toggle_smbd");

            if(data.ftpEnabled) {
                ftpStatusSpan.html('FTP &nbsp; <i class="material-icons" style="color: #26a69a;font-size:14px;">check_circle</i>');
                ftpToggleBtn.html("Disable FTP");
                ftpToggleBtn.attr("data", "disable_ftp");

            }
            else {
                ftpStatusSpan.html('FTP &nbsp; <i class="material-icons" style="color: #ff6347;font-size:14px;">cancel</i>');
                ftpToggleBtn.html("Enable FTP");
                ftpToggleBtn.attr("data", "enable_ftp");
            }

            if(data.smbdEnabled) {
                smbdStatusStan.html('SAMBA &nbsp; <i class="material-icons" style="color: #26a69a;font-size:14px;">check_circle</i>');
                smbdToggleBtn.html("Disable SAMBA");
                smbdToggleBtn.attr("data", "disable_smbd");
            }
            else {
                smbdStatusStan.html('SAMBA &nbsp; <i class="material-icons" style="color: #ff6347;font-size:14px;">cancel</i>');
                smbdToggleBtn.html("Enable SAMBA");
                smbdToggleBtn.attr("data", "enable_smbd");
            }

            //$("#nas_status_update_progress").fadeOut(500);
            $("#nas_status_update_progress").css("visibility", "hidden");
        }
        else {
            alert("Could not update NAS status");
        }
    });
}

function load24HHist() {

    $.ajax({
        url: "/getHourEnv/48/1800/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {

            labels = [];
            temp   = [];
            hum    = [];
            light  = [];

            /* Get data */
            for(i = 0; i < data.data.length; ++i) {
                dateInfo = new Date(data.data[i].time * 1000);
                h = dateInfo.getHours();
                m = dateInfo.getMinutes();
                h = (h < 10) ? '0' + h : h;
                m = (m < 10) ? '0' + m : m;
                labels.push(h + ':' + m);
                temp.push(parseFloat(data.data[i].t).toFixed(1));
                hum.push(parseFloat(data.data[i].h).toFixed(1));
                light.push(parseFloat(data.data[i].l).toFixed(1));
            }

            const data0 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#3498db',
                    borderColor: '#3498db',
                    data: temp,
                    tension: 0.4
                }]
            };

            const data1 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#16a085',
                    borderColor: '#16a085',
                    data: hum,
                    tension: 0.4
                }]
            };

            const data2 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#ff6384',
                    borderColor: '#ff6384',
                    data: light,
                    tension: 0.4
                }]
            };

            const DISPLAY = false;
            const BORDER = true;
            const CHART_AREA = true;
            const TICKS = true;

            const config0 = {
                type: 'line',
                data: data0,
                responsive: true,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config1 = {
                type: 'line',
                data: data1,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config2 = {
                type: 'line',
                data: data2,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const tempChart = new Chart(
                document.getElementById('temp_chart_24h'),
                config0
            );

            const humChart = new Chart(
                document.getElementById('hum_chart_24h'),
                config1
            );

            const lumChart = new Chart(
                document.getElementById('lum_chart_24h'),
                config2
            );

            tempChart.canvas.parentNode.style.height = '160px';
            tempChart.canvas.parentNode.style.width  = '655px';
            humChart.canvas.parentNode.style.height = '160px';
            humChart.canvas.parentNode.style.width  = '655px';
            lumChart.canvas.parentNode.style.height = '160px';
            lumChart.canvas.parentNode.style.width  = '655px';
        }
    });
}

function load7DHist() {

    $.ajax({
        url: "/getHourEnv/50/12096/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {

            labels = [];
            temp   = [];
            hum    = [];
            light  = [];

            const days = ["Sun", "Mon", "Tuey", "Wed", "Thu", "Fri", "Sat"];

            /* Get data */
            for(i = 0; i < data.data.length; ++i) {
                dateInfo = new Date(data.data[i].time * 1000 );
                h = dateInfo.getHours();
                h = (h < 10) ? '0' + h : h;
                labels.push(days[dateInfo.getDay()] + "  " + h + "h");
                temp.push(parseFloat(data.data[i].t).toFixed(1));
                hum.push(parseFloat(data.data[i].h).toFixed(1));
                light.push(parseFloat(data.data[i].l).toFixed(1));
            }

            const data0 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#3498db',
                    borderColor: '#3498db',
                    data: temp,
                    tension: 0.4
                }]
            };

            const data1 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#16a085',
                    borderColor: '#16a085',
                    data: hum,
                    tension: 0.4
                }]
            };

            const data2 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#ff6384',
                    borderColor: '#ff6384',
                    data: light,
                    tension: 0.4
                }]
            };

            const DISPLAY = false;
            const BORDER = true;
            const CHART_AREA = true;
            const TICKS = true;

            const config0 = {
                type: 'line',
                data: data0,
                responsive: true,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config1 = {
                type: 'line',
                data: data1,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config2 = {
                type: 'line',
                data: data2,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const tempChart = new Chart(
                document.getElementById('temp_chart_7d'),
                config0
            );

            const humChart = new Chart(
                document.getElementById('hum_chart_7d'),
                config1
            );

            const lumChart = new Chart(
                document.getElementById('lum_chart_7d'),
                config2
            );

            tempChart.canvas.parentNode.style.height = '160px';
            tempChart.canvas.parentNode.style.width  = '655px';
            humChart.canvas.parentNode.style.height = '160px';
            humChart.canvas.parentNode.style.width  = '655px';
            lumChart.canvas.parentNode.style.height = '160px';
            lumChart.canvas.parentNode.style.width  = '655px';
        }
    });
}

function load1MHist() {

    $.ajax({
        url: "/getHourEnv/30/86400/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {

            labels = [];
            temp   = [];
            hum    = [];
            light  = [];

            /* Get data */
            for(i = 0; i < data.data.length; ++i) {
                dateInfo = new Date(data.data[i].time * 1000);
                d = dateInfo.getDate();
                m = dateInfo.getMonth();
                d = (d < 10) ? '0' + d : d;
                m = (m < 10) ? '0' + m : m;
                labels.push(d + "/" + m);
                temp.push(parseFloat(data.data[i].t).toFixed(1));
                hum.push(parseFloat(data.data[i].h).toFixed(1));
                light.push(parseFloat(data.data[i].l).toFixed(1));
            }

            const data0 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#3498db',
                    borderColor: '#3498db',
                    data: temp,
                    tension: 0.4
                }]
            };

            const data1 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#16a085',
                    borderColor: '#16a085',
                    data: hum,
                    tension: 0.4
                }]
            };

            const data2 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#ff6384',
                    borderColor: '#ff6384',
                    data: light,
                    tension: 0.4
                }]
            };

            const DISPLAY = false;
            const BORDER = true;
            const CHART_AREA = true;
            const TICKS = true;

            const config0 = {
                type: 'line',
                data: data0,
                responsive: true,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config1 = {
                type: 'line',
                data: data1,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config2 = {
                type: 'line',
                data: data2,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const tempChart = new Chart(
                document.getElementById('temp_chart_1m'),
                config0
            );

            const humChart = new Chart(
                document.getElementById('hum_chart_1m'),
                config1
            );

            const lumChart = new Chart(
                document.getElementById('lum_chart_1m'),
                config2
            );

            tempChart.canvas.parentNode.style.height = '160px';
            tempChart.canvas.parentNode.style.width  = '655px';
            humChart.canvas.parentNode.style.height = '160px';
            humChart.canvas.parentNode.style.width  = '655px';
            lumChart.canvas.parentNode.style.height = '160px';
            lumChart.canvas.parentNode.style.width  = '655px';
        }
    });
}

function load1YHist() {
    $.ajax({
        url: "/getHourEnv/52/604800/" + settings.serverApiKey
    }).then(function(data) {
        if(data.error == 0) {

            labels = [];
            temp   = [];
            hum    = [];
            light  = [];

            const month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

            /* Get data */
            for(i = 0; i < data.data.length; ++i) {
                dateInfo = new Date(data.data[i].time * 1000);
                labels.push(month[dateInfo.getMonth()]);
                temp.push(parseFloat(data.data[i].t).toFixed(1));
                hum.push(parseFloat(data.data[i].h).toFixed(1));
                light.push(parseFloat(data.data[i].l).toFixed(1));
            }

            const data0 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#3498db',
                    borderColor: '#3498db',
                    data: temp,
                    tension: 0.4
                }]
            };

            const data1 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#16a085',
                    borderColor: '#16a085',
                    data: hum,
                    tension: 0.4
                }]
            };

            const data2 = {
                labels: labels,
                datasets: [{
                    backgroundColor: '#ff6384',
                    borderColor: '#ff6384',
                    data: light,
                    tension: 0.4
                }]
            };

            const DISPLAY = false;
            const BORDER = true;
            const CHART_AREA = true;
            const TICKS = true;

            const config0 = {
                type: 'line',
                data: data0,
                responsive: true,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config1 = {
                type: 'line',
                data: data1,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const config2 = {
                type: 'line',
                data: data2,
                options: {
                    interaction: {
                        intersect: false,
                    },
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        x: {
                            grid: {
                                display: DISPLAY,
                                drawBorder: BORDER,
                                drawOnChartArea: CHART_AREA,
                                drawTicks: TICKS,
                              }
                        }
                    },
                    elements: {
                        point: {
                            radius: 2,
                            pointStyle: "dash"
                        }
                    }
                }
            };

            const tempChart = new Chart(
                document.getElementById('temp_chart_1y'),
                config0
            );

            const humChart = new Chart(
                document.getElementById('hum_chart_1y'),
                config1
            );

            const lumChart = new Chart(
                document.getElementById('lum_chart_1y'),
                config2
            );

            tempChart.canvas.parentNode.style.height = '160px';
            tempChart.canvas.parentNode.style.width  = '655px';
            humChart.canvas.parentNode.style.height = '160px';
            humChart.canvas.parentNode.style.width  = '655px';
            lumChart.canvas.parentNode.style.height = '160px';
            lumChart.canvas.parentNode.style.width  = '655px';
        }
    });
}