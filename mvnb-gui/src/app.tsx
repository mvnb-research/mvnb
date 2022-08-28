import { Board } from "./board";
import { ReactFlowProvider } from "react-flow-renderer";

export const App = () => (
  <ReactFlowProvider>
    <div style={{ height: "100vh", width: "100vw" }}>
      <Board />
    </div>
  </ReactFlowProvider>
);
