document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('logs-table-body');
    const severityFilter = document.getElementById('severity-filter');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Pagination elements
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');

    const BACKEND_URL = 'http://127.0.0.1:5000';

    let allLogs = []; // Stores all data from the backend
    let filteredLogs = []; // Stores data after filtering
    let currentPage = 1;
    const recordsPerPage = 10;

    /**
     * Updates the pagination controls (buttons and page info).
     */
    const updatePaginationControls = () => {
        const totalPages = Math.ceil(filteredLogs.length / recordsPerPage);
        pageInfo.textContent = `Page ${currentPage} of ${totalPages || 1}`;
        prevBtn.disabled = currentPage === 1;
        nextBtn.disabled = currentPage === totalPages || totalPages === 0;
    };

    /**
     * Renders the log data for the current page into the HTML table.
     */
    const renderTable = () => {
        tableBody.innerHTML = '';
        const startIndex = (currentPage - 1) * recordsPerPage;
        const endIndex = startIndex + recordsPerPage;
        const pageLogs = filteredLogs.slice(startIndex, endIndex);

        if (pageLogs.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="5" class="no-data">No submissions found for this filter.</td></tr>';
            return;
        }

        pageLogs.forEach(log => {
            const row = document.createElement('tr');
            const truncatedSymptoms = log.symptoms.length > 100 ? `${log.symptoms.substring(0, 100)}...` : log.symptoms;
            // This line creates the dynamic class name for color-coding
            const severityClass = `severity-${log.severity.toLowerCase().replace(' ', '-')}`;

            row.innerHTML = `
                <td>${log.timestamp}</td>
                <td>${log.name}</td>
                <td>${log.age}</td>
                <td><span class="severity-badge ${severityClass}">${log.severity}</span></td>
                <td title="${log.symptoms}">${truncatedSymptoms}</td>
            `;
            tableBody.appendChild(row);
        });
    };

    /**
     * Fetches the log data from the backend.
     */
    const fetchLogs = async () => {
        loadingIndicator.style.display = 'block';
        tableBody.innerHTML = '';

        try {
            const response = await fetch(`${BACKEND_URL}/logs`);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            allLogs = await response.json();
            handleFilterChange(); // Apply initial filter and render
        } catch (error) {
            console.error("Failed to fetch logs:", error);
            tableBody.innerHTML = '<tr><td colspan="5" class="no-data error">Could not load data. Is the backend running?</td></tr>';
        } finally {
            loadingIndicator.style.display = 'none';
        }
    };

    /**
     * Filters the logs and resets the view to the first page.
     */
    const handleFilterChange = () => {
        const selectedSeverity = severityFilter.value;
        currentPage = 1; // Reset to page 1 on filter change

        if (selectedSeverity === 'all') {
            filteredLogs = [...allLogs];
        } else {
            filteredLogs = allLogs.filter(log => log.severity === selectedSeverity);
        }
        
        renderTable();
        updatePaginationControls();
    };

    // --- Event Listeners ---
    severityFilter.addEventListener('change', handleFilterChange);

    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTable();
            updatePaginationControls();
        }
    });

    nextBtn.addEventListener('click', () => {
        const totalPages = Math.ceil(filteredLogs.length / recordsPerPage);
        if (currentPage < totalPages) {
            currentPage++;
            renderTable();
            updatePaginationControls();
        }
    });

    // --- Initial Load ---
    fetchLogs();
});
