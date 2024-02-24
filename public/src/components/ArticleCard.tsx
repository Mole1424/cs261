import INewsArticle from "../types/INewsArticle";
import {formatDate, getIconFromCategory} from "../util";

import LinkIcon from "assets/link.svg";
import "styles/article-card.scss";


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

