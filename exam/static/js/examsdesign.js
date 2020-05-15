$(function(){
	addRandomStrategy();
	QuestionTypeChange();
	QuestionBankChange();
	QuestionNumberSet();
	QuestionScoreSet();
	deleteRandomStrategy();
	window.onload = CalculationSumNums();
	
	function addRandomStrategy(){
		$("#btnAddNode").on("click",function(){
			var content = {
				"exam-uuid": $(".append-box").attr("data-examid")
			};
			$.ajax({
				url:'/exam/addrandomnode',
				type:'POST',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					var tr = $('<tr>');
					tr.attr("data-uuid", data["exam"][0]);
					var td1 = '<td>'+
									'<select name="banktype_' + String(data['exam'][0]) + '" style="height: 28px;width: 80%;">'+
										'<option value="mc">单项选择题</option>'+
										'<option value="mcs">多项选择题</option>'+
										'<option value="tf">判断题</option>'+
									'</select>'+
								'</td>';
					var td2 = $('<td>');
					var sle = $('<select>');
					sle.attr("name", "bank_" + String(data['exam'][0]));
					sle.attr("style", "height: 28px;width: 80%;");
					for (var i=0;i<data["banks"].length;i++){
						var op = $("<option>");
						op.val(data["banks"][i]["uuid"]).text(data["banks"][i]["name"]);
						if (data["banks"][i]["uuid"]==data['exam'][1]) {
							op.attr("selected", "selected")
						}
						sle.append(op);
					}
					td2.append(sle);
					var td3 = '<td>'+
									'<input type="text" name="questionnum_' + String(data['exam'][0]) + '" id="" value="0" style="height: 28px;width: 30px;"/>'+
									'&#47;'+
									'<span class="max-num">' + String(data['exam'][2]) + '</span>'+
								'</td>'+
								'<td>'+
									'<input type="text" name="questionscore_' + String(data['exam'][0]) + '" id="" value="0.00" style="height: 28px;width: 50px;"/>'+
								'</td>'+
								'<td>0</td>'+
								'<td class="option_btn">'+
									'<a href="javascript:void(0);" style="position: relative;left: 15px;"><i class="iconfont icon-del"></i>删除</a>'+
								'</td>';
					tr.append(td1);
					tr.append(td2);
					tr.append(td3);
					$(".mc-table tbody").append(tr);
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});
		})
	}
	
	function QuestionTypeChange(){
		$(".append-box .mc-table tbody").on("change","tr td:first-child select",function(){
			$(this).parent().next().next().find("input").val(0);
			$(this).parent().next().next().next().find("input").val("0.00");
			$(this).parent().next().next().next().next().text(0);
			CalculationSumNums();
			var content = {
				"ruuid": $(this).parent().parent().attr("data-uuid"),
				"bank-type": $(this).find("option:selected").val()
			};
			var banks = $(this).parent().next().find("select");
			var obj_count = $(this).parent().next().next().find("span");
			$.ajax({
				url:'/exam/questiontypechange',
				type:'GET',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					banks.empty();
					if (data["status"]) {
						for (var i=0;i<data["banks"].length;i++){
							var op = $("<option>");
							op.val(data["banks"][i]["uuid"]).text(data["banks"][i]["name"]);
							if (i===0) {
								op.attr("selected", "selected")
							}
							banks.append(op);
						}
						obj_count.text(data["count"])
					} else {
						alert(data["message"]);
					}
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});

		})
	}
	
	function QuestionBankChange(){
		$(".append-box .mc-table tbody").on("change","tr td:nth-child(2) select",function(){
			$(this).parent().next().find("input").val(0);
			$(this).parent().next().next().find("input").val("0.00");
			$(this).parent().next().next().next().text(0);
			CalculationSumNums();
			var content = {
				"ruuid": $(this).parent().parent().attr("data-uuid"),
				"bank-uuid": $(this).find("option:selected").val()
			};
			var count_obj = $(this).parent().next().find("span");
			$.ajax({
				url:'/exam/questionbankchange',
				type:'GET',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					if (data["status"]) {
						count_obj.text(data["count"])
					} else {
						alert(data["message"]);
					}
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});
		})
	}
	
	function QuestionNumberSet(){
		$(".append-box .mc-table tbody").on("focusout","tr td:nth-child(3) input",function(){
			var max_num = Number($(this).next("span").text());
			var current_num = Number($(this).val());
			var re = /^[0-9]*$/;
			if (current_num>max_num) {
				$(this).val(0);
			} else if (!re.test(current_num) || current_num==0) {
				$(this).val(0);
			}
			current_num = $(this).val();
			var score = $(this).parent().next().find("input").val();
			$(this).parent().next().next().text(current_num*score);
			CalculationSumNums();
			var content = {
				"ruuid": $(this).parent().parent().attr("data-uuid"),
				"count": current_num
			};
			$.ajax({
				url:'/exam/questionnumberset',
				type:'GET',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					if (data["status"]) {
						console.log(data["message"])
					}
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});

		})
	}
	
	
	function QuestionScoreSet(){
		$(".append-box .mc-table tbody").on("focusout","tr td:nth-child(4) input",function(){
			var score = $(this).val();
			var re = /^[0-9]+(\.[0-9]{1,2})?$/;
			if (!re.test(score) || score==0) {
				$(this).val("0.00");
				score = 0
			}
			var num = $(this).parent().prev().find("input").val();
			$(this).parent().next().text(num*score);
			CalculationSumNums();
			var content = {
				"ruuid": $(this).parent().parent().attr("data-uuid"),
				"score": score
			};
			$.ajax({
				url:'/exam/questionscoreset',
				type:'GET',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					if (data["status"]) {
						console.log(data["message"])
					}
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});
		})
	}
	
	function deleteRandomStrategy(){
		$(".append-box .mc-table tbody").on("click","tr td.option_btn a",function(){
			var make_sure = confirm("确认删除当前这条随即策略？");
			if (!make_sure) {
				return false;
			}
			var obj_tr = $(this).parent().parent();
			var content = {
				"ruuid": $(this).parent().parent().attr("data-uuid"),
			};
			$.ajax({
				url:'/exam/deleterandomnode',
				type:'GET',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data) {
					if (data["status"]) {
						obj_tr.remove();
						CalculationSumNums();
					}
				},
				error:function (data) {
					alert("系统异常，请重试");
				}
			});
		})
	}

	function CalculationSumNums(){
		var mcnums=0;
		var mcsnums=0;
		var tfnums=0;
		var mcscores=0;
		var mcsscores=0;
		var tfscores=0;
		var sumnums=0
		var sumscores=0;
		$(".append-box .mc-table tbody tr").each(function(){
			var qt = $(this).find("td:first-child").find("option:selected").val();
			var num = $(this).find("td:nth-child(3)").find("input").val();
			var score = $(this).find("td:nth-child(4)").find("input").val();
			if (qt=='mc') {
				mcnums += Number(num);
				mcscores += Number(num) * Number(score);
			} else if (qt=='mcs') {
				mcsnums += Number(num);
				mcsscores += Number(num) * Number(score);
			} else if (qt=='tf') {
				tfnums += Number(num);
				tfscores += Number(num) * Number(score);
			}
		});
		sumnums = mcnums + mcsnums + tfnums;
		sumscores = mcscores + mcsscores + tfscores;
		$(".exam-info h5 #mcnums").text(mcnums);
		$(".exam-info h5 #mcsnums").text(mcsnums);
		$(".exam-info h5 #tfnums").text(tfnums);
		$(".exam-info h5 #mcscores").text(mcscores);
		$(".exam-info h5 #mcsscores").text(mcsscores);
		$(".exam-info h5 #tfscores").text(tfscores);
		$(".exam-info h5 #sumnums").text(sumnums);
		$(".exam-info h5 #sumscores").text(sumscores);
	}
});

function examSave(method) {
	var form_data = new FormData($(".append-box form")[0]);
	form_data.append("method", method);
	var exam_uuid = $(".append-box").attr("data-examid");
	console.log(form_data);
	for (var pair of form_data.entries()){
		console.log(pair[0]+':'+pair[1])
	}
	$.ajax({
		url:'/exam/exampublish/' + String(exam_uuid),
		type:'POST',
		dataType:'json',
		data:form_data,
		processData: false,
		contentType: false,
		headers:{ "X-CSRFtoken":getCookie("csrftoken")},
		success:function (data) {
			if (data["status"]) {
				console.log("保存成功");
				if (method === 'Publish') {
					alert("试卷信息已发布")
				}
			}else {
				alert(data["error"])
			}
		},
		error:function (data) {
			alert("系统异常，请重试");
		}
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