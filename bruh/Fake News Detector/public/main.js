async function postJson(path, body) {
  const res = await fetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const msg = await res.text().catch(()=>'');
    throw new Error(msg || ('HTTP '+res.status));
  }
  return res.json();
}

const resultEl = document.getElementById('result');
function badge(colorClass, text) {
  return `<span class="badge ${colorClass}"><span class="dot"></span>${text}</span>`;
}
function show(obj) {
  if (!obj || typeof obj !== 'object') {
    resultEl.textContent = String(obj);
    return;
  }
  const isFake = obj.predictedCategory === 'fake';
  const conf = undefined; // rules confidence removed
  const sentiment = obj.sentiment || {};
  const header = `Prediction: ${obj.predictedCategory || 'n/a'} ${conf ? `• Confidence: ${conf}` : ''}`;

  let html = '';
  html += `<div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">`;
  html += badge(isFake ? 'danger' : 'success', obj.predictedCategory || 'unknown');
  if (conf) html += badge('info', `confidence ${conf}`);
  html += `</div>`;

  if (obj.url) {
    html += `<div class="section-title">URL</div>`;
    html += `<div style="margin-bottom:8px;">${obj.url}</div>`;
  }

  if (obj.image || obj.imageName) {
    html += `<div class="section-title">Image</div>`;
    const imgSrc = obj.image || obj.imageName;
    html += `<div style="margin-bottom:8px;">`;
    html += `<img src="${imgSrc}" alt="Article Image" style="max-width:300px;max-height:200px;border-radius:6px;border:1px solid var(--border);background:#222;" />`;
    html += `</div>`;
  }

  if (obj.title) {
    html += `<div class="section-title">Article Title</div>`;
    html += `<div style="margin-bottom:8px;font-weight:500;">${obj.title}</div>`;
  }

  if (obj.datePublished) {
    html += `<div class="section-title">Date of Publication</div>`;
    html += `<div style="margin-bottom:8px;">${obj.datePublished}</div>`;
  }

  if (obj.author || obj.publisher) {
    html += `<div class="section-title">Source Information</div>`;
    html += `<div style="margin-bottom:8px;">`;
    if (obj.author) {
      html += `<div><strong>Author:</strong> ${obj.author}</div>`;
    }
    if (obj.publisher) {
      html += `<div><strong>Publisher:</strong> ${obj.publisher}</div>`;
    }
    html += `</div>`;
  }

  if (obj.description) {
    html += `<div class="section-title">Description</div>`;
    html += `<div style="margin-bottom:8px;opacity:.9;">${obj.description}</div>`;
  }

  if (obj.extractedText) {
    html += `<div class="section-title">Extracted Text</div>`;
    html += `<div style="margin-bottom:8px;opacity:.9;max-height:200px;overflow-y:auto;background:#0b1021;padding:8px;border-radius:6px;border:1px solid var(--border);">${obj.extractedText}</div>`;
  }

  // red flags removed (rules-based)

  if (obj.textPreview) {
    html += `<div class="section-title">Preview</div>`;
    html += `<div style="opacity:.9">${obj.textPreview}</div>`;
  }

  if (sentiment && (sentiment.compound != null)) {
    html += `<div class="section-title">Sentiment</div>`;
    html += `<div class="badges">
      ${badge('info', `compound ${sentiment.compound}`)}
      ${badge('info', `pos ${sentiment.pos}`)}
      ${badge('info', `neu ${sentiment.neu}`)}
      ${badge('info', `neg ${sentiment.neg}`)}
    </div>`;
  }

  // Raw JSON removed from UI
  resultEl.innerHTML = html;
}

document.getElementById('textForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = document.getElementById('textInput').value.trim();
  if (!text) { alert('Enter some text'); return; }
  show({ loading: true });
  try {
    const data = await postJson('/api/analyze', { text });
    show(data);
  } catch (err) {
    show({ error: err.message || String(err) });
  }
});

document.getElementById('urlForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const url = document.getElementById('urlInput').value.trim();
  if (!url) { alert('Enter a URL'); return; }
  show({ loading: true });
  try {
    const data = await postJson('/api/analyze-url', { url });
    show(data);
  } catch (err) {
    show({ error: err.message || String(err) });
  }
});

const imageInput = document.getElementById('imageInput');
const fileUploadArea = document.getElementById('fileUploadArea');
const imagePreview = document.getElementById('imagePreview');
const previewImg = document.getElementById('previewImg');
const removeImageBtn = document.getElementById('removeImage');

fileUploadArea.addEventListener('click', () => {
  imageInput.click();
});

fileUploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
  fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  fileUploadArea.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files.length > 0 && files[0].type.startsWith('image/')) {
    handleImageFile(files[0]);
  }
});

imageInput.addEventListener('change', (e) => {
  if (e.target.files.length > 0) {
    handleImageFile(e.target.files[0]);
  }
});

removeImageBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  clearImage();
});

function handleImageFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please select an image file');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    fileUploadArea.style.display = 'none';
    imagePreview.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

function clearImage() {
  imageInput.value = '';
  fileUploadArea.style.display = 'block';
  imagePreview.style.display = 'none';
  previewImg.src = '';
}

document.getElementById('imageForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  const file = imageInput.files[0];
  
  if (!file) {
    alert('Please select an image file');
    return;
  }

  show({ loading: true });
  
  try {
    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('/api/analyze-image', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const errorText = await response.text().catch(() => '');
      throw new Error(errorText || `HTTP ${response.status}`);
    }

    const data = await response.json();
    show(data);
  } catch (err) {
    show({ error: err.message || String(err) });
  }
});