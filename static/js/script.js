document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".menu-toggle");
  const nav = document.querySelector(".main-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
    });
  }
  document.querySelectorAll(".flash-close").forEach(button => {
    button.addEventListener("click", () => button.closest(".flash")?.remove());
  });
  document.querySelectorAll('input[type="number"]').forEach(input => {
    input.addEventListener("change", () => {
      const min = Number(input.min || 0);
      const max = Number(input.max || 99);
      let value = Number(input.value);
      if (!Number.isFinite(value)) value = min;
      input.value = Math.max(min, Math.min(max, value));
    });
  });
});
