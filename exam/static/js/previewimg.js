function preview(file) {
  	var prevDiv = $(file).parent().find('.previewImg');
  	if (file.files && file.files[0]) {
    	var reader = new FileReader();
    	reader.onload = function(evt) {
     	 	prevDiv.html('<img src="' + evt.target.result + '"onclick="javascript:$(this).parent().next().click();" /><i class="delete-img iconfont icon-off" onclick="javascript:$(this).parent().parent().remove();"></i>');
   		};
    	reader.readAsDataURL(file.files[0]);
 	 } else {//IE
   		prevDiv.html('<div class="img" style="filter:progid:DXImageTransform.Microsoft.AlphaImageLoader(sizingMethod=scale,src=\'' + file.value + '\'"></div>');
  	}
}

function addNextImg(obj){
	var name = $(obj).prev().attr("name");
	name = name.split("g")[0] + 'g' + String(Number(name.split('g')[1])+1);
	
	var img_li = '<li style="float: left;height: 120px;width: auto;">'+
					'<div class="previewImg"></div>'+
					'<input type="file" name="' + name + '" value="" onchange="preview(this)" style="display: none;"/>'+
					'<i class="add-img iconfont icon-add-image" onclick="javascript:$(this).prev().click();addNextImg(this);$(this).remove();"></i>'+
				'</li>';
	$(obj).parent().after(img_li);
}

function AddAnswerOption(obj,qt){
	var obj = obj || window.event;
    if ($(obj).parent().parent().parent().children().length==7) {
		alert(" 选择题至多有六个选项,不能增加了");
        return false;
	}
    var last = $(obj).parent().parent().prev().children("td:eq(0)").find("input").val();
    var current = String.fromCharCode(last.charCodeAt()+1);
    var it;
    if (qt=="mc") {
        it = "radio"
    } else if (qt=="mcs") {
        it = "checkbox"
    }
    var current_ele = '<tr>'+
                        '<td><label><input type="' + it + '" value="' + current + '" name="trueOption"/></label></td>'+
                        '<td>' + current + '</td>'+
                        '<td>'+
                            '<textarea name="txtQuestionOption' + current + '" style="width: 50%;height: 120px;resize: none;padding: 5px;font-size: 14px;color: #777;float: left;"></textarea>'+
                            '<div class="add-imgs-div">'+
                            '<ul>'+
                                '<li style="float: left;height: 120px;width: auto;">'+
                                    '<div class="previewImg"></div>'+
                                    '<input type="file" name="option' + current + 'img1" value="" onchange="preview(this)" style="display: none;"/>'+
                                    '<i class="add-img iconfont icon-add-image" onclick="javascript:$(this).prev().click();addNextImg(this);$(this).remove();"></i>'+
                                '</li>'+
                            '</ul>'+
                        '</div>'+
                        '</td>'+
                    '</tr>';
    $(obj).parent().parent().before(current_ele);
}



function DelAnswerOption(obj){
	if ($(obj).parent().parent().parent().children().length>3) {
		$(obj).parent().parent().prev().remove();
	} else{
		alert(" 选择题至少要保留两个选项 ")
	}
}


function doSave(obj, ops){
	var form_data = new FormData($(obj).parent().parent().children(".editor-body").find("form")[0]);
	if (!JudgeOptionNull(form_data)) {
		return false;
	} else {
        var quid = $("body .editor-content .topic-content-right input[name='question-uid']");

		$.ajax({
			url:'/exam/addquestion',
			type:'POST',
			dataType:'json',
			data:form_data,
			processData: false,
    		contentType: false,
			headers:{ "X-CSRFtoken":getCookie("csrftoken")},
			success:function (data) {
				if (data['status']){
				    console.log(data["quid"]);
					$("body .editor-content .topic-content-right input[name='question-uid']").attr("value", data["quid"]);
					for (var i=0;i<data["imgs"].length;i++ ) {
						var img = $("input[name=" + data["imgs"][i] + "]");
						img.prev().find("img").attr("src", data["urls"][i]);
						img.remove()
					}
                    if (ops === 'Save') {
                        alert(data["message"])
                    } else if (ops === 'SaveAndAdd') {
                        $(obj).parent().parent().remove();
                        $("body .mc-title .btn-group button:first-child").trigger("click")
                    } else if (ops === 'SaveAndClose') {
                        $(obj).parent().parent().remove();
                        window.location.reload();
                    }
				} else {
					alert(data["message"]);
				}
			},
			error:function (data) {
				alert("系统异常，请重试");
			}
		})
	}


	function JudgeOptionNull(fd){
		var allOptions = new Array();
		var content = new Array();
		var allKeys = fd.keys();
		var keys = new Array();

		for (var str of allKeys){
			if (str.slice(0,-1) == "txtQuestionOption") {
			allOptions.push(str)
			}
			if (str.includes("txtQuestionimg") || str =="txtQuestion") {
				content.push(str)
			}
			keys.push(str)
		}

		if (!Judge(content,fd)) {
			alert("请输入试题内容,试题内容不可为空");
			return false;
		} else if (!JudgeOptions(allOptions,fd,keys)) {
			alert("选项内容不能为空,请输入或删除选项");
			return false;
		} else if (!fd.get("trueOption")) {
			alert("请勾选设置正确答案");
			return false;
		} else {
			return true;
		}



		function JudgeOptions(arr,fd,keys){
//			console.log(arr.length)
			for (var i=0; i < arr.length; i++) {
				var tmp = new Array();
				var current =  String.fromCharCode('A'.charCodeAt()+i);
				for (var index in keys){
					if (keys[index].indexOf(current) != -1) {
						tmp.push(keys[index])
					}
				}
				if (!Judge(tmp,fd)) {
					return false;
				}
			}
			return true;
		}


		function Judge(arr,fd){
			if (fd.get(arr[0]) || fd.get(arr[1]).name) {
				return true;
			} else{
			    // console.log(arr[0]);
		        // console.log(arr[1]);
		        var img = $("body .editor-content input[name='" + arr[1] + "']").parent().prev().find("img").attr("src");
		        console.log(img);
		        if (typeof(img) !='undefined' && img.slice(0,4) === 'http') {
		            return true;
                }
				return false;
			}
		}
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
}

function deleteTopicImg(obj) {
    var cimg = $(obj).prev().attr("src");
    if (cimg.slice(0,4) === 'http') {
        var content = {
            "bank-uid":$("body input[name='bank-uid']").val(),
            "question-uid": $("body input[name='question-uid']").val(),
            "path": cimg,
            "option": $(obj).parent().attr("data-select")
        };
        // console.log(content);
        $.ajax({
            url: '/exam/deletetopicimg',
            type: 'get',
            dataType: 'json',
            data: content,
            headers: {"X-CSRFtoken": getCookie("csrftoken")},
            success: function (data) {
                if (data['status']) {
                    console.log(data["message"])
                } else {
                    alert(data["message"]);
                }
            },
            error: function (data) {
                alert("系统异常，请重试");
            }
        })
    }
    $(obj).parent().parent().remove();
}

