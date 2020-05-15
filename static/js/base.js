$(function(){
				
	$(".manage-top span").mouseenter(function(){
		$(this).find("ul").show();
    });
    $(".manage-top span").mouseleave(function(){
        $(this).find("ul").hide();
    });
	
	
	$(".menu1 > .menuli1 > .menua1").on("click",function(){
		if ($(this).parent().find(".menu2").length) {
			if ($(this).parent().find(".menu2").css("display")=="none") {
				$(this).find(".right").attr("class","iconfont icon-bottom right");
			} else{
				$(this).find(".right").attr("class","iconfont icon-left1 right");
			}
			$(this).parent().find(".menu2").slideToggle(300);
		} 
	});
})