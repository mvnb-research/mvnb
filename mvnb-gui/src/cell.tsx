import * as client from "./client";
import * as state from "./state";
import { Cell } from "./types";
import { python } from "@codemirror/lang-python";
import { Delete, PlayCircle } from "@mui/icons-material";
import { Card, CardActions, CardContent, IconButton } from "@mui/material";
import { Box } from "@mui/system";
import ReactCodeMirror from "@uiw/react-codemirror";
import { useState } from "react";
import { Handle, NodeProps, Position } from "react-flow-renderer";

export const CellView = (props: NodeProps<Cell>) => {
  const [source, setSource] = useState(props.data.source ?? "");
  const [outputs, setOutputs] = useState(props.data.outputs);
  const [editable, setEditable] = useState(state.isEditable(props.id));
  const [runnable, setRunnable] = useState(state.isRunnable(props.id));
  const [deletable, setDeletable] = useState(state.isDeletable(props.id));
  state.addSetSource(props.id, setSource);
  state.addSetOutputs(props.id, setOutputs);
  state.addSetEditable(props.id, setEditable);
  state.addSetRunnable(props.id, setEditable);
  state.addSetDeletable(props.id, setDeletable);
  return (
    <Box width={`${cellWidth}vw`}>
      {props.data.parent != null && (
        <Handle type="target" position={Position.Top} />
      )}
      <Card variant="outlined">
        <CardActions disableSpacing={true}>
          <IconButton
            color="primary"
            onClick={() => client.runCell(props.id)}
            disabled={!runnable}
          >
            <PlayCircle />
          </IconButton>
          <IconButton
            color="primary"
            onClick={() => client.deleteCell(props.id)}
            disabled={!deletable}
          >
            <Delete />
          </IconButton>
        </CardActions>
        <CardContent sx={{ pt: 0 }}>
          <ReactCodeMirror
            value={source}
            extensions={[python()]}
            editable={editable}
            onChange={(value, viewUpdate) => {
              client.updateCell(props.id, value);
            }}
          />
        </CardContent>
        {outputs.length > 0 && (
          <CardContent
            sx={{
              fontFamily: "Monospace",
              fontSize: 14,
              pl: "20px",
              pr: "20px",
              pt: 0,
              pb: "16px",
              "&:last-child": { pb: "16px" },
            }}
          >
            {outputs.map((o) => {
              return <Box key={o.id}>{o.data}</Box>;
            })}
          </CardContent>
        )}
      </Card>
      <Handle type="source" position={Position.Bottom} />
    </Box>
  );
};

const cellWidth = 48;
