// Has to be in the head tag, otherwise a flicker effect will occur.

let toggleTheme = (theme) => {
  if (theme == "dark") {
    setTheme("light");
  } else {
    setTheme("dark");
  }
}


// Only an explicit toggle is saved, so visitors who never toggle keep following
// their system setting.
let setTheme = (theme, persist = true) =>  {
  transTheme();
  if (theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }
  else {
    document.documentElement.removeAttribute("data-theme");
  }
  if (persist) {
    localStorage.setItem("theme", theme);
  }
  
  // Updates the background of medium-zoom overlay.
  if (typeof medium_zoom !== 'undefined') {
    medium_zoom.update({
      background: getComputedStyle(document.documentElement)
          .getPropertyValue('--global-bg-color') + 'ee',  // + 'ee' for trasparency.
    })
  }
};


let transTheme = () => {
  document.documentElement.classList.add("transition");
  window.setTimeout(() => {
    document.documentElement.classList.remove("transition");
  }, 500)
}


let initTheme = (theme) => {
  if (theme !== "dark" && theme !== "light") {
    // No saved choice (or a stale value such as "undefined"): follow the system.
    const userPref = window.matchMedia;
    theme = userPref && userPref('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    setTheme(theme, false);
    return;
  }
  setTheme(theme);
}


initTheme(localStorage.getItem("theme"));
