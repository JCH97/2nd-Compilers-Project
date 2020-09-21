const vue = new Vue({
    el: "#app",
    data: {
        msg: ""
    },
    created() {
        eel.handler("Test all")().then(data => {
            ast, errors, context, scope = data
        })
    },
});