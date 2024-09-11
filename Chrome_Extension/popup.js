// popup.js

function extractJobDescription() {
    return new Promise((resolve, reject) => {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.tabs.sendMessage(tabs[0].id, { action: "extractJobDescription" }, (response) => {
                if (chrome.runtime.lastError) {
                    reject(chrome.runtime.lastError);
                } else if (response && response.jobDescription) {
                    resolve(response.jobDescription);
                } else {
                    reject("No job description found.");
                }
            });
        });
    });
}
async function generateCoverLetter(resumeFile, jobDescription) {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('description', jobDescription);

    const loadingCircle = document.getElementById('loadingCircle');
    const coverLetterField = document.getElementById('coverLetter');

    try {
        // Show loading circle
        loadingCircle.style.display = 'block';
        coverLetterField.value = '';

        const response = await fetch('http://localhost:8000/generate', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            coverLetterField.value = result.cover_letter;
        } else {
            console.error('Failed to generate cover letter');
            coverLetterField.value = 'Failed to generate cover letter. Please try again.';
        }
    } catch (error) {
        console.error('Error generating cover letter:', error);
        coverLetterField.value = 'An error occurred. Please try again later.';
    } finally {
        // Hide loading circle
        loadingCircle.style.display = 'none';
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', async function() {
    const resumeUpload = document.getElementById('resumeUpload');
    const generateBtn = document.getElementById('generate-btn');
    const jobDescriptionField = document.getElementById('jobDescription');

    // Try to extract job description automatically
    try {
        const extractedJobDescription = await extractJobDescription();
        jobDescriptionField.value = extractedJobDescription;
    } catch (error) {
        console.error('Failed to extract job description:', error);
    }

    generateBtn.addEventListener('click', function() {
        const jobDescription = jobDescriptionField.value;
        const resumeFile = resumeUpload.files[0];

        if (jobDescription && resumeFile) {
            generateCoverLetter(resumeFile, jobDescription);
        } else {
            alert('Please enter a job description and upload a resume.');
        }
    });
});