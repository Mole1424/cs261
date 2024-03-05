export interface ICbEvent {
  type: 'load-company' | 'load-article' | 'load-notifications' | 'misc';
}

export interface ILoadCompanyEvent extends ICbEvent {
  type: 'load-company';
  companyId: number;
}

export interface ILoadArticleEvent extends ICbEvent {
  type: 'load-article';
  articleId: number;
}

export type EventCallback = (event: ICbEvent) => void;

/** Parse hash string to event */
export function parseStringToEvent(str: string): ICbEvent | null {
  if (str.startsWith('company/')) {
    return {
      type: 'load-company',
      companyId: parseInt(str.substring(8))
    } as ILoadCompanyEvent;
  } else if (str.startsWith('article/')) {
    return {
      type: 'load-article',
      articleId: parseInt(str.substring(8))
    } as ILoadArticleEvent;
  } else {
    return null;
  }
}
