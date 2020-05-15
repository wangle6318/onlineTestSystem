$(function () {
	window.onload = CalculationScore();
   	setQuestionScore();
	deleteStaticQuestion();

    function setQuestionScore() {
    	var o_score = 0;
    	$(".append-box .mc-table tbody tr td:nth-child(3) input").on("focusin", function () {
    		o_score = $(this).val();
    		console.log(o_score)
		});

        $(".append-box .mc-table tbody tr td:nth-child(3) input").on("focusout", function () {
        	var score = $(this).val();
        	var re = /^[0-9]+(\.[0-9]{1,2})?$/;
			if (!re.test(score) || score==0 || score==o_score) {
				$(this).val(o_score);
				return false;
			}
            var content = {
                "data": $(this).parent().parent().attr("data-uuid"),
				"score": score
            };
            $.ajax({
                url:'/exam/setstaticquestionscore',
                type:'GET',
                dataType:'json',
                data:content,
                headers:{ "X-CSRFtoken":getCookie("csrftoken")},
                success:function (data) {
                    if (data["status"]) {
                    	CalculationScore();
						console.log("分数修改成功");
                    }
                },
                error:function (data) {
                    alert("系统异常，请重试");
                }
            });
        })
    }

    function deleteStaticQuestion() {
		 $(".append-box .mc-table tbody tr td.option_btn a").on("click", function () {
			var make_sure = confirm("确认删除当前题目？");
			if (!make_sure) {
				return false;
			}
		 	var content = {
                "data": $(this).parent().parent().attr("data-uuid"),
            };
			var current = $(this).parent().parent();
            $.ajax({
                url:'/exam/deletestaticquestion',
                type:'GET',
                dataType:'json',
                data:content,
                headers:{ "X-CSRFtoken":getCookie("csrftoken")},
                success:function (data) {
                    if (data["status"]) {
                    	current.remove();
                    	CalculationScore();
						alert("删除成功");
                    }
                },
                error:function (data) {
                    alert("系统异常，请重试");
                }
            });
		 })
	}

    function CalculationScore() {
    	var mcnums=Number(0),mcsnums=Number(0),tfnums=Number(0);
    	var mcscores = Number(0),mcsscores=Number(0),tfscores=Number(0);
		$(".append-box .mc-table:nth-child(2) tbody tr").each(function () {
			mcnums += 1;
			mcscores += Number($(this).find("td:nth-child(3)").find("input").val());
		});
		$(".append-box .mc-table:nth-child(4) tbody tr").each(function () {
			mcsnums += 1;
			mcsscores += Number($(this).find("td:nth-child(3)").find("input").val());
		});
		$(".append-box .mc-table:nth-child(6) tbody tr").each(function () {
			tfnums += 1;
			tfscores += Number($(this).find("td:nth-child(3)").find("input").val());
		});

		$("#mcnums").text(mcnums);
		$("#mcscores").text(mcscores);
		$("#mcsnums").text(mcsnums);
		$("#mcsscores").text(mcsscores);
		$("#tfnums").text(tfnums);
		$("#tfscores").text(tfscores);
	}
    
});

function openQuestions(bt,uuid){
	$("#full-screen").css({"display":"block"});
	var str_head = '<div class="select-question">'+
						'<div>'+
							'<span>从试题库选择</span>'+
							'<span style="float: right;"><i class="iconfont icon-off" style="cursor: pointer;" onclick="closeQuestion()"></i></span>'+
						'</div>'+
						'<form action="." method="post"><div style="height: 490px;overflow-y: scroll;margin-bottom: 5px;">'+
							'<table class="mc-table">'+
								'<thead>'+
									'<tr>'+
										'<th style="width: 60px;">选择</th>'+
										'<th style="min-width: 105px;">试题类型</th>'+
										'<th style="min-width: 220px;">试题库</th>'+
										'<th style="min-width: 600px;">试题内容</th>'+
									'</tr>'+
								'</thead>'+
								'<tbody>';
	var str_body = '';
	
	str_save_btn = '';

	str_save_btn = '<button type="button" class="btn btn-blue" onclick="selectQuestion(\'' + bt + '\',\'' + uuid + '\',false);">选择</button>'+
					'<button type="button" class="btn btn-default" onclick="selectQuestion(\'' + bt + '\',\'' + uuid + '\',true);">选择并关闭</button>'+
					'<button type="button" class="btn btn-default" onclick="closeQuestion()">关闭</button>';

	var str_foot = '</tbody>'+
				'</table>'+
			'</div></form>'+
			'<div class="topic-save">'+ str_save_btn +
			'</div>'+
		'</div>';
	var content = {
		"question_type": bt,
		"uuid": uuid
	};
	$.ajax({
		url:'/exam/getSelectQuestions',
		type:'GET',
		dataType:'json',
		data:content,
		headers:{ "X-CSRFtoken":getCookie("csrftoken")},
		success:function (data) {
			if (data["status"]) {
				for (var question of data["questions"]){
					str_body += '<tr>'+
									'<td><input type="checkbox" name="QuestionSelect" id="" value="' + question[0] + '" /></td>'+
									'<td>' + question[1] + '</td>'+
									'<td>' + question[2] + '</td>'+
									'<td>' + question[3] + '</td>'+
								'</tr>';
				}
				$("#full-screen").before(str_head+str_body+str_foot);
			}
		},
		error:function (data) {
			alert("系统异常，请重试");
		}
	});
}


function selectQuestion(bt, uuid, mark) {
	var form_data = new FormData($(".select-question form")[0]);
	form_data.append("question_type", bt);
	form_data.append("uuid", uuid);
	$.ajax({
		url:'/exam/selectquestions',
		type:'POST',
		dataType:'json',
		data:form_data,
		processData: false,
		contentType: false,
		headers:{ "X-CSRFtoken":getCookie("csrftoken")},
		success:function (data) {
			if (data["status"]) {
				console.log("保存成功");
				$("body .select-question div:first-child span i").trigger("click");
				if (mark) {
                    window.location.reload();
                } else {
				    openQuestions(bt,uuid);
                }
			}
		},
		error:function (data) {
			alert("系统异常，请重试");
		}
	});
}

function closeQuestion(){
	$("body").on("click",".select-question div:first-child span i",function(){
		$("body .select-question").remove();
	});

	$("body").on("click",".select-question .topic-save button:last-child",function(){
		$("body .select-question").remove();
	});

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