import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        fpt: {
          orange: "#F26F21",
          orangeHover: "#D95A0E",
          orangeLight: "#FFF4ED",
          navy: "#0C2B4E",
          navyDark: "#071B33",
          navyLight: "#133E6E",
        },
      },
    },
  },
  plugins: [],
};
export default config;
