$(function(){
				
	$("tbody > tr").on("click",".editor-content .editor-content-top p i",function(){
		$("tbody > tr .editor-content").remove();
		$("#full-screen").css({"display":"none"});
	});
	
	
	$("tbody > tr").on("mouseenter",".editor-content .input-right .student-id a i",function(){
		if ($(this).hasClass("icon-suoding")) {
			var dialog = '<span class="lock-info">解除锁定</span>';
		} else{
			var dialog = '<span class="lock-info">锁定输入</span>';
		}
		$(this).parent().after(dialog);
	});
	
	$("tbody > tr").on("mouseleave",".editor-content .input-right .student-id a i",function(){
		$(this).parent().next().remove();
	});
	
	
	$("tbody > tr").on("click",".editor-content .input-right .student-id a i",function(){
		if ($(this).hasClass("icon-suoding")) {
			$(this).parent().prev().attr("disabled", false);
			$(this).attr("class","iconfont icon-jiesuo");
		} else{
			$(this).parent().prev().attr("disabled", true);
			$(this).attr("class","iconfont icon-suoding");
		}
	});
	
	$("tbody > tr").on("click",".editor-content .input-right input[type='radio']",function(){
		if ($(this).attr("checked")!='checked') {
			$(this).attr("checked", "checked").siblings("input").removeAttr("checked")
		} 
	});
	
	editorStuInfo();
	submitEditorStuInfo();
	changeStudentStatus();
	deleteStudentInfo();
	
	function changeStudentStatus() {
		$(".mc-table tbody tr .Switch label").on("click",function () {
			var content = {
				"student": $(this).parent().parent().attr("data-stuid")
			};
			var current = $(this);
			$.ajax({
				url:'/role/changeStudentStatus',
				type:'POST',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data){
					if(data['status']=='0'){
						alert("状态修改失败");
					}
				},
				error:function (data) {
					alert("系统异常，请重试")
				}
			})
		})
	}
	
	function editorStuInfo(){
		
		$(".editor-stu-info").on("click",function(){
			var ww = $(document).width();
			var wh = $(document).height();
			var est_left = (ww - 400)/2;
			var est_top = (wh - 350)/2;
			var stu_dict = $(this).parent().parent().find("td");
			var stu_id = $.trim(stu_dict.eq(0).text());
			var stu_name = $.trim(stu_dict.eq(1).text());
			var stu_sex = '';
			var stu_phone = $.trim(stu_dict.eq(3).text());
			var stu_email = $.trim(stu_dict.eq(4).text());
			switch ($.trim(stu_dict.eq(2).text())){
				case '男':
					stu_sex = 'male';
					break;
				case'女':
					stu_sex = 'female';
					break;
				default:
					stu_sex = 'nomale';
					break;
			}
			editor_content = '<div class="editor-content" data-stuid="' + String(stu_id) + '" style="left:' + String(est_left)+ 'px;top:' + String(est_top) + 'px">'+
							'<div class="editor-content-top">'+
								'<p>考生信息编辑<i class="iconfont icon-off"></i></p>'+
							'</div>'+
							'<form action="." method="post">'+
								'<div class="label-left">'+
									'<ul>'+
										'<li>学号：</li>'+
										'<li>姓名：</li>'+
										'<li>性别：</li>'+
										'<li>手机号：</li>'+
										'<li>邮箱：</li>'+
									'</ul>'+
								'</div>'+
								'<div class="input-right">'+
									'<ul>'+
										'<li class="student-id">'+
											'<input type="text" disabled="disabled" name="studentId"/>'+
											'<a href="javascript:void(0);">'+
												'<i class="iconfont icon-suoding" style="margin-left:10px"></i>'+
											'</a>'+
										'</li>'+
										'<li><input type="text" name="name"/></li>'+
										'<li>'+
											'<input type="radio" name="gender" value="male" /><span>男</span>'+
											'<input type="radio" name="gender" value="female" /><span>女</span>'+
											'<input type="radio" name="gender" value="nomale" /><span>保密</span>'+
										'</li>'+
										'<li><input type="text" name="phone"/></li>'+
										'<li><input type="text" name="email"/></li>'+
									'</ul>'+
								'</div>'+
								'<div class="sub-bottom">'+
									'<a href="javascript:void(0);">确认修改</a>'+
								'</div>'+
							'</form>'+
						'</div>';
			$(this).parent().after(editor_content);
			$("#full-screen").css({"display":"block"});
			var tmp = $(this).parent().next();
			tmp.find("input[name='studentId']").val(stu_id);
			tmp.find("input[name='name']").val(stu_name);
			tmp.find("input[name='phone']").val(stu_phone);
			tmp.find("input[name='email']").val(stu_email);		
			tmp.find("input[name='gender']").each(function(){
				if ($(this).val()==stu_sex) {
					$(this).attr("checked", true);
				} 
			})
		})
		
	}
	
	function submitEditorStuInfo(){
		
		$("tbody > tr").on("click",".editor-content .sub-bottom a", function(){
			var old_stu_id = $("tbody > tr .editor-content").attr("data-stuid");
			var tmp = $("tbody > tr .editor-content .input-right ul li");
			var stu_id = $.trim(tmp.eq(0).find("input").val());
			var stu_name = $.trim(tmp.eq(1).find("input").val());
			var stu_sex = '';
			var stu_phone = $.trim(tmp.eq(3).find("input").val());
			var stu_email = $.trim(tmp.eq(4).find("input").val());
			tmp.eq(2).find("input").each(function(){
				if ($(this).attr("checked") == 'checked') {
					stu_sex = $(this).val();
				}
			});

			if(!stu_id){
				alert("学号不能为空，请输入学号");
				return false;
			}

			var content = {
				"username": old_stu_id,
				"newname": stu_id,
				"name": stu_name,
				"sex":stu_sex,
				"phone":stu_phone,
				"email":stu_email
			};
			$.ajax({
				url:'/role/editorStudentInfo',
				type:'POST',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
				success:function (data){
					if(data['status']){
						$("tbody > tr .editor-content").remove();
						$("#full-screen").css({"display":"none"});
						switch (stu_sex){
							case 'male':
								stu_sex = '男';
								break;
							case 'female':
								stu_sex = '女';
								break;
							default:
								stu_sex = '保密';
								break;
						}
						$("tbody tr").each(function(){
							if ($(this).attr("data-stuid") == old_stu_id) {
								$(this).attr("data-stuid", stu_id);
								$(this).children("td").eq(0).text(stu_id);
								$(this).children("td").eq(1).text(stu_name);
								$(this).children("td").eq(2).text(stu_sex);
								$(this).children("td").eq(3).text(stu_phone);
								$(this).children("td").eq(4).text(stu_email);
							}
						})
					}else {
						alert(data["message"]);
					}
				},
				error:function (data) {
					alert("系统异常，请重试")
				}
			});
		})
	}
	
	function deleteStudentInfo() {
        $(".delete-stu-info").on("click", function () {
            var username = $(this).parent().parent().attr("data-stuid");
            var sure = confirm("确认删除当前考生？学号："+ username);
            if(!sure){
                return false;
            }
            var content = {
                "username": username
            };
            var current = $(this);
            $.ajax({
                url:'/role/deleteStudentInfo',
				type:'POST',
				dataType:'json',
				data:content,
				headers:{ "X-CSRFtoken":getCookie("csrftoken")},
                success:function (data) {
                    if (data['status']){
                        $(current).parent().parent().remove();
                    } else {
                        alert(data["message"]);
                    }
                },
                error:function (data) {
                    alert("系统异常，请重试");
                }
            })
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