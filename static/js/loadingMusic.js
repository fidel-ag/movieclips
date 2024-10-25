
function checkVideoStatus() {
    fetch("/checkEditing")
        .then(response => response.json())
        .then(data => {
            if (data.status === true) {
                // Redirect to success page when the video is processed
                window.location.href = "/download";
            } else {
                // Retry after a delay
                setTimeout(checkVideoStatus, 20000);
            }
        });
}
checkVideoStatus();