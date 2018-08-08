$(function () {
    var oExports = {
        initialize: fInitialize,
        encode: fEncode
    };
    oExports.initialize();

    function del_comm() {
        var rm_parent = this.parentNode
        var comment_id = this.id
        if (confirm("确定要删除？", '确定', '取消')) {
            $.ajax({
                url: '/deletecomment/',
                type: 'post',
                dataType: 'json',
                data: {comment_id: comment_id}
            }).done(function (oResult) {
                if (oResult.code !== 0) {
                    return alert(oResult.msg || '提交失败，请重试');
                }
                rm_parent.remove()
            }).fail(function (oResult) {
                alert(oResult.msg || '提交失败，请重试');
            }).always(function () {

            });
        }
    }

    function fInitialize() {
        var that = this;
        var sImageId = window.imageId;
        var oCmtIpt = $('#jsCmt');
        var oListDv = $('ul.js-discuss-list');

        // 点击添加评论
        var bSubmit = false;
        $('#jsSubmit').on('click', function () {
            var sCmt = $.trim(oCmtIpt.val());
            // 评论为空不能提交
            if (!sCmt) {
                return alert('评论不能为空');
            }
            // 上一个提交没结束之前，不再提交新的评论
            if (bSubmit) {
                return;
            }
            bSubmit = true;
            $.ajax({
                url: '/addcomment/',
                type: 'post',
                dataType: 'json',
                data: {image_id: sImageId, content: sCmt}
            }).done(function (oResult) {
                if (oResult.code !== 0) {
                    return alert(oResult.msg || '提交失败，请重试');
                }
                // 清空输入框
                oCmtIpt.val('');
                // 渲染新的评论
                var li = $('<li>');
                var remove_a = $('<a>').attr('class',' icon-remove remove_comment')
                    .attr('title','删除评论').attr('id',oResult.comment_id)
                    .attr('href','javascript:void(0)');
                remove_a.click(del_comm);
                var user_a = $('<a>').attr('class','_4zhc5 _iqaka')
                    .attr('title',that.encode(oResult.username))
                    .attr('href','/profile/'+oResult.user_id)
                    .text(that.encode(oResult.username))
                var comment_space = $('<span>').text(that.encode(sCmt))
                li.append(remove_a).append(user_a).append(comment_space)
                oListDv.prepend(li);
            }).fail(function (oResult) {
                alert(oResult.msg || '提交失败，请重试');
                // 清空输入框
                oCmtIpt.val('');
            }).always(function () {
                bSubmit = false;
            });
        });

        $('ul.js-discuss-list li .remove_comment').click(del_comm)

    }

    function fEncode(sStr, bDecode) {
        var aReplace =["&#39;", "'", "&quot;", '"', "&nbsp;", " ", "&gt;", ">", "&lt;", "<", "&amp;", "&", "&yen;", "¥"];
        !bDecode && aReplace.reverse();
        for (var i = 0, l = aReplace.length; i < l; i += 2) {
             sStr = sStr.replace(new RegExp(aReplace[i],'g'), aReplace[i+1]);
        }
        return sStr;
    };

});