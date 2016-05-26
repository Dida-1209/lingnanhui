build_label_in_js()
var page = 1;
// 拉取一页数据
function get_all_card() {

    if(ajax_lock||empty_data_sign){
        return;
    }
    ajax_lock = true;
    document.getElementById('loading_div').style.display = "block";

    var u = location.pathname;
    us = u.split("/");

    mui.ajax('/api/v1/get_all_card_in_a_group', {
        data: {
            'group_token': us[us.length - 1],
            'page': page,
            'count_of_page': 10,
            'search_key': getPar('search_key') == '关键词' ? '' : getPar('search_key'),
            'industry': getPar('industry'),
            'role': getPar('role')

        },
        dataType: 'json',
        //服务器返回json格式数据
        type: 'post',
        //HTTP请求类型
        timeout: 10000,
        //超时时间设置为10秒；
        success: function(data) {

            if(data['objs'].length < 10){
                empty_data_sign = true;
            }

            page++
            //服务器返回响应，根据响应结果，分析是否登录成功；
            for (var i in data['objs']) {
                if (data['objs'][i]['redundancy_labels'] != '') data['objs'][i]['resources_key'] = data['objs'][i]['redundancy_labels'].split("#")
                else data['objs'][i]['resources_key'] = []
            }
            var temp_arr = vm1.objs.concat(data['objs'])
            vm1.$set('objs', temp_arr)
            update_title(data['group_data']['group_title'])
            delete_lock()
        },
        error: function(xhr, type, errorThrown) {

            if('abort' == type){
                // 用户终止的异常不处理
                return
            }

            mui.alert('拉取名片失败！')
            //delete_lock()
        }
    });
}

var vm1;
var ajax_lock = false;
var empty_data_sign = false
$(document).ready(function() {

    vm1 = new Vue({
        el: '#all_card',
        data: {
            objs: []
        },
        compiled: function() {
            check_buttom()
            get_all_card()
            $("#all_card").show()
        }
    })

})

// 上拉加载触发的函数
function loadin_trigger_function(){
    get_all_card()
}

// 拉取个人信息
function get_own_message(){
    mui.ajax('/api/v1/getNameCard',{
        dataType:'json',//服务器返回json格式数据
        type:'get',//HTTP请求类型
        timeout:10000,//超时时间设置为10秒；
        success:function(data){
            vm2.$set('avatar', data['content']['avatar'])
            vm2.$set('name', data['content']['name'])
        },
        error:function(xhr,type,errorThrown){
            //异常处理；
            if('abort' == type){
                // 用户终止的异常不处理
                return
            }
            mui.alert('服务器无法响应！')
        }
    });
}

// 初始化渲染个人中心
var vm2 = new Vue({
    el: '#own',
    data:{
        avatar: '',
        name: ''
    },
    compiled: function(){
        get_own_message()
    }
})

// 跳转到通讯录
function goto_contact_list(){
    location.href = '/web/v1/contact_list';
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