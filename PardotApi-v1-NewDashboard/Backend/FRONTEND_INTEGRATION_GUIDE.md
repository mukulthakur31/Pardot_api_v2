# Frontend Integration Guide for Prospect Health Modal

## Issue Resolution
The PDF download button was showing the old PDF because the frontend needs to be updated to use the new modal system.

## Required Frontend Changes

### 1. **Update PDF Download Button Click Handler**

Instead of directly calling the PDF download, first show the modal:

```javascript
// OLD CODE (remove this):
function downloadDatabaseHealthPDF() {
    // Direct PDF download
    fetch('/download-pdf', {
        method: 'POST',
        body: JSON.stringify({
            data_type: 'database_health',
            data: databaseHealthData
        })
    });
}

// NEW CODE (implement this):
function downloadDatabaseHealthPDF() {
    // First get modal options
    fetch('/get-pdf-modal-options')
        .then(response => response.json())
        .then(modalOptions => {
            showPDFSelectionModal(modalOptions);
        });
}
```

### 2. **Create Modal Component**

```html
<!-- Add this modal HTML -->
<div id="pdfSelectionModal" class="modal" style="display: none;">
    <div class="modal-content">
        <div class="modal-header">
            <h3 id="modalTitle">Select Report Sections</h3>
            <span class="close" onclick="closePDFModal()">&times;</span>
        </div>
        <div class="modal-body">
            <p id="modalDescription"></p>
            <div id="sectionCheckboxes"></div>
        </div>
        <div class="modal-footer">
            <button onclick="closePDFModal()">Cancel</button>
            <button onclick="generateSelectedPDF()" class="btn-primary">Generate PDF</button>
        </div>
    </div>
</div>
```

### 3. **Modal JavaScript Functions**

```javascript
function showPDFSelectionModal(modalOptions) {
    const modal = document.getElementById('pdfSelectionModal');
    const title = document.getElementById('modalTitle');
    const description = document.getElementById('modalDescription');
    const checkboxContainer = document.getElementById('sectionCheckboxes');
    
    // Set modal content
    title.textContent = modalOptions.title;
    description.textContent = modalOptions.description;
    
    // Clear previous checkboxes
    checkboxContainer.innerHTML = '';
    
    // Create checkboxes for each section
    modalOptions.sections.forEach(section => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'checkbox-item';
        
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = section.id;
        checkbox.checked = section.default && section.enabled;
        checkbox.disabled = !section.enabled;
        
        const label = document.createElement('label');
        label.htmlFor = section.id;
        label.innerHTML = `
            <strong>${section.label}</strong>
            <br><small>${section.description}</small>
        `;
        
        checkboxDiv.appendChild(checkbox);
        checkboxDiv.appendChild(label);
        checkboxContainer.appendChild(checkboxDiv);
    });
    
    // Show modal
    modal.style.display = 'block';
}

function closePDFModal() {
    document.getElementById('pdfSelectionModal').style.display = 'none';
}

function generateSelectedPDF() {
    // Get selected sections
    const sections = {};
    const checkboxes = document.querySelectorAll('#sectionCheckboxes input[type="checkbox"]');
    
    checkboxes.forEach(checkbox => {
        sections[checkbox.id] = checkbox.checked;
    });
    
    // Generate PDF with selected sections
    fetch('/download-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            data_type: 'database_health',
            data: window.currentDatabaseHealthData, // Store this globally
            sections: sections
        })
    })
    .then(response => response.blob())
    .then(blob => {
        // Download the PDF
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'prospect_health_comprehensive_report.pdf';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    });
    
    // Close modal
    closePDFModal();
}
```

### 4. **Modal CSS Styling**

```css
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: #fefefe;
    margin: 10% auto;
    padding: 0;
    border: none;
    border-radius: 8px;
    width: 500px;
    max-width: 90%;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.modal-header {
    padding: 20px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #dee2e6;
    border-radius: 8px 8px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h3 {
    margin: 0;
    color: #1f2937;
}

.close {
    font-size: 24px;
    font-weight: bold;
    cursor: pointer;
    color: #6b7280;
}

.close:hover {
    color: #374151;
}

.modal-body {
    padding: 20px;
}

.checkbox-item {
    margin-bottom: 15px;
    padding: 10px;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    display: flex;
    align-items: flex-start;
}

.checkbox-item input[type="checkbox"] {
    margin-right: 12px;
    margin-top: 2px;
}

.checkbox-item label {
    cursor: pointer;
    flex: 1;
}

.checkbox-item:hover {
    background-color: #f9fafb;
}

.checkbox-item input[type="checkbox"]:disabled + label {
    color: #9ca3af;
    cursor: not-allowed;
}

.modal-footer {
    padding: 15px 20px;
    background-color: #f8f9fa;
    border-top: 1px solid #dee2e6;
    border-radius: 0 0 8px 8px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.modal-footer button {
    padding: 8px 16px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
    cursor: pointer;
}

.btn-primary {
    background-color: #3b82f6;
    color: white;
    border-color: #3b82f6;
}

.btn-primary:hover {
    background-color: #2563eb;
}
```

### 5. **Update Data Storage**

Make sure to store the database health data globally when fetched:

```javascript
// When fetching database health data
fetch('/get-prospect-health-data')
    .then(response => response.json())
    .then(data => {
        // Store globally for PDF generation
        window.currentDatabaseHealthData = data;
        
        // Display the data in your UI
        displayDatabaseHealthData(data);
    });
```

## API Endpoints Available

1. **GET `/get-pdf-modal-options`** - Get modal configuration
2. **POST `/download-pdf`** - Generate PDF (now supports sections parameter)
3. **GET `/get-prospect-health-data`** - Get complete prospect health data

## Testing the Integration

1. **Click PDF Download Button** → Should show modal
2. **Select/Deselect Sections** → Should enable/disable checkboxes
3. **Click Generate PDF** → Should download PDF with selected sections
4. **Modal Should Close** → After PDF generation

The modal will automatically disable sections that have no data and show which sections are available based on your current prospect health data.