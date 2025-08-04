document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const symptomForm = document.getElementById('symptom-form');
    const submitButton = document.getElementById('submit-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const buttonLoader = submitButton.querySelector('.loader');

    const resultView = document.getElementById('result-view');
    const responseContainer = document.getElementById('response-container');
    const severityText = document.getElementById('severity-text');
    const responseMessage = document.getElementById('response-message');
    
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
                // 1. Set the text for the recommendation and severity
                responseMessage.textContent = result.message;
                severityText.textContent = `Severity: ${result.severity}`;

                // 2. Reset the container's classes to remove old colors
                responseContainer.className = ''; 
                
                // 3. Add the new severity class to the WHOLE container for color-coding
                const severityClass = `severity-${result.severity.toLowerCase().replace(' ', '-')}`;
                responseContainer.classList.add(severityClass);

                // Show the results
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
