mui('.mui-bar-tab').on('tap', 'a', function() {
			document.location.href = this.href;
		});
var html = "";
var pin = "";

   function get_dom_use_own_sign(dom_obj, own_sign_key, own_sign_value){
        for(var i =0; i<dom_obj.children.length; i++){
            if(dom_obj.children[i].getAttribute(own_sign_key) == own_sign_value){
                return dom_obj.children[i];
            }else{
                var r = get_dom_use_own_sign(dom_obj.children[i], own_sign_key, own_sign_value);
                if(r){
                    return r;
                }
            }
        }
        return undefined;
    }

function append_user(user_obj){

    var dom_clone = document.getElementById('list_').cloneNode(true);
    get_dom_use_own_sign(dom_clone, 'own-sign', 'avatar').src = user_obj['avatar']
    get_dom_use_own_sign(dom_clone, 'own-sign', 'name').innerHTML = user_obj['name']
    get_dom_use_own_sign(dom_clone, 'own-sign', 'role').innerHTML = user_obj['company'] + " | " + user_obj['role'] + " | " + user_obj['industry']
    get_dom_use_own_sign(dom_clone, 'own-sign', 'link').href = '/web/v1/people/' + user_obj['open_id']

    var arrs = user_obj['redundancy_labels'].split("#")
    if(user_obj['redundancy_labels'])
    for(var i in arrs){
        var string_tag = '<i class="fa fa-tag"></i>' + arrs[i]
        get_dom_use_own_sign(dom_clone, 'own-sign', 'tag').innerHTML += string_tag
    }

    //dom_clone.children[1].children[0].children[0].src = user_obj['avatar'];
    //dom_clone.children[1].children[1].children[0].children[0].innerHTML = user_obj['name'];
    //dom_clone.children[1].children[1].children[1].innerHTML = user_obj['company'] + dom_clone.children[1].children[1].children[1].innerHTML;
    //dom_clone.children[1].children[1].children[1].children[0].innerHTML = user_obj['industry'];
    //dom_clone.children[1].href = "javascript:goto_url('"+user_obj['open_id']+"');";

    if(pin != user_obj['name_pinyin'].substr(0,1)){
        pin = user_obj['name_pinyin'].substr(0,1);
        var html_str = '</div><div id="content" class="oneset"><div class="tou">'+pin.toLocaleUpperCase()+'</div>';
        html += html_str;
    }

    html += dom_clone.children[1].outerHTML;
}

function goto_url(open_id){
    location.href = "/web/v1/people/" + open_id;
}

function init(){
build_label_in_js()
    mui.ajax('/api/v1/getContacts',{
        dataType:'json',//服务器返回json格式数据
        type:'post',//HTTP请求类型
        data:{
            search_key: getPar('search_key') == '关键词' ? '': getPar('search_key'),
            industry: getPar('industry'),
            role: getPar('role'),
        },
        timeout:10000,//超时时间设置为10秒；
        success:function(data){
            for(var i in data['content']){
                append_user(data['content'][i]);
            }

            document.getElementById('content').innerHTML += html;
            mui.init();
            $("#loading_div").hide()
        },
        error:function(xhr,type,errorThrown){
            if('abort' == type){
                // 用户终止的异常不处理
                return
            }
            mui.alert("服务器异常，请刷新页面！");
            $("#loading_div").hide()
        }
    });
}

mui.ajax('/api/v1/getNameCard',{
        dataType:'json',//服务器返回json格式数据
        type:'get',//HTTP请求类型
        timeout:10000,//超时时间设置为10秒；
        success:function(data){
            if(data['code'] != 0){
                location.href = '/web/v1/buildCard';
            }else{
                init();
            }
        },
        error:function(xhr,type,errorThrown){
            if('abort' == type){
                // 用户终止的异常不处理
                return
            }
            mui.alert("服务器异常，请刷新页面！");
        }
    });

// 获取未读消息
get_not_read_message_number()