
<h1 align="center">Agent Tracker</h1>

<p align="center">
<img src="https://img.shields.io/badge/License-Apache_2.0-brightgreen.svg">
<img src="https://img.shields.io/github/languages/top/ostorlab/agent_tracker">
<img src="https://img.shields.io/github/stars/ostorlab/agent_tracker">
<img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg">
</p>

_Tracker is responsible for tracking a scan, e.g. its status, data queues._

---

<p align="center">
<img src="https://raw.githubusercontent.com/Ostorlab/agent_tracker/main/images/logo.png" alt="agent_tracker" />
</p>

This repository is an implementation of the default tracker agent. Tracker is a default agent needed to run a scan using the local runtime.

## Usage

Agent Tracker can be installed directly from the oxo agent store or built from this repository.

 ### Install directly from oxo agent store

 ```shell
 oxo agent install agent/ostorlab/tracker
 ```
The agent will be automatically installed and updated by simply passing `--install` flag:

```shell
oxo scan run --install --agent agent/ostorlab/tsunami ip 8.8.8.8
```

## License
[Apache](./LICENSE)
