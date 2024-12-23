document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const dateInputs = document.querySelectorAll('#start-date, #end-date');

    // Submit the form only when Enter is pressed
    dateInputs.forEach(input => {
        input.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                event.preventDefault(); // Prevent default behavior (e.g., changing focus)
                filterForm.submit();
            }
        });
    });
});