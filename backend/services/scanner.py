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

async def run_command_ssh(cmd: str, conn=None) -> str:
    """Helper to run a shell command on an external Kali VM over SSH."""
    if not settings.KALI_HOST or not settings.KALI_USER or not settings.KALI_PASSWORD:
        return "Error: SSH credentials for Kali Linux are not fully configured in the .env file."
    
    host = settings.KALI_HOST
    user = settings.KALI_USER
    password = settings.KALI_PASSWORD
    port = settings.SSH_PORT

    try:
        logger.info(f"Running SSH command: {cmd}")
        # Use existing connection if provided, otherwise connect
        if conn:
            # Prepend go bin to PATH to prioritize newer tool versions
            full_command = f"export PATH=$HOME/go/bin:/usr/local/go/bin:$PATH; {cmd}"
            result = await conn.run(full_command, check=False, timeout=600.0)
        else:
            async with asyncssh.connect(host, port=port, username=user, password=password, known_hosts=None) as new_conn:
                full_command = f"export PATH=$HOME/go/bin:/usr/local/go/bin:$PATH; {cmd}"
                result = await new_conn.run(full_command, check=False, timeout=600.0) 
            
        if result.exit_status != 0:
            logger.error(f"SSH Command '{cmd}' failed (Exit {result.exit_status}). Stderr: {result.stderr}")
            return f"Error running command: {result.stderr or result.stdout}"
        logger.info(f"SSH command '{cmd}' completed successfully.")
        return result.stdout
    except asyncio.TimeoutError:
        logger.error(f"SSH command '{cmd}' timed out after 600s")
        return "Error: Remote command execution timed out after 600 seconds."
    except Exception as e:
        logger.error(f"SSH Exception running command '{cmd}': {e}")
        return f"SSH connection failed: {str(e)}"

async def run_command(cmd: str, conn=None) -> str:
    """Route command execution based on configuration."""
    if settings.KALI_HOST:
        return await run_command_ssh(cmd, conn=conn)
    return await run_command_local(cmd)

class ScannerService:
    @staticmethod
    async def run_nmap(target: str, conn=None) -> str:
        logger.info(f"Starting Nmap for {target}")
        return await run_command(f"nmap -F {target}", conn=conn)

    @staticmethod
    async def run_whatweb(target: str, conn=None) -> str:
        logger.info(f"Starting WhatWeb for {target}")
        return await run_command(f"whatweb {target}", conn=conn)

    @staticmethod
    async def run_subfinder(target: str, conn=None) -> str:
        logger.info(f"Starting Subfinder for {target}")
        # Improved domain extraction
        domain = target
        if "://" in target:
            domain = target.split("://")[1].split("/")[0].split(":")[0]
        else:
            domain = target.split("/")[0].split(":")[0]
        
        # Strip 'www.' if present for better results on root domain
        if domain.startswith("www."):
            domain = domain[4:]
            
        # Check if it's an IP
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            return "Skipping subfinder (target is an IP address, not a domain)."
            
        return await run_command(f"subfinder -d {domain} -silent", conn=conn)

    @staticmethod
    async def run_nikto(target: str, conn=None) -> str:
        logger.info(f"Starting Nikto for {target}")
        # Sanitize target - strip scheme and trailing slashes for nikto host
        hostname = target
        if "://" in target:
            hostname = target.split("://")[1].split("/")[0].split(":")[0]
        else:
            hostname = target.split("/")[0].split(":")[0]

        # -Tuning 1: Interesting files
        # -evasion 1: Random URL encoding
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        # Reduced maxtime to 180s and simplified for speed
        return await run_command(f'nikto -h {hostname} -Tuning 1 -maxtime 180s -nointeractive -evasion 1 -useragent "{ua}" -Ignore404', conn=conn)

    @staticmethod
    async def run_httpx(target: str, conn=None) -> str:
        logger.info(f"Starting HTTPX for {target}")
        # Add timeout and simplify to avoid hangs
        return await run_command(f"httpx -u {target} -title -status-code -silent -timeout 5 -retries 0", conn=conn)

    @staticmethod
    async def run_nuclei(target: str, conn=None) -> str:
        logger.info(f"Starting Nuclei for {target}")
        # Nuclei can be slow, but we'll use a silent fast scan
        # Use 'timeout' utility for tools that don't have native maxtime
        return await run_command(f"timeout 120s nuclei -u {target} -silent -severity low,medium,high,critical -timeout 5", conn=conn)

    @staticmethod
    async def run_amass(target: str, conn=None) -> str:
        logger.info(f"Starting Amass for {target}")
        domain = target
        if "://" in target:
            domain = target.split("://")[1].split("/")[0].split(":")[0]
        else:
            domain = target.split("/")[0].split(":")[0]
        
        if domain.startswith("www."):
            domain = domain[4:]
            
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            return "Skipping amass (target is an IP address)."
            
        # Passive mode is faster and doesn't require complex setup
        return await run_command(f"amass enum -passive -d {domain} -timeout 2", conn=conn)

    @staticmethod
    async def run_katana(target: str, conn=None) -> str:
        logger.info(f"Starting Katana for {target}")
        # -crawl-duration is the correct flag for katana
        return await run_command(f"katana -u {target} -silent -nc -jc -timeout 5 -crawl-duration 120s", conn=conn)

    @staticmethod
    async def run_gau(target: str, conn=None) -> str:
        logger.info(f"Starting GAU for {target}")
        domain = target
        if "://" in target:
            domain = target.split("://")[1].split("/")[0].split(":")[0]
        else:
            domain = target.split("/")[0].split(":")[0]
            
        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", domain):
            return "Skipping gau (target is an IP address)."
            
        return await run_command(f"gau {domain} --subs --timeout 5", conn=conn)

    @classmethod
    async def run_all_scans(cls, target: str, conn=None) -> dict:
        """Run all scans concurrently to save time."""
        results = await asyncio.gather(
            cls.run_nmap(target, conn=conn),
            cls.run_whatweb(target, conn=conn),
            cls.run_subfinder(target, conn=conn),
            cls.run_nikto(target, conn=conn),
            cls.run_httpx(target, conn=conn),
            cls.run_nuclei(target, conn=conn),
            cls.run_amass(target, conn=conn),
            cls.run_katana(target, conn=conn),
            cls.run_gau(target, conn=conn),
            return_exceptions=True
        )
        return {
            "nmap": results[0] if not isinstance(results[0], Exception) else str(results[0]),
            "whatweb": results[1] if not isinstance(results[1], Exception) else str(results[1]),
            "subfinder": results[2] if not isinstance(results[2], Exception) else str(results[2]),
            "nikto": results[3] if not isinstance(results[3], Exception) else str(results[3]),
            "httpx": results[4] if not isinstance(results[4], Exception) else str(results[4]),
            "nuclei": results[5] if not isinstance(results[5], Exception) else str(results[5]),
            "amass": results[6] if not isinstance(results[6], Exception) else str(results[6]),
            "katana": results[7] if not isinstance(results[7], Exception) else str(results[7]),
            "gau": results[8] if not isinstance(results[8], Exception) else str(results[8])
        }
