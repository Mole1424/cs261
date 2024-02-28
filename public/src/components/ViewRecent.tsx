import {useEffect, useState} from "react";
import axios, {AxiosResponse} from "axios";
import INewsArticle from "../types/INewsArticle";
import ArticleCard from "./ArticleCard";

import "styles/view-cards.scss";
import IViewProps from "../types/IViewProps";

export const ViewRecent = ({ }: IViewProps) => {
  const [newsArticles, setNewsArticles] = useState<INewsArticle[]>([]);

  useEffect(() => {
    requestRecentNewsArticles()
      .then(response => {
        if (response) {
          setNewsArticles(response);
        } else {
          console.log("Failed to retrieve recent news articles");
        }
      });
  }, []);

  return (
    <main className={'content-recent content-cards'}>
      <div className={'cards'}>
        {newsArticles.map(article =>
          <ArticleCard key={article.id} article={article} />
        )}
      </div>
    </main>
  );
};

export default ViewRecent;

/**
 * Attempt to fetch recent news articles.
 */
export async function requestRecentNewsArticles() {
  try {
    const response = await axios.get('/news/recent') as AxiosResponse<INewsArticle[], unknown>;
    return response.data;
  } catch {
    return null;
  }
}
