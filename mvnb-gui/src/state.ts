import { Cell, Output } from "./types";
import { Dispatch, SetStateAction } from "react";
import { Edge, Node } from "react-flow-renderer";

export const setNodes = (f: (nodes: Node<Cell>[]) => Node<Cell>[]) =>
  _setNodes!((ns) => {
    nodes = f(ns);
    return nodes;
  });

export const setEdges = (f: (edges: Edge<void>[]) => Edge<void>[]) =>
  _setEdges!(f);

export const setOutputs = (id: string, f: (edges: Output[]) => Output[]) => {
  _setOutputs.get(id)!.call(this, f);
};

export const setSource = (id: string, source: string) => {
  _setSource.get(id)!.call(this, (_) => source);
};

export const setEditable = (id: string) => {
  _setEditable.get(id)?.call(this, (_) => isEditable(id));
};

export const setRunnable = (id: string) => {
  _setRunnable.get(id)?.call(this, (_) => isRunnable(id));
};

export const setDeletable = (id: string) => {
  _setDeletable.get(id)?.call(this, (_) => isDeletable(id));
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

export const addSetEditable = (
  id: string,
  f: Dispatch<SetStateAction<boolean>>
) => {
  _setEditable.set(id, f);
};

export const addSetRunnable = (
  id: string,
  f: Dispatch<SetStateAction<boolean>>
) => {
  _setRunnable.set(id, f);
};

export const addSetDeletable = (
  id: string,
  f: Dispatch<SetStateAction<boolean>>
) => {
  _setDeletable.set(id, f);
};

export const removeSetSource = (id: string) => {
  _setSource.delete(id);
};

export const removeSetOutputs = (id: string) => {
  _setOutputs.delete(id);
};

export const isEditable = (id: string) => {
  for (const n of nodes) {
    if (n.id === id && 0 < n.data.outputs.length) {
      return false;
    }
  }
  return true;
};

export const isRunnable = (id: string): boolean => {
  for (const n of nodes) {
    if (n.id === id && 0 < n.data.outputs.length) {
      return false;
    }
  }
  const parent = nodes
    .filter((n) => n.id === id)
    .map((n) => n.data.parent)
    .at(0);
  if (parent) {
    return !isRunnable(parent);
  }
  return true;
};

export const isDeletable = (id: string) => {
  for (const n of nodes) {
    if (n.data.parent === id) {
      return false;
    }
  }
  return true;
};

var _setNodes = null as Dispatch<SetStateAction<Node<Cell>[]>> | null;

var _setEdges = null as Dispatch<SetStateAction<Edge<void>[]>> | null;

var _setSource = new Map<string, Dispatch<SetStateAction<string>>>();

var _setOutputs = new Map<string, Dispatch<SetStateAction<Output[]>>>();

var _setEditable = new Map<string, Dispatch<SetStateAction<boolean>>>();

var _setRunnable = new Map<string, Dispatch<SetStateAction<boolean>>>();

var _setDeletable = new Map<string, Dispatch<SetStateAction<boolean>>>();

var nodes: Node<Cell>[] = [];
