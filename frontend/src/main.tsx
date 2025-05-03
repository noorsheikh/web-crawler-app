import { PrimeReactProvider } from "primereact/api";
import { createRoot } from "react-dom/client";
import "primereact/resources/themes/viva-dark/theme.css";
import "/node_modules/primeflex/primeflex.css";
import "primeicons/primeicons.css";
import "primeflex/themes/primeone-dark.css";
import "./index.css";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <PrimeReactProvider>
    <App />
  </PrimeReactProvider>
);
