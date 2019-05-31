// a helper function: just grab DOM element
var el = x => document.getElementById(x);



// when u hit the upload to pick...
function showPicker(inputId) { el('file-input').click(); }



// when the image show up
function showPicked(input) {

    // display name
    el('upload-label').innerHTML = input.files[0].name;

    var reader = new FileReader();
    reader.onload = function (e) {
    // get src
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
    }
    reader.readAsDataURL(input.files[0]);
}

// when hit analyze....
function analyze() {
    // get file
    var uploadFiles = el('file-input').files;

    // alert if no file upload
    if (uploadFiles.length != 1) alert('Please select 1 file to analyze!');

    // display 'Analyzing...'
    el('analyze-button').innerHTML = 'Analyzing...';

    // open a Ajax post request
    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            var response = JSON.parse(e.target.responseText);
            el('result-label').innerHTML = `Result = ${response['result']}`;
        }
        el('analyze-button').innerHTML = 'Analyze';
    }

    // send to server
    var fileData = new FormData();
    fileData.append('file', uploadFiles[0]);
    xhr.send(fileData);
}