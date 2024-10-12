// lettergenscript.js

document.addEventListener('DOMContentLoaded', () => {
  // Grab all necessary DOM elements
  const form = document.getElementById('dispute-form');
  const generateButton = document.getElementById('generate-button');
  const responseElement = document.getElementById('response');
  const editorContainer = document.getElementById('editor-container');
  const quillEditorDiv = document.getElementById('quill-editor');
  const downloadPdfButton = document.getElementById('download-pdf-button');

  // Initialize Quill editor with the 'snow' theme
  const quill = new Quill('#quill-editor', {
    theme: 'snow'
  });

  // Check if all elements are present
  if (!form || !generateButton || !responseElement || !editorContainer || !quillEditorDiv || !downloadPdfButton) {
    console.error('One or more required DOM elements are missing.');
    return;
  }

  // Event listener for the Generate Letter button
  generateButton.addEventListener('click', async (event) => {
    event.preventDefault();

    // Disable the button to prevent multiple submissions
    generateButton.disabled = true;
    responseElement.innerText = 'Generating letter, please wait...';
    quill.setText(''); // Clear previous content
    editorContainer.scrollIntoView({ behavior: 'smooth' }); // Scroll to editor

    const formData = new FormData(form);

    try {
      // Send POST request to backend
      const response = await fetch('http://localhost:8000/generate-letter/', {
        method: 'POST',
        body: formData
      });

      // Check if response is OK
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Server error');
      }

      const data = await response.json();
      const letter = data.letter;

      // Update response message
      responseElement.innerText = 'Letter generated successfully. You can now edit it above.';

      // Load the generated letter into Quill editor
      quill.setText(letter);
      // Alternatively, if the letter contains HTML formatting, use:
      // quill.setContents(quill.clipboard.convert(letter));

    } catch (error) {
      console.error('Error generating letter:', error);
      responseElement.innerText = `Error generating letter: ${error.message}`;
    } finally {
      // Re-enable the button
      generateButton.disabled = false;
    }
  });

  // Event listener for the Download PDF button
  downloadPdfButton.addEventListener('click', async () => {
    // Get the edited content from Quill (in plain text or HTML)
    const editedContent = quill.getText().trim(); // Using plain text
    // If you prefer HTML, use:
    // const editedContent = quill.root.innerHTML;

    if (!editedContent) {
      alert('The letter is empty. Please generate and edit the letter before downloading.');
      return;
    }

    try {
      // Disable the button to prevent multiple submissions
      downloadPdfButton.disabled = true;
      responseElement.innerText = 'Generating PDF, please wait...';

      // Send the edited content to the backend to generate a PDF
      const response = await fetch('http://localhost:8000/generate-pdf/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ letter: editedContent })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Server error');
      }

      // Receive the PDF as a Blob
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

      responseElement.innerText = 'PDF generated and downloaded successfully.';
    } catch (error) {
      console.error('Error downloading PDF:', error);
      responseElement.innerText = `Error downloading PDF: ${error.message}`;
    } finally {
      // Re-enable the button
      downloadPdfButton.disabled = false;
    }
  });
});
