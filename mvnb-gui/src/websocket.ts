import { v4 as uuid } from "uuid";

export const connect = () => {
  webSocket = new WebSocket("ws://127.0.0.1:8000/message");
  webSocket.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    listener!(data._type, data);
  };
};

export const send = (data: any) => {
  data.user = userId;
  webSocket!.send(JSON.stringify(data));
};

export const setListener = (f: (type: string, data: any) => void) => {
  listener = f;
};

export const userId = uuid();

var webSocket = null as WebSocket | null;

var listener = null as ((type: string, data: any) => void) | null;
