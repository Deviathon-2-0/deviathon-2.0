tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary":           "#AA7000",
        "primary-hover":     "#917247",
        "primary-dim":       "#7A5000",
        "primary-subtle":    "#FBF3E0",
        "primary-border":    "#E8C97A",
        "secondary":         "#594300",
        "tertiary":          "#AA7000",
        "neutral":           "#7F766C",
        "bg-canvas":         "#FAF6EE",
        "bg-white":          "#FFFDF8",
        "surface-container": "#F2EBD8",
        "canvas-secondary":  "#F5EDD8",
        "text-main":         "#2C1F0E",
        "text-muted":        "#8C7B6B",
        "border-subtle":     "#E8DFD0",
        "metric-green":      "#4F6B2D",
        "metric-green-subtle":"#EFF4E8",
        "metric-purple":     "#8B5CF6",
        "metric-amber":      "#F5A623",
        "dark-canvas":       "#1A1208",
        "dark-surface":      "#251A0A",
        "dark-surface-2":    "#2E2010",
        "dark-border":       "#3D2E15"
      },
      fontFamily: {
        sans: ["Plus Jakarta Sans", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"]
      },
      borderRadius: {
        "2xl": "1.25rem",
        "3xl": "1.75rem",
        "4xl": "2.25rem"
      },
      boxShadow: {
        "soft":       "0 8px 30px -4px rgba(42,25,0,0.05), 0 2px 6px -1px rgba(42,25,0,0.03)",
        "card":       "0 2px 8px -2px rgba(42,25,0,0.05), 0 8px 24px -4px rgba(42,25,0,0.07)",
        "card-hover": "0 12px 32px -4px rgba(42,25,0,0.12)",
        "pill":       "0 4px 14px 0 rgba(170,112,0,0.28)",
        "glow-amber": "0 0 40px rgba(170,112,0,0.15)",
        "glow-coral": "0 0 40px rgba(170,112,0,0.15)"
      }
    }
  }
};
