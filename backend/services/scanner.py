import asyncio
import logging
import asyncssh
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
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            logger.error(f"Command '{cmd}' failed with error: {stderr.decode()}")
            return f"Error running command: {stderr.decode()}"
        return stdout.decode()
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
            username=settings.KALI_USER, 
            password=settings.KALI_PASSWORD,
            known_hosts=None # Ignore known_hosts verification for local VMs
        ) as conn:
            result = await conn.run(cmd, check=False)
            if result.exit_status != 0:
                logger.error(f"SSH Command '{cmd}' failed. Stderr: {result.stderr}")
                return f"Error running command: {result.stderr}"
            return result.stdout
    except Exception as e:
        logger.error(f"SSH Exception running command '{cmd}': {e}")
        return f"SSH connection failed: {str(e)}"

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
        # Note: Subfinder usually needs to run against a domain, not a full URL or IP. 
        # For this PoC, we run it directly.
        return await run_command(f"subfinder -d {target} -silent")

    @staticmethod
    async def run_nikto(target: str) -> str:
        # Nikto can take a long time, we run a short tuned scan (-Tuning 1 for interesting files)
        return await run_command(f"nikto -h {target} -Tuning 1 -maxtime 60s")

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
