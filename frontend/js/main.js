/**
 * IMAIRA+ Main Frontend Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // ── Scroll Reveal via IntersectionObserver ──
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    const observer = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add("visible"); observer.unobserve(e.target); } }),
      { threshold: 0.12 }
    );
    revealEls.forEach(el => observer.observe(el));
  }

  // ── Bento Scroll-Assembly (Apple / plastic.audio Butter-Smooth Lerp) ──
  const bentoSection = document.getElementById('bento-showcase');
  const bentoSticky = document.getElementById('bento-sticky');
  if (bentoSection && bentoSticky) {
    const c1 = document.getElementById('bento-c1');
    const c2 = document.getElementById('bento-c2');
    const c3 = document.getElementById('bento-c3');
    const c4 = document.getElementById('bento-c4');
    const c5 = document.getElementById('bento-c5');
    const c6 = document.getElementById('bento-c6');
    const boyContainer = document.getElementById('boy-container');
    const sketchImg = document.getElementById('boy-sketch-img');
    const colorImg = document.getElementById('boy-color-img');
    const boyGlow = document.getElementById('boy-glow');
    const boyRipple = document.getElementById('boy-ripple');
    const h1 = document.getElementById('bento-header-1');
    const h2 = document.getElementById('bento-header-2');
    const scrollText = document.getElementById('bento-scroll-text');

    let currentProgress = 0;
    let targetProgress = 0;
    let isTicking = false;

    function renderBento(p) {
      // Mobile fallback
      if (window.innerWidth < 1024) {
        if (sketchImg) sketchImg.style.opacity = '1';
        if (colorImg) colorImg.style.opacity = '0';
        return;
      }

      // Fast card rush-in: complete assembly within first 26% of scroll!
      const cardP = Math.min(1, p / 0.26);
      // Snappy quartic ease-out
      const ease = 1 - Math.pow(1 - cardP, 4);

      // Fast rush-in from wide perimeters with rotation and scale
      if (c1) {
        const x = -260 * (1 - ease);
        const y = -140 * (1 - ease);
        const rot = -7 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c1.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rot}deg) scale(${sc})`;
        c1.style.opacity = op.toFixed(3);
      }
      if (c2) {
        const x = -280 * (1 - ease);
        const y = 50 * (1 - ease);
        const rot = -4 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c2.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rot}deg) scale(${sc})`;
        c2.style.opacity = op.toFixed(3);
      }
      if (c3) {
        const y = 140 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c3.style.transform = `translate3d(-50%, ${y}px, 0) scale(${sc})`;
        c3.style.opacity = op.toFixed(3);
      }
      if (c4) {
        const x = 260 * (1 - ease);
        const y = -140 * (1 - ease);
        const rot = 7 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c4.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rot}deg) scale(${sc})`;
        c4.style.opacity = op.toFixed(3);
      }
      if (c5) {
        const x = 280 * (1 - ease);
        const y = 40 * (1 - ease);
        const rot = 5 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c5.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rot}deg) scale(${sc})`;
        c5.style.opacity = op.toFixed(3);
      }
      if (c6) {
        const x = 260 * (1 - ease);
        const y = 130 * (1 - ease);
        const rot = -5 * (1 - ease);
        const sc = 0.75 + 0.25 * ease;
        const op = Math.min(1, ease * 1.6);
        c6.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rot}deg) scale(${sc})`;
        c6.style.opacity = op.toFixed(3);
      }

      // Phase 2: Morph sketch to color (p from 0.28 to 0.72)
      const morphRaw = Math.max(0, Math.min(1, (p - 0.28) / 0.44));
      // Smoothstep interpolation
      const morph = morphRaw * morphRaw * (3 - 2 * morphRaw);

      if (sketchImg && colorImg) {
        sketchImg.style.opacity = (1 - morph).toFixed(3);
        colorImg.style.opacity = morph.toFixed(3);
      }

      // Parallax breathing scale on central boy
      if (boyContainer) {
        const boyScale = 0.90 + 0.10 * ease + 0.04 * morph;
        boyContainer.style.transform = `scale(${boyScale.toFixed(4)})`;
      }

      // Ambient aura and resonant ripple wave
      if (boyGlow) {
        boyGlow.style.opacity = (morph * 0.95).toFixed(3);
        boyGlow.style.transform = `scale(${(0.75 + 0.35 * morph).toFixed(3)})`;
      }
      if (boyRipple) {
        if (morph > 0.05 && morph < 0.95) {
          const ripScale = 0.6 + 1.4 * morph;
          const ripOp = Math.sin(morph * Math.PI) * 0.8;
          boyRipple.style.transform = `scale(${ripScale.toFixed(3)})`;
          boyRipple.style.opacity = ripOp.toFixed(3);
        } else {
          boyRipple.style.opacity = '0';
        }
      }

      // Crossfade headers
      if (h1 && h2) {
        const h1Op = Math.max(0, 1 - morph * 2.2);
        h1.style.opacity = h1Op.toFixed(3);
        h1.style.transform = `translateY(${-20 * morph}px)`;

        const h2Op = Math.max(0, Math.min(1, (morph - 0.25) * 1.8));
        h2.style.opacity = h2Op.toFixed(3);
        h2.style.transform = `translateY(${16 * (1 - morph)}px)`;
      }

      if (scrollText) {
        if (p > 0.65) {
          scrollText.textContent = "Walk in with confidence";
        } else {
          scrollText.textContent = "Scroll to see it come together";
        }
      }
    }

    // 60fps/120fps physics loop with inertia damping
    function tickPhysics() {
      const diff = targetProgress - currentProgress;
      if (Math.abs(diff) > 0.0008) {
        currentProgress += diff * 0.14; // smooth magnetic lerp
        renderBento(currentProgress);
        requestAnimationFrame(tickPhysics);
      } else {
        currentProgress = targetProgress;
        renderBento(currentProgress);
        isTicking = false;
      }
    }

    function onScrollUpdate() {
      const rect = bentoSection.getBoundingClientRect();
      const totalScroll = bentoSection.offsetHeight - window.innerHeight;
      if (totalScroll <= 0) return;

      const scrolled = -rect.top;
      targetProgress = Math.max(0, Math.min(1, scrolled / totalScroll));

      if (!isTicking) {
        isTicking = true;
        requestAnimationFrame(tickPhysics);
      }
    }

    window.addEventListener('scroll', onScrollUpdate, { passive: true });
    window.addEventListener('resize', onScrollUpdate, { passive: true });
    onScrollUpdate();
  }

  // ── Back to top button ──
  const backToTopBtn = document.getElementById('back-to-top');
  if (backToTopBtn) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 400) {
        backToTopBtn.style.opacity = '1';
        backToTopBtn.style.pointerEvents = 'auto';
      } else {
        backToTopBtn.style.opacity = '0';
        backToTopBtn.style.pointerEvents = 'none';
      }
    });
  }

  // ── Mobile Nav ──
  const mobileMenuBtn = document.getElementById("mobile-menu-toggle");
  const mobileNav = document.getElementById("mobile-nav");
  if (mobileMenuBtn && mobileNav) {
    mobileMenuBtn.addEventListener("click", () => mobileNav.classList.toggle("hidden"));
  }

  // ── Sidebar (dashboard pages) ──
  const openSidebar = document.getElementById("open-sidebar-btn");
  const mobileSidebarToggle = document.getElementById("mobile-sidebar-toggle");
  const closeSidebar = document.getElementById("close-sidebar-btn");
  const sidebar = document.getElementById("app-sidebar");
  if (openSidebar && sidebar) openSidebar.addEventListener("click", () => sidebar.classList.remove("-translate-x-full"));
  if (mobileSidebarToggle && sidebar) mobileSidebarToggle.addEventListener("click", () => sidebar.classList.remove("-translate-x-full"));
  if (closeSidebar && sidebar) closeSidebar.addEventListener("click", () => sidebar.classList.add("-translate-x-full"));

  // ── Smooth Scroll ──
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener("click", function(e) {
      const id = this.getAttribute("href");
      if (id === "#" || id.length <= 1) return;
      const el = document.querySelector(id);
      if (el) { e.preventDefault(); el.scrollIntoView({ behavior: "smooth", block: "start" }); }
    });
  });

  console.log("IMAIRA+ platform initialized.");
});
