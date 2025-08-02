document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const symptomForm = document.getElementById('symptom-form');
    const submitButton = document.getElementById('submit-btn');
    const responseContainer = document.getElementById('response-container');
    const responseMessage = document.getElementById('response-message');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    // --- Backend API Configuration ---
    // This is the URL where your Flask backend is running.
    const BACKEND_URL = 'http://127.0.0.1:5000';

    /**
     * Hides all message containers (response and error).
     */
    const hideMessages = () => {
        responseContainer.classList.add('hidden');
        errorContainer.classList.add('hidden');
    };

    /**
     * Displays a success message from the backend.
     * @param {string} message - The message to display.
     */
    const showSuccessMessage = (message) => {
        hideMessages();
        responseMessage.textContent = message;
        responseContainer.classList.remove('hidden');
    };

    /**
     * Displays an error message.
     * @param {string} message - The error message to display.
     */
    const showErrorMessage = (message) => {
        hideMessages();
        errorMessage.textContent = message;
        errorContainer.classList.remove('hidden');
    };

    /**
     * Handles the form submission event.
     * @param {Event} event - The form submission event.
     */
    const handleFormSubmit = async (event) => {
        event.preventDefault(); // Prevent the default form submission
        hideMessages();

        // --- Get Form Data ---
        const formData = new FormData(symptomForm);
        const name = formData.get('name');
        const age = formData.get('age');
        const symptoms = formData.get('symptoms');

        // --- Prepare for API Call ---
        submitButton.disabled = true;
        submitButton.textContent = 'Analyzing...';

        try {
            // --- Make the API Request ---
            const response = await fetch(`${BACKEND_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ name, age, symptoms }),
            });

            // --- Handle Non-OK Responses ---
            if (!response.ok) {
                // Try to get a specific error message from the backend
                const errorData = await response.json().catch(() => null);
                const detail = errorData ? errorData.error : `HTTP error! Status: ${response.status}`;
                throw new Error(detail);
            }

            // --- Handle Successful Responses ---
            const result = await response.json();
            if (result.status === 'success') {
                showSuccessMessage(result.message);
                symptomForm.reset(); // Clear the form on success
            } else {
                // Handle cases where the request succeeded but the app returned an error
                showErrorMessage(result.message || 'An unknown application error occurred.');
            }

        } catch (error) {
            // --- Handle Network or Fetch Errors ---
            console.error('Fetch Error:', error);
            showErrorMessage(`Could not connect to the backend. Please ensure it's running and accessible. Details: ${error.message}`);
        } finally {
            // --- Reset Button State ---
            submitButton.disabled = false;
            submitButton.textContent = 'Get Recommendation';
        }
    };

    // --- Event Listener ---
    symptomForm.addEventListener('submit', handleFormSubmit);
});
