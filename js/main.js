function validate() {
  const outputElement = document.getElementById("output");
  const errorContainer = document.getElementById("error-container");
  const errorList = document.getElementById("error-list");

  try {
    const parser = new WebVTTParser();
    const inputText = outputElement.value;
    const tree = parser.parse(inputText, "subtitles/captions/descriptions");

    if (tree.errors && tree.errors.length > 0) {
      console.log("Validation errors:", tree.errors);
      outputElement.classList.remove("border-success");
      outputElement.classList.add("border-danger");

      // Show and populate error list
      errorContainer.style.display = "block";
      errorList.innerHTML = "";
      const errorCount = tree.errors.length;

      tree.errors.forEach((error, index) => {
        const button = document.createElement("button");
        button.className = "list-group-item list-group-item-action list-group-item-danger";
        button.innerHTML = `Line ${error.line}, character ${error.col} <br> ${error.message}`;
        button.onclick = () => selectLine(error.line);
        errorList.appendChild(button);
      });

      return false;
    } else {
      console.log("No validation errors");
      outputElement.classList.remove("border-danger");
      outputElement.classList.add("border-success");
      errorContainer.style.display = "none";
      return true;
    }
  } catch (error) {
    console.error("Validation error:", error);
    return false;
  }
}

function selectLine(lineNumber) {
  const textarea = document.getElementById("output");
  const lines = textarea.value.split("\n");

  if (lineNumber <= 0 || lineNumber > lines.length) return;

  // Calculate character positions for selection
  let startPos = 0;
  for (let i = 0; i < lineNumber - 1; i++) {
    startPos += lines[i].length + 1;
  }
  const endPos = startPos + lines[lineNumber - 1].length;

  // Select the text
  textarea.focus();
  textarea.setSelectionRange(startPos, endPos);

  // calculate scroll position
  const lineHeight = textarea.scrollHeight / lines.length;
  const padding = 2; // Number of lines padding from top
  const targetScrollTop = Math.max(0, (lineNumber - padding) * lineHeight);
  
  // don't scroll past the bottom
  const maxScroll = textarea.scrollHeight - textarea.clientHeight;
  textarea.scrollTop = Math.min(targetScrollTop, maxScroll);
}

function clearOutput() {
  document.getElementById("input-text").value = "";
  document.getElementById("output").value = "";
  document.getElementById("error-container").style.display = "none";
  const outputElement = document.getElementById("output");
  outputElement.classList.remove("border-danger", "border-success");
};

function downloadWebVTT() {
  const webvttText = document.getElementById("output").value;

  if (!webvttText || webvttText === "Please paste some text to convert.") {
    return;
  }

  let filename = prompt("Enter filename (will be saved as .vtt):", "transcript");
  
  // If user cancels prompt, abort download
  if (filename === null) return;
  
  // Sanitize filename: remove extension if provided and invalid characters
  filename = filename.replace(/\.[^/.]+$/, ""); // Strip any existing extension
  filename = filename.replace(/[^a-zA-Z0-9-_]/g, "_"); // Replace invalid chars with underscore
  
  if (!filename) filename = "transcript";
  
  const blob = new Blob([webvttText], { type: "text/vtt" });
  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `${filename}.vtt`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function convert() {
  const inputText = document.getElementById("input-text").value;
  const outputElement = document.getElementById("output");

  // Use the Python function
  const webvttText = window.pyConvertToWebVtt(inputText);
  outputElement.value = webvttText;
  validate();
  document.getElementById("tab-group").show("output");
}

document.addEventListener("DOMContentLoaded", () => {
  // validate on output on input so user can fix errors in real-time
  const outputElement = document.getElementById("output");
  outputElement.addEventListener("input", () => {
    setTimeout(validate, 100);
  });
});