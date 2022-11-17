export type Notebook = {
  cells: Cell[];
};

export type Cell = {
  id: string;
  source: string | null;
  parent: string | null;
  outputs: Output[];
  x: number;
  y: number;
  done: boolean;
  editable: boolean;
  runnable: boolean;
  deletable: boolean;
  loading: boolean;
};

export type Output = {
  id: string;
  type: string;
  data: string;
};

export type CreateCell = {
  user: string;
  cell: string;
  parent: string | null;
  x: number;
  y: number;
};

export type MoveCell = {
  user: string;
  cell: string;
  x: number;
  y: number;
};

export type RunCell = {
  user: string;
  cell: string;
};

export type UpdateCell = {
  user: string;
  cell: string;
  source: string;
};

export type DeleteCell = {
  user: string;
  cell: string;
};

export type Stdout = {
  id: string;
  user: string;
  cell: string;
  text: string;
};

export type RawData = {
  id: string;
  user: string;
  cell: string;
  type: string;
  data: string;
};
