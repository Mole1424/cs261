import {IUserData} from "./IUserData";
import {EventCallback} from "./AppEvent";

export interface IViewProps {
  user: IUserData;
  eventCallback: EventCallback;
}

export default IViewProps;
