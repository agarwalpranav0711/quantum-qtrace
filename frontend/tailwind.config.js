/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        dark: {
          950: "#080C14",
          900: "#0D131F",
          850: "#121A2A",
          800: "#182236",
          750: "#1E2B44",
          700: "#273756",
          600: "#364A70",
          500: "#4B638F",
        },
        qtrace: {
          cyan: "#00E5FF",
          "cyan-dim": "#00B4D8",
          emerald: "#10B981",
          amber: "#F59E0B",
          rose: "#F43F5E",
          indigo: "#6366F1",
        },
      },
      fontFamily: {
        sans: [
          "Inter",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "JetBrains Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "Monaco",
          "Consolas",
          "monospace",
        ],
      },
      boxShadow: {
        glow: "0 0 15px -3px rgba(0, 229, 255, 0.15)",
        "glow-emerald": "0 0 15px -3px rgba(16, 185, 129, 0.2)",
        "glow-rose": "0 0 15px -3px rgba(244, 63, 94, 0.2)",
      },
    },
  },
  plugins: [],
};

