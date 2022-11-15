import * as client from "./client";
import AddIcon from "@mui/icons-material/Add";
import SaveIcon from "@mui/icons-material/Save";
import { ButtonGroup, Card, IconButton } from "@mui/material";

export const Panel = () => (
  <Card
    variant="outlined"
    style={{ position: "absolute", top: 10, right: 10, zIndex: 99 }}
  >
    <ButtonGroup orientation="vertical">
      <IconButton color="primary">
        <SaveIcon />
      </IconButton>
      <IconButton color="primary" onClick={() => client.createCell(null)}>
        <AddIcon />
      </IconButton>
    </ButtonGroup>
  </Card>
);
