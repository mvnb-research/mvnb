import * as client from "./client";
import { Cell } from "./types";
import { python } from "@codemirror/lang-python";
import { Delete, PlayCircle } from "@mui/icons-material";
import { Card, CardActions, CardContent, IconButton } from "@mui/material";
import { Box } from "@mui/system";
import ReactCodeMirror from "@uiw/react-codemirror";
import { Handle, NodeProps, Position } from "react-flow-renderer";

export const CellView = (props: NodeProps<Cell>) => {
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
            disabled={!props.data.runnable}
          >
            <PlayCircle />
          </IconButton>
          <IconButton
            color="primary"
            onClick={() => client.deleteCell(props.id)}
            disabled={!props.data.deletable}
          >
            <Delete />
          </IconButton>
        </CardActions>
        <CardContent sx={{ pt: 0 }}>
          <ReactCodeMirror
            style={{ border: "1px solid rgba(0, 0, 0, 0.12)" }}
            basicSetup={{
              lineNumbers: false,
              highlightActiveLineGutter: false,
              highlightActiveLine: false,
              tabSize: 4
            }}
            value={props.data.source ?? ""}
            extensions={[python()]}
            editable={props.data.editable}
            onChange={(value, viewUpdate) => {
              client.updateCell(props.id, value);
            }}
          />
        </CardContent>
        {props.data.outputs.length > 0 && (
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
            {props.data.outputs.map((o) => {
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
