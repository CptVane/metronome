document.addEventListener("DOMContentLoaded", function () {
  // Get all highlight forms
  const highlightForms = document.querySelectorAll(".toggle-highlight-form");

  highlightForms.forEach((form) => {
    const button = form.querySelector("button");
    const rowId = form.dataset.rowId;
    let isHighlighted = form.dataset.highlighted === "true";

    button.addEventListener("click", function () {
      fetch(form.action, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ highlighted: !isHighlighted }),
      })
        .then((response) => {
          if (response.ok) {
            // Toggle the row's highlighted class
            const row = document.getElementById(rowId);
            if (row) {
              row.classList.toggle("highlighted-row");
            }

            // Update the button icon and title
            const icon = form.querySelector("i");
            if (isHighlighted) {
              icon.classList.remove("fas", "fa-star");
              icon.classList.add("far", "fa-star");
              button.title = "Highlight";
            } else {
              icon.classList.remove("far", "fa-star");
              icon.classList.add("fas", "fa-star");
              button.title = "Unhighlight";
            }

            // Toggle the state
            isHighlighted = !isHighlighted;
          } else {
            alert("Failed to toggle highlight. Please try again.");
          }
        })
        .catch((error) => {
          console.error("Error toggling highlight:", error);
          alert("An error occurred. Please try again.");
        });
    });
  });
});
