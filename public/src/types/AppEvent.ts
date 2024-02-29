export interface ICbEvent {
  type: 'load-company' | 'misc';
}

export interface ILoadCompanyEvent extends ICbEvent {
  type: 'load-company';
  companyId: number;
}

export type EventCallback = (event: ICbEvent) => void;

/** Parse hash string to event */
export function parseStringToEvent(str: string): ICbEvent | null {
  if (str.startsWith('company/')) {
    return {
      type: 'load-company',
      companyId: parseInt(str.substring(8))
    } as ILoadCompanyEvent;
  } else {
    return null;
  }
}
