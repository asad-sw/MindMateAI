document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const symptomForm = document.getElementById('symptom-form');
    const submitButton = document.getElementById('submit-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const buttonLoader = submitButton.querySelector('.loader');

    const resultView = document.getElementById('result-view');
    const responseMessage = resultView.querySelector('#response-message');
    const severityIndicator = document.getElementById('severity-indicator');
    
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    const newSubmissionButton = document.getElementById('new-submission-btn');

    // --- Backend API Configuration ---
    const BACKEND_URL = 'http://127.0.0.1:5000';

    const showLoader = () => {
        buttonText.textContent = 'Analyzing...';
        buttonLoader.classList.remove('hidden');
        submitButton.disabled = true;
    };

    const hideLoader = () => {
        buttonText.textContent = 'Get Recommendation';
        buttonLoader.classList.add('hidden');
        submitButton.disabled = false;
    };

    const handleFormSubmit = async (event) => {
        event.preventDefault();
        errorContainer.classList.add('hidden');
        showLoader();

        const formData = new FormData(symptomForm);
        const name = formData.get('name');
        const age = formData.get('age');
        const symptoms = formData.get('symptoms');

        try {
            const response = await fetch(`${BACKEND_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, age, symptoms }),
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            if (result.status === 'success') {
                // Handle both message and severity from the API response
                responseMessage.textContent = result.message;
                severityIndicator.textContent = `Severity: ${result.severity}`;
                
                // Reset classes and add the new one for color-coding
                severityIndicator.className = 'severity-indicator'; 
                severityIndicator.classList.add(`severity-${result.severity.toLowerCase().replace(' ', '-')}`);

                resultView.classList.remove('hidden');
                symptomForm.classList.add('hidden');
            } else {
                throw new Error(result.message || 'An unknown application error occurred.');
            }

        } catch (error) {
            errorMessage.textContent = `Error: ${error.message}`;
            errorContainer.classList.remove('hidden');
        } finally {
            hideLoader();
        }
    };

    const handleNewSubmission = () => {
        resultView.classList.add('hidden');
        symptomForm.reset();
        symptomForm.classList.remove('hidden');
    };

    symptomForm.addEventListener('submit', handleFormSubmit);
    newSubmissionButton.addEventListener('click', handleNewSubmission);
});
