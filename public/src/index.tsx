import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import Login from "./components/Login";

// Load APP_NAME
export const APP_NAME: string = (window as any).APP_NAME;

// Create root element
const root = createRoot(document.body);

// Prepare and render application
(async function () {
  // Check if a user is already signed in
  const userData = await Login.getCurrentUserData();

  root.render(
    <StrictMode>
        <App initialUser={userData} />
    </StrictMode>
  );
})();
