export type Notebook = {
  cells: Cell[];
};

export type Cell = {
  id: string;
  source: string | null;
  parent: string | null;
  outputs: Output[];
  x: number | null;
  y: number | null;
};

export type Output = {
  type: string;
  data: string;
};

export type CreateCell = {
  user: string;
  cell: string;
  parent: string | null;
  x: number | null;
  y: number | null;
};

export type MoveCell = {
  user: string;
  cell: string;
  x: number | null;
  y: number | null;
};

export type DeleteCell = {
  user: string;
  cell: string;
};

export type Stdout = {
  user: string;
  cell: string;
  text: string;
};
