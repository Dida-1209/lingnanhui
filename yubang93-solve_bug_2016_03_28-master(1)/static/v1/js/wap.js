function myfun(){
	$("#mask").addClass("mask");
	$("#mask").on("click",function(e){
		$(this).removeClass("mask");
		e.stopPropagation();
	});
}
	window.onload=myfun;
  
var v1_wap_js_g_timeout_sign_not_read_message_number = null;
function get_not_read_message_number(){
    if(v1_wap_js_g_timeout_sign_not_read_message_number){
        clearTimeout(v1_wap_js_g_timeout_sign_not_read_message_number)
    }
    mui.ajax('/api/v1/get_own_new_message_number',{
        data:{},
        dataType:'json',
        type:'get',
        timeout:10000,
        cache: false,// 禁用缓存，防止返回消息显示问题
        success:function(data){
            if(data['nums'] != 0){
               document.getElementById('message_tip_in_tab').style.display='inline-block';
            }else{
                v1_wap_js_g_timeout_sign_not_read_message_number = setTimeout('get_not_read_message_number()', 10000)
            }
        },
        error:function(xhr,type,errorThrown){
            v1_wap_js_g_timeout_sign_not_read_message_number = setTimeout('get_not_read_message_number()', 30000)
        }
    });

}

function getParFromUrl(par){
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

// 处理申请信息
function handle_apply_in_chat(apply_id, handle_status){

     if(!confirm("你确定要" + (handle_status == 1 ? '同意' : '不同意') + "该资源申请？")){
        return
     }

    $.ajax({
      type: 'GET',
      url: '/api/v1/handle_apply_friend/' + apply_id + '/' + handle_status,
      data: {},
      success: function(data){
           if(data['code'] == 0){
            alert(handle_status == 1 ? '同意成功！' : '不同意成功！')
           }else{
            alert('不能重复处理！')
           }
      },error: function(){
        alert('服务器无法响应！')
      }
    })
}


function get_end_args(){
    var url = window.location.pathname
    urls = url.split('/')
    return urls[urls.length - 1]
}

// 获取滚动条高度
function getScrollTop()
{
    var scrollTop=0;
    if(document.documentElement&&document.documentElement.scrollTop)
    {
        scrollTop=document.documentElement.scrollTop;
    }
    else if(document.body)
    {
        scrollTop=document.body.scrollTop;
    }
    return scrollTop;
}


function update_title(title){

    //需要jQuery
    var $body = $('body');
    document.title = title;
    // hack在微信等webview中无法修改document.title的情况
    var $iframe = $('<iframe style="display:none;" src="/favicon.ico" ></iframe>');
    $iframe.on('load',function() {
        setTimeout(function() {
            $iframe.off('load').remove();
        }, 0);
    }).appendTo($body);
}