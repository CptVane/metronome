document.addEventListener('DOMContentLoaded', () => {
    const deleteButtons = document.querySelectorAll('.delete-button');

    deleteButtons.forEach(button => {
        button.addEventListener('click', () => {
            const workId = button.getAttribute('data-workid');
            const date = button.getAttribute('data-date');
            const rowId = button.getAttribute('data-row-id');
            const formId = button.getAttribute('data-form-id');

            const row = document.getElementById(rowId);

            if (row) {
                // Aggiunge la classe e forza il rendering prima del popup
                row.classList.add('highlight-row');
                row.style.backgroundColor = '#ffcccc'; // Fallback per lo stile in linea

                // Usa setTimeout per mostrare il popup dopo il rendering
                setTimeout(() => {
                    const confirmDelete = confirm(`Are you sure you want to delete ${workId} on ${date}?`);

                    if (confirmDelete) {
                        document.getElementById(formId).submit();
                    } else {
                        // Rimuove l'evidenziazione se l'utente annulla
                        row.classList.remove('highlight-row');
                        row.style.backgroundColor = ''; // Ripristina il colore originale
                    }
                }, 100); // Ritardo di 100 ms per consentire il rendering
            } else {
                console.error(`Row not found: ${rowId}`);
            }
        });
    });
});
