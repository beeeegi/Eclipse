// looking for a file input change
document.getElementById('file-upload').addEventListener('change', function() {
    var fileInput = this;
    var fileNameSpan = document.getElementById('file-name');
    var fileSizeSpan = document.getElementById('file-size');
    var filePreviewImg = document.getElementById('file-preview');
    var fileInfo = document.getElementById('file-info');
    var file = fileInput.files[0];

    // when file is selected
    if (file) {
        // formatting size
        var fileSize = formatBytes(file.size);

        // file name and size
        fileNameSpan.textContent = `${file.name}`;
        fileSizeSpan.textContent = `${fileSize}`;
        fileInfo.style.display = 'block';

        // handle image files
        if (file.type.startsWith('image/')) {
            var reader = new FileReader();
            reader.onload = function(event) {
                filePreviewImg.src = event.target.result;
                filePreviewImg.style.display = 'inline';
            };
            reader.readAsDataURL(file);
        } else {
            filePreviewImg.style.display = 'none';
        }
    } else {
        fileInfo.style.display = 'none';
        filePreviewImg.style.display = 'none';
    }
});

// send files
function sendFileToServer(file) {
    const fileData = new FormData();
    fileData.append('file', file);

    // sending the file
    fetch('/upload', {
        method: 'POST',
        body: fileData
    })
    .then(response => response.json())
    .then(data => {
        // handle server response
        if (data.success) {
            showNotification('ფაილი წარმატებით გაიგზავნა!', '#27ae60');
            fetchUploadedFiles();
        } else if (data.error) {
            showNotification(data.error, '#e74c3c');
        } else {
            showNotification('ამოუცნობი ხარვეზი...', '#e74c3c');
        }
    })
    .catch(error => {
        console.error('დაფიქსირდა ხარვეზი:', error);
        showNotification('დაფიქსირდა ხარვეზი. გთხოვთ შეამოწმოთ კონსოლი.', '#e74c3c');
    });
}

// cd variable
let uploadCooldown = false;

// send button
document.getElementById('send-btn').addEventListener('click', function() {
    let fileInput = document.getElementById('file-upload');
    const file = fileInput.files[0];
    var filePreviewImg = document.getElementById('file-preview');
    var fileInfo = document.getElementById('file-info');

    // if file is selected
    if (file) {
        if (!uploadCooldown) {
            uploadCooldown = true; // setting cd to true
            sendFileToServer(file);

            // clearing file input after 3 sec
            setTimeout(function(){
                fileInput.value = null;
                fileInfo.style.display = 'none';
                filePreviewImg.style.display = 'none';    
            }, 3000);

            // reseting cd after 15sec
            setTimeout(() => {
                uploadCooldown = false;
            }, 15000);
        } else {
            showNotification('გთხოვთ მოიცადოთ!', '#ff9966');
        }
    } else {
        showNotification('გთხოვთ აირჩიოთ ასატვირთი ფაილი.', '#e74c3c');
    }
});

function displayUploadedFiles(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = ''; // clearing the file list

    // looking for new files
    if (files.length === 0) {
        fileList.innerHTML = '<tr><td colspan="4">თქვენ არ გაქვთ ატვირთული ფაილები.</td></tr>';
    } else {
        files.forEach((file) => {
            // format filesize
            const fileSize = parseInt(file.file_size, 10);
            const formattedSize = formatBytes(fileSize);

            const listItem = document.createElement('tr');
            const uploadDate = new Date(file.upload_time);
            const formattedDate = `${String(uploadDate.getDate()).padStart(2, '0')}/${String(uploadDate.getMonth() + 1).padStart(2, '0')}/${uploadDate.getFullYear()}`;

            // file details
            listItem.innerHTML = `
                <td>${file.file_name}</td>
                <td>${formattedSize}</td>
                <td>${formattedDate}</td>
                <td>
                    <a target="_blank" href="https://cdn.discordapp.com/attachments/${file.channel_id}/${file.attachment_id}/${file.file_name}">გადმოწერა</a>
                </td>
            `;
            fileList.appendChild(listItem);
            console.log(file);
        });
    }
}

// fetching uploaded files from the server
function fetchUploadedFiles() {
    fetch('/uploaded_files')
        .then(response => response.json())
        .then(files => {
            displayUploadedFiles(files);
        })
        .catch(error => {
            console.error('დაფიქსირდა ხარვეზი:', error);
            showNotification('დაფიქსირდა ხარვეზი. გთხოვთ შეამოწმოთ კონსოლი.', '#e74c3c');
        });
}

// toggle section visibility
function toggleSections() {
    const uploadSection = document.getElementById('upload-section');
    const library = document.getElementById('library');
    const switchBtn = document.getElementById('switch-btn');

    if (uploadSection.style.display === 'none') {
        uploadSection.style.display = 'block';
        library.style.display = 'none';
        switchBtn.textContent = 'ბიბლიოთეკა';
    } else {
        uploadSection.style.display = 'none';
        library.style.display = 'block';
        switchBtn.textContent = 'ატვირთვა';
        fetchUploadedFiles(); // fetching library when switching sections
    }
}

// notif function
function showNotification(message, color) {
    const notificationsContainer = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    notification.style.backgroundColor = color;

    notificationsContainer.appendChild(notification);

    // removing notif
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// formatting file size
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    if (isNaN(bytes) || bytes < 0) return 'Invalid size';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

// fetch the uploaded files on page load
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('library').style.display === 'block') {
        fetchUploadedFiles();
    }
});
