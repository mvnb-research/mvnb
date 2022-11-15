export const connect = () => {
  webSocket = new WebSocket("ws://127.0.0.1:8000/message");
  webSocket.onmessage = (msg) => {
    const data = JSON.parse(msg.data);
    listener!(data._type, data);
  };
};

export const send = (data: any) => {
  webSocket!.send(JSON.stringify(data));
};

export const setListener = (f: (type: string, data: any) => void) => {
  listener = f;
};

var webSocket = null as WebSocket | null;

var listener = null as ((type: string, data: any) => void) | null;
