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
            isRequired: false,
            label: "",
            value: "",
            options: []
        };
    }
    const wrapper = document.querySelector("#form-fields");
    const fieldTemplate = document.querySelector("#form-item");

    const fieldClone = fieldTemplate.content.cloneNode(true);
    const select = fieldClone.querySelector("select");
    const selectLabel = fieldClone.querySelector("#item-type-label");
    const fieldId = Math.random().toString(16).slice(2);

    selectLabel.setAttribute('for', `item-type-${fieldId}`);
    selectLabel.setAttribute('id', `item-type-label-${fieldId}`);
    select.setAttribute("id", `item-type-${fieldId}`);
    function processSelect(event) {
        const settingsWrapper = event.target.parentNode.parentNode.querySelector(".form-item-settings");
        while (settingsWrapper.lastChild) {
            settingsWrapper.removeChild(settingsWrapper.lastChild);
        }
        console.log(settingsWrapper);

        const settingsTemplate = document.querySelector("#general-setting");
        const settingsClone = settingsTemplate.content.cloneNode(true);

        const labelLabel = settingsClone.querySelector(".label label");
        labelLabel.setAttribute("for", `label-input-${fieldId}`);
        const labelInput = settingsClone.querySelector(".label input");
        labelInput.setAttribute("name", `label-input-${fieldId}`);
        labelInput.setAttribute("id", `label-input-${fieldId}`);

        const inputLabel = settingsClone.querySelector(".input label");
        inputLabel.setAttribute("name", `label-input-${fieldId}`);
        const inputInput = settingsClone.querySelector(".input input");
        inputInput.setAttribute("name", `label-input-${fieldId}`);
        inputInput.setAttribute("id", `label-input-${fieldId}`);
        debugger;
        if (event.target.value === "select") {
            settingsClone.querySelector(".add-option").classList.remove("hidden");
            settingsClone.querySelector(".options-wrapper").classList.remove("hidden");
        } else {
            settingsClone.querySelector(".add-option").classList.add("hidden");
            settingsClone.querySelector(".options-wrapper").classList.add("hidden");
        }

        settingsWrapper.appendChild(settingsClone);
        debugger;
    };
    select.addEventListener('change', processSelect);

    for (const child of select.childNodes) {
        if (child.value === formField.selectValue) {
            child.setAttribute("selected","");
        }
    }
    if (formField.selectValue === "select") {
        for (const option in formField?.options) {

        }
    }
    const isRequired = fieldClone.querySelector("#is-required");
    const isRequiredLabel = fieldClone.querySelector("#is-required-label");
    if (formField.isRequired) {
        isRequired.setAttribute("checked","");
    }
    isRequiredLabel.setAttribute('for', `is-required-${fieldId}`);
    isRequiredLabel.removeAttribute('id');
    isRequired.setAttribute("id", `is-required-${fieldId}`);
    isRequired.setAttribute("name", `is-required-${fieldId}`);

    const deleteButton = fieldClone.querySelector("button.delete");
    deleteButton.addEventListener('click', (event) => {
        event.target.parentNode.parentNode.removeChild(event.target.parentNode);
    })

    wrapper.appendChild(fieldClone);
}

/*
    <template id="option-item">
        <div>
            <label data-for="option"></label>
            <input type="text" data-id="option" data-name="option">
        </div>
    </template>
* */