function botintro(ele,conv) {
    $.getJSON('/botintro',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p style="color: wheat;margin: 0px;">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}
function humanIntro(ele,conv) {
    $.getJSON('/humanIntro',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p style="color: wheat;margin: 0px;">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}
function askExercise(ele,conv) {
    $.getJSON('/askExercise',
            function(data) {
                console.log(data)
                ele.html(data.buttonName)
                var convtag = '<p style="color: wheat;margin: 0px;">'+ data.botanswers +'</p>'
                conv.append(convtag)
        });
}
$(function() {
    var conv = $("#conversations")
    var ele =  $('#circle-object')
    ele.bind('click', function() {
        botintro(ele,conv);
        humanIntro(ele,conv);
        askExercise(ele,conv);
        return false;
    });
});