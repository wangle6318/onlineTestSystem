$(function(){
    window.onload = CountDown();
    MarkHasBeenAnswer();
    SubmitAnswer();

    function CountDown(){
        var time_str = $(".test_time .alt-1 .countdown-alt-1").attr("datetime");
        var hour = time_str.substring(2,4);
        var minute = time_str.substring(5,7);
        var second = time_str.substring(8,10);
        var obj_hour = $(".item-hh");
        var obj_minute = $(".item-mm");
        var obj_second = $(".item-ss");
        obj_hour.text(FormatTwoBits(hour));
        obj_minute.text(FormatTwoBits(minute));
        obj_second.text(FormatTwoBits(second));
        t = setTimeout(CountTime, 1000);

        function CountTime(){
            if (second==0) {
                if (minute==0) {
                    if (hour == 0) {
                        $("#submit-answer").trigger("click");
                        return false;
                    } else{
                        hour -= 1;
                        minute = 59;
                        second = 59;
                        obj_hour.text(FormatTwoBits(hour));
                        obj_minute.text(FormatTwoBits(minute));
                        obj_second.text(FormatTwoBits(second));
                    }
                } else{
                    minute -= 1;
                    second = 59;
                    obj_minute.text(FormatTwoBits(minute));
                    obj_second.text(FormatTwoBits(second));
                }
            } else{
                second -= 1;
                obj_second.text(FormatTwoBits(second))
            }
            setTimeout(CountTime, 1000)
        }

        function FormatTwoBits(num){
            num = Number(num);
            if (num<10) {
                return '0' + String(num);
            }
            return String(num);
        }
    }

    function MarkHasBeenAnswer(){
        $(".option > label").on("click",function(){
            var str_for = $(this).attr("for");
            var question_num = str_for.split("_");
            var uuid = $(".test_title").attr("data-uuid");
            var mark_href = "#qu_" + uuid + "_" + question_num[1];
            if ($(this).siblings().attr("type")=="checkbox" && $(this).siblings().is(":checked")) {
                var name = $(this).siblings().attr("name");
                var num = $("input[type='checkbox'][name='" + name + "']:checked").length;
                if (num==0) {
                    $(".answerSheet ul li").each(function(){
                        if ($(this).hasClass("hasBeenAnswer")) {
                            if ($(this).children().attr("href")==mark_href) {
                                $(this).removeClass("hasBeenAnswer")
                            }
                        }
                    })
                }
            } else{
                $(".answerSheet ul li").each(function(){
                    if (!$(this).hasClass("hasBeenAnswer")) {
                        if ($(this).children().attr("href")==mark_href) {
                            $(this).addClass("hasBeenAnswer")
                        }
                    }
                })
            }

        });

        $(".option > input").on("change",function(){
            var str_for = $(this).attr("id");
            var question_num = str_for.split("_");
            var uuid = $(".test_title").attr("data-uuid");
            var mark_href = "#qu_" + uuid + "_" + question_num[1];
            if ($(this).attr("type")=="checkbox" && !$(this).is(":checked")) {
                var name = $(this).attr("name");
                var num = $("input[type='checkbox'][name='" + name + "']:checked").length;
                if (num==0) {
                    $(".answerSheet ul li").each(function(){
                        if ($(this).hasClass("hasBeenAnswer")) {
                            if ($(this).children().attr("href")==mark_href) {
                                $(this).removeClass("hasBeenAnswer")
                            }
                        }
                    })
                }
            } else{
                $(".answerSheet ul li").each(function(){
                    if (!$(this).hasClass("hasBeenAnswer")) {
                        if ($(this).children().attr("href")==mark_href) {
                            $(this).addClass("hasBeenAnswer")
                        }
                    }
                })
            }
        })
    }

    function SubmitAnswer(){

        $("#submit-answer").on("click", function () {
            var sure = confirm("确认交卷？");
            if (!sure) {
                return false;
            }
            var form_data = new FormData($(".test").find("form")[0]);
            var examiner_uuid = $(".test_title").attr("data-uuid");

            for (var pair of form_data.entries()){
                console.log(pair[0]+':'+pair[1])
            }

            $.ajax({
                url:'/exam/exam_paper/' + String(examiner_uuid),
                type:'POST',
                dataType:'json',
                data:form_data,
                processData: false,
                contentType: false,
                headers:{ "X-CSRFtoken":getCookie("csrftoken")},
                success:function (data) {
                    if (data["status"]) {
                        console.log("保存成功");
                        new_href = '/' ;
                        window.location.href = new_href;
                    }
                },
                error:function (data) {
                    alert("系统异常，请重试");
                }
            });

        })

    }

    function getCookie(name) {
        var start = document.cookie.indexOf(name + "="); //得到cookie字符串中的名称
        var len = start + name.length + 1; //得到从起始位置到结束cookie位置的长度
        //如果起始没有值且name不存在于cookie字符串中，则返回null
        if ((!start) && (name != document.cookie.substring(0, name.length))) {
            return null;
        }
        if (start == -1) return null; //如果起始位置为-1也为null
        var end = document.cookie.indexOf(';', len); //获取cookie尾部位置
        if (end == -1) end = document.cookie.length; //计算cookie尾部长度
        return unescape(document.cookie.substring(len, end)); //获取cookie值
    }
});