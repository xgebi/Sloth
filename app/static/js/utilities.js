function getCurrentTimezone(options) {
     for (const option of options) {
         if (option.value === Intl.DateTimeFormat().resolvedOptions().timeZone) {
             option.setAttribute("selected", "true");
         } else {
             option.removeAttribute("selected");
         }
     }
}