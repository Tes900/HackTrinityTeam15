const form = document.getElementById('dispute-form');
const generateButton = document.getElementById('generate-button');
const responseElement = document.getElementById('response');

generateButton.addEventListener('click', async (event) => {
  event.preventDefault();

  responseElement.innerText = 'Generating letter, please wait...';

  const formData = new FormData(form);

  try {
    const response = await fetch('http://localhost:8000/generate-letter/', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Server error');
    }

    const data = await response.json();
    const letter = data.letter;

    responseElement.innerText = 'Letter generated successfully. Redirecting to editor...';

    // Store the letter in sessionStorage
    sessionStorage.setItem('generatedLetter', letter);

    // Redirect to the editor page
    window.location.href = 'editor.html';

  } catch (error) {
    console.error('Error generating letter:', error);
    responseElement.innerText = 'Error generating letter. Please try again later.';
  }
});
