import asyncio
from app.config import TERRAFORM_DIR


async def initialize_terraform():
    """Initialize Terraform once at application startup"""
    print("Initializing Terraform...")
    try:
        process = await asyncio.create_subprocess_shell(
            "terraform init",
            cwd=TERRAFORM_DIR,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        async for line in process.stdout:
            print(line.decode().rstrip())
        await process.wait()
        if process.returncode != 0:
            raise RuntimeError("Terraform initialization failed")
        print("Terraform initialized successfully")
    except Exception as e:
        print(f"ERROR during initialization: {str(e)}")
        raise
