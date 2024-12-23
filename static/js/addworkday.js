document.addEventListener('DOMContentLoaded', function () {
    const addWorkdayBtn = document.getElementById('add-workday-btn');
    const workdaysContainer = document.getElementById('workdays-container');
    let hasLoadedDefaultRow = false;

    // Function to fetch and add a workday row
    async function addWorkdayRow(nextDate, isDefault = false) {
        try {
            const response = await fetch(`/workday_row_template?next_date=${nextDate.toISOString().split('T')[0]}`);
            if (!response.ok) {
                throw new Error(`Failed to fetch template: ${response.statusText}`);
            }

            const html = await response.text();
            const workdayRow = document.createElement('div');
            workdayRow.innerHTML = html;

            // Remove the "Remove" button for the default row
            if (isDefault) {
                const removeButton = workdayRow.querySelector('.remove-workday-btn');
                if (removeButton) removeButton.remove();
            }

            // Add "Remove" button functionality for dynamic rows
            if (!isDefault) {
                const removeButton = workdayRow.querySelector('.remove-workday-btn');
                if (removeButton) {
                    removeButton.addEventListener('click', () => {
                        console.log("Removing row:", workdayRow);
                        workdayRow.remove();
                    });
                }
            }

            // Append the new row to the container
            workdaysContainer.appendChild(workdayRow);
            console.log(`Workday row added: ${nextDate.toISOString().split('T')[0]}`);
        } catch (error) {
            console.error('Error adding workday row:', error);
        }
    }

    // Load the default workday row on page load
    if (!hasLoadedDefaultRow) {
        console.log('Loading default workday row...');
        const today = new Date();
        addWorkdayRow(today, true);
        hasLoadedDefaultRow = true;
    }

    // Add new workday row when "Add Another Workday" button is clicked
    addWorkdayBtn.addEventListener('click', async () => {
        console.log('Add Another Workday button clicked.');

        // Fetch the last date input dynamically every time
        const lastRowDateInput = workdaysContainer.querySelectorAll('.workday-date');
        if (lastRowDateInput.length === 0) {
            console.error('No date input found in the container.');
            return;
        }

        // Get the last row's date and increment it by one day
        const lastDateInput = lastRowDateInput[lastRowDateInput.length - 1];
        const lastDate = new Date(lastDateInput.value);
        if (isNaN(lastDate.getTime())) {
            console.error('Invalid date in last row:', lastDateInput.value);
            return;
        }

        // Increment the last date by one day
        const nextDate = new Date(lastDate);
        nextDate.setDate(lastDate.getDate() + 1);
        console.log(`Next date calculated: ${nextDate.toISOString().split('T')[0]}`);

        // Add the new workday row
        await addWorkdayRow(nextDate);
    });
});
