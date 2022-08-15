(function($) {
    $(document).ready(function () {
        var new_tag_input = $(this).find("#new_tag_input");
        var tag_wrap = $(".taggit-labels");
        
        new_tag_input.change(function () {  
            var inputs = $('input[name="tags"]')[0];
            let newTag = [];
            let tmp = new_tag_input[0].value.split(",");
            tmp.map((t) =>  {
                if (typeof (t) === 'string') {
                    newTag.push(t.trim())
                }
            })
            var tagItemsWrap = tag_wrap.find(".selected");
            var tagItems = []
            tagItemsWrap.each(function () {
                tagItems.push($(this).attr("data-tag-name"))
            })

            let tagList = [... new Set(tagItems.concat(newTag))];
            $(inputs).attr("value", tagList.join(", "));
        })
    });
})(jQuery || django.jQuery);