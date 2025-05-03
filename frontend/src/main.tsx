import { PrimeReactProvider } from "primereact/api";
import { createRoot } from "react-dom/client";
import "primereact/resources/themes/viva-dark/theme.css";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <PrimeReactProvider>
    <App />
  </PrimeReactProvider>
);
