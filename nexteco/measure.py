"""
Power Measurement Profilers.

This module provides an abstraction layer for measuring the energy and
power footprint of external shell commands across different operating
systems using native system utilities.
"""

import re
import statistics
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class MeasurementResult:
    """
    Structured outcome of a power consumption measurement run.

    Attributes
    ----------
    command : str
        The literal command that was executed.
    duration_seconds : float
        Elapsed wall-clock time in seconds.
    average_power_watts : float, optional
        The measured average active power consumption in Watts.
    energy_joules : float, optional
        The deduced total energy consumption in Joules.
    samples_collected : int
        Number of power samples aggregated during the run.
    os_tool : str
        The underlying OS native tool used for profiling.
    warnings : List[str]
        Advisory warnings generated during the measurement lifecycle.
    """
    command: str
    duration_seconds: float
    average_power_watts: Optional[float]
    energy_joules: Optional[float]
    samples_collected: int
    os_tool: str
    warnings: List[str]

    def to_dict(self) -> dict:
        """
        Serialize the measurement outcome to a standard Python dictionary.

        Returns
        -------
        dict
            Dictionary representation of the measurement data.
        """
        return {
            "command": self.command,
            "duration_seconds": round(self.duration_seconds, 3),
            "average_power_watts": round(self.average_power_watts, 3)
            if self.average_power_watts is not None
            else None,
            "energy_joules": round(self.energy_joules, 3)
            if self.energy_joules is not None
            else None,
            "samples_collected": self.samples_collected,
            "os_tool": self.os_tool,
            "warnings": self.warnings,
        }


class BaseProfiler:
    """
    Abstract base class defining the contract for OS-specific power profilers.

    Attributes
    ----------
    samples_watts : list[float]
        Accumulated raw power readings.
    process : subprocess.Popen, optional
        The active subprocess running the target tool.
    running : bool
        Indicates whether the profiler is currently actively sampling.
    warnings : list[str]
        Collected irregularities or system limitations.
    """
    def __init__(self):
        self.samples_watts: List[float] = []
        self.process: Optional[subprocess.Popen] = None
        self.running = False
        self.warnings: List[str] = []

    def start(self) -> None:
        """
        Initialize and begin the measurement subprocess.

        Raises
        ------
        NotImplementedError
            If invoked on the abstract base class.
        """
        raise NotImplementedError

    def stop(self) -> None:
        """
        Terminate the background sampling subprocess cleanly.
        """
        self.running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def get_average_watts(self) -> Optional[float]:
        if not self.samples_watts:
            return None
        return statistics.mean(self.samples_watts)


class MacOSProfiler(BaseProfiler):
    """
    macOS specific power profiler using the native `powermetrics` utility.
    """
    def start(self) -> None:
        self.running = True
        cmd = ["sudo", "powermetrics", "--samplers", "cpu_power", "-i", "1000"]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            threading.Thread(target=self._read_output, daemon=True).start()
        except FileNotFoundError:
            self.warnings.append("sudo or powermetrics not found.")

    def _read_output(self) -> None:
        """
        Internal worker to consume the stdout stream of the `powermetrics` process.
        """
        if not self.process or not self.process.stdout:
            return

        # Matches Apple Silicon "Combined Power (CPU + GPU + ANE): 1025 mW"
        # Matches Intel "Package Power: 45.67 W"
        pattern_apple = re.compile(r"Combined Power .*?:\s+([\d.]+)\s*mW")
        pattern_intel = re.compile(r"Package Power:\s*([\d.]+)\s*W")

        for line in self.process.stdout:
            if not self.running:
                break

            match_apple = pattern_apple.search(line)
            if match_apple:
                milliwatts = float(match_apple.group(1))
                self.samples_watts.append(milliwatts / 1000.0)
                continue

            match_intel = pattern_intel.search(line)
            if match_intel:
                watts = float(match_intel.group(1))
                self.samples_watts.append(watts)


class LinuxProfiler(BaseProfiler):
    """
    Linux specific power profiler using the native `turbostat` utility.
    """
    def start(self) -> None:
        self.running = True
        # Try turbostat first
        cmd = ["sudo", "turbostat", "--quiet", "--show", "PkgWatt", "--interval", "1"]
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            threading.Thread(target=self._read_turbostat, daemon=True).start()
        except FileNotFoundError:
            self.warnings.append(
                "turbostat not found. powertop parsing not fully supported yet."
            )
            # Fallback to powertop could be implemented here

    def _read_turbostat(self) -> None:
        """
        Internal worker to consume the stdout stream of the `turbostat` process.
        """
        if not self.process or not self.process.stdout:
            return

        for line in self.process.stdout:
            if not self.running:
                break
            parts = line.strip().split()
            # Try to grab the first numeric column which represents PkgWatt
            if parts and parts[0].replace(".", "", 1).isdigit():
                try:
                    watts = float(parts[0])
                    self.samples_watts.append(watts)
                except ValueError:
                    pass


class WindowsProfiler(BaseProfiler):
    """
    Windows specific power profiler fallback.
    """
    def start(self) -> None:
        self.running = True
        # Windows powercfg/perfmon realtime metrics are highly hardware dependent.
        # This provides a scaffold using typeperf to measure Total Processor Power if available,
        # or defaults to warning.
        self.warnings.append(
            "Windows native CLI power streams (perfmon/powercfg) require hardware-specific counters. Returning placeholder data."
        )
        pass


def get_profiler() -> BaseProfiler:
    """
    Factory function to instantiate the correct profiler for the current operating system.

    Returns
    -------
    BaseProfiler
        An instance of an OS-specific subclass of BaseProfiler.
    """
    if sys.platform == "darwin":
        return MacOSProfiler()
    elif sys.platform == "linux":
        return LinuxProfiler()
    elif sys.platform == "win32":
        return WindowsProfiler()
    else:
        return BaseProfiler()


def measure_command(cmd_args: List[str]) -> MeasurementResult:
    """
    Execute a target shell command while simultaneously profiling its power consumption.

    Parameters
    ----------
    cmd_args : list[str]
        The command and arguments to aggressively profile.

    Returns
    -------
    MeasurementResult
        The deduced power and duration metrics wrapped into a result context.
    """
    profiler = get_profiler()

    # 1. Start the profiler (this may prompt for sudo)
    profiler.start()

    # Give a tiny delay if it needs to spin up or auth sudo (ideally user has auth'd caching or responds)
    time.sleep(0.5)

    # 2. Start the target command
    start_time = time.perf_counter()
    target_proc = None
    try:
        target_proc = subprocess.Popen(cmd_args)
        target_proc.wait()
    except KeyboardInterrupt:
        if target_proc:
            target_proc.terminate()
    except FileNotFoundError:
        profiler.warnings.append(f"Command not found: {cmd_args[0]}")
    finally:
        end_time = time.perf_counter()

    # 3. Stop profiler
    profiler.stop()

    duration = end_time - start_time
    avg_watts = profiler.get_average_watts()
    energy_joules = (avg_watts * duration) if avg_watts is not None else None

    tool_name = (
        "powermetrics"
        if sys.platform == "darwin"
        else ("turbostat" if sys.platform == "linux" else "perfmon/powercfg")
    )

    return MeasurementResult(
        command=" ".join(cmd_args),
        duration_seconds=duration,
        average_power_watts=avg_watts,
        energy_joules=energy_joules,
        samples_collected=len(profiler.samples_watts),
        os_tool=tool_name,
        warnings=profiler.warnings,
    )
