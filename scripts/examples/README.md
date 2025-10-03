# Introduction

`examples` directory contains the scripts written during the course of development of the source code, mainly for the experimental purposes.

The scripts here are written both in Python 2 & 3 depending on their applications.

### Organization

```
|-- examples
  |-- read_position.py
  |-- UDPServer.py
  |-- UDPClient.py
  ...
```

- `read_postion.py`

  A simple python script to read the axes position of an Industrial Robot in degrees from *Maya/Mimic* plugin.

- `UDPServer.py`

  A simple UDP socket server communicates with the corresponding client.

- `UDPClient.py`

  A simple UDP socket client communicates with the corresponding server.
