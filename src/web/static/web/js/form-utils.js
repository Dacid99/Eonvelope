function clearFormElement(formElement) {
    // see https://stackoverflow.com/questions/3786694/how-to-reset-clear-form-through-javascript

    var elements = formElement.elements;

    formElement.reset();

    for (i = 0; i < elements.length; i++) {

        field_type = elements[i].type.toLowerCase();

        switch (field_type) {

            case "text":
            case "search":
            case "password":
            case "textarea":
            case "hidden":
            case "number":
            case "date":
                elements[i].value = "";
                break;

            case "radio":
            case "checkbox":
                if (elements[i].checked) {
                    elements[i].checked = false;
                }
                break;

            case "select-one":
            case "select-multi":
                elements[i].selectedIndex = 0;
                break;

            default:
                break;
        }
    }
}

function clearForm() {
    const form = document.querySelector('form');
    clearFormElement(form);
    return form;
}

document.addEventListener('DOMContentLoaded', function () {
    const offcanvas = document.getElementById('offcanvasFilter');
    if (offcanvas) {
        offcanvas.addEventListener('shown.bs.offcanvas', function () {
            const searchInput = offcanvas.querySelector('input[type="search"]');
            if (searchInput) {
                searchInput.focus();
            }
        });
    }
});
