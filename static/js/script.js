document.addEventListener("DOMContentLoaded", function() {
    // Get the menu toggle button and side navigation elements
    const menuToggle = document.getElementById("menuToggle");
    const sideNav = document.getElementById("sideNav");

    // Add event listener for the menu toggle button
    menuToggle.addEventListener("click", function() {
        sideNav.classList.toggle("open");
    });

    // Add event listener for the back button
    const backBtn = document.getElementById("backBtn");
    if (backBtn) {
        backBtn.addEventListener("click", function() {
            window.history.back();
        });
    }
});
