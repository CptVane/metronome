document.addEventListener('DOMContentLoaded', function () {
    const createNewClientLink = document.getElementById('create-new-client-link');
    const revertExistingClientLink = document.getElementById('revert-existing-client-link');
    const existingClientSection = document.getElementById('existing-client-section');
    const newClientSection = document.getElementById('new-client-section');

    // Show the "New Client" section and hide the "Existing Client" section
    createNewClientLink.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent default link behavior
        existingClientSection.style.display = 'none';
        newClientSection.style.display = 'block';
    });

    // Show the "Existing Client" section and hide the "New Client" section
    revertExistingClientLink.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent default link behavior
        existingClientSection.style.display = 'block';
        newClientSection.style.display = 'none';
    });
});