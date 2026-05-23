window.addEventListener("scroll", () => {
    const nav = document.querySelector("nav");
    if (window.scrollY > 50) {
        nav.style.background = "rgba(11, 11, 15, 0.85)";
        nav.style.boxShadow = "0 4px 30px rgba(0, 0, 0, 0.5)";
    } else {
        nav.style.background = "transparent";
        nav.style.boxShadow = "none";
    }
});