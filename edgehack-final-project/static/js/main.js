
function showDiv(text){
    var conv = $("#"+text)
    conv.show();
}
function hideDiv(text){
    var conv = $("#"+text)
    conv.hide();
}
function botintro(ele,conv) {
    hideDiv("showListening");
    $.getJSON('/botintro',
            function(data) {
                hideDiv("showListening");
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                conv.append(convtag)
                setTimeout(() => {
                    hideDiv("showListening");
                    humanIntro(ele,conv);
                }, 4000);
        });
}
function humanIntro(ele,conv) {
    hideDiv("showListening");
    $.getJSON('/humanIntro',
            function(data) {
                hideDiv("showListening");
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                conv.append(convtag)
                setTimeout(() => {
                    hideDiv("showListening");
                    askExercise(ele,conv);
                }, 3000);
        });
}
function askExercise(ele,conv) {
    hideDiv("showListening");
    $.getJSON('/askExercise',
            function(data) {
                hideDiv("showListening");
                // console.log(data)
                // ele.html(data.buttonName)
                // var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                // conv.append(convtag)
        });
}

function trainer(ele,conv) {
    $.getJSON('/trainer',
            function(data) {
                console.log("starting trainer...")
        });
}

$(function() {
    var conv = $("#conversations")
    var ele =  $('#circle-object')
    ele.bind('click', function() {
        botintro(ele,conv);
        return false;
    });

    var mytrainer =  $('#circle-objectify')
    mytrainer.bind('click', function() {
        trainer();
        return false;
    });
});

$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('uisend', {data: 'I am UI calling to python!'});
    });
    socket.on("pysend", function(msg) {
        // console.log("pysend 2:"+msg.data)
        showDiv("accuracydiv")
        $("#accuracytext").html("Accuracy: "+parseInt(msg.data))
     });
    socket.on("botlog", function(msg) {
        console.log("botlog 2:"+msg.data)
        showDiv("summary")
        var summ = $("#conversations")
        var botloagtag = '<p class="convtag">'+ msg.data +'</p>'
        summ.append(botloagtag)
     });
     socket.on("convsend", function(msg) {
         console.log(msg.data)
         if(msg.data=="True"){
            showDiv("showListening");
            $("#showListening").html("Listening..Please say something.")
         }else if(msg.data=="False"){
            hideDiv("showListening");
         }else if(msg.data=="doingexercise"){
            var conv = $("#conversations")
            var ele =  $('#circle-object')
            hideDiv("showListening");
            ele.html("Let's do it!")
            var convtag = '<p class="convtag">'+ 'Great, get in the position for plank and we will start in.' +'</p>'
            conv.append(convtag)
         }
         else{
            showDiv("showListening");
            $("#showListening").html("Detected: "+msg.data)
         }
     });
});