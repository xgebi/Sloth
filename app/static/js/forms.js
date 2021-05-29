document.addEventListener('DOMContentLoaded', (event) => {
    document.querySelector("#add-field").addEventListener('click', addFormItem);
    for (const formField of formFields) {
        addFormItem(formField)
    }
});

function addFormItem(formField) {
    if (typeof(formField.preventDefault)) {
        formField = {
            selectValue: "",
            isRequired: false
        };
    }
    const wrapper = document.querySelector("#form-fields");
    wrapper.setAttribute("class", wrapper.getAttribute("id"));
    wrapper.removeAttribute("id");
    const fieldTemplate = document.querySelector("#form-item");

    const fieldClone = fieldTemplate.content.cloneNode(true);
    const select = fieldClone.querySelector("select");
    const selectLabel = fieldClone.querySelector("#item-type-label");
    const selectId = Math.random().toString(16).slice(2);

    selectLabel.setAttribute('for', `item-type-${selectId}`);
    selectLabel.setAttribute('id', `item-type-label-${selectId}`);
    select.setAttribute("id", `item-type-${selectId}`);
    select.addEventListener('change', typeSelected);

    for (const child of select.childNodes) {
        if (child.value === formField.selectValue) {
            child.setAttribute("selected","");
        }
    }
    const isRequiredId = Math.random().toString(16).slice(2);
    const isRequired = fieldClone.querySelector("#is-required");
    const isRequiredLabel = fieldClone.querySelector("#is-required-label");
    if (formField.isRequired) {
        isRequired.setAttribute("checked","");
    }
    isRequiredLabel.setAttribute('for', `is-required-${isRequiredId}`);
    isRequiredLabel.removeAttribute('id');
    isRequired.setAttribute("id", `is-required-${isRequiredId}`);
    isRequired.setAttribute("name", `is-required-${isRequiredId}`);

    wrapper.appendChild(fieldClone);
}

function typeSelected(event) {
    const settingsWrapper = event.target.parentNode.parentNode.querySelector(".form-item-settings");
    console.log(settingsWrapper);
}

/*
    <template id="general-setting">
        <div>
            <div>
                <label for="label"></label>
                <input type="text" data-name="label" id="label" />
            </div>
            <div>
                <label for="name"></label>
                <input type="text" data-name="name" id="name" />
            </div>
        </div>
    </template>

    <template id="option-item">
        <div>
            <label data-for="option"></label>
            <input type="text" data-id="option" data-name="option">
        </div>
    </template>
* */