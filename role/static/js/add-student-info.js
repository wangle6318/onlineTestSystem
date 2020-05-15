$(function(){
	$(".mc-per-add .add-ul-right ul li span i").on("click",function(){
		if ($(this).hasClass("icon-eye-on")) {
			$(this).attr("class", "iconfont icon-EyeOff");
			$(this).parent().siblings("input").attr("type","text");
		} else{
			$(this).attr("class", "iconfont icon-eye-on");
			$(this).parent().siblings("input").attr("type","password");
		}
	});
	
	$(".add-ul-right ul li input[name='stuId']").on("focusout",function(){
		if ($.trim($(this).val())=='' && !$(this).siblings().hasClass("warn-message")) {
			var warn_message = '<span class="warn-message">学号不能为空</span>';
			$(this).parent().append(warn_message)
		} else if($.trim($(this).val())!='') {
			$(this).siblings(".warn-message").remove();
		}
	});
	
	$(".add-ul-right ul li input[name='password']").on("focusout",function(){
		if ($.trim($(this).val())=='' && !$(this).siblings().hasClass("warn-message")) {
			var warn_message = '<span class="warn-message">密码不能为空</span>';
			$(this).parent().append(warn_message)
		} else if($.trim($(this).val())!='') {
			$(this).siblings(".warn-message").remove();
		}
	});
	
	$(".add-ul-right ul li input[name='cpassword']").on("focusout",function(){
		if ($.trim($(this).val())=='' && !$(this).siblings().hasClass("warn-message")) {
			var warn_message = '<span class="warn-message">密码不能为空</span>';
			$(this).parent().append(warn_message)
		} else if($.trim($(this).val())!='' && $.trim($(this).val()) != $.trim($(this).parent("li").prev().find("input[name='password']").val())){
			var warn_message = '<span class="warn-message">两次输入的密码不一致</span>';
			if($(this).siblings().hasClass("warn-message")){
				$(this).siblings(".warn-message").text("两次输入的密码不一致");
			}else{
				$(this).parent().append(warn_message);
			}
		} else{
			$(this).siblings(".warn-message").remove();
		}
	});
	
	perAddStudentInfo();
	batchAddStudentInfo();
	
	function perAddStudentInfo(){
		$(".make-sure-add").on("click",function(){
			var info = $(".mc-per-add .add-ul-right ul li");
			var id = $.trim(info.eq(0).find("input").val());
			var pwd = $.trim(info.eq(1).find("input").val());
			var cpwd = $.trim(info.eq(2).find("input").val());
			if (id && pwd && cpwd && pwd==cpwd) {
				return true;
			} else{
				alert("学号，密码为空或两次输入的密码不一致");
				return false;
			}
		})
	}
	
	
	function batchAddStudentInfo(){
		$(".mc-batch-add .add-batch form p button").on("click",function(){
			var upload_file = $(".mc-batch-add form input").get(0).files[0];
			if (!upload_file) {
				alert("上传的文件不能为空")
			} else {
			    var btn = $(this).parent();
				var form_data = new FormData();
				form_data.append("file", upload_file);
				$.ajax({
					url:'/role/uploadstudentfile',
					type:'POST',
					dataType:'json',
					data:form_data,
					processData: false,
					contentType: false,
					headers:{ "X-CSRFtoken":getCookie("csrftoken")},
					success:function (data) {
						if (data['status']){
							var str_result = '<p>导入模板下载：<span><a href="' + data['address'] + '" style="color: #2b71c8">考生信息批量上传模板-结果.xlsx</a></span></p>';
							btn.before(str_result)
						} else {
							alert(data["message"]);
						}
					},
					error:function (data) {
						alert("系统异常，请重试");
					}
				})

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
	
	
});
