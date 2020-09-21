eel.handler("from main.js");

const vue = new Vue({
    el: "#app",
    data: {
        msg: ""
    },
    created() {
        // eel.handler("from main.js");
        this.msg = "msg from created"
    },
});