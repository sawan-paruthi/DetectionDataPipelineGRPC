function toggleDropdown() {
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.toggle('open');
}

function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.dropdown-content input[type="checkbox"]:not(#selectAll)');

    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
    });
}

async function uploadVideo() {
    const input = document.getElementById('videoInput');
    const uploadButton = document.getElementById('uploadButton');
    const loadingText = document.getElementById('loadingText');
    const responseText = document.getElementById('responseText');
    const dropdown = document.querySelector('.dropdown');
    dropdown.classList.remove('open');

    if (!input.files.length) {
        alert("Please select a image to upload.");
        return;
    }

    // Get selected models from the checkboxes
    const checkboxes = document.querySelectorAll('.dropdown-content input[type="checkbox"]:checked:not(#selectAll)');
    const models = Array.from(checkboxes).map(checkbox => checkbox.value);

    if (models.length === 0) {
        alert("Please select at least one model.");
        return;
    }

    // Disable the upload button and show processing indicator
    uploadButton.disabled = true;
    uploadButton.textContent = "Uploading...";
    loadingText.style.display = 'block';
    
    responseText.textContent = "";

    const imageFile = input.files[0];
    const formData = new FormData();
    formData.append('image', imageFile);

    try {
        // Loop through each selected model and send the request sequentially
        for (const model of models) {
            formData.set('model', model); // Update model name in form data
            loadingText.textContent="Processing ... Currently Running  " + model;
            // Track start time for round-trip calculation
            const startTime = performance.now();

            const response = await fetch('/upload', {
                method: 'POST', 
                body: formData
            });

            const result = await response.json();
            console.log("result recived from 1st request");
            console.log(result)
            const endTime = performance.now();
            const roundTripTime = endTime - startTime; 
            result["service_name"] = model
            result["total_response_time"] = Number(roundTripTime.toFixed(4)); //adding response time to json response

            console.log(`Model: ${model}`);
            console.log('Response:', result);
            console.log('Round Trip Time:', roundTripTime.toFixed(2) + ' ms');



            // Log response and round-trip time for each model

            const logResponse = await fetch('/log_round_trip_time', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(result)
            });

            const logResult = await logResponse.json();
            console.log('Logging response:', logResult);
            console.log(logResult.success)

            // Display results for each model in the UI

            if(logResult.success){
                log_message = {message:result.message, logs: JSON.parse(logResult.message)} //logResult is a valid json string
            }else{
                log_message = {message:result.message, logs: logResult.message}
            }
                

            // responseText.textContent += `Model: ${model}\n\n` + 
            //                 // JSON.stringify(result)+'\n\n'+
            //                 JSON.stringify(log_message, null, 4) + 
            //                 '\n\n';

            responseText.textContent += 
                `Model: ${model}\n\n` + 
                `Message: ${result.message}\n\n` + 
                `Logs:\n` + JSON.stringify(log_message.logs, null, 4) + // Pretty print the logs with 4-space indentation
                '\n\n';
        }
    } catch (error) {
        console.error('Error:', error);
        alert("Error uploading video, please try again.");
    } finally {
        // Re-enable the upload button and hide the processing indicator
        uploadButton.disabled = false;
        uploadButton.textContent = "Upload";
        loadingText.style.display = 'none';
    }
}
