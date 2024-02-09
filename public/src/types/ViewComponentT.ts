import {IUserData} from "./IUserData";
import React from "react";

/** Function signature of function in TabGroup. */
export type ViewComponentT = (user: IUserData) => React.JSX.Element;
