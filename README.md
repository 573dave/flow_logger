# Flow Logger

A lightweight Python function call logger that generates beautiful HTML reports with function call traces, system information, and performance metrics.

## Features
- Rapidly diagnose LLM requests or responses
- Beautiful Material Dark themed HTML reports
- Function call tracing with arguments and return values
- System resource monitoring
- Performance metrics
- Easy to use decorator syntax

## Installation
```bash
pip install flow_logger
```

## Usage
```python
from flow_logger import flow_logger

@flow_logger
def your_function(x, y):
    return x + y

result = your_function(2, 3)
# An HTML report will be generated when your program exits
```

## Example Output
![Report Screenshot](https://github.com/573dave/flow_logger/blob/main/FlowLogger.png?raw=true)

## Configuration
You can disable logging globally:
```
from flow_logger import FLOW_LOGGER_ENABLED
FLOW_LOGGER_ENABLED = False
```

## License
MIT License
Permission is hereby granted to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: none.

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
