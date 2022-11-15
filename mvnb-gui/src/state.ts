import { Cell } from "./message";
import { Dispatch, SetStateAction } from "react";
import { Edge, Node } from "react-flow-renderer";

export const setNodes = (f: (nodes: Node<Cell>[]) => Node<Cell>[]) =>
  _setNodes!(f);

export const setEdges = (f: (edges: Edge<void>[]) => Edge<void>[]) =>
  _setEdges!(f);

export const initSetNodes = (f: Dispatch<SetStateAction<Node<Cell>[]>>) => {
  _setNodes = f;
};

export const initSetEdges = (f: Dispatch<SetStateAction<Edge<void>[]>>) => {
  _setEdges = f;
};

var _setNodes = null as Dispatch<SetStateAction<Node<Cell>[]>> | null;

var _setEdges = null as Dispatch<SetStateAction<Edge<void>[]>> | null;
