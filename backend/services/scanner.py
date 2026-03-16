import asyncio
import logging
import asyncssh
import re
from core.config import settings

logger = logging.getLogger(__name__)

async def run_command_local(cmd: str, callback=None) -> str:
    """Helper to run a shell command asynchronously and capture output locally."""
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout_data = ""
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            decoded_line = line.decode(errors='replace')
            stdout_data += decoded_line
            if callback:
                await callback(decoded_line)
                
        await process.wait()
        
        if process.returncode != 0:
            stderr_data = (await process.stderr.read()).decode(errors='replace')
            err_msg = stderr_data
            logger.error(f"Command '{cmd}' failed with error: {err_msg}")
            return f"Error running command (Exit {process.returncode}): {err_msg}"
        return stdout_data
    except asyncio.TimeoutError:
        logger.error(f"Local command '{cmd}' timed out after 600s")
        return "Error: Command execution timed out after 600 seconds."
    except Exception as e:
        logger.error(f"Exception running command '{cmd}': {e}")
        return str(e)

async def run_command_ssh(cmd: str, conn=None, callback=None) -> str:
    """Helper to run a shell command on an external Kali VM over SSH."""
    if not settings.KALI_HOST or not settings.KALI_USER or not settings.KALI_PASSWORD:
        return "Error: SSH credentials for Kali Linux are not fully configured in the .env file."
    
    host = settings.KALI_HOST
    user = settings.KALI_USER
    password = settings.KALI_PASSWORD
    port = settings.SSH_PORT

    try:
        logger.info(f"Running SSH command: {cmd}")
        # Prepend go bin to PATH to prioritize newer tool versions
        full_command = f"export PATH=$HOME/go/bin:/usr/local/go/bin:$PATH; {cmd}"
        
        async def stream_output(connection):
            async with connection.create_process(full_command) as process:
                stdout_data = ""
                async for line in process.stdout:
                    stdout_data += line
                    if callback:
                        await callback(line)
                await process.wait()
                if process.returncode != 0:
                    stderr_data = await process.stderr.read()
                    logger.error(f"SSH Command '{cmd}' failed. Stderr: {stderr_data}")
                    return f"Error running command: {stderr_data or stdout_data}"
                return stdout_data

        if conn:
            return await stream_output(conn)
        else:
            async with asyncssh.connect(host, port=port, username=user, password=password, known_hosts=None) as new_conn:
                return await stream_output(new_conn)
                
    except Exception as e:
        logger.error(f"SSH Exception running command '{cmd}': {e}")
        return f"SSH connection failed: {str(e)}"

async def run_command(cmd: str, conn=None, callback=None) -> str:
    """Route command execution based on configuration."""
    if settings.KALI_HOST:
        return await run_command_ssh(cmd, conn=conn, callback=callback)
    return await run_command_local(cmd, callback=callback)

async def run_command(cmd: str, conn=None) -> str:
    """Route command execution based on configuration."""
    if settings.KALI_HOST:
        return await run_command_ssh(cmd, conn=conn)
    return await run_command_local(cmd)

class ScannerService:
    @staticmethod
    async def run_nmap(target: str, conn=None) -> str:
        logger.info(f"Starting Nmap for {target}")
        # Strip scheme for nmap target
        host = target.split("://")[-1].split("/")[0]
        # Run a comprehensive scan: Service versioning, default scripts, all ports, with aggressive timing
        return await run_command(f"nmap -sV -sC -T4 -p- {host}", conn=conn)

    @staticmethod
    async def run_whatweb(target: str, conn=None) -> str:
        logger.info(f"Starting WhatWeb for {target}")
        return await run_command(f"whatweb -v -a 3 {target}", conn=conn)

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
            
        return await run_command(f"subfinder -d {domain} -silent -all", conn=conn)

    @staticmethod
    async def run_nikto(target: str, conn=None) -> str:
        logger.info(f"Starting Nikto for {target}")
        # Sanitize target - strip scheme and trailing slashes for nikto host
        hostname = target
        if "://" in target:
            hostname = target.split("://")[1].split("/")[0].split(":")[0]
        else:
            hostname = target.split("/")[0].split(":")[0]

        # -evasion 1: Random URL encoding
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        # Removed Tuning for a fuller default scan to get real, substantial output. Maxtime increased for full evaluation.
        return await run_command(f'nikto -h {hostname} -maxtime 300s -nointeractive -evasion 1 -useragent "{ua}" -Ignore404', conn=conn)

    @staticmethod
    async def run_httpx(target: str, conn=None) -> str:
        logger.info(f"Starting HTTPX for {target}")
        # Added -tech-detect for much deeper fingerprinting
        return await run_command(f"httpx -u {target} -title -status-code -tech-detect -silent -timeout 5 -retries 0", conn=conn)

    @staticmethod
    async def run_nuclei(target: str, conn=None) -> str:
        logger.info(f"Starting Nuclei for {target}")
        # Extract templates for more specific, complex queries
        return await run_command(f"timeout 300s nuclei -u {target} -t cves/ -t vulnerabilities/ -t misconfiguration/ -t exposures/ -silent -severity low,medium,high,critical", conn=conn)

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
