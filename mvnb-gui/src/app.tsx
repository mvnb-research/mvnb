import ReactFlow, { ReactFlowProvider } from "react-flow-renderer";

export const App = () => (
  <ReactFlowProvider>
    <div style={{ height: "100vh", width: "100vw" }}>
      <ReactFlow />
    </div>
  </ReactFlowProvider>
);
