export interface ICbEvent {
  type: 'load-company' | 'misc';
}

export interface ILoadCompanyEvent extends ICbEvent {
  type: 'load-company';
  companyId: number;
}

export type EventCallback = (event: ICbEvent) => void;
