import { Cell, Output } from "./types";
import { Dispatch, SetStateAction } from "react";
import { Edge, Node } from "react-flow-renderer";

export const setNodes = (f: (nodes: Node<Cell>[]) => Node<Cell>[]) =>
  _setNodes!(f);

export const setEdges = (f: (edges: Edge<void>[]) => Edge<void>[]) =>
  _setEdges!(f);

export const setOutputs = (id: string, f: (edges: Output[]) => Output[]) => {
  _setOutputs.get(id)!.call(this, f);
};

export const setSource = (id: string, source: string) => {
  _setSource.get(id)!.call(this, source);
};

export const initSetNodes = (f: Dispatch<SetStateAction<Node<Cell>[]>>) => {
  _setNodes = f;
};

export const initSetEdges = (f: Dispatch<SetStateAction<Edge<void>[]>>) => {
  _setEdges = f;
};

export const addSetSource = (
  id: string,
  f: Dispatch<SetStateAction<string>>
) => {
  _setSource.set(id, f);
};

export const addSetOutputs = (
  id: string,
  f: Dispatch<SetStateAction<Output[]>>
) => {
  _setOutputs.set(id, f);
};

export const removeSetSource = (id: string) => {
  _setSource.delete(id);
};

export const removeSetOutputs = (id: string) => {
  _setOutputs.delete(id);
};

var _setNodes = null as Dispatch<SetStateAction<Node<Cell>[]>> | null;

var _setEdges = null as Dispatch<SetStateAction<Edge<void>[]>> | null;

var _setSource = new Map<string, Dispatch<SetStateAction<string>>>();

var _setOutputs = new Map<string, Dispatch<SetStateAction<Output[]>>>();
