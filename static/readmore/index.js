$(document).ready(function(){
    var lineheight = $(".setheight").css("line-height");
   $(".hidebtn").click(function(){
        var defheight = $(this).next().height();
        if(defheight < 2*parseFloat(lineheight)){
            $(this).next().removeClass("setheight").css("height","auto!important");
            $(this).html("hide");
        }else{
            $(this).next().addClass("setheight");
            $(this).html("more>>");
        }
   });   
});