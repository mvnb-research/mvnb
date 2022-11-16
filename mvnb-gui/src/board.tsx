import { CellView } from "./cell";
import * as client from "./client";
import { Panel } from "./controls";
import * as state from "./state";
import { Cell } from "./types";
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
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onInit={() => websocket.connect()}
      zoomOnScroll={false}
      zoomOnPinch={false}
      zoomOnDoubleClick={false}
      onNodeDragStop={(event, node) => {
        client.moveCell(node.id, node.position.x, node.position.y);
        console.log(event);
      }}
    >
      <Panel />
    </ReactFlow>
  );
};

const nodeTypes = { cell: CellView };
