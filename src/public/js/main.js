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
            this.code = document.querySelector("#code").value;
            // console.log(this.code.length)
            
            eel.handler(this.code)().then(data => {
                this.errors = data.errors;

                if (data.context) {
                    this.context = data.context;
                    this.inference = data.inference;
                }

                document.querySelector("#result").value = `${data.errors}\n\n${data.context}\n\n${data.inference}`;
            })

        },
        selectCode: function () {
            this.code = "";
            
            let input = document.querySelector("#codeChoose");
            let file = input.files[0];
            let fr = new FileReader();

            fr.readAsText(file);
            fr.onload = (function () {
                this.code = fr.result;
                document.querySelector("#code").value = this.code;
            }).bind(this);
        },
    },
});