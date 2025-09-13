// see styles.css
export default {
  content: ["./**/*.html", "./**/*.css", "./**/*.jsx"],
  theme: {
    extend: {
      colors: {
        itbs_dark_red    : "#C4493F",
        itbs_light_red   : "#F49084",
        itbs_dark_orange : "#F5914A",
        itbs_light_orange: "#FBD19A",
        itbs_dark_blue   : "#40829B",
        itbs_light_blue  : "#80C3DC",
        itbs_dark_black  : "#38373A",
        itbs_light_black : "#889099",
        itbs_light_gray  : "#B2B2B2",
        itbs_white_blue  : "#EAF3FD"
      },
      fontFamily: {
        itbs_default: ["sans"]
      },
      fontSize: {
        itbs_title_small           : "24px",
        itbs_subtitle_small        : "20px",
        itbs_usual_text_small      : "16px",
        itbs_usual_text_bold_small : ["16px", { fontWeight: "700" }],
        itbs_annotation_small      : "12px",
        itbs_annotation_light_small: ["12px", { fontWeight: "200" }],
        // itbs_title_big            : "32px",
        // itbs_subtitle_big         : "24px",
        // itbs_usual_text_big       : "20px",
        // itbs_usual_text_bold_big  : ["20px", { fontWeight: "700" }],
        // itbs_annotation_big       : "16px",
        // itbs_annotation_light_big : ["16px", { fontWeight: "200" }]
      }
    }
  },
  // plugins: [require('tailwind-scrollbar')],
};