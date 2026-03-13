import asyncio
import logging
import asyncssh
import re
from core.config import settings

logger = logging.getLogger(__name__)

async def run_command_local(cmd: str) -> str:
    """Helper to run a shell command asynchronously and capture output locally."""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        # Add a global timeout for the whole command execution
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=600.0)
        
        if process.returncode != 0:
            err_msg = stderr.decode()
            logger.error(f"Command '{cmd}' failed with error: {err_msg}")
            return f"Error running command (Exit {process.returncode}): {err_msg}"
        return stdout.decode()
    except asyncio.TimeoutError:
        logger.error(f"Local command '{cmd}' timed out after 600s")
        return "Error: Command execution timed out after 600 seconds."
    except Exception as e:
        logger.error(f"Exception running command '{cmd}': {e}")
        return str(e)

async def run_command_ssh(cmd: str) -> str:
    """Helper to run a shell command on an external Kali VM over SSH."""
    if not settings.KALI_HOST or not settings.KALI_USER or not settings.KALI_PASSWORD:
        return "Error: SSH credentials for Kali Linux are not fully configured in the .env file."
    
    try:
        async with asyncssh.connect(
            settings.KALI_HOST,
            port=settings.SSH_PORT,
            username=settings.KALI_USER, 
            password=settings.KALI_PASSWORD,
            known_hosts=None
        ) as conn:
            # Nikto and Subfinder can take time, increased timeout via wait_for
            result = await asyncio.wait_for(conn.run(cmd, check=False), timeout=600.0)
            
            if result.exit_status != 0:
                logger.error(f"SSH Command '{cmd}' failed. Stderr: {result.stderr}")
                return f"Error running command: {result.stderr or result.stdout}"
            return result.stdout
    except asyncio.TimeoutError:
        logger.error(f"SSH command '{cmd}' timed out after 600s")
        return "Error: Remote command execution timed out after 600 seconds."
    except Exception as e:
        logger.error(f"SSH Exception running command '{cmd}': {e}")
        return f"SSH connection failed: {str(e)}"
    
    return "Error: Unknown SSH execution failure"

async def run_command(cmd: str) -> str:
    """Route command execution based on configuration."""
    if settings.KALI_HOST:
        return await run_command_ssh(cmd)
    return await run_command_local(cmd)

class ScannerService:
    @staticmethod
    async def run_nmap(target: str) -> str:
        # Basic fast scan for common ports
        return await run_command(f"nmap -F {target}")

    @staticmethod
    async def run_whatweb(target: str) -> str:
        # Basic whatweb scan
        return await run_command(f"whatweb {target}")

    @staticmethod
    async def run_subfinder(target: str) -> str:
        # Subfinder needs a domain (e.g. google.com). Strip http/https/paths.
        domain = target
        if "://" in target:
            domain = target.split("://")[1].split("/")[0].split(":")[0]
        
        # Check if it's an IP (subfinder doesn't work on raw IPs)
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            return "Skipping subfinder (target is an IP address, not a domain)."
            
        return await run_command(f"subfinder -d {domain} -silent")

    @staticmethod
    async def run_nikto(target: str) -> str:
        # maxtime 600s gives Nikto 10 minutes to find more vulnerabilities
        # -Tuning 1 focuses on finding interesting files (quickest valuable scan)
        return await run_command(f"nikto -h {target} -Tuning 1 -maxtime 600s")

    @classmethod
    async def run_all_scans(cls, target: str) -> dict:
        """Run all scans concurrently to save time."""
        results = await asyncio.gather(
            cls.run_nmap(target),
            cls.run_whatweb(target),
            cls.run_subfinder(target),
            cls.run_nikto(target)
        )
        return {
            "nmap": results[0],
            "whatweb": results[1],
            "subfinder": results[2],
            "nikto": results[3]
        }
