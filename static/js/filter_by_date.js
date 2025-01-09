document.addEventListener("DOMContentLoaded", function () {
  const startDateInput = document.getElementById("start-date");
  const endDateInput = document.getElementById("end-date");

  // Function to send the date range update
  function updateDateRange(startDate, endDate) {
    if (startDate && endDate) {
      fetch("/update_date_range", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
        }),
      })
        .then((response) => {
          if (response.ok) {
            window.location.reload();
          } else {
            alert("Failed to update date range. Please try again.");
          }
        })
        .catch((error) => console.error("Error updating date range:", error));
    } else {
      alert("Please select both start and end dates.");
    }
  }

  // Add event listeners for committing changes on focusout (blur) or Enter key press
  function attachCommitEvent(inputElement) {
    inputElement.addEventListener("blur", function () {
      const startDate = startDateInput.value;
      const endDate = endDateInput.value;
      updateDateRange(startDate, endDate);
    });

    inputElement.addEventListener("keypress", function (event) {
      if (event.key === "Enter") {
        const startDate = startDateInput.value;
        const endDate = endDateInput.value;
        updateDateRange(startDate, endDate);
      }
    });
  }

  // Attach events to both start and end date inputs
  attachCommitEvent(startDateInput);
  attachCommitEvent(endDateInput);
});
