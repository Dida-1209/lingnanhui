function build_label_in_js(){
// 生成标签
        var labels = [
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
            el: '#search_div',
            data: {"objs": labels},
            compiled: function(){
                $("div[own-d2='zhineng']").hide()
                $('div[own-d1="industry"] > span').on('click', function(){
                    select_industry($(this).html())
                    $('div[own-d1="industry"] > span').attr("class", "mui-badge mui-badge-inverted")
                    $(this).attr("class", "mui-badge mui-badge-primary")
                });
                $('div[own-d2="zhineng"] > span').on('click', function(){
                    select_zhineng($(this).html())
                    show_or_hide_search_div()
                    $("#submit").trigger("click")
                });

                $('div[own-d1="industry"] > span').each(function(){
                    if($(this).html() == '全部行业'){
                        $(this).trigger('click')
                        return false
                    }
                });
                select_zhineng('全部类别')
                init_in_js()
            }
        })
}

        function select_industry(industry_name){
            $("div[own-d2='zhineng']").hide()
            $("div[own-d1='"+industry_name+"']").show()
            select_zhineng("全部类别")
            if(industry_name=='全部行业')industry_name=''
            $("input[name='industry']").val(industry_name)
        }

        function select_zhineng(role_name){
            $('div[own-d2="zhineng"] > span').attr("class", "mui-badge mui-badge-inverted")
            $('div[own-d2="zhineng"] > span').each(function(){
                if($(this).html() == role_name){
                    $(this).attr("class", "mui-badge mui-badge-primary")
                }
            })
            if(role_name == "全部类别")role_name=''
                $("input[name='role']").val(role_name)
        }



 function getPar(par){
    //获取当前URL
    var local_url = document.location.href;
    //获取要取得的get参数位置
    var get = local_url.indexOf(par +"=");
    if(get == -1){
        return '';
    }
    //截取字符串
    var get_par = local_url.slice(par.length + get + 1);
    //判断截取后的字符串是否还有其他get参数
    var nextPar = get_par.indexOf("&");
    if(nextPar != -1){
        get_par = get_par.slice(0, nextPar);
    }
    return unescape(decodeURI(get_par));
}

        function show_or_hide_search_div(){
            var obj = document.getElementById('search_div');
            if(obj.style.display == 'none'){
                obj.style.display = 'block';
            }else{
                obj.style.display = 'none';
            }
        }
        function init_in_js(){
            $("#s").val(getPar('search_key'))
            var industry = getPar('industry')
            var role = getPar('role')
            var temp_industry = (industry == '') ? '全部行业' : industry
            var temp_role = (role == '') ? '全部类别' : role

            $('div[own-d1="industry"] > span').each(function(){
                if($(this).html() == temp_industry){
                    $(this).trigger('click')
                    return false
                }
            });
            select_zhineng(temp_role)
        }