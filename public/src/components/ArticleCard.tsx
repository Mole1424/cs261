import INewsArticle, {SentimentCategory} from "../types/INewsArticle";

import FaceWinkIcon from "assets/face-wink.svg"
import FaceHappyIcon from "assets/face-happy.svg";
import FaceNeutralIcon from "assets/face-neutral.svg";
import FaceSadIcon from "assets/face-sad.svg";
import FaceAngryIcon from "assets/face-angry.svg";
import LinkIcon from "assets/link.svg";
import "styles/article-card.scss";
import {formatDate} from "../util";


export const ArticleCard = ({ article }: { article: INewsArticle }) => {
  const [sentimentIcon, sentimentIconClass] = getIconFromCategory(article.sentimentCategory);
  const published = new Date(article.published);

  return <div className={'article-card'}>
    <span className={'article-title'}>{article.title}</span>
    <span className={'article-sentiment'}>
      <img src={sentimentIcon} alt={article.sentimentCategory} className={'icon ' + sentimentIconClass} />
      <span>{article.sentimentScore}</span>
    </span>
    <span className={'article-link'}>
      <a target="_blank" href={article.url}>
        <img src={LinkIcon} className={'icon'} alt={'Visit news source'} />
      </a>
    </span>
    <span className={'article-about'}>
      Published by {article.publisher} on {formatDate(published)}
    </span>
    <span className={'article-overview'}>
      {article.overview}
    </span>
  </div>;
};

export default ArticleCard;

/** Given the sentiment category, return the appropriate SVG icon string and class */
export function getIconFromCategory(category: SentimentCategory): [string, string] {
  switch (category) {
    case "neutral":
      return [FaceNeutralIcon, ""];
    case "good":
      return [FaceHappyIcon, "style-green"];
    case "very good":
      return [FaceWinkIcon, "style-green"];
    case "bad":
      return [FaceSadIcon, "style-red"];
    case "very bad":
      return [FaceAngryIcon, "style-red"];
  }
}
