import { CellView, cellWidth } from "./cell";
import * as client from "./client";
import { Panel } from "./controls";
import * as state from "./state";
import { Cell } from "./types";
import * as websocket from "./websocket";
import ReactFlow, {
  OnConnectStartParams,
  useEdgesState,
  useNodesState,
} from "react-flow-renderer";

export const Board = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<Cell>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<void>([]);
  const [onConnectStart, onConnectEnd] = createConnector();
  state.initSetNodes(setNodes);
  state.initSetEdges(setEdges);
  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      nodeTypes={nodeTypes}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnectStart={onConnectStart}
      onConnectEnd={onConnectEnd}
      onInit={() => websocket.connect()}
      zoomOnScroll={false}
      zoomOnPinch={false}
      zoomOnDoubleClick={false}
      onNodeDrag={(e, node) =>
        client.moveCell(node.id, node.position.x, node.position.y)
      }
    >
      <Panel />
    </ReactFlow>
  );
};

const nodeTypes = { cell: CellView };

const createConnector = () => {
  var startId: string | null = null;

  const onConnectStart = (
    event: React.MouseEvent,
    params: OnConnectStartParams
  ) => {
    startId = params.nodeId;
  };

  const onConnectEnd = (event: MouseEvent) => {
    const x = event.x - (window.innerWidth * cellWidth) / 100 / 2;
    const y = event.y;
    client.createCell(startId!, x, y);
  };

  return [onConnectStart, onConnectEnd] as [
    (event: React.MouseEvent, params: OnConnectStartParams) => void,
    (event: MouseEvent) => void
  ];
};
