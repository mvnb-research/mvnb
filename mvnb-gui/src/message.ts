export type Notebook = {
  cells: Cell[];
};

export type Cell = {
  id: string;
  source: string | null;
  parent: string | null;
  outputs: Output[];
};

export type Output = {
  type: string;
  data: string;
};

export type CreateCell = {
  cell: string;
  parent: string | null;
};

export type DeleteCell = {
  cell: string;
};

export type Stdout = {
  cell: string;
  text: string;
};
