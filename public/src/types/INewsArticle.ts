import SentimentCategory from "./SentimentCategory";

export default interface INewsArticle {
  id: number;
  title: string;
  publisher: string;
  published: string; // Date in format 'dd-MM-yyyy hh:mm'
  overview: string;
  sentimentScore: number;
  sentimentCategory: SentimentCategory;
  url: string;
}
