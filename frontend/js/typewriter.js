/**
 * Typewriter Animation Module
 * Cycles through headline phrases with typing and deleting effect.
 * Respects user's prefers-reduced-motion system preference.
 */
function initTypewriter(options = {}) {
  const words = options.words || ["Job Interviews", "Resume Checker", "Technical Rounds"];
  const targetId = options.targetId || "typewriter-text";
  const targetElement = document.getElementById(targetId);

  if (!targetElement) return;

  // Reduced motion check
  const prefersReducedMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReducedMotion) {
    targetElement.textContent = words[0];
    return;
  }

  let wordIndex = 0;
  let charIndex = words[0].length;
  let isDeleting = true; // start after full initial display
  const typingSpeed = options.typingSpeed || 90;
  const deletingSpeed = options.deletingSpeed || 50;
  const pauseBeforeDelete = options.pauseBeforeDelete || 1800;
  const pauseBeforeNextWord = options.pauseBeforeNextWord || 450;

  function tick() {
    const currentWord = words[wordIndex];

    if (isDeleting) {
      charIndex--;
      targetElement.textContent = currentWord.substring(0, charIndex);

      if (charIndex <= 0) {
        isDeleting = false;
        wordIndex = (wordIndex + 1) % words.length;
        setTimeout(tick, pauseBeforeNextWord);
        return;
      }
      setTimeout(tick, deletingSpeed);
    } else {
      charIndex++;
      targetElement.textContent = currentWord.substring(0, charIndex);

      if (charIndex === currentWord.length) {
        isDeleting = true;
        setTimeout(tick, pauseBeforeDelete);
        return;
      }
      setTimeout(tick, typingSpeed);
    }
  }

  // Initial pause before beginning deletion of initial word
  setTimeout(tick, pauseBeforeDelete);
}

// Auto-initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => initTypewriter());
} else {
  initTypewriter();
}
