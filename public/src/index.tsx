import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import {getCurrentUserData} from "./components/Login";

// Load APP_NAME
export const APP_NAME: string = (window as any).APP_NAME;

const container = document.createElement("div");
container.id = "container";
document.body.appendChild(container);

// Create root element
const root = createRoot(container);

// Prepare and render application
(async function () {
  // Check if a user is already signed in
  const userData = await getCurrentUserData();

  // TODO change default tab to 'Recent'
  root.render(
    <StrictMode>
      <App initialUser={userData} defaultTab={'For You'} />
    </StrictMode>
  );
})();
