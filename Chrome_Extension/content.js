// content.js

function extractJobDescription() {
    // This is a basic example. You might need to adjust this based on the structure of the job posting websites you're targeting.
    innerbody = document.body.innerText
    console.log(innerbody);
    const jobDescriptionElement = document.querySelector('.job-description') || document.querySelector('[data-testid="jobDescriptionText"]');
    return jobDescriptionElement ? jobDescriptionElement.innerText : null;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "extractJobDescription") {
        const jobDescription = extractJobDescription();
        sendResponse({ jobDescription: jobDescription });
    }
});