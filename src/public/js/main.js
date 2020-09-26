const vue = new Vue({
    el: "#app",
    data: {
        errors: [],
        inference: [],
        context: "",
        code: ""
    },
    mounted() {
    },
    methods: {
        run: function () {
            if (!this.code)
                this.code = document.querySelector("#writteCode").value;

            eel.handler(this.code)().then(data => {
                this.errors = data.errors;

                if (data.context) {
                    this.context = data.context;
                    this.inference = data.inference;
                }

                document.querySelector("#context").value = data.context;
            })

        },
        selectCode: function () {
            this.code = "";
            
            let input = document.querySelector("#code");
            let file = input.files[0];
            let fr = new FileReader();

            fr.readAsText(file);
            fr.onload = (function () {
                this.code = fr.result;
            }).bind(this);
        },
    },
});