import asyncio
import asyncssh
import sys

async def test_ssh():
    try:
        async with asyncssh.connect('127.0.0.1', port=2222, username='kali', password='kali', known_hosts=None) as conn:
            result = await conn.run("echo 'Kali Connected Successfully'", check=True)
            print(result.stdout)
    except Exception as exc:
        print(f"SSH connection failed: {exc}", file=sys.stderr)

asyncio.run(test_ssh())
