const closeModal = (elementId) => {
    $(`#${elementId}`).addClass("d-none")
}


const alert = ({ elementId, text, confirmButtonTxt = "Ok", onConfirm, declineButtonTxt = "Cancel" }) => {
    $(`#${elementId}`).removeClass("d-none")
    
    $(`#${elementId}`).html(
        `<div class="alert alert-danger flex-column">
            <span class="mb-1">
                ${text}
            </span>
            <div class="mt-2">
                <button
                    id="confirmbtn-${elementId}"
                    type="button"
                    class="btn btn-primary fs-9"
                >
                    ${confirmButtonTxt}
                </button>
                <button
                    id="declinebtn-${elementId}"
                    type="button"
                    class="btn btn-secondary fs-9"
                >
                    ${declineButtonTxt}
                </button>
            </div>
        </div>`
    )

    $(`#declinebtn-${elementId}`).click(() => closeModal(elementId));
    $(`#confirmbtn-${elementId}`).click(() => onConfirm());

}