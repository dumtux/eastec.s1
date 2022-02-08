var SaunaID = $("#deviceId").val();

var BaseUrl = '/sauna/' + SaunaID;


function _getStatus() {

  fetch(BaseUrl + '/status')
  .then(response => response.json())
  .then(data => {
    configureStatus(data)
  })
  .catch((error) => {
    console.error('Error:', error);
  });

  fetch(BaseUrl + '/schedules')
  .then(response => response.json())
  .then(data => {
    configureSchedule(data)
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

function _setStatus(field, value) {
  console.log("here");
  var post_data = {};
  post_data[field] = value;
  fetch(BaseUrl + '/state', {
    method: "PUT",
    body: JSON.stringify(post_data),
    headers: {
        "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log(data)
  })
  .catch((error) => {
    console.error('Error:', error);
  });
}

var $tabs = $('#bottomMenubar .bottomMenuItem');
var previousPage = 0;

function showPage(pageId) {
  var $pageToHide = $("#mainContainer").find('div.content-page').filter('.is-active'), $pageToShow = $(pageId);

  $pageToHide.removeClass('is-active').addClass('is-animating is-exiting');
  $pageToShow.addClass('is-animating is-active');

  $pageToShow.on('transitionend webkitTransitionEnd', function() {
    $pageToHide.removeClass('is-animating is-exiting');
    $pageToShow.removeClass('is-animating').off('transitionend webkitTransitionEnd');
  });
}

var $saunaControlPage = $("#saunaControlPage");
var $stateStandby = $('#stateStandby'), $stateHeating = $('#stateHeating'), $stateReady = $('#stateReady'), $stateInsession = $('#stateInsession'), $statePause = $('#statePause');

function setSaunaState(state) {
  $(".state-btns").addClass("d-none");
  switch (state) {
    case "standby":
      $stateStandby.removeClass("d-none");
      break;
    case "heating":
      $stateHeating.removeClass("d-none");
      break;
    case "ready":
      $stateReady.removeClass("d-none");
      break;
    case "insession":
      $stateInsession.removeClass("d-none");
      break;
    case "paused":
      $statePause.removeClass("d-none");
      break;
  }
}

function goStandBy() {
  _setStatus("state", "standby");
  setSaunaState("standby");
}

function goReady() {
  _setStatus("state", "ready");
  setSaunaState("ready");
}

function goHeating() {
  _setStatus("state", "heating");
  setSaunaState("heating");
}

function goInsession() {
  _setStatus("state", "insession");
  setSaunaState("insession");
}

function goPause() {
  _setStatus("state", "paused");
  setSaunaState("paused");
}


function drawDial(eleId) {
  let type = $(eleId + '.gauge').data('type'); //temperature, time
  let points = 43;
  let radius = 257;
  let max = 0;
  let peaks = [0];

  if(type == "temperature") {
    max = 100; peaks = [0, 25, 50, 75, 100];
  } else if(type == "time") {
    max = 80; peaks = [0, 20, 40, 60, 80];
  }

  let step = (max + 1) / points;
  let realPeaks = peaks.map(peak => Math.floor(peak * (1 / step)));
  let hueStep = 120 / points;

  let gaugeDigits = $(eleId + ' .gauge-digits');

  let digit = $(eleId + '.gauge').data('digit');
  let labelTxt = $(eleId + '.gauge').data('label');
  gaugeDigits.html("");
  gaugeDigits.prepend(`<span class="digit current-digit count">${labelTxt}</span>`);

  for (let i = 0; i < points; i++) {
    let degree = i * (radius / (points - 1)) - radius / 2;
    let isPeak = realPeaks.indexOf(i) > -1;

    let intStep = Math.ceil(step * i);
    let intNextStep = Math.ceil(step * (i + 1));

    // let styles = `transition-delay: ${ (i / digit) * (i / digit) + 1 }s;`;
    let inner_styles = `transform: rotate(${degree}deg);`;
    let outer_styles = '';
    if (intStep <= digit) {
      // styles += `background-color: hsl(${240 + i * hueStep}, 92%, 64%);`;
      if(type == 'temperature') {
        outer_styles += `background-color: #EFAB46;`;
        inner_styles += `background-color: #EFAB46;`;
      } else if(type == 'time') {
        outer_styles += `background-color: #7CB7B7;`;
        inner_styles += `background-color: #7CB7B7;`;
      }
    }

    if (intStep > digit || (intStep <= digit && intNextStep <= digit)) {
      outer_styles += `-webkit-transform: rotate(${degree}deg);
      -moz-transform: rotate(${degree}deg);
      -ms-transform: rotate(${degree}deg);
      -o-transform: rotate(${degree}deg);
      transform: rotate(${degree}deg);`;
    } else {
        if (intNextStep > digit)
          outer_styles += `
          -webkit-transform: rotate(${degree}deg) translateY(-.1em);
          -moz-transform: rotate(${degree}deg) translateY(-.1em);
          -ms-transform: rotate(${degree}deg) translateY(-.1em);
          -o-transform: rotate(${degree}deg) translateY(-.1em);
          transform: rotate(${degree}deg) translateY(-.1em);
          height: 0.8em;`;
    }


    $(eleId + ' .gauge-outer').append(`<i class="bar" style="${outer_styles}"></i>`);
    let gaugeInner = $(eleId + ' .gauge-inner').append(`<i class="bar${isPeak ? ' peak' : ''}" style="${inner_styles}"></i>`);

    if (isPeak) {
      let digit = $(`<span class="digit">${peaks[realPeaks.indexOf(i)]}</span>`);
      let peakOffset = gaugeInner.find('.peak').last().offset();

      gaugeDigits.append(digit);

      if (degree > -5 && degree < 5) {
          digit.offset({left: peakOffset.left - 5, top: peakOffset});
      } else {
        digit.offset({left: peakOffset.left - 10, top: peakOffset.top + 15});
      }

      setTimeout(function () {
          gaugeDigits.addClass('scale');
      }, 1)
      }
  }
}

function openCard(ele) {
  ele.find(".block-card-collapsed").addClass("d-none");
  ele.find(".block-card-expand").removeClass("d-none");
  if(ele.find(".block-card-expand .gauge").length) {
    drawDial("#" + ele.find(".block-card-expand .gauge").attr('id'));
  }
}

function closeCard(ele) {
  ele.find(".block-card-collapsed").removeClass("d-none");
  ele.find(".block-card-expand").addClass("d-none");
}

function configureStatus(status) {
  console.log(">>>>>>>>>>>>>>>>>>>");
  console.log(status);
  setSaunaState(status.state);

  $(".current_temperature").html(calcTemp(status.current_temperature));
  $(".target_temperature").html(calcTemp(status.target_temperature));
  $(".program_temperature").html(calcTemp(status.program.target_temperature));
  $("#temperature-dial").data("label", calcTemp(status.current_temperature));
  $("#temperature-dial").data("digit", status.current_temperature);


  $(".remaining_timer").html(calcTimer(status.timer));
  $(".program_timer").html(calcTimer(status.program.timer_duration));
  $("#time-dial").data("label", calcTimer(status.timer));
  $("#time-dial").data("digit", 0);

  if(status.lights[0]) {
    if(status.lights[0].state == "on") {
      $("#halo_light input").val(RGBToHex(status.lights[0].color.r, status.lights[0].color.g, status.lights[0].color.b));
      openCard($("#halo_light"));
    } else {
      closeCard($("#halo_light"));
    }
  }

  if(status.lights[1]) {
    if(status.lights[1].state == "on") {
      $("#halo_light input").val(RGBToHex(status.lights[0].color.r, status.lights[0].color.g, status.lights[0].color.b));
      openCard($("#halo_light"));
    } else {
      closeCard($("#halo_light"));
    }
  }

  $("#current_program .program-time > span").html(calcTimer(status.program.timer_duration));
  $("#current_program .program-temperature > span").html(calcTemp(status.program.target_temperature));

}

function configureSchedule(status) {
  console.log(status);
  var program_cnt = status.length;
  var content = `<div><h3 class="card-section-title">Program Lists</h3></div>`;
  for (i = 0;i<program_cnt;i++) {
    content += `<div class="program-card">
                  <div class="program-card-header">
                      <div class="program-time">
                          <img src="./assets/images/icons/time-color.png">
                          <span> ${calcTimer(status[i].program.timer_duration)} </span>
                      </div>
                      <div class="program-temperature">
                          <img src="./assets/images/icons/temperature-color.png">
                          <span> ${calcTemp(status[i].program.target_temperature)} </span>
                      </div>
                  </div>
                  <div class="program-card-body">
                      <h4 class="program-title" data-toggle="collapse" data-target="#program1">${status[i].program.name}</h4>
                      <div id="program1" class="program-detail collapse">
                          <ul>
                              <li>Frequency: ${status[i].frequency}</li>
                              <li>User: ${status[i].user}</li>
                              <li>Sauna: ${status[i].sauna}</li>
                          </ul>
                          <button id="program_start" class="btn btn-primary">Start</button>
                      </div>
                  </div>
              </div>`;
  }
  $("#program_lists").html(content)
}

function configureApp() {

  // drawDial("#temperature-dial", 100, [0, 25, 50, 75, 100]);
  // drawDial("#time-dial", 80, [0, 20, 40, 60, 80]);
}

function calcTemp(temp) {
  return Math.round(temp) + "°C";
}

function calcTimer(timer) {
  return timer + "m"

  // if( timer <= 60)
  //   return timer + "s"

  //   var minutes = Math.floor(timer / 60);
  // var seconds = timer - minutes * 60;

  // return minutes + "m " + seconds + "s"
}

function RGBToHex(r,g,b) {
  r = r.toString(16);
  g = g.toString(16);
  b = b.toString(16);

  if (r.length == 1)
    r = "0" + r;
  if (g.length == 1)
    g = "0" + g;
  if (b.length == 1)
    b = "0" + b;

  return "#" + r + g + b;
}

function setupSettings() {
    document.getElementById("restartApp").onclick =() => {
        fetch(BaseUrl + '/restart').then(console.log).catch(console.error)
    }
    document.getElementById("rebootOS").onclick =() => {
        fetch(BaseUrl + '/reboot').then(console.log).catch(console.error)
    }
    document.getElementById("updateFirmware").onclick =() => {
        fetch(BaseUrl + '/upgrade').then(console.log).catch(console.error)
    }
}

$(document).ready(function(){
  _getStatus();
  setupSettings();
  setTimeout(function(){$("#loading").addClass("d-none");}, 1500);
  setInterval(() => {
    _getStatus();
  }, 6000);
});

$tabs.on('click', function() {
  $tabs.removeClass("active");
  $(this).addClass("active");
  showPage($(this).data("target"));
});

$('.program-title').on('click', function () {
  if($(this).hasClass('active'))
    $(this).removeClass('active');
  else
    $(this).addClass('active');
});

$('.program-title').on('hide.bs.collapse', function () {
  $(this).removeClass('active');
});

$('.block-card .block-card-collapsed').on('click', function() {
  openCard($(this).parent());
});


$('#temperature .block-card-collapsed').on('click', function() {
  openCard($("#temperature"));
});

$('#temperature .block-card-expand').on('click', function() {
  closeCard($("#temperature"));
});

$('#timer .block-card-collapsed').on('click', function() {
  openCard($("#timer"));
});

$('#timer .block-card-expand').on('click', function() {
  closeCard($("#timer"));
});



$("#halo_light .block-card-collapsed").on("click", function(){
  // _setStatus('light', 'on');
  openCard($("#halo_light"));
});

$("#overhead_light .block-card-collapsed").on("click", function(){
  // _setStatus('light', 'on');
  openCard($("#overhead_light"));
});

$("#halo_light .off-button").on("click", function(){
  // _setStatus('light', 'off');
  closeCard($("#halo_light"));
});

$("#overhead_light .off-button").on("click", function(){
  // _setStatus('light', 'off');
  closeCard($("#overhead_light"));
});


$("#searchWifi").on("click", function(){

  // testData = ["dreamteam", "tp_link_324", "tele_34d"];
  // var network_cnt = testData.length;
  // for (i = 0;i<network_cnt;i++) {
  //   var eleList = "<li class='list-group-item wifi-item' data-ssid='" + testData[i] + "'>" + testData[i] + "</li>"
  //   $("#wifiList").append(eleList);
  // }
  // $("#wifiList").addClass("show");
  $("#wifiList").html("");
  fetch('/sauna/wifi/networks')
  .then(response => response.json())
  .then(data => {
    if(data.detail) {
      $("#errorModal .modal-body").html("<p>" + data.detail + "</p>");
      $("#errorModal").modal();
    } else {
      var eleList = "";
      var network_cnt = data.length;
      for (i = 0;i<network_cnt;i++) {
        eleList += "<li class='list-group-item wifi-item'>" + data[i] + "</li>"
      }
      $("#wifiList").html(eleList);
      $("#wifiList").addClass("show");
    }
  })
  .catch((error) => {
    console.error('Error:', error);
    $("#errorModal .modal-body").html("<p>No Wifi Network</p>");
    $("#errorModal").modal();
  });
});

$(document).on("click", "#wifiList .wifi-item", function(){
  $("#wifiModal .wifi-name").html($(this).text());
  $("#wifiList").removeClass("show");
  $("#wifiModal").modal();
});

$("#connect").on("click", function(){
  var ssid = $("#wifiModal .wifi-name").text();
  var key = $("#wifiModal .wifi-key").val();
  sessionStorage.setItem('ssid', ssid);
  sessionStorage.setItem('key', key);
  var post_data = {};
  post_data['ssid'] = ssid;
  post_data['key'] = key;
  fetch('/sauna/wifi/connect', {
    method: "POST",
    body: JSON.stringify(post_data),
    headers: {
        "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log(data)
    alert("Connection Succcess");
    $("#wifiModal").modal("hide");
  })
  .catch((error) => {
    alert("Connection Failed");
    console.error('Error:', error);
    $("#wifiModal").modal("hide");
  });
});


$(function(){
    $('.wifi-key').keyboard({
    // options here
    usePreview: false,
    // useCombos: false,
    autoAccept: true,
  });
});

$(document).ready(function(){
  console.log("okok");
  if(getCookie("_ColorMode") == 1) {
    $("body").addClass("dark-mode");
    $("#switchColorMode").attr("checked", true);
  } else {
    $("body").removeClass("dark-mode");
  }
  setInterval(function () {  
    fetch('/sauna/wifi/status', {
      method: "GET",
      headers: {
        "Content-type": "application/json; charset=UTF-8"
      }
    })
    .then(response => response.json())
    .then(data => {
      if(data){
        console.log(data)
        $("#connected").show()
        $('#disconnected').hide()
      }
      else {
        $("#connected").hide()
        $('#disconnected').show()
        var post_data = {};
        post_data['ssid'] = sessionStorage.getItem('ssid');;
        post_data['key'] = sessionStorage.getItem('key');;
        if (post_data['ssid'] != null && post_data['key'] != null){
          fetch('/sauna/wifi/connect', {
            method: "POST",
            body: JSON.stringify(post_data),
            headers: {
              "Content-type": "application/json; charset=UTF-8"
            }
          })
          .catch((error) => {
          console.error('Error:', error);
          });
        }
      }
    })
  }, 5000);
});

$("#switchColorMode").on("change", function(){
  if($(this).prop("checked")) {
    $("body").addClass("dark-mode");
    setCookie("_ColorMode", "1", 365);
  } else {
    $("body").removeClass("dark-mode");
    setCookie("_ColorMode", "0", 365);
  }
});

function setCookie(cname, cvalue, exdays) {
  const d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}