To active virtual Environments
```
source .venv/bin/activate
```

To install Requirements
```
pip install -r requirements-train.txt
```

## Installing training dependencies (WSL2)

Standard method, from a VS Code Remote-WSL terminal:

```bash
source .venv/bin/activate
pip install -r requirements-train.txt
```



### If VS Code repeatedly shows "Disconnected. Attempting to reconnect..."

This install pulls in torch plus a full split CUDA 13 toolkit (several
hundred-MB to multi-GB wheels). Heavy disk I/O while these unpack can
stall the VS Code Remote-WSL connection long enough that VS Code reports
WSL as disconnected, even though the underlying Linux VM and the install
itself are both fine. If this happens repeatedly, run the install as a
background process directly in Ubuntu instead, decoupled from VS Code's
connection entirely:

```bash
cd ~/projects/nepal-fintech-toolcall-qlora
source .venv/bin/activate
nohup pip install --no-cache-dir -r requirements-train.txt > install.log 2>&1 &
disown
```

Monitor progress from any Ubuntu terminal (VS Code's or a standalone
Ubuntu-24.04 window) without risk of interrupting the install:

```bash
tail -n 20 install.log
```

Check whether it has finished:

```bash
ps aux | grep pip
```

If only the `grep` line itself is listed, the process has exited. Confirm
it exited *successfully* (not crashed) by checking the end of the log:

```bash
tail -n 5 install.log
```

A successful run ends with a line starting `Successfully installed ...`
naming every package. An `ERROR:` block instead means it failed even
though the process also exited — don't rely on `ps aux` alone.

**Important:** this method only survives your terminal or VS Code
closing — it does **not** survive the PC sleeping or restarting, since
that shuts down the entire WSL virtual machine. Disable sleep
(Settings → System → Power & battery → "put my device to sleep" → Never)
and stay plugged in for the duration of a large install.