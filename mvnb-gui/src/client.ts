import * as state from "./state";
import {
  Cell,
  CreateCell,
  DeleteCell,
  MoveCell,
  Notebook,
  RawData,
  RunCell,
  Stdout,
  UpdateCell,
} from "./types";
import * as websocket from "./websocket";
import { Node } from "react-flow-renderer";
import { v4 as uuid } from "uuid";

export const saveNotebook = () => websocket.send({ _type: "SaveNotebook" });

export const createCell = (parent: string | null, x: number, y: number) =>
  websocket.send({ _type: "CreateCell", cell: uuid(), parent: parent, x, y });

export const updateCell = (id: string, source: string) =>
  websocket.send({ _type: "UpdateCell", cell: id, source: source });

export const deleteCell = (id: string) =>
  websocket.send({ _type: "DeleteCell", cell: id });

export const moveCell = (id: string, x: number, y: number) =>
  websocket.send({ _type: "MoveCell", cell: id, x: x, y: y });

export const runCell = (id: string) =>
  websocket.send({ _type: "RunCell", cell: id });

const onMessage = (type: string, data: any) => {
  if (type === "Notebook") return didLoadNotebook(data);
  if (type === "Stdout") return didReceiveStdout(data);
  if (type === "RawData") return didReceiveRawData(data);
  if (type === "DidSaveNotebook") return didSaveNotebook(data.request);
  if (type === "DidCreateCell") return didCreateCell(data.request);
  if (type === "DidUpdateCell") return didUpdateCell(data.request);
  if (type === "DidDeleteCell") return didDeleteCell(data.request);
  if (type === "DidMoveCell") return didMoveCell(data.request);
  if (type === "DidRunCell") return didRunCell(data.request);
};

const didSaveNotebook = (_: void) => null;

const didLoadNotebook = (data: Notebook) => {
  state.setNodes((_) =>
    data.cells.map((cell) => {
      return {
        id: cell.id,
        type: "cell",
        position: { x: cell.x, y: cell.y },
        data: {
          id: cell.id,
          parent: cell.parent,
          source: cell.source,
          outputs: cell.outputs,
          x: cell.x,
          y: cell.y,
          done: cell.done,
          editable: false,
          runnable: false,
          deletable: false,
        },
      };
    })
  );
  state.setEdges((_) => {
    return data.cells
      .filter((cell) => cell.parent)
      .map((cell) => {
        return {
          id: createEdgeId(cell.parent!, cell.id),
          source: cell.parent!,
          target: cell.id,
        };
      });
  });
  updateButtons();
};

const didCreateCell = (request: CreateCell) => {
  state.setNodes((nodes) => {
    return [
      ...nodes,
      {
        id: request.cell,
        type: "cell",
        position: { x: request.x, y: request.y },
        data: {
          id: request.cell,
          parent: request.parent,
          source: "",
          outputs: [],
          x: request.x,
          y: request.y,
          done: false,
          editable: false,
          runnable: false,
          deletable: false,
        },
      },
    ];
  });
  if (request.parent) {
    const id = createEdgeId(request.parent, request.cell);
    const edge = { id, source: request.parent, target: request.cell };
    state.setEdges((edges) => [...edges, edge]);
  }
  updateButtons();
};

const didUpdateCell = (request: UpdateCell) => {
  state.setNodes((nodes) =>
    nodes.map((n) => {
      if (n.id === request.cell) {
        return {
          ...n,
          data: { ...n.data, source: request.source },
        };
      }
      return n;
    })
  );
};

const didDeleteCell = (data: DeleteCell) => {
  state.setNodes((nodes) => nodes.filter((node) => node.id !== data.cell));
  state.setEdges((edges) => {
    return edges.filter(
      (e) => e.source !== data.cell && e.target !== data.cell
    );
  });

  updateButtons();
};

const didMoveCell = (request: MoveCell) => {
  if (websocket.userId !== request.user) {
    state.setNodes((nodes) => {
      return nodes.map((n) => {
        if (n.id === request.cell) {
          const position = { x: request.x, y: request.y };
          return { ...n, position };
        }
        return n;
      });
    });
  }
};

const didRunCell = (request: RunCell) => {
  state.setNodes((ns) =>
    ns.map((n) => {
      if (n.id === request.cell) {
        return {
          ...n,
          data: {
            ...n.data,
            done: true,
          },
        };
      }
      return n;
    })
  );
  updateButtons();
};

const didReceiveStdout = (data: Stdout) => {
  state.setNodes((ns) =>
    ns.map((n) => {
      if (n.id === data.cell) {
        return {
          ...n,
          data: {
            ...n.data,
            outputs: [
              ...n.data.outputs,
              { id: data.id, type: "text", data: data.text },
            ],
          },
        };
      }
      return n;
    })
  );
};

const didReceiveRawData = (data: RawData) => {
  state.setNodes((ns) =>
    ns.map((n) => {
      if (n.id === data.cell) {
        return {
          ...n,
          data: {
            ...n.data,
            outputs: [
              ...n.data.outputs,
              { id: data.id, type: "image", data: data.data },
            ],
          },
        };
      }
      return n;
    })
  );
  console.log(data);
};

const updateButtons = () => {
  state.setNodes((nodes) =>
    nodes.map((node) => {
      return {
        ...node,
        data: {
          ...node.data,
          editable: isEditable(node.id, nodes),
          runnable: isRunnable(node.id, nodes),
          deletable: isDeletable(node.id, nodes),
        },
      };
    })
  );
};

const isRunnable = (id: string, nodes: Node<Cell>[]) => {
  for (const n of nodes) {
    if (n.id === id) {
      if (n.data.done) {
        return false;
      }
    }
  }
  const parent = nodes
    .filter((n) => n.id === id)
    .map((n) => n.data.parent)
    .at(0);
  for (const n of nodes) {
    if (n.id === parent) {
      return n.data.done;
    }
  }
  return true;
};

const isEditable = (id: string, nodes: Node<Cell>[]) => {
  for (const n of nodes) {
    if (n.id === id) {
      return !n.data.done;
    }
  }
  return false;
};

const isDeletable = (id: string, nodes: Node<Cell>[]) => {
  for (const n of nodes) {
    if (n.data.parent === id) {
      return false;
    }
  }
  return true;
};

const createEdgeId = (source: string, target: string) => `${source}_${target}`;

websocket.setListener(onMessage);
