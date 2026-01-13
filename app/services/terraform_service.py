import asyncio
import time
import secrets
from typing import Optional
from app.config import TERRAFORM_DIR, LIFETIME_SECONDS, VM_URL


class LabState:
    """Manages the state of the lab environment"""
    
    def __init__(self):
        self.execution_log = []
        self.execution_state = "IDLE"
        self.start_time: Optional[float] = None
        self.vm_url: Optional[str] = None
        self.vm_creds: Optional[dict] = None
    
    def log(self, msg: str):
        """Add a log message"""
        self.execution_log.append(msg)
    
    def reset(self):
        """Reset the lab state"""
        self.execution_log = []
        self.execution_state = "STARTING"
        self.start_time = None
        self.vm_url = None
        self.vm_creds = None
    
    def get_remaining_time(self) -> Optional[int]:
        """Calculate remaining time in seconds"""
        if self.start_time:
            return max(0, LIFETIME_SECONDS - int(time.time() - self.start_time))
        return None


# Global lab state instance
lab_state = LabState()


async def run_command(cmd: str):
    """Execute a terraform command asynchronously"""
    process = await asyncio.create_subprocess_shell(
        cmd,
        cwd=TERRAFORM_DIR,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT
    )

    async for line in process.stdout:
        lab_state.log(line.decode().rstrip())

    await process.wait()
    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


async def wait_with_timer(seconds: int):
    """Wait for specified seconds with early termination support"""
    for _ in range(seconds):
        await asyncio.sleep(1)
        if lab_state.execution_state not in ["RUNNING", "STOPPING"]:
            return
        if lab_state.execution_state == "STOPPING":
            lab_state.log("Stop signal received, terminating early")
            return


async def terraform_lifecycle():
    """Main terraform lifecycle: apply, wait, destroy"""
    vnc_password = secrets.token_urlsafe(10)

    try:
        lab_state.vm_creds = {
            "type": "VNC",
            "username": "kasm_user",
            "password": vnc_password
        }

        lab_state.execution_state = "APPLYING"
        lab_state.log(">>> terraform apply")
        await run_command(
            f'terraform apply -auto-approve '
            f'-var="vnc_password={vnc_password}"'
        )

        lab_state.execution_state = "RUNNING"
        lab_state.vm_url = VM_URL
        lab_state.start_time = time.time()

        await wait_with_timer(LIFETIME_SECONDS)

    except Exception as e:
        lab_state.log(f"ERROR: {str(e)}")
        lab_state.execution_state = "FAILED"

    finally:
        lab_state.execution_state = "DESTROYING"
        lab_state.log(">>> terraform destroy")
        try:
            await run_command(
                f'terraform destroy -auto-approve '
                f'-var="vnc_password={vnc_password}"'
            )
            lab_state.execution_state = "COMPLETED"
            lab_state.log("Cleanup completed successfully")
        except Exception as e:
            lab_state.log(f"DESTROY FAILED: {str(e)}")
            lab_state.execution_state = "DESTROY_FAILED"
            lab_state.log("Attempting force cleanup...")
            try:
                await run_command(
                    f'terraform destroy -auto-approve -refresh=false '
                    f'-var="vnc_password={vnc_password}"'
                )
                lab_state.execution_state = "COMPLETED"
                lab_state.log("Force cleanup successful")
            except:
                lab_state.log("Force cleanup also failed - manual intervention required")


async def force_destroy():
    """Force cleanup with dummy password"""
    lab_state.log("=== FORCE CLEANUP INITIATED ===")
    lab_state.execution_state = "DESTROYING"
    
    await run_command('terraform destroy -auto-approve -var="vnc_password=dummy"')
    
    lab_state.execution_state = "COMPLETED"
    lab_state.log("Force cleanup completed")
