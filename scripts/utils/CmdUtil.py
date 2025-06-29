import subprocess


def run(cmd: str, check: bool=True) -> subprocess.CompletedProcess[str]:
    """Run a shell command and return CompletedProcess."""
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if check and result.returncode != 0:
        raise subprocess.SubprocessError
    
    return result
