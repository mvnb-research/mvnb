import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { python } from "@codemirror/lang-python";
import CodeMirror from "@uiw/react-codemirror";
import "normalize.css";

const App = () => {
  return (
    <CodeMirror
      value="print('Hello, world!')"
      height="100vh"
      extensions={[python()]}
    />
  );
};

const app = <App />;

const div = document.getElementById("app");

const root = createRoot(div!);

root.render(<StrictMode>{app}</StrictMode>);
