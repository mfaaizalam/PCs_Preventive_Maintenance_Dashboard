/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#0B1220",
          900: "#111827",
          800: "#1B2537",
          700: "#2A3548",
          600: "#3E4C63",
          500: "#5C6B84",
          400: "#8592A6",
          300: "#B4BECC",
          200: "#DCE1E8",
          100: "#EEF1F5",
          50: "#F6F8FA",
        },
        brand: {
          950: "#052024",
          900: "#08333A",
          800: "#0C4750",
          700: "#115763",
          600: "#166A78",
          500: "#1C8194",
          400: "#3FA0B2",
          300: "#7EC3D1",
          200: "#BFE3EA",
          100: "#E3F3F6",
          50: "#F1FAFB",
        },
        signal: {
          healthy: "#1C9A6C",
          healthyBg: "#E7F6EF",
          attention: "#C67E10",
          attentionBg: "#FDF2E1",
          critical: "#D33B3B",
          criticalBg: "#FCEAEA",
          offline: "#6B7688",
          offlineBg: "#EEF1F5",
        },
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        sans: ["'Inter'", "sans-serif"],
        mono: ["'IBM Plex Mono'", "monospace"],
      },
      boxShadow: {
        card: "0 1px 2px rgba(16, 24, 40, 0.04), 0 1px 3px rgba(16, 24, 40, 0.06)",
        cardHover: "0 4px 10px rgba(16, 24, 40, 0.08), 0 2px 4px rgba(16, 24, 40, 0.06)",
        panel: "0 1px 3px rgba(16,24,40,0.05)",
      },
      borderRadius: {
        xl2: "1.1rem",
      },
    },
  },
  plugins: [],
}
