// 用于上拉刷新
var last_message_id = 0;
var get_a_page_data_lock = false
function get_a_page_data(){

    // 锁问题
    if(get_a_page_data_lock){
        return
    }
    get_a_page_data_lock = true
    $("#loading_div").show()
    $.ajax({
      type: 'POST',
      url: '/api/v1/getChat/' + get_end_args() + '/1/10',
      data: {
        "last_message_id": last_message_id
      },
      success: function(data){

        var objs = data
        if(objs.length != 0){
            objs.reverse()
            last_message_id = objs[0]['id']
            objs.reverse()
            for(var i in objs){
                vm_chats.unshift(objs[i])
            }
            vm.$set('chats', vm_chats)
            get_a_page_data_lock = false
            $("#loading_div").hide()
        }else{
            // 没有数据了
            $("#loading_div").html('<span style="color: orange;">没有更多消息了～</span>')
        }

        if(!read_first_page_sign){
            Vue.nextTick(function () {
                goto_buttom()
            })
            // 处理新消息与第一页冲突的问题
            read_first_page_sign = true
            // 关闭遮罩层
            $(".loadin_div_first").hide()
        }


      },
      error: function(){
        get_a_page_data_lock = false
      }
    })


}


// 获取最新消息
var get_new_message_sign = null
function get_new_message(){

    if(get_new_message_sign){
        clearTimeout(get_new_message_sign)
    }
     if(!read_first_page_sign){
        get_new_message_sign = setTimeout('get_new_message()', 5000)
        return
     }
    $.ajax({
      type: 'GET',
      url: '/api/v1/getNewChat/' + get_end_args(),
      data: {},
      success: function(data){
        var objs = data
        for(var i in objs){
            vm_chats.push(objs[i])
        }
        vm.$set('chats', vm_chats)
        get_new_message_sign = setTimeout('get_new_message()', 5000)
      },
      error: function(){
        get_new_message_sign = setTimeout('get_new_message()', 30000)
      }
    })

}


// 发送消息
send_message_lock = false
function send_message(){

    if(send_message_lock || from_open_id == null){
        return;
    }
    send_message_lock = true

    var message = $("#message").val()
    if(!$.trim(message)){
        alert('发送的内容不能为空！')
        return
    }
    $.ajax({
      type: 'POST',
      url: '/api/v1/sendMessage/' + get_end_args(),
      data: {"message": message},
      success: function(data){
        // 清空数据
        $("#message").val('')
        vm_chats.push({"message_content": message, "from_open_id": from_open_id})
        vm.$set('chats', vm_chats)
        send_message_lock = false

        Vue.nextTick(function () {
            goto_buttom()
        })

      },
      error: function(){
        send_message_lock = false
      }
    })

}

var vm
var vm_chats = []
var from_open_id = null

// 处理新消息在上拉可以获取并且获取未读消息可以获取的问题
var read_first_page_sign = false

function build_chat_dom(obj){
    from_open_id = obj['own_card']['open_id']
    vm = new Vue({
        el: '#container',
        data: {
            chats: vm_chats,
            own_avatar: obj['own_card']['avatar'],
            friend_avatar: obj['obj']['friend_card']['avatar'],
            own_open_id: obj['own_card']['open_id']
        },
        ready:function(){
            $("#container").show()
            get_a_page_data()
            get_new_message()
        }
    })
}

function handle_down(){
    touch.on('body', 'dragend', function(ev){
        var scrollTop = getScrollTop()
        if(scrollTop == 0){
            get_a_page_data()
        }
    });
}

$(document).ready(function(){

    $.ajax({
      type: 'POST',
      url: '/api/v1/get_chat_need_message',
      data: {
        'friend_open_id': get_end_args()
      },
      success: function(data){
        document.title = data['title']
        build_chat_dom(data)
        handle_down()
      },
      error: function(xhr, errorType, error){
        if('abort' == errorType){
            // 用户终止的异常不处理
            return
        }
        alert('拉取信息失败，请刷新页面！')
      }
    })

})

// 到达页面最底部
function goto_buttom(){
    location.href = '#new_a'
}