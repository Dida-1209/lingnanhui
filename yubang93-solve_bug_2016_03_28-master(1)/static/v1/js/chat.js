// 兼容性代码入口
function log_chat_init(friend_open_id_obj, own_card_avatar, friend_card_avatar) {

    mui.init();
    var index = 0;
    function addMessage(type_str, message, img, is_append) {
        var clone_dom = document.getElementById(type_str).cloneNode(true);
        clone_dom.id = type_str + index;
        clone_dom.children[0].src = img;
        clone_dom.children[1].children[0].children[0].innerHTML = message;
        if (is_append) {
            document.getElementById('chat_div').innerHTML = document.getElementById('chat_div').innerHTML + clone_dom.outerHTML;
        } else {
            document.getElementById('chat_div').innerHTML = clone_dom.outerHTML + document.getElementById('chat_div').innerHTML;
        }
        index++;
    }

    mui.ajax('/api/v1/getChat/' + friend_open_id_obj + '/1/500', {
        dataType: 'json',
        //服务器返回json格式数据
        success: function(data) {
            for (var i in data) {
                if (data[i]['from_open_id'] == friend_open_id_obj) {
                    addMessage("rec", data[i]['message_content'], friend_card_avatar, false);
                } else {
                    addMessage("sen", data[i]['message_content'], own_card_avatar, false);
                }
            }
            get_new_message()
            window.location.hash = 'lastMessage'
            window.location = window.location
            document.getElementById('loading_div').style.display = 'none'

        },
        error: function(xhr, type, errorThrown) {
            mui.alert("服务器异常！");
        }
    });

    this.send_message = function() {
        if (!document.getElementById('message').value) {
            mui.alert("发送的消息不能为空！");
            return;
        }
        mui.ajax('/api/v1/sendMessage/' + friend_open_id_obj, {
            data: {
                message: document.getElementById('message').value
            },
            dataType: 'json',
            //服务器返回json格式数据
            type: 'post',
            //HTTP请求类型
            success: function(data) {
                //服务器返回响应，根据响应结果，分析是否登录成功；
                if (data['code'] != 0) {
                    mui.alert("发送消息失败！");
                    return;
                }
                addMessage("sen", document.getElementById('message').value, own_card_avatar, true);
                document.getElementById('message').value = "";
                window.location = window.location
            },
            error: function(xhr, type, errorThrown) {
                //异常处理；
                console.log(type);
            }
        });
    }

    // 获取最新的消息
    var setTimeoutSign = null;
    this.get_new_message = function() {
        if (setTimeoutSign) {
            clearTimeout(setTimeoutSign)
        }
        mui.ajax('/api/v1/getNewChat/' + friend_open_id_obj, {
            dataType: 'json',
            //服务器返回json格式数据
            type: 'get',
            //HTTP请求类型
            success: function(data) {
                //服务器返回响应，根据响应结果，分析是否登录成功；
                for (var i in data) {
                    if (data[i]['from_open_id'] == friend_open_id_obj) {
                        addMessage("rec", data[i]['message_content'], friend_card_avatar, true);
                    } else {
                        addMessage("sen", data[i]['message_content'], own_card_avatar, true);
                    }
                }
                setTimeoutSign = setTimeout('get_new_message()', 3000)
            },
            error: function(xhr, type, errorThrown) {
                //异常处理；
                setTimeoutSign = setTimeout('get_new_message()', 10000)
            }
        });
    }
    document.getElementById('mui-content').style.height = "100%";
    return this.send_message
}

function get_people_id() {
    var url = window.location.pathname
    urls = url.split('/')
    return urls[urls.length - 1]
}

var send_message;

mui.ajax('/api/v1/get_chat_need_message', {
    data: {
        'friend_open_id': get_people_id()
    },
    dataType: 'json',
    type: 'post',
    timeout: 10000,
    success: function(data) {
        document.title = data['title']
        send_message = log_chat_init(get_people_id(), data['own_card']['avatar'], data['own_card']['friend_card'])
    },
    error: function(xhr, type, errorThrown) {
        mui.alert('服务器无法响应！')
    }
});
