# Introduction

## Overview

`comm` directory contains the scripts to run Server/Client applications to send/receive data to/from Maya and the Robot. The scripts are written in Python3.8.

### Installation

For now, the scripts can be launched via command prompt/Powershell/terminal. In future, the scripts will be included in the software stack.

### Organization

```
|-- comm
  |-- MayaTcpNodeStream.py
  ...
```

- `MayaTcpNodeStream.py`

  This script connects to Maya `commandPort` to send/receive data. For now, localhost and hard-coded ports are used but in the future, they will be user-assigned.
