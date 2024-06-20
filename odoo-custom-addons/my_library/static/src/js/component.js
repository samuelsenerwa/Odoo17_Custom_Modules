odoo.define("my.component", function (require){
    "use strict";

    const {Component} = owl;
    const {xml} = owl.tags;

    class MyComponent extends Component {
    static template = xml`
           <div class="bg-info text-center-p">
           <b>Welcome to Odoo</b>
           </div>`
    }

    owl.utils.whenReady().then(()=>{
            const app = new MyComponent();
            app.mount(document.body)
    });
});