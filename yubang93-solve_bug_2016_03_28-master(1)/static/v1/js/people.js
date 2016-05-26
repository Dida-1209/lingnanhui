var own_vm;
function get_people_message(){

    mui.ajax('/api/v1/get_card_of_a_prople/' + get_people_id(),{
        data:{},
        dataType:'json',
        type:'get',
        timeout:10000,
        success:function(data){
            //document.title = data['name']
            update_title(data['name'])

            own_vm.$set('card', data)
            document.getElementById('mui-content').style.display = 'block'
            document.getElementById('loading_div').style.display = 'none'
        },
        error:function(xhr,type,errorThrown){
            if('abort' == type){
                // 用户终止的异常不处理
                return
            }
            mui.alert('服务器无法响应！')
        }
    });

}

function own_init(){

    own_vm = new Vue({
        el: '#mui-content',
        data:{
            card: {}
        },
        ready: function(){
            get_people_message()
        }
    })

}

function goto_chat(){
    location.href = '/web/v1/chat/' + get_people_id() + '#new_a'
}


function get_people_id(){
    var url = window.location.pathname
    urls = url.split('/')
    return urls[urls.length - 1]
}

function add_friend(open_id){
    location.href = '/web/v1/apply_friend?open_id=' + open_id;
}

own_init()