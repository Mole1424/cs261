import SentimentCategory from "./SentimentCategory";

export default interface INewsArticle {
  id: number;
  headline: string;
  publisher: string;
  published: string; // Date in format 'dd-MM-yyyy hh:mm'
  summary: string;
  sentimentScore: number;
  sentimentCategory: SentimentCategory;
  url: string;
}
