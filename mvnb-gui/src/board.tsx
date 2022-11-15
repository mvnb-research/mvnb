import { Panel } from "./controls";
import { Cell } from "./message";
import * as state from "./state";
import * as websocket from "./websocket";
import ReactFlow, { useEdgesState, useNodesState } from "react-flow-renderer";

export const Board = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Cell>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<void>([]);
  state.initSetNodes(setNodes);
  state.initSetEdges(setEdges);
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onInit={() => websocket.connect()}
    >
      <Panel />
    </ReactFlow>
  );
};
