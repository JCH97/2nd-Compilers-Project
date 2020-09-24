const vue = new Vue({
    el: "#app",
    data: {
        errors: [],
        context: "",
        code: ""
    },
    mounted() {
    },
    methods: {
        run: function () {
            eel.handler(this.code)().then(data => {
                this.errors = data.errors;
                this.context = data.context;
            })
        },
        selectCode: function () {
            let input = document.querySelector("#code");
            let file = input.files[0];
            let fr = new FileReader();

            fr.readAsText(file);
            fr.onload = (function () {
                this.code = fr.result;
            }).bind(this);
        }
    },
});