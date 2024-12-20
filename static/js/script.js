document.addEventListener('DOMContentLoaded', () => {
    const startDateInput = document.getElementById('start-date');
    const endDateInput = document.getElementById('end_date');

    const filterForm = document.getElementById('date-filter-form');
    const applyFilter = () => {
        filterForm.submit();
    };

    startDateInput.addEventListener('change', applyFilter);
    endDateInput.addEventListener('change', applyFilter);
});
