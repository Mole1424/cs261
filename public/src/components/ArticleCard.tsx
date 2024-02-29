import INewsArticle from "../types/INewsArticle";
import {formatDateTime, getIconFromCategory} from "../util";

import LinkIcon from "assets/link.svg";
import "styles/article-card.scss";
import axios, {AxiosResponse} from "axios";
import {headerFormData} from "../constants";


export const ArticleCard = ({ article }: { article: INewsArticle }) => {
  const [sentimentIcon, sentimentIconClass] = getIconFromCategory(article.sentimentCategory);
  const published = new Date(article.published);

  return <div className={'article-card'}>
    <span className={'article-title'}>{article.headline}</span>
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
      Published by {article.publisher} on {formatDateTime(published)}
    </span>
    <span className={'article-overview'}>
      {article.summary}
    </span>
  </div>;
};

export default ArticleCard;

/**
 * Attempt to fetch details on the given article.
 */
export async function requestArticle(articleId: number) {
  try {
    const response = await axios.post('/news/article', {
      id: articleId
    }, headerFormData) as AxiosResponse<{
      data?: INewsArticle;
      error: boolean;
    }, unknown>;
    return response.data;
  } catch {
    return null;
  }
}
