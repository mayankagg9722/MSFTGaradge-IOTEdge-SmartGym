$(document).ready(function(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        socket.emit('uisend', {data: 'I am UI calling to python!'});
    });
    socket.on("pysend", function(msg) {
        console.log("yes baby 2:"+msg.data)
     });
});

function botintro(ele,conv) {
    $.getJSON('/botintro',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}
function humanIntro(ele,conv) {
    $.getJSON('/humanIntro',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}
function askExercise(ele,conv) {
    $.getJSON('/askExercise',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p class="convtag">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}

$(function() {
    var conv = $("#conversations")
    var ele =  $('#circle-object')
    ele.bind('click', function() {
        botintro(ele,conv);
        setTimeout(() => {
            humanIntro(ele,conv);
        }, 5000);
        setTimeout(()=>{
            askExercise(ele,conv);
        },11000)
        return false;
    });
});