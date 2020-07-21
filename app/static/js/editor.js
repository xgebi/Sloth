document.addEventListener('DOMContentLoaded', (event) => {
    for (const wrapper of document.querySelectorAll(".sloth-editor")) {
        const editorObj = Object.create(editor);
        editorObj.init(wrapper);
    }

});

const editor = {
    init: function(wrapper) {
        // toolbar
        const toolbar = document.createElement("div");

        wrapper.appendChild(toolbar);
        // content
        const content = document.createElement("div");
        content.setAttribute("contenteditable", "true");
        content.addEventListener('keyup', function(event) {
            event.preventDefault();
            //event.key Enter Tab
        })
        wrapper.appendChild(wrapper);
    },
    replace: function(action) {
        let range;
        if (window.getSelection && window.getSelection().getRangeAt) {
            debugger;
            range = window.getSelection().getRangeAt(0);
            if (range.endOffset - range.startOffset <= 0) {
                return;
            }
            const insideRange = range.extractContents();
            const div = document.createElement("div");
            div.appendChild(insideRange)
            range.insertNode(div);
        }
    }
}