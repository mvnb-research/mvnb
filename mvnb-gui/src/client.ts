import { CreateCell, Notebook } from "./message";
import * as state from "./state";
import * as websocket from "./websocket";
import { v4 as uuid } from "uuid";

export const createCell = (parent: string | null) => {
  websocket.send({ _type: "CreateCell", cell: uuid(), parent: parent });
};

const onMessage = (type: string, data: any) => {
  if (type === "Notebook") {
    for (const cell of (data as Notebook).cells) {
      createNode(cell.id, cell.parent);
      createEdge(cell.parent, cell.id);
    }
  } else if (type === "DidCreateCell") {
    const request = data.request as CreateCell;
    createNode(request.cell, request.parent);
    createEdge(request.parent, request.cell);
  }
};

const createNode = (id: string, parent: string | null) => {
  state.setNodes((nodes) => {
    const data = { id, parent, source: "", outputs: [] };
    const position = { x: 0, y: 0 };
    return [...nodes, { id, data, position }];
  });
};

const createEdge = (source: string | null, target: string) => {
  if (source) {
    const id = createEdgeId(source, target);
    state.setEdges((edges) => [...edges, { id, source, target }]);
  }
};

const createEdgeId = (source: string, target: string) => `${source}_${target}`;

websocket.setListener(onMessage);
