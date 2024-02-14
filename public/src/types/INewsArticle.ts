export type SentimentCategory = "very bad" | "bad" | "neutral" | "good" | "very good";

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
