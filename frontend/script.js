document.addEventListener('DOMContentLoaded', () => {
    // --- DOM Element References ---
    const symptomForm = document.getElementById('symptom-form');
    const submitButton = document.getElementById('submit-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const buttonLoader = submitButton.querySelector('.loader');
    const symptomsTextarea = document.getElementById('symptoms');
    const languageSelect = document.getElementById('language'); // Language dropdown

    const resultView = document.getElementById('result-view');
    const responseContainer = document.getElementById('response-container');
    const severityText = document.getElementById('severity-text');
    const responseMessage = document.getElementById('response-message');
    
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    const newSubmissionButton = document.getElementById('new-submission-btn');

    const micButton = document.getElementById('mic-btn');
    const speakerButton = document.getElementById('speaker-btn');

    // --- Backend API Configuration ---
    const BACKEND_URL = 'http://127.0.0.1:5000';

    // --- Multi-language Support ---
    const translations = {
        English: {
            nameLabel: "Name",
            ageLabel: "Age",
            symptomsLabel: "Describe how you're feeling",
            namePlaceholder: "e.g., Ibrahim Fofanah",
            agePlaceholder: "e.g., 28",
            symptomsPlaceholder: "e.g., I've been feeling anxious and having trouble sleeping...",
            submitButton: "Get Recommendation",
            analyzing: "Analyzing...",
            newSubmission: "New Submission",
            recommendationTitle: "Recommendation",
            microphoneTooltip: "Click to speak your symptoms"
        },
        Spanish: {
            nameLabel: "Nombre",
            ageLabel: "Edad",
            symptomsLabel: "Describe cómo te sientes",
            namePlaceholder: "p. ej., Alex Pérez",
            agePlaceholder: "p. ej., 28",
            symptomsPlaceholder: "p. ej., Me he sentido ansioso/a y tengo problemas para dormir...",
            submitButton: "Obtener Recomendación",
            analyzing: "Analizando...",
            newSubmission: "Nueva Consulta",
            recommendationTitle: "Recomendación",
            microphoneTooltip: "Haz clic para hablar tus síntomas"
        },
        French: {
            nameLabel: "Nom",
            ageLabel: "Âge",
            symptomsLabel: "Décrivez comment vous vous sentez",
            namePlaceholder: "p. ex., Alex Dupont",
            agePlaceholder: "p. ex., 28",
            symptomsPlaceholder: "p. ex., Je me sens anxieux/se et j'ai des problèmes de sommeil...",
            submitButton: "Obtenir une Recommandation",
            analyzing: "Analyse en cours...",
            newSubmission: "Nouvelle Consultation",
            recommendationTitle: "Recommandation",
            microphoneTooltip: "Cliquez pour dire vos symptômes"
        },
        German: {
            nameLabel: "Name",
            ageLabel: "Alter",
            symptomsLabel: "Beschreiben Sie, wie Sie sich fühlen",
            namePlaceholder: "z.B., Alex Müller",
            agePlaceholder: "z.B., 28",
            symptomsPlaceholder: "z.B., Ich fühle mich ängstlich und habe Schlafprobleme...",
            submitButton: "Empfehlung Erhalten",
            analyzing: "Analysiere...",
            newSubmission: "Neue Anfrage",
            recommendationTitle: "Empfehlung",
            microphoneTooltip: "Klicken Sie, um Ihre Symptome zu sprechen"
        },
        Portuguese: {
            nameLabel: "Nome",
            ageLabel: "Idade",
            symptomsLabel: "Descreva como você está se sentindo",
            namePlaceholder: "ex., Alex Silva",
            agePlaceholder: "ex., 28",
            symptomsPlaceholder: "ex., Tenho me sentido ansioso/a e com problemas para dormir...",
            submitButton: "Obter Recomendação",
            analyzing: "Analisando...",
            newSubmission: "Nova Consulta",
            recommendationTitle: "Recomendação",
            microphoneTooltip: "Clique para falar seus sintomas"
        },
        Chinese: {
            nameLabel: "姓名",
            ageLabel: "年龄",
            symptomsLabel: "描述您的感受",
            namePlaceholder: "例如：张三",
            agePlaceholder: "例如：28",
            symptomsPlaceholder: "例如：我最近感到焦虑，睡眠有问题...",
            submitButton: "获取建议",
            analyzing: "分析中...",
            newSubmission: "新咨询",
            recommendationTitle: "建议",
            microphoneTooltip: "点击说出您的症状"
        }
    };

    // Function to update form language
    const updateFormLanguage = (language) => {
        const t = translations[language] || translations.English;
        
        // Update labels
        document.querySelector('label[for="name"]').textContent = t.nameLabel;
        document.querySelector('label[for="age"]').textContent = t.ageLabel;
        document.querySelector('label[for="symptoms"]').textContent = t.symptomsLabel;
        
        // Update placeholders
        document.getElementById('name').placeholder = t.namePlaceholder;
        document.getElementById('age').placeholder = t.agePlaceholder;
        document.getElementById('symptoms').placeholder = t.symptomsPlaceholder;
        
        // Update button text
        if (!submitButton.disabled) {
            buttonText.textContent = t.submitButton;
        }
        document.getElementById('new-submission-btn').textContent = t.newSubmission;
        
        // Update recommendation title
        const recTitle = document.querySelector('#response-container h2');
        if (recTitle) recTitle.textContent = t.recommendationTitle;
        
        // Update microphone tooltip
        const micButton = document.getElementById('mic-button');
        if (micButton) micButton.title = t.microphoneTooltip;
    };

    // --- Speech Recognition (Voice-to-Text) Setup ---
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition;

    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;
        
        // Update recognition language when dropdown changes
        languageSelect.addEventListener('change', () => {
            const langMap = { 
                'Spanish': 'es-ES', 
                'French': 'fr-FR', 
                'German': 'de-DE', 
                'English': 'en-US',
                'Portuguese': 'pt-PT',
                'Italian': 'it-IT',
                'Chinese': 'zh-CN',
                'Japanese': 'ja-JP',
                'Arabic': 'ar-SA',
                'Hindi': 'hi-IN'
            };
            recognition.lang = langMap[languageSelect.value] || 'en-US';
            
            // Update form language
            updateFormLanguage(languageSelect.value);
        });
        recognition.lang = 'en-US'; // Default

        recognition.onresult = (event) => {
            symptomsTextarea.value = event.results[0][0].transcript;
        };
        recognition.onspeechend = () => {
            recognition.stop();
            micButton.classList.remove('is-listening');
        };
        recognition.onerror = (event) => {
            console.error("Speech recognition error:", event.error);
            micButton.classList.remove('is-listening');
        };
    } else {
        if(micButton) micButton.style.display = 'none';
    }

    // --- Speech Synthesis (Text-to-Speech) Setup ---
    const synth = window.speechSynthesis;

    const showLoader = () => {
        const t = translations[languageSelect.value] || translations.English;
        buttonText.textContent = t.analyzing;
        buttonLoader.classList.remove('hidden');
        submitButton.disabled = true;
    };

    const hideLoader = () => {
        const t = translations[languageSelect.value] || translations.English;
        buttonText.textContent = t.submitButton;
        buttonLoader.classList.add('hidden');
        submitButton.disabled = false;
    };

    const handleFormSubmit = async (event) => {
        event.preventDefault();
        errorContainer.classList.add('hidden');
        showLoader();
        if (synth.speaking) synth.cancel();

        const formData = new FormData(symptomForm);
        const name = formData.get('name');
        const age = formData.get('age');
        const symptoms = formData.get('symptoms');
        const language = formData.get('language'); // Get selected language
        
        console.log(`Submitting form with language: ${language}`); // Debug log

        try {
            const response = await fetch(`${BACKEND_URL}/analyze`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                // Add language to the request payload
                body: JSON.stringify({ name, age, symptoms, language }),
            });
            
            console.log(`Request sent with language: ${language}`); // Debug log

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! Status: ${response.status}`);
            }

            const result = await response.json();
            if (result.status === 'success') {
                responseMessage.textContent = result.message;
                severityText.textContent = `Severity: ${result.severity}`;

                responseContainer.className = ''; 
                const severityClass = `severity-${result.severity.toLowerCase().replace(' ', '-')}`;
                responseContainer.classList.add(severityClass);

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
        if (synth.speaking) synth.cancel();
    };

    if (micButton) {
        micButton.addEventListener('click', () => {
            if (recognition) {
                recognition.start();
                micButton.classList.add('is-listening');
            }
        });
    }

    if (speakerButton) {
        speakerButton.addEventListener('click', () => {
            if (synth.speaking) {
                synth.cancel();
                return;
            }
            const textToSpeak = `${severityText.textContent}. ${responseMessage.textContent}`;
            const utterance = new SpeechSynthesisUtterance(textToSpeak);
            
            // Enhanced language mapping for TTS
            const ttsLangMap = { 
                'Spanish': 'es-ES', 
                'French': 'fr-FR', 
                'German': 'de-DE', 
                'English': 'en-US',
                'Portuguese': 'pt-PT',
                'Italian': 'it-IT',
                'Chinese': 'zh-CN',
                'Japanese': 'ja-JP',
                'Arabic': 'ar-SA',
                'Hindi': 'hi-IN'
            };
            utterance.lang = ttsLangMap[languageSelect.value] || 'en-US';
            
            // Set voice quality and rate
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            
            console.log(`Speaking in language: ${utterance.lang}`); // Debug log
            
            utterance.onerror = (event) => {
                console.error("Speech synthesis error:", event.error);
            };
            synth.speak(utterance);
        });
    }

    symptomForm.addEventListener('submit', handleFormSubmit);
    newSubmissionButton.addEventListener('click', handleNewSubmission);
    
    // Initialize default language
    updateFormLanguage('English');
});
