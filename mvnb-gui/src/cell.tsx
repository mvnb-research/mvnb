import * as client from "./client";
import { Cell } from "./message";
import * as state from "./state";
import { python } from "@codemirror/lang-python";
import { Delete, PlayCircle } from "@mui/icons-material";
import { ButtonGroup, Card, CardContent, IconButton } from "@mui/material";
import { Box } from "@mui/system";
import ReactCodeMirror from "@uiw/react-codemirror";
import { useState } from "react";
import { Handle, NodeProps, Position } from "react-flow-renderer";

export const CellView = (props: NodeProps<Cell>) => {
  const [source, setSource] = useState(props.data.source ?? "");
  const [outputs, setOutputs] = useState(props.data.outputs);
  state.addSetSource(props.id, setSource);
  state.addSetOutputs(props.id, setOutputs);
  return (
    <Box width={`${cellWidth}vw`}>
      <Handle type="target" position={Position.Top} />
      <Card>
        <ButtonGroup>
          <IconButton color="primary">
            <PlayCircle />
          </IconButton>
          <IconButton
            color="primary"
            onClick={() => client.deleteCell(props.id)}
          >
            <Delete />
          </IconButton>
        </ButtonGroup>
        <CardContent>
          <ReactCodeMirror
            value={source}
            extensions={[python()]}
            onChange={(value, viewUpdate) => setSource(value)}
          />
        </CardContent>
        {outputs.length > 0 && (
          <CardContent>
            {outputs.map((o) => {
              return <Box>{o.data}</Box>;
            })}
          </CardContent>
        )}
      </Card>
      <Handle type="source" position={Position.Bottom} />
    </Box>
  );
};

const cellWidth = 45;
