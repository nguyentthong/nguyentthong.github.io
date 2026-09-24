$(document).ready(function() {
    const mode_toggle = document.getElementById("light-toggle");

    mode_toggle.addEventListener("click", function() {
        toggleTheme(document.documentElement.getAttribute("data-theme"));
    });
});
