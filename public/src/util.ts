import SentimentCategory from "./types/SentimentCategory";
import FaceWinkIcon from "assets/face-wink.svg"
import FaceHappyIcon from "assets/face-happy.svg";
import FaceNeutralIcon from "assets/face-neutral.svg";
import FaceSadIcon from "assets/face-sad.svg";
import FaceAngryIcon from "assets/face-angry.svg";

export const formatDateTime = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    hour12: true
  }).format;

export const formatDate = new Intl.DateTimeFormat('en-US', {
    weekday: 'short',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  }).format;

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

export const formatNumber = (n: number) => n.toLocaleString("en-GB");

/** Capitalise the first character, lowercase the rest. */
export const capitalise = (s: string) => s[0].toUpperCase() + s.substring(1);

/** Create list of dates, with given start and end dates, spanning over `n` entries. Assume `end > start`.
 * Returned array: `[start, ..., end]`. */
export function createDateArray(start: Date, end: Date, count: number) {
  const delta = (end.valueOf() - start.valueOf()) / count;
  return Array.from({ length: count }, (_, i) => new Date(start.valueOf() + delta * i));
}
