import { App } from "./app";
import "normalize.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

const app = <App />;

const div = document.getElementById("app");

const root = createRoot(div!);

root.render(<StrictMode>{app}</StrictMode>);
