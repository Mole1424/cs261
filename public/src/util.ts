import SentimentCategory from "./types/SentimentCategory";
import FaceWinkIcon from "assets/face-wink.svg"
import FaceHappyIcon from "assets/face-happy.svg";
import FaceNeutralIcon from "assets/face-neutral.svg";
import FaceSadIcon from "assets/face-sad.svg";
import FaceAngryIcon from "assets/face-angry.svg";

const dateFormatter = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  });

export const formatDate = dateFormatter.format;

/** Given the sentiment category, return the appropriate SVG icon string and class */
export function getIconFromCategory(category: SentimentCategory): [string, string] {
  switch (category) {
    case "Neutral":
      return [FaceNeutralIcon, ""];
    case "Positive":
      return [FaceHappyIcon, "style-green"];
    case "Very Positive":
      return [FaceWinkIcon, "style-green"];
    case "Negative":
      return [FaceSadIcon, "style-red"];
    case "Very Negative":
      return [FaceAngryIcon, "style-red"];
  }
}
