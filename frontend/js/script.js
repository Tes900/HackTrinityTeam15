const form = document.getElementById('dispute-form');
const responseElement = document.getElementById('response');
const letterContainer = document.getElementById('letter-container');
const downloadPdfButton = document.getElementById('download-pdf-button');

let quill; // Declare quill variable

form.addEventListener('submit', async (event) => {
  event.preventDefault();

  responseElement.innerText = 'Generating letter, please wait...';
  letterContainer.style.display = 'none';

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

    responseElement.innerText = 'Letter generated successfully.';
    letterContainer.style.display = 'block';

    // Initialize Quill editor if not already initialized
    if (!quill) {
      quill = new Quill('#editor-container', {
        theme: 'snow'
      });
    }

    // Set the content of the editor
    quill.setText(letter);
  } catch (error) {
    console.error('Error generating letter:', error);
    responseElement.innerText = 'Error generating letter. Please try again later.';
  }
});

// Handle the Download as PDF button click
downloadPdfButton.addEventListener('click', async () => {
  const editedLetter = quill.getText(); // Get text content from Quill editor

  try {
    const response = await fetch('http://localhost:8000/generate-pdf/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ letter: editedLetter })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Server error');
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);

    // Create a temporary link to trigger the download
    const a = document.createElement('a');
    a.href = url;
    a.download = 'edited_letter.pdf';
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Error downloading PDF:', error);
    alert('Error downloading PDF. Please try again later.');
  }
});
