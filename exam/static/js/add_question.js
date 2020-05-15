function doOpenQuestion(ctype,uuid,buuid){
	var trueOption="A";
	var txtAnalysis = "";
	var dict = {};
	dict['txtContent'] = "";
	dict['imgs'] = [];
	
	var dictOptions = {};
	dictOptions['Txt'] = dict;
	dictOptions['A'] = dict;
	dictOptions['B'] = dict;
    // console.log(typeof(dictOptions));
	
	if (uuid) {
        var content = {
            "bank-uid":buuid,
            "question-uid": uuid
        };
		$.ajax({
			url:'/exam/getquestion',
			type:'get',
			dataType:'json',
			data:content,
			async:false,
			headers:{ "X-CSRFtoken":getCookie("csrftoken")},
			success:function (data) {
				if (data['status']){
					var dict = {};
					trueOption = data['other'][0];
                    txtAnalysis = data['other'][1];

                    dict['txtContent'] = data['txt'][0];
                    dict['imgs'] = data['imgs'][0];
                    dictOptions['Txt'] = dict;

                    for (var i=1;i<7;i++) {
                        var current = String.fromCharCode('A'.charCodeAt() + i - 1);
                        var dict = {};

						if (typeof(data['txt'][i]) != 'undefined' || data['imgs'][i].length){

							dict['txtContent'] = data['txt'][i];
							if (typeof(data['txt'][i]) == 'undefined'){
								dict['txtContent'] = "";
							}
							dict['imgs'] = data['imgs'][i];
							dictOptions[current] = dict;
						}
                    }
				} else {
					alert(data["message"]);
				}
			},
			error:function (data) {
				alert("系统异常，请重试");
			}
		});
	}

	var editor_header_str = '<div class="editor-header">'+
								'<div style="padding: 2px 0 0 4px; float: left;color:#5A5A5A;margin-left:6px;font-size:15px;font-family:Microsoft YaHei,宋体;">'+
									'<span>试题新增&amp;编辑</span>'+
								'</div>'+
								'<div id="ButtonClose" onclick="javascript:$(this).parent().parent().remove();" style="float: right;right: 10px;position: relative;cursor: pointer;">'+
									'<i class="iconfont icon-off"></i>'+
								'</div>'+
							'</div>';
	
	
	var top_content_left_str = '<div class="topic-content-left">'+
									'<ul>'+
										'<li>题库：</li>'+
										'<li>题目类型：</li>'+
										'<li>试题内容：</li>'+
									'</ul>'+
								'</div>';
								
	var bank_name = $(".mc-title font a:last-child").text();
	var input_type="";
	var bank_type="";
	switch (ctype){
		case "mc":
			bank_type = "单项选择题";
			input_type = 'radio';
			break;
		case "mcs":
			bank_type = "多项选择题";
			input_type = 'checkbox';
			break;
		case "tf":
			bank_type = "判断题";
			break;
	}
	
	
	var top_content_right_str1 = '<div class="topic-content-right">'+
									'<ul>'+
										'<li data-rel=""><span>' + bank_name + '<input type="text" name="bank-uid" value="' + buuid + '" hidden="hidden"/></span></li>'+
										'<li data-type="mc"><span>' + bank_type + '<input type="text" name="question-uid" value="' + uuid + '" hidden="hidden"/></span></li>'+
										'<li>'+
											'<div style="width: 50%;clear: both;float: left;">'+
												'<textarea name="txtQuestion" style="width: 100%;height: 120px;resize: none;padding: 5px;font-size: 14px;color: #777;">' + dictOptions['Txt']['txtContent'] + '</textarea>'+
											'</div>'+
											'<div class="add-imgs-div">'+
												'<ul>';
			
	var top_content_right_str2="";
	for (var i=0;i<dictOptions['Txt']['imgs'].length;i++){
		top_content_right_str2 += '<li style="float: left;height: 120px;width: auto;">'+
									'<div class="previewImg" data-select="txt"><img src="' + dictOptions['Txt']['imgs'][i] + '" onclick="javascript:$(this).parent().next().click();"><i class="delete-img iconfont icon-off" onclick="deleteTopicImg(this)"></i></div>'+
										// '<input type="file" name="txtQuestionimg1" value="" onchange="preview(this)" style="display: none;">'+
								'</li>';
	}
	
	top_content_right_str2 += '<li style="float: left;height: 120px;width: auto;">'+
								'<div class="previewImg"></div>'+
								'<input type="file" name="txtQuestionimg1" value="" onchange="preview(this)" style="display: none;"/>'+
								'<i class="add-img iconfont icon-add-image" onclick="javascript:$(this).prev().click();addNextImg(this);$(this).remove();"></i>'+
							'</li>';
	
	var top_content_right_str3 = '</ul></div></li></ul></div>';
	var top_content_right_str = top_content_right_str1 + top_content_right_str2 + top_content_right_str3;
	var top_content_str = '<div class="topic-content">' + top_content_left_str + top_content_right_str + '</div>';
	
	var aditor_main="";
	if (ctype == 'tf') {
		var topic_judge_str1 = '<div class="topic-judge">'+
								'<table cellspacing="0" cellpadding="0" class="common-table" style="border: none;">'+
									'<tbody><tr><td>选项：</td>';
		var topic_judge_str2;
		if (trueOption=='1') {
			topic_judge_str2 =  '<td><label><input type="radio" name="trueOption" value="1" checked="checked"/>正确</label></td>'+
								'<td><label><input type="radio" name="trueOption" value="0" />错误</label></td>';
		} else{
			topic_judge_str2 =  '<td><label><input type="radio" name="trueOption" value="1" />正确</label></td>'+
								'<td><label><input type="radio" name="trueOption" value="0" checked="checked"/>错误</label></td>';
		}
		var topic_judge_str3='</tr></tbody></table></div>';
		var topic_judge_str = topic_judge_str1 + topic_judge_str2 + topic_judge_str3;
		editor_main = topic_judge_str;
		
		
	} else{
		var topic_choice_str1 = '<div class="topic-choice">'+
									'<table cellspacing="0" cellpadding="0" style="border:1px solid #f2f4f8;width:100%;text-align: center;" class="common-table">'+
										'<thead>'+
											'<tr>'+
												'<th colspan="2" width="10%">勾选设置正确答案	</th>'+
												'<th width="90%">选项内容</th>'+
											'</tr>'+
										'</thead>'+
										'<tbody>';
		var topic_choice_str2 = "";
		for (var i=0;i<Object.keys(dictOptions).length-1;i++){
			var current = String.fromCharCode('A'.charCodeAt()+i);
			var check;
			var tmp1="";
			var tmp2="";
			var tmp3="";
			if (trueOption.indexOf(current)==-1) {
				check = "";
			} else{
				check='checked="checked"';
			}
			tmp1 = '<tr>'+
						'<td><label><input type="' + input_type + '" value="' + current + '" name="trueOption" ' + check + '/></label></td>'+
						'<td>' + current + '</td>'+
						'<td>'+
							'<textarea name="txtQuestionOption' + current + '" style="width: 50%;height: 120px;resize: none;padding: 5px;font-size: 14px;color: #777;float: left;">' 
							+ dictOptions[current]['txtContent'] + '</textarea>'+
							'<div class="add-imgs-div">'+
							'<ul>';
			var j=0;				
			for (j=0;j<dictOptions[current]['imgs'].length;j++){
				tmp2 += '<li style="float: left;height: 120px;width: auto;">'+
							'<div class="previewImg" data-select="' + current + '"><img src="' + dictOptions[current]['imgs'][j] + '" onclick="javascript:$(this).parent().next().click();"><i class="delete-img iconfont icon-off" onclick="deleteTopicImg(this)"></i></div>'+
								//'<input type="file" name="option' + current + 'img' + String(j+1) + '" value="" onchange="preview(this)" style="display: none;">'+
						'</li>';
			}
			tmp2 += '<li style="float: left;height: 120px;width: auto;">'+
						'<div class="previewImg"></div>'+
						'<input type="file" name="option' + current + 'img' + String(j+1) + '" value="" onchange="preview(this)" style="display: none;"/>'+
						'<i class="add-img iconfont icon-add-image" onclick="javascript:$(this).prev().click();addNextImg(this);$(this).remove();"></i>'+
					'</li>';
			tmp3 = '</ul></div></td></tr>';
			topic_choice_str2 += tmp1 + tmp2 + tmp3;
		}
		var topic_choice_str3 = '<tr>'+
									'<td colspan="3" style="padding-left:38px;padding-bottom:15px;text-align: left;padding-top: 10px;">'+
										'<button type="button" style="height:25px;line-height:10px;font-size:12px;" id="btnAddObjectiveOption" class="btn btn-default" onclick=AddAnswerOption(this,\"' + ctype + '\")><i class="iconfont icon-add1"></i>添加选项</button>'+
										'<button type="button" style="height:25px;line-height:10px;font-size:12px;" id="btnDelObjectiveOption" class="btn btn-red" onclick="DelAnswerOption(this)"><i class="iconfont icon-minus1"></i>删减选项</button>'+
									'</td>'+
								'</tr>'+
							'</tbody>'+
						'</table>'+
					'</div>';
		var topic_choice_str = topic_choice_str1 + topic_choice_str2 + topic_choice_str3;
		editor_main = topic_choice_str;
	}
	var topic_analysis_str = '<div class="topic-Analysis">'+
								'<label for="">试题分析</label>'+
								'<div>'+
									'<textarea name="txtAnalysis">' + txtAnalysis + '</textarea>'+
								'</div>'+
							'</div>';

	var editor_body_str = '<div class="editor-body"><form action="." method="post" id="txtQuestionForm">' + top_content_str + editor_main + topic_analysis_str + '</form></div>'
	var topic_save_str = '<div class="topic-save">'+
							'<button type="button" class="btn btn-blue" onclick="doSave(this,\'Save\');">保存</button>'+
							'<button type="button" class="btn btn-default" onclick="doSave(this,\'SaveAndAdd\');">保存并新增</button>'+
							'<button type="button" class="btn btn-default"  onclick="doSave(this,\'SaveAndClose\');">保存并关闭</button>'+
						'</div>';
	var editor_content_str =  '<div class="editor-content">' + editor_header_str + editor_body_str + topic_save_str + '</div>'
	$("#full-screen").before(editor_content_str);
}


function doDeleteQuestion(ctype,uuid,buuid){
	var makeSure = confirm("确定删除吗?");
	if (makeSure) {
		var content = {
			"bank-uid": buuid,
			"question-uid" :uuid
		};
		$.ajax({
			url:'/exam/deletequestion',
			type:'get',
			dataType:'json',
			data:content,
			headers:{ "X-CSRFtoken":getCookie("csrftoken")},
			success:function (data) {
				if (data['status']){
					window.location.reload();
				} else {
					alert(data["message"]);
				}
			},
			error:function (data) {
				alert("系统异常，请重试");
			}
		});
	}
}

function importQuestion(uuid){
	var host = String(window.location.host);
	var mc = "http://" + host + '/role/downloadexcel/mc';
	var mcs = "http://" + host + '/role/downloadexcel/mcs';
	var tf = "http://" + host + '/role/downloadexcel/tf';

	var str_import = '<div class="batch-add-question" data-uuid="' + uuid + '">'+
						'<div style="height: 40px;line-height: 30px;font-size: 16px;text-align: left;border-bottom: 1px solid gainsboro;padding: 5px 10px;">'+
							'<p>批量导入试题<span style="float: right;cursor: pointer;" onclick="CloseImportQuestion()"><i class="iconfont icon-off"></i></span></p>'+
						'</div>'+
						'<div class="batch-content-nr">'+
							'<form action="." method="post">'+
								'<table>'+
									'<tr>'+
										'<td>模板下载</td>'+
										'<td><a href="' + mc + '">单项选择题上传模板.xlsx</a><a href="' + mcs + '">多项选择题上传模板.xlsx</a><a href="' + tf + '">判断题上传模板.xlsx</a></td>'+
									'</tr>'+
									'<tr>'+
										'<td>试题文件</td>'+
										'<td><input type="file" name="uploadfile" value="" /></td>'+
									'</tr>'+
									'<tr>'+
										'<td>导入结果</td>'+
										'<td id="import-result"><a href="" style="color: #2b71c8;font-size: 14px;"></a></td>'+
									'</tr>'+
								'</table>'+
							'</form>'+
						'</div>'+
						'<div class="topic-save" style="top: 260px;">'+
							'<button type="button" class="btn btn-blue" onclick="batchAddQuestion(this)">保存</button>'+
							'<button type="button" class="btn btn-default"  onclick="CloseImportQuestion()">关闭</button>'+
						'</div>'+
					'</div>';
	$("#full-screen").before(str_import);
}

function CloseImportQuestion() {
	$("body .batch-add-question").remove();
}

function batchAddQuestion(obj){
	var upload_file = $(obj).parent().prev().find("input[name='uploadfile']").get(0).files[0];
	if (!upload_file) {
		alert("上传的文件不能为空");
		return false;
	}
	var uuid = $(obj).parent().parent().attr("data-uuid");
	console.log(uuid);
	var form_data = new FormData();
	form_data.append("file", upload_file);
	form_data.append("uuid", uuid);
	$.ajax({
		url:'/exam/importquestion',
		type:'POST',
		dataType:'json',
		data:form_data,
		processData: false,
		contentType: false,
		headers:{ "X-CSRFtoken":getCookie("csrftoken")},
		success:function (data) {
			if (data['status']){
				var btn = $(obj).parent().prev().find("#import-result").find("a")
				btn.attr("href" ,data['address']);
				btn.text(data['name']);
			} else {
				alert(data["message"]);
			}
		},
		error:function (data) {
			alert("系统异常，请重试");
		}
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
	
	



