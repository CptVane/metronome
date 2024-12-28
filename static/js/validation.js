function submitAddWorkForm() {
    const workIdInput = document.getElementById('work-id');
    const workNameInput = document.getElementById('event-name');
    const clientSelect = document.getElementById('client-selection');
    const newClientNameInput = document.getElementById('new-client-name');
    const newClientSection = document.getElementById('new-client-section');

    const workId = workIdInput.value.trim();
    const workName = workNameInput.value.trim();
    const clientSelected = clientSelect.value !== "" && clientSelect.value !== null;
    const newClientName = newClientNameInput.value.trim();

    // Controllo di validazione
    const isValid = workId !== "" &&
                    workName !== "" &&
                    (clientSelected || (newClientSection.style.display === 'block' && newClientName !== ""));

    if (!isValid) {
        alert("Please fill out all required fields before saving.");
        return; // Interrompe l'invio del modulo
    }

    // Invia il modulo se tutti i campi sono validi
    const form = document.getElementById('add-work-form');
    if (form) {
        console.log("Submitting form...");
        form.submit();
    } else {
        console.error("Form not found!");
    }
}

document.addEventListener('DOMContentLoaded', function () {
    const saveWorkBtn = document.getElementById('save-work-btn'); // Pulsante Save Work
    const workIdInput = document.getElementById('work-id');
    const workNameInput = document.getElementById('event-name');
    const clientSelect = document.getElementById('client-selection');
    const newClientNameInput = document.getElementById('new-client-name');
    const existingClientSection = document.getElementById('existing-client-section');
    const newClientSection = document.getElementById('new-client-section');

    // Funzione per validare il modulo
    function validateForm() {
        const workId = workIdInput.value.trim();
        const workName = workNameInput.value.trim();
        const clientSelected = clientSelect.value !== "" && clientSelect.value !== null;
        const newClientName = newClientNameInput.value.trim();

        console.log(`Work ID: ${workId}, Work Name: ${workName}, Client Selected: ${clientSelected}, New Client Name: ${newClientName}`);

        // Condizioni di validazione
        const isValid = workId !== "" &&
                        workName !== "" &&
                        (clientSelected || (newClientSection.style.display === 'block' && newClientName !== ""));

        console.log(`Validation Result: ${isValid}`);

        // Abilita/disabilita il pulsante Save Work
        saveWorkBtn.disabled = !isValid;
    }

    // Event Listeners per i campi di input
    workIdInput.addEventListener('input', validateForm);
    workNameInput.addEventListener('input', validateForm);
    clientSelect.addEventListener('change', validateForm);
    newClientNameInput.addEventListener('input', validateForm);

    // Gestione della sezione cliente
    document.getElementById('create-new-client-link').addEventListener('click', function (event) {
        event.preventDefault();
        existingClientSection.style.display = 'none';
        newClientSection.style.display = 'block';
        validateForm();
    });

    document.getElementById('revert-existing-client-link').addEventListener('click', function (event) {
        event.preventDefault();
        existingClientSection.style.display = 'block';
        newClientSection.style.display = 'none';
        validateForm();
    });

    // Validazione iniziale
    validateForm();
});
