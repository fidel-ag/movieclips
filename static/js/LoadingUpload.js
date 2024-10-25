function delayedRedirect() {
    // Sleep for 60 seconds (60,000 milliseconds)
    setTimeout(function() {
        // Redirect after the delay
        window.location.href = '/create-lead';  // Replace with the desired URL
    }, 3000);  // 60,000 milliseconds = 60 seconds
}
delayedRedirect();