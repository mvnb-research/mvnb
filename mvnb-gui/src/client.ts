import * as state from "./state";
import {
  CreateCell,
  DeleteCell,
  MoveCell,
  Notebook,
  Output,
  Stdout,
  UpdateCell,
} from "./types";
import * as websocket from "./websocket";
import { v4 as uuid } from "uuid";

export const saveNotebook = () => {
  websocket.send({ _type: "SaveNotebook" });
};

export const createCell = (
  parent: string | null,
  x: number | null,
  y: number | null
) => {
  websocket.send({ _type: "CreateCell", cell: uuid(), parent: parent, x, y });
};

export const moveCell = (id: string, x: number | null, y: number | null) => {
  websocket.send({ _type: "MoveCell", cell: id, x: x, y: y });
};

export const deleteCell = (id: string) => {
  websocket.send({ _type: "DeleteCell", cell: id });
};

export const updateCell = (id: string, source: string) => {
  websocket.send({ _type: "UpdateCell", cell: id, source: source });
};

export const runCell = (id: string) => {
  websocket.send({ _type: "RunCell", cell: id });
};

const onMessage = (type: string, data: any) => {
  if (type === "Notebook") {
    for (const cell of (data as Notebook).cells) {
      createNode(cell.id, cell.parent, cell.x, cell.y, cell.source, cell.outputs);
      createEdge(cell.parent, cell.id);
    }
  } else if (type === "DidCreateCell") {
    const request = data.request as CreateCell;
    createNode(request.cell, request.parent, request.x, request.y, null, []);
    createEdge(request.parent, request.cell);
  } else if (type === "DidMoveCell") {
    const request = data.request as MoveCell;
    if (websocket.userId !== request.user) {
      moveNode(request.cell, request.x, request.y);
    }
  } else if (type === "DidUpdateCell") {
    const request = data.request as UpdateCell;
    if (websocket.userId !== request.user) {
      updateSource(request.cell, request.source);
      console.log(websocket.userId, request.user);
    }
  } else if (type === "DidDeleteCell") {
    const request = data.request as DeleteCell;
    deleteNode(request.cell);
    deleteEdge(request.cell);
  } else if (type === "Stdout") {
    console.log(data);
    const stdout = data as Stdout;
    state.setOutputs(stdout.cell, (os) => [
      ...os,
      { id: stdout.id, type: "text", data: stdout.text },
    ]);
  }
};

const createNode = (
  id: string,
  parent: string | null,
  x: number | null,
  y: number | null,
  source: string | null,
  outputs: Output[]
) => {
  state.setNodes((nodes) => {
    const type = "cell";
    const data = {
      id,
      parent,
      source: source ?? "",
      outputs: outputs,
      x: x!,
      y: y!,
    };
    const position = { x: x!, y: y! };
    return [...nodes, { id, data, type, position }];
  });
};

const moveNode = (id: string, x: number | null, y: number | null) => {
  state.setNodes((nodes) => {
    return nodes.map((n) => {
      if (n.id === id) {
        return { ...n, position: { x: x!, y: y! } };
      }
      return n;
    });
  });
};

const updateSource = (id: string, source: string) => {
  state.setSource(id, source);
};

const deleteNode = (id: string) => {
  state.setNodes((nodes) => {
    return nodes.filter((n) => n.id != id);
  });
};

const deleteEdge = (id: string) => {
  state.setEdges((edges) => {
    return edges.filter((e) => e.source != id && e.target != id);
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
