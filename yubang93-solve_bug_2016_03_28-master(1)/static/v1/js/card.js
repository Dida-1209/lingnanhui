function own_init(){
(function(){
	$(function(){
		//点击菜单下滑
				$("#i-btn").on("click",function(e){
					$("#i-mask").addClass("i-mask");
					$(".i-menu").show();
					e.stopPropagation();
					init_select_role()
				});
//              $("#f-btn").on("click",function(e){
//					$("#mask").addClass("mask");
//					$(".i-menu").show();
//					e.stopPropagation();
//					init_select_role()
//				});
				
		//点击li子菜单变化
			
//				$(".i-menu>li").on("click",function(e){
//						var curIndex=$(this).index();
//						var litop="-"+(curIndex+1)*5.88+"vh";
//						if(!$(this).hasClass("lihover")){
//						$(this).addClass("lihover").siblings().removeClass("lihover");
//						e.stopPropagation();
//					}
//				});

		//点击菜单上滑
	          
	            $("#i-mask").click(function(){
					$(".i-menu").removeAttr("style");
					$(".i-menu").hide();
					$("#i-mask").removeClass("i-mask");
	            });
	            
	    //阻止冒泡
			  	
			  	$(".i-menu").click(function(e){
			  		e.stopPropagation();
			  	});
		})
})()
}

var target_url;
var after_login_url;
function add_industry_and_function(){

	var datas = [
		{"a": "互联网/软件", "b": ["产品","开发","设计","测试","技术运维","项目管理","游戏策划","运营","编辑","市场公关","销售","财务","人力资源","战略投资","法务","行政IT","高管","数据","其他"]}
		,{"a": "金融", "b":["银行", "证券", "公募基金", "VC/PE", "信托", "资产管理", "保险", "金融租凭", "财务公司", "典当拍卖", "金融市场管理机构", "其他"]}
		,{"a": "重工制造", "b":["电气设备", "工业机械", "仪器仪表", "机械部件", "汽车", "化工", "铁路船舶航天设备", "采矿", "冶炼", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "法律/会计/资讯", "b":["法律服务", "审计税务", "商业资讯", "资产评估", "市场调查", "广告公关", "租赁服务", "猎头服务", "其他"]}
		,{"a": "贸易", "b":["项目管理", "采购", "物流跟单", "仓储", "单证报关", "市长公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "房产建筑", "b":["规划设计", "工程施工", "项目管理", "物业管理", "房地产中介", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "学生", "b":["互联网", "电子", "电信", "金融", "法律/会计/资讯", "教育科研", "文化传媒", "贸易", "零售", "酒店旅游", "生活服务", "政府/社会组织", "轻工制造", "重工制造", "制药/生物技术", "医疗", "房产建筑", "交通运输", "能源环保水利", "农林牧渔"]}
		,{"a": "文化传媒", "b":["记者编辑", "策划", "设计", "摄影", "导演", "主持", "演员模特", "发行制片", "后期", "经纪人", "其他"]}
		,{"a": "电子/硬件", "b":["研发/工艺", "采购", "供应链", "项目管理", "生产", "仓储", "质检", "维修", "市场公关", "销售", "财务", "人力资源", "战略资源", "法务", "行政IT", "高管", "其他"]}
		,{"a": "轻工制造", "b":["家用电器", "食品饮料", "生活日用品", "纺织服装", "皮革箱包", "建材家居", "珠宝首饰", "烟草", "市场公关", "销售", "财务", "人力资源", "战略资源", "法务", "行政IT", "高管", "其他"]}
		,{"a": "教育科研", "b":["科学研究", "中小学老师", "培训老师", "教学管理", "课程开发", "招生顾问", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "零售", "b":["市场公关", "销售", "招商采购", "店员导购", "安防仓储", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "能源环保水利", "b":["石油", "天然气", "煤炭", "电力", "新能源", "水利", "环保", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "酒店旅游", "b":["酒店服务", "采购", "产品设计", "景点管理", "导游", "厨师", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "制药/生物科技", "b":["研发试验", "生产", "供应链", "采购", "仓储", "质检", "注册", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "医疗", "b":["医生", "医院管理", "药剂师", "麻醉师", "医学影像师", "预防医生", "护理", "营养师", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "生活服务", "b":["美容美发", "家政", "维修", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "交通运输", "b":["司机", "仓储", "货代", "调度", "快递", "船员", "机长", "乘务", "地勤", "路政", "港务", "市场公关", "销售", "财务", "人力资源", "战略资源", "法务", "行政IT", "高管", "其他"]}
		,{"a": "电信", "b":["技术研发", "采购", "工程", "项目管理", "维修", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
		,{"a": "政府/社会组织", "b":["事业单位", "公务员", "军人", "军工", "社会团体及非营利组织", "其他"]}
		,{"a": "农林牧渔", "b":["农林牧渔", "市场公关", "销售", "财务", "人力资源", "战略投资", "法务", "行政IT", "高管", "其他"]}
	]

    new Vue({
    	el: '#role_div',
    	data:{objs:datas},
    	ready: function(){
    		init_select_role()
    	}
    })

    $("li[own-sign='zhiwei']").hide();
	own_init();
}

$(document).ready(function(){
	get_own_card_in_make_card();

});

function init_select_role(){


	$("li[own-sign='zhiwei']").on('click', function(){
		$("#role").html(this.children[0].innerHTML);
		$("#mask").trigger('click');
		select_color($("#industry").html(), this.children[0].innerHTML);
	});

	$("li[own-sign='hangye']").on('click', function(){
		$("#industry").html(this.children[0].innerHTML);
		$("li[own-sign='zhiwei']").hide();
		$("li[own-index='"+$(this).attr("own-index")+"']").show();
        select_color(this.children[0].innerHTML, '');
	});


	// 模拟点击行业
	var temp_index = 0;
	$("li[own-sign='hangye']").each(function(){
	    if(this.children[0].innerHTML == $("#industry").html()){
	        $(this).trigger('click');
	        temp_index = $(this).attr("own-index")
	    }
	});

	select_color($("#industry").html(), $("#role").html())

}

// 标志选择的行业和职位
function select_color(a, b){

    $("li[own-sign='hangye']").css("border-left", " 10px solid white");
    $("li[own-sign='hangye']").css("background-color", "white");
    $("li[own-sign='hangye']").each(function(){
        if(this.children[0].innerHTML == a){
            $(this).css("border-left", " 10px solid #23B9AB");
	        $(this).css("background-color", "#B3ADAD");
        }
    });
    $("li[own-sign='zhiwei']").css("background-color", "#B3ADAD");
    $("li[own-sign='zhiwei']").each(function(){
        if(this.children[0].innerHTML == b){
            $(this).css("background-color", "white");
        }
    });
}

function click_img(){
	$("#img_upload").trigger("click");
	/*if(confirm("你是否要更换头像？")){
		upload_file();
	}*/
}

function upload_file(){

	var formData = new FormData();
	formData.append("file", document.getElementById('img_upload').files[0]);
	$.ajax({
		"url": "/api/v1/update_pic",
		"type": "POST",
		"processData": false,
		"contentType": false,
		"cache": false,
		"data":formData,
		"success": function(data){
			document.getElementById('avatar').src=data;
		},
		"error": function(){
			mui.alert('图片上传失败！')
		}
	});

}

function next_page(){
	$(".first_page").hide();
	$(".two_page").show();
}

function last_page(){
	$(".first_page").show();
	$(".two_page").hide();
}

function delete_span(obj){
	obj.parentNode.outerHTML = '';
}

function add_label(get_content_id, add_content_id){

	if(!$.trim($("#"+get_content_id).val())){
		alert('关键字不能为空！')
		return;
	}

	var html = '<span class="bigdata"><img src="/static/v1/images/2.png"/>';
	html += $("#"+get_content_id).val();
    html += '<img src="/static/v1/images/5.png" onclick="delete_span(this);"/></span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;';
	$("#"+add_content_id).html($("#"+add_content_id).html() + html);
	$("#"+get_content_id).val('');
}

function build_card(){
	var name = $("#name").val();
	var company = $("#company").val();
	var industry = $("#industry").html();
	var role = $("#role").html();
	var resources = $("#resources").val();
	var out_resource_type = "";
	var out_keyword = "";
	var avatar = document.getElementById('avatar').src;
	var invitation_code = $("#invitation_code").val();

	var province_and_city = handle_province_and_city()

	$("#out_resource_type span").each(function(){
		if(out_resource_type){
			out_resource_type += "#";
		}
		out_resource_type += $(this).text();
	});

	$("#out_keyword span").each(function(){
		if(out_keyword){
			out_keyword += "#";
		}
		out_keyword += $(this).text();
	});

	// 判断数据是否为空，为空不允许提交
	if(!$.trim(avatar)){
		last_page()
		alert('头像不能为空！')
		return
	}
	if(!$.trim(name)){
		last_page()
		alert('名字不能为空！')
		return
	}
	if(!$.trim(company)){
		last_page()
		alert('公司不能为空！')
		return
	}
	if(!$.trim(industry)){
		last_page()
		alert('行业不能为空！')
		return
	}
	if(!$.trim(role)){
		last_page()
		alert('职能不能为空！')
		return
	}
	if(!$.trim(invitation_code)){
		last_page()
		alert('邀请码不能为空！')
		return
	}

	if(!$.trim(out_keyword)){
		alert('资源关键字不能为空！')
		return
	}

	if(province_and_city.length == 0){
		alert('省和城市不能为空！')
		return
	}

	$.ajax({
		url: target_url,
		type: 'POST',
		data: {
			"avatar": avatar,
			"name": name,
			"company": company,
			"industry": industry,
			"resources_key": out_keyword,
			"role": role,
			"invitation_code": invitation_code,
			"from_open_id": getParFromUrl('from_open_id'),
			"province": province_and_city[0],
			'city': province_and_city[1],
			'area': province_and_city[2]
		},
		success: function(data){
			if(data['code'] == 0){
				mui.alert("生成名片成功！");
				location.href = after_login_url;
			}else{
				last_page()
				mui.alert(data['msg'])
			}
		},
		error: function(){
			mui.alert('服务器无法响应！');
		}
	});
}


function handle_label(aaa){
	var arrs = aaa.split("#");

	if(aaa)
	for(var i in arrs){
		$("#input_keyword_type").val(arrs[i]);
		add_label("input_keyword_type", "out_keyword");
	}
}

// 图片转base64
function readFile(obj){
        var file = obj.files[0];
        //判断类型是不是图片
        if(!/image\/\w+/.test(file.type)){
                alert("请确保文件为图像类型");
                return false;
        }
        var reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = function(e){
                alert(this.result); //就是base64

        }
}


function get_own_card_in_make_card(){

	$.ajax({
		url: '/api/v1/get_own_card_in_make_card',
		type: 'get',
		data: {},
		success: function(data){
			$("#avatar").attr("src", data['avatar']);
			$("#name").val(data['name'])
			$("#company").val(data['company'])

			$("#industry").html(data['industry'])
			$("#role").html(data['role'])

			if(data['invitation_code'])
			$("#invitation_code").val(data['invitation_code'])

			target_url = data['target_url']
			after_login_url = data['after_login_url']
			handle_label(data['resources_key'])

			add_industry_and_function();

			// 填充省市
			$("#province_and_city").val(data['province'] + ',' + data['city'] + ',' + data['area'])

			wait_data_from_server()
		},
		error: function(xhr,type,errorThrown){
		                if('abort' == type){
                // 用户终止的异常不处理
                return
            }
			mui.alert('服务器无法响应！');
		}
	});
}


// 填充邀请码
$("#invitation_code").val(getParFromUrl('invitation_code'))


function handle_province_and_city(){
	var t = $("#province_and_city").val()
	if(t == ',,'){
		return []
	}
	arrs = t.split(",")
	if(arrs.length == 2){
		arrs[2] = ''
	}
	return arrs
}


function wait_data_from_server(){
	// 初始化显示
	last_page()
	$('.loadin_div_first').hide()


	var area = new LArea();
	area.init({
		'trigger': '#province_and_city',//触发选择控件的文本框，同时选择完毕后name属性输出到该位置
		'valueTo':'#out_province_and_city',//选择完毕后id属性输出到该位置
		'keys':{id:'id',name:'name'},//绑定数据源相关字段 id对应valueTo的value属性输出 name对应trigger的value属性输出
		'type':1,//数据源类型
		'data':LAreaData//数据源
	});
}