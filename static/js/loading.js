// function delayedRedirect() {
//     // Sleep for 60 seconds (60,000 milliseconds)
//     setTimeout(function() {
//         // Redirect after the delay
//         window.location.href = '/music';  // Replace with the desired URL
//     }, 120000);  // 60,000 milliseconds = 60 seconds
// }
// // delayedRedirect();

function checkVideoStatus() {
    fetch("/checkEditing")
        .then(response => response.json())
        .then(data => {
            if (data.status === true) {
                // Redirect to success page when the video is processed
                window.location.href = "/music";
            } else {
                // Retry after a delay
                setTimeout(checkVideoStatus, 20000);
            }
        });
}
checkVideoStatus();